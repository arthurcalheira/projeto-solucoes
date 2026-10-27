"""Avisa a equipe do escritório quando um caso fica pronto ou precisa de humano."""

from __future__ import annotations

import logging

import httpx2 as httpx

from .ficha import Ficha
from .whatsapp import mascarar

log = logging.getLogger(__name__)


class Avisos:
    def __init__(self, webhook_url: str = "") -> None:
        self._url = webhook_url

    async def notificar(self, telefone: str, evento: str, ficha: Ficha | None, motivo: str = "") -> None:
        """evento: "concluido" (caso pronto) ou "humano" (precisa de atendimento)."""
        log.info("Aviso para a equipe: %s (%s)", evento, mascarar(telefone))
        if not self._url:
            return
        corpo = {
            "evento": evento,
            "telefone": telefone,
            "motivo": motivo,
            "ficha": ficha.model_dump() if ficha else None,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as http:
                (await http.post(self._url, json=corpo)).raise_for_status()
        except httpx.HTTPError:
            log.exception("Não foi possível enviar o aviso para a equipe")
