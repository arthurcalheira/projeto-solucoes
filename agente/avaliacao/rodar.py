"""Roda as conversas de teste contra a API do Claude e confere as regras do agente.

Uso (dentro da pasta agente/, com o venv ativo e a chave no .env):
    python -m avaliacao.rodar                      # todos os cenários, modelo do .env
    python -m avaliacao.rodar --modelo claude-opus-5-5 --esforco medium
    python -m avaliacao.rodar --cenario pede-humano

Cada cenário é uma conversa com mensagens do cliente já escritas (não muda
conforme as perguntas do agente). O que se confere:
- nenhuma resposta quebra as regras (dizer se tem direito, pedir senha, prometer
  resultado, informar valor);
- a ação, o assunto e a prioridade esperados em cada cenário.

ATENÇÃO: cada execução faz chamadas pagas à API. O script mostra uma estimativa
antes de começar e pede confirmação (pule com --confirmar).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

import anthropic

from app.agente import AgenteTriagem
from app.config import carregar_config
from app.prompt import montar_prompt_sistema

CENARIOS = Path(__file__).with_name("cenarios.json")
CONTEXTO = "Agora: terça-feira, 27/10/2026 10:00. O escritório está dentro do horário de atendimento."
NIVEL = {"": 0, "baixa": 1, "media": 2, "alta": 3}

# US$ por milhão de tokens (entrada, saída). Conferir em claude.com/pricing.
PRECOS = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}


def custo(uso: dict, modelo: str) -> float:
    entrada, saida = PRECOS.get(modelo, (0.0, 0.0))
    return (
        uso.get("input_tokens", 0) * entrada
        + uso.get("cache_creation_input_tokens", 0) * entrada * 1.25
        + uso.get("cache_read_input_tokens", 0) * entrada * 0.10
        + uso.get("output_tokens", 0) * saida
    ) / 1_000_000


async def rodar_cenario(agente: AgenteTriagem, cenario: dict, proibidos: list[dict], modelo: str) -> dict:
    historico: list[dict] = []
    turnos = []
    gasto = 0.0
    falhas: list[str] = []
    for texto in cenario["mensagens"]:
        resultado = await agente.responder(historico, [{"type": "text", "text": texto}], CONTEXTO)
        historico.extend(resultado.novas_mensagens)
        gasto += custo(resultado.uso, modelo)
        turno = resultado.turno
        turnos.append(turno)
        for resposta in turno.mensagens:
            for regra in proibidos:
                if re.search(regra["padrao"], resposta, flags=re.IGNORECASE):
                    falhas.append(f"{regra['motivo']}: \"{resposta[:120]}\"")
        if turno.acao == "humano":
            break  # o agente para de responder quando passa para a equipe

    espera = cenario.get("espera", {})
    final = turnos[-1]
    if "acao_final" in espera and final.acao not in espera["acao_final"]:
        falhas.append(f"ação final '{final.acao}', esperado {espera['acao_final']}")
    if "acao_em_algum_turno" in espera and not any(t.acao in espera["acao_em_algum_turno"] for t in turnos):
        falhas.append(f"nunca chegou a {espera['acao_em_algum_turno']}")
    if "assunto" in espera and final.ficha.assunto not in espera["assunto"]:
        falhas.append(f"assunto '{final.ficha.assunto}', esperado {espera['assunto']}")
    if "prioridade_minima" in espera and NIVEL[final.ficha.prioridade] < NIVEL[espera["prioridade_minima"]]:
        falhas.append(f"prioridade '{final.ficha.prioridade or 'vazia'}', esperado pelo menos {espera['prioridade_minima']}")

    return {
        "id": cenario["id"],
        "ok": not falhas,
        "falhas": falhas,
        "custo": gasto,
        "conversa": [{"cliente": m, "agente": t.mensagens, "acao": t.acao} for m, t in zip(cenario["mensagens"], turnos)],
        "ficha": final.ficha.model_dump(),
    }


async def main() -> None:
    cfg = carregar_config()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--modelo", default=cfg.modelo)
    parser.add_argument("--esforco", default=cfg.esforco)
    parser.add_argument("--cenario", help="roda só o cenário com este id")
    parser.add_argument("--confirmar", action="store_true", help="não pede confirmação antes de gastar")
    args = parser.parse_args()

    dados = json.loads(CENARIOS.read_text(encoding="utf-8"))
    cenarios = [c for c in dados["cenarios"] if not args.cenario or c["id"] == args.cenario]
    chamadas = sum(len(c["mensagens"]) for c in cenarios)
    print(f"{len(cenarios)} cenários, até {chamadas} chamadas ao modelo {args.modelo} (esforço {args.esforco}).")
    if args.modelo == "claude-haiku-5-5":
        print("Estimativa: menos de US$ 1 no total.")
    else:
        print("Estimativa: alguns dólares no total, dependendo do modelo.")
    if not args.confirmar and input("Continuar? [s/N] ").strip().lower() != "s":
        return

    agente = AgenteTriagem(anthropic.AsyncAnthropic(), args.modelo, args.esforco, montar_prompt_sistema(cfg.escritorio))
    resultados = []
    for cenario in cenarios:
        r = await rodar_cenario(agente, cenario, dados["proibido_em_qualquer_resposta"], args.modelo)
        resultados.append(r)
        marca = "OK  " if r["ok"] else "FALHOU"
        print(f"{marca} {r['id']:<32} US$ {r['custo']:.4f}")
        for f in r["falhas"]:
            print(f"       - {f}")

    aprovados = sum(r["ok"] for r in resultados)
    total = sum(r["custo"] for r in resultados)
    print(f"\n{aprovados}/{len(resultados)} cenários aprovados · custo estimado US$ {total:.4f}")

    saida = Path("dados") / f"avaliacao-{args.modelo}-{args.esforco}.json"
    saida.parent.mkdir(exist_ok=True)
    saida.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Conversas completas em {saida}: leia algumas para julgar o tom, que o script não mede.")


if __name__ == "__main__":
    asyncio.run(main())
