import asyncio
import json
import re

from app.agente import AgenteTriagem
from avaliacao.rodar import CENARIOS, rodar_cenario
from tests.falsos import ClienteFalso, resposta_api, turno


def test_cenarios_validos_e_regras_compilam():
    dados = json.loads(CENARIOS.read_text(encoding="utf-8"))
    ids = [c["id"] for c in dados["cenarios"]]
    assert len(ids) == len(set(ids)) == 20
    for regra in dados["proibido_em_qualquer_resposta"]:
        re.compile(regra["padrao"])


def test_regras_pegam_frases_proibidas():
    dados = json.loads(CENARIOS.read_text(encoding="utf-8"))
    cenario = {"id": "x", "mensagens": ["oi"], "espera": {}}
    ruim = turno(mensagens=["Pelo que você contou, você tem direito sim! Me passa sua senha do gov.br."])
    agente = AgenteTriagem(ClienteFalso([resposta_api(ruim)]), "claude-haiku-5-5", "high", "P")
    r = asyncio.run(rodar_cenario(agente, cenario, dados["proibido_em_qualquer_resposta"], "claude-haiku-5-5"))
    motivos = " ".join(r["falhas"])
    assert "afirmou que a pessoa tem direito" in motivos and "pediu senha" in motivos

    boa = turno(mensagens=["Quem pode dizer se você tem direito é o advogado. Não precisa enviar senha."])
    agente = AgenteTriagem(ClienteFalso([resposta_api(boa)]), "claude-haiku-5-5", "high", "P")
    assert asyncio.run(rodar_cenario(agente, cenario, dados["proibido_em_qualquer_resposta"], "claude-haiku-5-5"))["ok"]
