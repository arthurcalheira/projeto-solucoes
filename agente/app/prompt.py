"""Monta o prompt de sistema a partir do modelo e da configuração do escritório.

O prompt é montado uma vez, na inicialização, e não muda depois: assim ele fica
no cache do Claude e é compartilhado por todas as conversas. Data, hora e outros
dados que mudam vão numa mensagem de sistema no fim da conversa (ver agente.py).
"""

from __future__ import annotations

from .config import RAIZ, Escritorio

MODELO_PROMPT = RAIZ / "prompts" / "sistema.md"


def montar_prompt_sistema(escritorio: Escritorio) -> str:
    texto = MODELO_PROMPT.read_text(encoding="utf-8")
    trocas = {
        "{{NOME_ESCRITORIO}}": escritorio.nome,
        "{{PRAZO_RETORNO}}": escritorio.prazo_retorno,
        "{{POLITICA_HONORARIOS}}": escritorio.politica_honorarios,
        "{{HORARIO}}": escritorio.horario.descricao(),
        "{{GUIA_TRIAGEM}}": escritorio.guia_triagem.read_text(encoding="utf-8").strip(),
    }
    for marcador, valor in trocas.items():
        texto = texto.replace(marcador, valor)
    if "{{" in texto:
        raise ValueError("O prompt de sistema ainda tem marcadores {{...}} sem valor.")
    return texto
