"""Configuração lida do ambiente (.env) e do arquivo do escritório."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Horario:
    dias: tuple[int, ...]  # 0 = segunda-feira
    inicio: str  # "08:00"
    fim: str  # "18:00"
    fuso: str  # "America/Sao_Paulo"

    def descricao(self) -> str:
        nomes = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
        dias = ", ".join(nomes[d] for d in self.dias)
        return f"{dias}, das {self.inicio} às {self.fim}"


@dataclass(frozen=True)
class Escritorio:
    nome: str
    prazo_retorno: str
    politica_honorarios: str
    horario: Horario
    guia_triagem: Path


@dataclass(frozen=True)
class Config:
    modelo: str
    esforco: str
    banco: Path
    escritorio: Escritorio
    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    whatsapp_app_secret: str
    whatsapp_api_versao: str
    painel_token: str
    aviso_webhook_url: str
    agrupar_segundos: float


def carregar_escritorio(caminho: Path) -> Escritorio:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    h = dados["horario"]
    guia = Path(dados["guia_triagem"])
    if not guia.is_absolute():
        guia = (caminho.parent / guia).resolve()
    return Escritorio(
        nome=dados["nome"],
        prazo_retorno=dados["prazo_retorno"],
        politica_honorarios=dados["politica_honorarios"],
        horario=Horario(tuple(h["dias"]), h["inicio"], h["fim"], h["fuso"]),
        guia_triagem=guia,
    )


def carregar_config() -> Config:
    from dotenv import load_dotenv

    load_dotenv(RAIZ / ".env")
    env = os.environ.get

    caminho_escritorio = Path(env("ESCRITORIO_CONFIG", "escritorio.json"))
    if not caminho_escritorio.is_absolute():
        caminho_escritorio = RAIZ / caminho_escritorio
    if not caminho_escritorio.exists():
        caminho_escritorio = RAIZ / "escritorio.example.json"

    banco = Path(env("BANCO", "dados/atendimento.db"))
    if not banco.is_absolute():
        banco = RAIZ / banco

    return Config(
        modelo=env("CLAUDE_MODELO", "claude-haiku-5-5"),
        esforco=env("CLAUDE_ESFORCO", "high"),
        banco=banco,
        escritorio=carregar_escritorio(caminho_escritorio),
        whatsapp_token=env("WHATSAPP_TOKEN", ""),
        whatsapp_phone_number_id=env("WHATSAPP_PHONE_NUMBER_ID", ""),
        whatsapp_verify_token=env("WHATSAPP_VERIFY_TOKEN", ""),
        whatsapp_app_secret=env("WHATSAPP_APP_SECRET", ""),
        whatsapp_api_versao=env("WHATSAPP_API_VERSAO", "v23.0"),
        painel_token=env("PAINEL_TOKEN", ""),
        aviso_webhook_url=env("AVISO_WEBHOOK_URL", ""),
        agrupar_segundos=float(env("AGRUPAR_SEGUNDOS", "4")),
    )
