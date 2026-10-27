"""Chamada ao Claude: recebe o histórico e a nova entrada, devolve o turno do agente.

Decisões importantes:
- O histórico é só acrescentado, nunca editado. Os blocos de raciocínio (thinking)
  que o modelo devolve precisam voltar intactos nas próximas chamadas; editar
  mensagens antigas invalida esses blocos e o cache.
- Cache: o prompt de sistema tem um ponto de cache próprio (compartilhado entre
  todas as conversas) e o cache automático cobre o histórico de cada conversa.
- Data, hora e horário de atendimento vão numa mensagem de sistema no fim, para
  não alterar o começo do prompt e não perder o cache.
- Se o modelo recusar o pedido, o caso vai para um humano. Nos modelos que
  aceitam, o servidor antes tenta outro modelo (fallbacks="default"); o Haiku
  5.5 não tem esse recurso.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import anthropic
from pydantic import ValidationError

from .ficha import SCHEMA, Ficha, TurnoAgente

log = logging.getLogger(__name__)

# Modelos que aceitam fallbacks="default" (o Haiku 5.5 não aceita).
MODELOS_COM_FALLBACK = {"claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5"}
BETAS_FALLBACK = ["server-side-fallback-2026-07-01"]
MAX_TOKENS = 16000

MENSAGEM_FALHA = (
    "Recebi sua mensagem. Uma pessoa da nossa equipe vai continuar o atendimento "
    "por aqui, tudo bem?"
)


@dataclass
class Resultado:
    turno: TurnoAgente
    # Mensagens a acrescentar ao histórico da conversa, já no formato da API.
    novas_mensagens: list[dict[str, Any]]
    uso: dict[str, Any] = field(default_factory=dict)


def turno_para_humano(motivo: str, ficha: Ficha | None = None) -> TurnoAgente:
    return TurnoAgente(
        mensagens=[MENSAGEM_FALHA],
        acao="humano",
        motivo_humano=motivo,
        ficha=ficha or Ficha.vazia(),
    )


def conteudo_para_historico(blocos: list[Any]) -> list[dict[str, Any]]:
    """Converte a resposta da API em blocos para guardar no histórico.

    Se houve troca de modelo no meio da resposta (bloco "fallback"), os blocos de
    raciocínio e de ferramenta anteriores à troca não podem ser reenviados.
    """
    dicts = [b.to_dict(exclude_none=True) for b in blocos]
    indices_fallback = [i for i, b in enumerate(dicts) if b.get("type") == "fallback"]
    if not indices_fallback:
        return dicts
    ultimo = indices_fallback[-1]
    descartar_antes = {"thinking", "redacted_thinking", "tool_use", "server_tool_use"}
    return [
        b for i, b in enumerate(dicts)
        if b.get("type") != "fallback" and not (i < ultimo and b.get("type") in descartar_antes)
    ]


class AgenteTriagem:
    def __init__(
        self,
        cliente: anthropic.AsyncAnthropic,
        modelo: str,
        esforco: str,
        prompt_sistema: str,
    ) -> None:
        self.cliente = cliente
        self.modelo = modelo
        self.esforco = esforco
        self.sistema = [
            {"type": "text", "text": prompt_sistema, "cache_control": {"type": "ephemeral"}}
        ]

    async def responder(
        self,
        historico: list[dict[str, Any]],
        entrada: list[dict[str, Any]],
        contexto: str,
        ficha_atual: Ficha | None = None,
    ) -> Resultado:
        msg_usuario = {"role": "user", "content": entrada}
        msg_contexto = {"role": "system", "content": contexto}

        extras: dict[str, Any] = {}
        if self.modelo in MODELOS_COM_FALLBACK:
            extras = {"betas": BETAS_FALLBACK, "fallbacks": "default"}

        try:
            resposta = await self.cliente.beta.messages.create(
                model=self.modelo,
                max_tokens=MAX_TOKENS,
                system=self.sistema,
                messages=[*historico, msg_usuario, msg_contexto],
                output_config={
                    "effort": self.esforco,
                    "format": {"type": "json_schema", "schema": SCHEMA},
                },
                cache_control={"type": "ephemeral"},
                **extras,
            )
        except anthropic.RateLimitError:
            log.warning("Limite de uso da API atingido")
            return Resultado(turno_para_humano("Instabilidade no sistema (limite da API).", ficha_atual), [msg_usuario])
        except anthropic.APIStatusError as e:
            log.error("Erro da API do Claude: status=%s request_id=%s", e.status_code, e.request_id)
            return Resultado(turno_para_humano("Instabilidade no sistema (erro da API).", ficha_atual), [msg_usuario])
        except anthropic.APIConnectionError:
            log.error("Sem conexão com a API do Claude")
            return Resultado(turno_para_humano("Instabilidade no sistema (sem conexão).", ficha_atual), [msg_usuario])

        uso = resposta.usage.to_dict(exclude_none=True) if resposta.usage else {}

        # A mensagem de contexto só pode ficar no histórico se vier seguida da resposta.
        # Nos casos abaixo, guardamos apenas a mensagem do cliente.
        if resposta.stop_reason == "refusal":
            categoria = resposta.stop_details.category if resposta.stop_details else None
            log.warning("Pedido recusado pelo modelo (categoria=%s)", categoria)
            return Resultado(turno_para_humano("O assistente não conseguiu responder a esta mensagem.", ficha_atual), [msg_usuario], uso)
        if resposta.stop_reason == "max_tokens":
            log.warning("Resposta cortada por limite de tokens")
            return Resultado(turno_para_humano("Resposta do assistente incompleta.", ficha_atual), [msg_usuario], uso)

        textos = [b.text for b in resposta.content if b.type == "text"]
        try:
            turno = TurnoAgente.model_validate_json(textos[-1])
        except (IndexError, ValidationError):
            log.error("Resposta fora do formato esperado")
            return Resultado(turno_para_humano("Resposta do assistente fora do formato.", ficha_atual), [msg_usuario], uso)

        msg_assistente = {"role": "assistant", "content": conteudo_para_historico(resposta.content)}
        return Resultado(turno, [msg_usuario, msg_contexto, msg_assistente], uso)
