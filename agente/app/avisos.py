"""Avisa a equipe do escritório quando um caso fica pronto ou precisa de humano.

Dois canais, ambos opcionais:
- e-mail (SMTP), com nome, assunto, prioridade e o link do caso no painel.
  Por segurança (LGPD), o e-mail não leva o resumo nem dados de saúde;
- webhook (POST com a ficha completa), para n8n, Make, Slack etc.
"""

from __future__ import annotations

import asyncio
import logging
import smtplib
from dataclasses import dataclass, field
from email.message import EmailMessage

import httpx2 as httpx

from .ficha import ASSUNTOS, Ficha
from .whatsapp import mascarar

log = logging.getLogger(__name__)

PRIORIDADE = {"alta": "alta", "media": "média", "baixa": "baixa", "": "a definir"}


@dataclass(frozen=True)
class ConfigEmail:
    host: str = ""
    porta: int = 587
    usuario: str = ""
    senha: str = ""
    remetente: str = ""
    destinatarios: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ativo(self) -> bool:
        return bool(self.host and self.remetente and self.destinatarios)


def montar_email(evento: str, telefone: str, ficha: Ficha | None, motivo: str, painel_url: str, remetente: str, destinatarios: tuple[str, ...]) -> EmailMessage:
    nome = (ficha.nome if ficha and ficha.nome else "") or f"contato {mascarar(telefone)}"
    assunto = ASSUNTOS[ficha.assunto] if ficha and ficha.assunto else "assunto a definir"
    prioridade = PRIORIDADE[ficha.prioridade if ficha else ""]
    link = f"{painel_url.rstrip('/')}/painel/caso/{telefone}" if painel_url else "(configure PAINEL_URL)"

    if evento == "concluido":
        titulo = f"Caso pronto para análise: {nome} ({assunto}, prioridade {prioridade})"
        corpo = "A triagem terminou e o caso está pronto para análise."
    else:
        titulo = f"Cliente precisa de atendimento: {nome}"
        corpo = f"O agente passou a conversa para a equipe. Motivo: {motivo or 'não informado'}."
        corpo += "\nResponda pelo painel; enquanto isso, o agente não responde este contato."

    msg = EmailMessage()
    msg["Subject"] = titulo
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    msg.set_content(f"{corpo}\n\nAbrir o caso: {link}\n")
    return msg


class Avisos:
    def __init__(self, webhook_url: str = "", email: ConfigEmail | None = None, painel_url: str = "") -> None:
        self._url = webhook_url
        self._email = email or ConfigEmail()
        self._painel_url = painel_url

    async def notificar(self, telefone: str, evento: str, ficha: Ficha | None, motivo: str = "") -> None:
        """evento: "concluido" (caso pronto), "humano" (precisa de atendimento) ou
        "nova_mensagem" (cliente escreveu durante o atendimento humano)."""
        log.info("Aviso para a equipe: %s (%s)", evento, mascarar(telefone))
        if self._email.ativo and evento in ("concluido", "humano"):
            await self._enviar_email(evento, telefone, ficha, motivo)
        if self._url:
            await self._enviar_webhook(evento, telefone, ficha, motivo)

    async def _enviar_email(self, evento: str, telefone: str, ficha: Ficha | None, motivo: str) -> None:
        cfg = self._email
        msg = montar_email(evento, telefone, ficha, motivo, self._painel_url, cfg.remetente, cfg.destinatarios)

        def enviar() -> None:
            with smtplib.SMTP(cfg.host, cfg.porta, timeout=20) as smtp:
                smtp.starttls()
                if cfg.usuario:
                    smtp.login(cfg.usuario, cfg.senha)
                smtp.send_message(msg)

        try:
            await asyncio.to_thread(enviar)
        except (smtplib.SMTPException, OSError):
            log.exception("Não foi possível enviar o e-mail de aviso")

    async def _enviar_webhook(self, evento: str, telefone: str, ficha: Ficha | None, motivo: str) -> None:
        corpo = {
            "evento": evento,
            "telefone": telefone,
            "motivo": motivo,
            "ficha": ficha.model_dump() if ficha else None,
            "link": f"{self._painel_url.rstrip('/')}/painel/caso/{telefone}" if self._painel_url else "",
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as http:
                (await http.post(self._url, json=corpo)).raise_for_status()
        except httpx.HTTPError:
            log.exception("Não foi possível enviar o aviso por webhook")
