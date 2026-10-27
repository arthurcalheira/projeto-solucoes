"""Formato da resposta do agente: mensagens ao cliente, ação e ficha do caso.

O SCHEMA vai para a API (saída estruturada) e garante JSON válido nesse formato.
Os modelos Pydantic validam a resposta do lado de cá e dão tipos ao resto do código.
Se mudar um, mude o outro: tests/test_ficha.py confere que estão iguais.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

Nivel = Literal["alta", "media", "baixa"]
Acao = Literal["continuar", "humano", "concluido"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Resposta(_Base):
    pergunta: str
    resposta: str


class Sinal(_Base):
    texto: str
    nivel: Nivel


class Ficha(_Base):
    nome: str
    caso_de: Literal["proprio", "familiar", ""]
    assunto: Literal["aposentadoria", "incapacidade", "bpc", "pensao", "negativa", "outro", ""]
    beneficio_negado: str
    cidade_uf: str
    respostas: list[Resposta]
    sinais: list[Sinal]
    documentos_recebidos: list[str]
    documentos_pendentes: list[str]
    prioridade: Literal["alta", "media", "baixa", ""]
    resumo_para_advogado: str

    @classmethod
    def vazia(cls) -> "Ficha":
        return cls(
            nome="", caso_de="", assunto="", beneficio_negado="", cidade_uf="",
            respostas=[], sinais=[], documentos_recebidos=[], documentos_pendentes=[],
            prioridade="", resumo_para_advogado="",
        )


class TurnoAgente(_Base):
    mensagens: list[str]
    acao: Acao
    motivo_humano: str
    ficha: Ficha


def _objeto(propriedades: dict) -> dict:
    return {
        "type": "object",
        "properties": propriedades,
        "required": list(propriedades),
        "additionalProperties": False,
    }


_TEXTO = {"type": "string"}
_LISTA_TEXTO = {"type": "array", "items": _TEXTO}

SCHEMA: dict = _objeto({
    "mensagens": _LISTA_TEXTO,
    "acao": {"type": "string", "enum": ["continuar", "humano", "concluido"]},
    "motivo_humano": _TEXTO,
    "ficha": _objeto({
        "nome": _TEXTO,
        "caso_de": {"type": "string", "enum": ["proprio", "familiar", ""]},
        "assunto": {
            "type": "string",
            "enum": ["aposentadoria", "incapacidade", "bpc", "pensao", "negativa", "outro", ""],
        },
        "beneficio_negado": _TEXTO,
        "cidade_uf": _TEXTO,
        "respostas": {"type": "array", "items": _objeto({"pergunta": _TEXTO, "resposta": _TEXTO})},
        "sinais": {
            "type": "array",
            "items": _objeto({
                "texto": _TEXTO,
                "nivel": {"type": "string", "enum": ["alta", "media", "baixa"]},
            }),
        },
        "documentos_recebidos": _LISTA_TEXTO,
        "documentos_pendentes": _LISTA_TEXTO,
        "prioridade": {"type": "string", "enum": ["alta", "media", "baixa", ""]},
        "resumo_para_advogado": _TEXTO,
    }),
})
