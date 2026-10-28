"""Guarda os arquivos que os clientes enviam (fotos e PDFs de documentos).

Os arquivos ficam numa pasta do servidor e o advogado os abre pelo painel.
Para copiar para o Drive do escritório, ligue a cópia em `salvar` (ver README).
"""

from __future__ import annotations

import mimetypes
import re
import uuid
from pathlib import Path

from .memoria import Memoria

_EXTENSOES = {"image/jpeg": ".jpg", "application/pdf": ".pdf", "audio/ogg": ".ogg"}


def _seguro(texto: str) -> str:
    return re.sub(r"[^0-9A-Za-z._-]", "_", texto)[:80]


class Arquivo:
    def __init__(self, pasta: Path, memoria: Memoria) -> None:
        self.pasta = pasta
        self.memoria = memoria

    def salvar(self, telefone: str, conteudo: bytes, mime: str, nome_original: str = "") -> str:
        """Grava o arquivo e registra no banco. Devolve o id do documento."""
        id_documento = uuid.uuid4().hex
        extensao = _EXTENSOES.get(mime) or mimetypes.guess_extension(mime or "") or ".bin"
        pasta = self.pasta / _seguro(telefone)
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = pasta / f"{id_documento}{extensao}"
        caminho.write_bytes(conteudo)
        nome = nome_original or f"arquivo{extensao}"
        self.memoria.salvar_documento(id_documento, telefone, nome, mime or "application/octet-stream", caminho)
        return id_documento

    @staticmethod
    def apagar(caminhos: list[str]) -> None:
        for c in caminhos:
            Path(c).unlink(missing_ok=True)
