"""Converse com o agente pelo terminal, sem WhatsApp.

Uso:
    python simulador.py

Comandos durante a conversa:
    /foto caminho/da/imagem.jpg   envia uma foto (ex.: documento)
    /pdf caminho/do/arquivo.pdf   envia um PDF
    /ficha                        mostra a ficha do caso como o advogado vê
    /sair                         encerra

Precisa de ANTHROPIC_API_KEY no .env. Cada mensagem é uma chamada paga à API.
"""

from __future__ import annotations

import asyncio
import json
import mimetypes
from pathlib import Path

import anthropic

from app.agente import AgenteTriagem
from app.atendimento import Atendimento
from app.avisos import Avisos
from app.config import carregar_config
from app.memoria import Memoria
from app.prompt import montar_prompt_sistema
from app.whatsapp import MensagemRecebida

TELEFONE = "5511999990000"


class CanalTerminal:
    async def enviar_texto(self, telefone: str, texto: str) -> None:
        print(f"\nAgente: {texto}")

    async def baixar_midia(self, midia_id: str) -> tuple[bytes, str]:
        caminho = Path(midia_id)  # no simulador, o "id" da mídia é o caminho do arquivo
        mime = mimetypes.guess_type(caminho.name)[0] or "application/octet-stream"
        return caminho.read_bytes(), mime


async def main() -> None:
    cfg = carregar_config()
    memoria = Memoria(":memory:")
    agente = AgenteTriagem(
        anthropic.AsyncAnthropic(), cfg.modelo, cfg.esforco, montar_prompt_sistema(cfg.escritorio)
    )
    atendimento = Atendimento(
        agente, memoria, CanalTerminal(), Avisos(), cfg.escritorio.horario, agrupar_segundos=0
    )
    print(f"Simulador: {cfg.escritorio.nome} · modelo {cfg.modelo}. Escreva como se fosse o cliente.")

    contador = 0
    while True:
        try:
            linha = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not linha:
            continue
        if linha == "/sair":
            break
        if linha == "/ficha":
            ficha = memoria.ficha(TELEFONE)
            print(json.dumps(ficha.model_dump() if ficha else None, ensure_ascii=False, indent=2))
            print(f"status: {memoria.status(TELEFONE)}")
            continue

        contador += 1
        if linha.startswith(("/foto ", "/pdf ")):
            comando, caminho = linha.split(" ", 1)
            caminho = caminho.strip()
            if not Path(caminho).is_file():
                print("Arquivo não encontrado.")
                continue
            tipo = "image" if comando == "/foto" else "document"
            msg = MensagemRecebida(
                id=f"sim-{contador}", telefone=TELEFONE, tipo=tipo,
                midia_id=caminho, nome_arquivo=Path(caminho).name,
            )
        else:
            msg = MensagemRecebida(id=f"sim-{contador}", telefone=TELEFONE, tipo="text", texto=linha)

        await atendimento.receber(msg)
        await atendimento.aguardar()
        if memoria.status(TELEFONE) == "humano":
            print("\n[caso passado para a equipe: o agente parou de responder]")


if __name__ == "__main__":
    asyncio.run(main())
