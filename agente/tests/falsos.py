"""Dublês para testar sem chamar a API do Claude nem o WhatsApp."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from anthropic.types.beta import BetaTextBlock, BetaThinkingBlock

from app.ficha import Ficha, TurnoAgente


def turno(acao: str = "continuar", mensagens: list[str] | None = None, **ficha: Any) -> TurnoAgente:
    dados = Ficha.vazia().model_dump() | ficha
    return TurnoAgente(
        mensagens=mensagens if mensagens is not None else ["Olá!"],
        acao=acao,
        motivo_humano="Pediu atendimento humano" if acao == "humano" else "",
        ficha=Ficha.model_validate(dados),
    )


def resposta_api(t: TurnoAgente | None = None, stop_reason: str = "end_turn", texto: str | None = None):
    conteudo = [BetaThinkingBlock(type="thinking", thinking="", signature="assinatura")]
    if stop_reason == "end_turn":
        corpo = texto if texto is not None else (t or turno()).model_dump_json()
        conteudo.append(BetaTextBlock(type="text", text=corpo, citations=None))
    return SimpleNamespace(
        stop_reason=stop_reason,
        stop_details=SimpleNamespace(category="cyber") if stop_reason == "refusal" else None,
        content=conteudo,
        usage=None,
    )


class ClienteFalso:
    """Imita client.beta.messages.create e guarda os argumentos de cada chamada."""

    def __init__(self, respostas: list[Any]) -> None:
        self.respostas = list(respostas)
        self.chamadas: list[dict[str, Any]] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    async def _create(self, **kwargs: Any):
        # Copia profunda via JSON: o histórico é mutável e queremos o estado da chamada.
        self.chamadas.append(json.loads(json.dumps(kwargs, default=str)))
        resposta = self.respostas.pop(0)
        if isinstance(resposta, Exception):
            raise resposta
        return resposta


class CanalFalso:
    def __init__(self, midias: dict[str, tuple[bytes, str]] | None = None) -> None:
        self.enviadas: list[tuple[str, str]] = []
        self.midias = midias or {}

    async def enviar_texto(self, telefone: str, texto: str) -> None:
        self.enviadas.append((telefone, texto))

    async def baixar_midia(self, midia_id: str) -> tuple[bytes, str]:
        return self.midias[midia_id]


class AvisosFalsos:
    def __init__(self) -> None:
        self.eventos: list[tuple[str, str]] = []

    async def notificar(self, telefone: str, evento: str, ficha, motivo: str = "") -> None:
        self.eventos.append((telefone, evento))
