import asyncio

import anthropic
import httpx2 as httpx
from anthropic.types.beta import BetaTextBlock, BetaThinkingBlock

from app.agente import AgenteTriagem, conteudo_para_historico
from app.ficha import SCHEMA
from tests.falsos import ClienteFalso, resposta_api, turno


def _agente(cliente):
    return AgenteTriagem(cliente, "claude-opus-5-5", "medium", "PROMPT FIXO")


def _responder(agente, historico=None):
    return asyncio.run(agente.responder(
        historico=historico or [],
        entrada=[{"type": "text", "text": "Oi"}],
        contexto="Agora: segunda-feira, 27/10/2026 10:00.",
    ))


def test_monta_requisicao_com_cache_saida_estruturada_e_fallback():
    cliente = ClienteFalso([resposta_api(turno())])
    _responder(_agente(cliente))
    req = cliente.chamadas[0]
    assert req["model"] == "claude-opus-5-5"
    assert req["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert req["cache_control"] == {"type": "ephemeral"}
    assert req["output_config"]["format"]["schema"] == SCHEMA
    assert req["output_config"]["effort"] == "medium"
    assert req["fallbacks"] == "default"
    assert req["betas"] == ["server-side-fallback-2026-07-01"]
    # A mensagem com data e hora vem por último, depois da mensagem do cliente.
    assert [m["role"] for m in req["messages"]] == ["user", "system"]


def test_historico_so_cresce_e_guarda_raciocinio():
    cliente = ClienteFalso([resposta_api(turno())])
    historico = [
        {"role": "user", "content": [{"type": "text", "text": "Olá"}]},
        {"role": "system", "content": "Agora: ..."},
        {"role": "assistant", "content": [{"type": "text", "text": "{}"}]},
    ]
    resultado = _responder(_agente(cliente), historico)
    assert cliente.chamadas[0]["messages"][:3] == historico
    assert [m["role"] for m in resultado.novas_mensagens] == ["user", "system", "assistant"]
    assert resultado.novas_mensagens[2]["content"][0] == {"type": "thinking", "thinking": "", "signature": "assinatura"}


def test_haiku_vai_sem_fallback():
    cliente = ClienteFalso([resposta_api(turno())])
    _responder(AgenteTriagem(cliente, "claude-haiku-5-5", "high", "PROMPT FIXO"))
    req = cliente.chamadas[0]
    assert req["model"] == "claude-haiku-5-5"
    assert req["output_config"]["effort"] == "high"
    assert "fallbacks" not in req and "betas" not in req


def test_recusa_vai_para_humano_sem_guardar_contexto():
    resultado = _responder(_agente(ClienteFalso([resposta_api(stop_reason="refusal")])))
    assert resultado.turno.acao == "humano"
    assert [m["role"] for m in resultado.novas_mensagens] == ["user"]


def test_json_invalido_vai_para_humano():
    resultado = _responder(_agente(ClienteFalso([resposta_api(texto="não é json")])))
    assert resultado.turno.acao == "humano"


def test_erro_de_conexao_vai_para_humano():
    erro = anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com"))
    resultado = _responder(_agente(ClienteFalso([erro])))
    assert resultado.turno.acao == "humano"
    assert [m["role"] for m in resultado.novas_mensagens] == ["user"]


def test_troca_de_modelo_remove_raciocinio_anterior():
    from anthropic.types.beta import BetaFallbackBlock

    fallback = BetaFallbackBlock.construct(type="fallback")
    blocos = [
        BetaThinkingBlock(type="thinking", thinking="", signature="a"),
        BetaTextBlock(type="text", text="parcial", citations=None),
        fallback,
        BetaThinkingBlock(type="thinking", thinking="", signature="b"),
        BetaTextBlock(type="text", text="final", citations=None),
    ]
    tipos = [(b["type"], b.get("signature") or b.get("text")) for b in conteudo_para_historico(blocos)]
    assert tipos == [("text", "parcial"), ("thinking", "b"), ("text", "final")]
