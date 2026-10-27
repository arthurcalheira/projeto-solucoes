"""Integração com a WhatsApp Business Platform (Cloud API da Meta)."""

from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass
from typing import Any

import httpx2 as httpx

log = logging.getLogger(__name__)

GRAPH = "https://graph.facebook.com"


@dataclass(frozen=True)
class MensagemRecebida:
    id: str
    telefone: str
    tipo: str  # text, image, document, audio, ...
    nome_perfil: str = ""
    texto: str = ""  # corpo do texto ou legenda da mídia
    midia_id: str = ""
    mime: str = ""
    nome_arquivo: str = ""


def mascarar(telefone: str) -> str:
    """Telefone parcial para logs: não registre dados pessoais completos."""
    return f"{telefone[:4]}****{telefone[-2:]}" if len(telefone) > 6 else "****"


def assinatura_valida(corpo: bytes, cabecalho: str | None, segredo: str) -> bool:
    """Confere o cabeçalho X-Hub-Signature-256 que a Meta envia em cada webhook."""
    if not cabecalho or not cabecalho.startswith("sha256=") or not segredo:
        return False
    esperado = hmac.new(segredo.encode(), corpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, cabecalho.removeprefix("sha256="))


def extrair_mensagens(payload: dict[str, Any]) -> list[MensagemRecebida]:
    """Lê as mensagens recebidas de um webhook. Ignora avisos de entrega e leitura."""
    mensagens: list[MensagemRecebida] = []
    for entrada in payload.get("entry", []):
        for mudanca in entrada.get("changes", []):
            valor = mudanca.get("value", {})
            nomes = {
                c.get("wa_id"): c.get("profile", {}).get("name", "")
                for c in valor.get("contacts", [])
            }
            for m in valor.get("messages", []):
                tipo = m.get("type", "")
                midia = m.get(tipo, {}) if tipo in ("image", "document", "audio", "video", "sticker") else {}
                mensagens.append(MensagemRecebida(
                    id=m["id"],
                    telefone=m["from"],
                    tipo=tipo,
                    nome_perfil=nomes.get(m["from"], ""),
                    texto=m.get("text", {}).get("body", "") if tipo == "text" else midia.get("caption", ""),
                    midia_id=midia.get("id", ""),
                    mime=midia.get("mime_type", ""),
                    nome_arquivo=midia.get("filename", ""),
                ))
    return mensagens


class CanalWhatsApp:
    def __init__(self, token: str, phone_number_id: str, versao: str) -> None:
        self._phone_number_id = phone_number_id
        self._versao = versao
        self._http = httpx.AsyncClient(
            timeout=30.0, headers={"Authorization": f"Bearer {token}"}
        )

    async def enviar_texto(self, telefone: str, texto: str) -> None:
        url = f"{GRAPH}/{self._versao}/{self._phone_number_id}/messages"
        resposta = await self._http.post(url, json={
            "messaging_product": "whatsapp",
            "to": telefone,
            "type": "text",
            "text": {"body": texto},
        })
        if resposta.is_error:
            log.error("Falha ao enviar mensagem para %s: %s", mascarar(telefone), resposta.status_code)
        resposta.raise_for_status()

    async def baixar_midia(self, midia_id: str) -> tuple[bytes, str]:
        """Baixa uma mídia recebida. Devolve (conteúdo, tipo MIME)."""
        info = await self._http.get(f"{GRAPH}/{self._versao}/{midia_id}")
        info.raise_for_status()
        dados = info.json()
        arquivo = await self._http.get(dados["url"])
        arquivo.raise_for_status()
        return arquivo.content, dados.get("mime_type", "")

    async def fechar(self) -> None:
        await self._http.aclose()
