"""Servidor HTTP: webhook do WhatsApp e API simples para o painel do advogado.

Rodar: uvicorn app.main:app --port 8000
"""

from __future__ import annotations

import hmac
import json
import logging
from contextlib import asynccontextmanager

import anthropic
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Query, Request, Response

from .agente import AgenteTriagem
from .atendimento import Atendimento
from .avisos import Avisos, ConfigEmail
from .config import carregar_config
from .documentos import Arquivo
from .memoria import Memoria
from .painel import router as painel_router
from .prompt import montar_prompt_sistema
from .whatsapp import CanalWhatsApp, assinatura_valida, extrair_mensagens

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = carregar_config()
    canal = CanalWhatsApp(cfg.whatsapp_token, cfg.whatsapp_phone_number_id, cfg.whatsapp_api_versao)
    agente = AgenteTriagem(
        cliente=anthropic.AsyncAnthropic(),
        modelo=cfg.modelo,
        esforco=cfg.esforco,
        prompt_sistema=montar_prompt_sistema(cfg.escritorio),
    )
    memoria = Memoria(cfg.banco)
    email = ConfigEmail(
        cfg.smtp_host, cfg.smtp_porta, cfg.smtp_usuario, cfg.smtp_senha, cfg.aviso_email_de, cfg.aviso_email_para
    )
    avisos = Avisos(cfg.aviso_webhook_url, email, cfg.painel_url)
    app.state.cfg = cfg
    app.state.memoria = memoria
    app.state.arquivo = Arquivo(cfg.pasta_documentos, memoria)
    app.state.atendimento = Atendimento(
        agente, memoria, canal, avisos, cfg.escritorio.horario, app.state.arquivo, cfg.agrupar_segundos
    )
    if not cfg.painel_token:
        log.warning("PAINEL_TOKEN vazio: o painel e a API de casos ficam bloqueados")
    log.info("Agente pronto: escritório=%s modelo=%s", cfg.escritorio.nome, cfg.modelo)
    yield
    await canal.fechar()


app = FastAPI(title="Agente de triagem previdenciária", lifespan=lifespan)
app.include_router(painel_router)


@app.get("/saude")
async def saude() -> dict:
    return {"ok": True}


@app.get("/webhook")
async def verificar_webhook(
    request: Request,
    modo: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    desafio: str = Query("", alias="hub.challenge"),
) -> Response:
    """A Meta chama este endereço uma vez para confirmar que o webhook é seu."""
    esperado = request.app.state.cfg.whatsapp_verify_token
    if modo == "subscribe" and esperado and hmac.compare_digest(token, esperado):
        return Response(content=desafio, media_type="text/plain")
    raise HTTPException(status_code=403)


@app.post("/webhook")
async def receber_webhook(
    request: Request,
    tarefas: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
) -> dict:
    corpo = await request.body()
    if not assinatura_valida(corpo, x_hub_signature_256, request.app.state.cfg.whatsapp_app_secret):
        raise HTTPException(status_code=401, detail="Assinatura inválida")
    # Responde logo (a Meta reenvia se demorar) e processa em segundo plano.
    for msg in extrair_mensagens(json.loads(corpo)):
        tarefas.add_task(request.app.state.atendimento.receber, msg)
    return {"ok": True}


def _checar_painel(request: Request, token: str | None) -> None:
    esperado = request.app.state.cfg.painel_token
    if not esperado or not token or not hmac.compare_digest(token, esperado):
        raise HTTPException(status_code=401)


@app.get("/casos")
async def listar_casos(request: Request, x_painel_token: str | None = Header(default=None)) -> list[dict]:
    _checar_painel(request, x_painel_token)
    return request.app.state.memoria.listar_casos()


@app.post("/casos/{telefone}/devolver-ao-agente")
async def devolver_ao_agente(telefone: str, request: Request, x_painel_token: str | None = Header(default=None)) -> dict:
    """Depois que a equipe resolveu, o agente volta a responder este contato."""
    _checar_painel(request, x_painel_token)
    request.app.state.atendimento.devolver_ao_agente(telefone)
    return {"ok": True}


@app.delete("/casos/{telefone}")
async def apagar_caso(telefone: str, request: Request, x_painel_token: str | None = Header(default=None)) -> dict:
    """Apaga todos os dados guardados do contato (pedido de exclusão pela LGPD)."""
    _checar_painel(request, x_painel_token)
    caminhos = request.app.state.memoria.apagar_conversa(telefone)
    Arquivo.apagar(caminhos)
    return {"ok": True}
