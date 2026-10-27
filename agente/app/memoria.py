"""Guarda conversas, fichas e status em SQLite.

Atenção (LGPD): este banco guarda dados pessoais e de saúde, inclusive as fotos
dos documentos que estão no histórico. Em produção, use disco criptografado,
backup protegido e uma política de exclusão (ver apagar_conversa).
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .ficha import Ficha

Status = Literal["bot", "humano", "concluido"]

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS conversas (
    telefone      TEXT PRIMARY KEY,
    nome_perfil   TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'bot',
    motivo_humano TEXT NOT NULL DEFAULT '',
    ficha         TEXT,
    criado_em     TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mensagens (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    telefone TEXT NOT NULL,
    conteudo TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mensagens_telefone ON mensagens (telefone, id);
CREATE TABLE IF NOT EXISTS processadas (
    id_mensagem TEXT PRIMARY KEY
);
"""


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Memoria:
    def __init__(self, caminho: Path | str) -> None:
        if caminho != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(caminho), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._trava = threading.Lock()
        with self._trava:
            self._db.executescript(_ESQUEMA)

    def _garantir_conversa(self, telefone: str, nome_perfil: str = "") -> None:
        agora = _agora()
        self._db.execute(
            "INSERT OR IGNORE INTO conversas (telefone, nome_perfil, criado_em, atualizado_em) VALUES (?, ?, ?, ?)",
            (telefone, nome_perfil, agora, agora),
        )

    def marcar_processada(self, id_mensagem: str) -> bool:
        """Registra o id da mensagem do WhatsApp. Devolve False se já tinha sido vista
        (a Meta reenvia webhooks quando não recebe resposta a tempo)."""
        with self._trava, self._db:
            cur = self._db.execute("INSERT OR IGNORE INTO processadas VALUES (?)", (id_mensagem,))
            return cur.rowcount == 1

    def historico(self, telefone: str) -> list[dict[str, Any]]:
        with self._trava:
            linhas = self._db.execute(
                "SELECT conteudo FROM mensagens WHERE telefone = ? ORDER BY id", (telefone,)
            ).fetchall()
        return [json.loads(l["conteudo"]) for l in linhas]

    def acrescentar(self, telefone: str, mensagens: list[dict[str, Any]], nome_perfil: str = "") -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone, nome_perfil)
            self._db.executemany(
                "INSERT INTO mensagens (telefone, conteudo) VALUES (?, ?)",
                [(telefone, json.dumps(m, ensure_ascii=False)) for m in mensagens],
            )
            self._db.execute("UPDATE conversas SET atualizado_em = ? WHERE telefone = ?", (_agora(), telefone))

    def status(self, telefone: str) -> Status:
        with self._trava:
            linha = self._db.execute("SELECT status FROM conversas WHERE telefone = ?", (telefone,)).fetchone()
        return linha["status"] if linha else "bot"

    def definir_status(self, telefone: str, status: Status, motivo_humano: str = "") -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone)
            self._db.execute(
                "UPDATE conversas SET status = ?, motivo_humano = ?, atualizado_em = ? WHERE telefone = ?",
                (status, motivo_humano, _agora(), telefone),
            )

    def ficha(self, telefone: str) -> Ficha | None:
        with self._trava:
            linha = self._db.execute("SELECT ficha FROM conversas WHERE telefone = ?", (telefone,)).fetchone()
        if not linha or not linha["ficha"]:
            return None
        return Ficha.model_validate_json(linha["ficha"])

    def salvar_ficha(self, telefone: str, ficha: Ficha) -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone)
            self._db.execute(
                "UPDATE conversas SET ficha = ?, atualizado_em = ? WHERE telefone = ?",
                (ficha.model_dump_json(), _agora(), telefone),
            )

    def listar_casos(self) -> list[dict[str, Any]]:
        with self._trava:
            linhas = self._db.execute(
                "SELECT telefone, nome_perfil, status, motivo_humano, ficha, criado_em, atualizado_em "
                "FROM conversas ORDER BY atualizado_em DESC"
            ).fetchall()
        casos = []
        for l in linhas:
            caso = dict(l)
            caso["ficha"] = json.loads(l["ficha"]) if l["ficha"] else None
            casos.append(caso)
        return casos

    def apagar_conversa(self, telefone: str) -> None:
        """Apaga tudo o que foi guardado sobre um contato (pedido de exclusão, LGPD)."""
        with self._trava, self._db:
            self._db.execute("DELETE FROM mensagens WHERE telefone = ?", (telefone,))
            self._db.execute("DELETE FROM conversas WHERE telefone = ?", (telefone,))
