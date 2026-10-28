"""Guarda conversas, fichas, documentos e status em SQLite.

Há dois registros de cada conversa:
- `mensagens`: o histórico no formato da API do Claude (só cresce, nunca é editado);
- `transcricao`: a conversa legível para a equipe, com cliente, agente e equipe.

Atenção (LGPD): este banco e a pasta de documentos guardam dados pessoais e de
saúde. Em produção, use disco criptografado, backup protegido e uma política de
exclusão (ver apagar_conversa).
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
Autor = Literal["cliente", "agente", "equipe"]

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS conversas (
    telefone           TEXT PRIMARY KEY,
    nome_perfil        TEXT NOT NULL DEFAULT '',
    status             TEXT NOT NULL DEFAULT 'bot',
    motivo_humano      TEXT NOT NULL DEFAULT '',
    ficha              TEXT,
    notas_para_agente  TEXT NOT NULL DEFAULT '',
    ultima_do_cliente  TEXT,
    criado_em          TEXT NOT NULL,
    atualizado_em      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mensagens (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    telefone TEXT NOT NULL,
    conteudo TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mensagens_telefone ON mensagens (telefone, id);
CREATE TABLE IF NOT EXISTS transcricao (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    telefone     TEXT NOT NULL,
    autor        TEXT NOT NULL,
    texto        TEXT NOT NULL,
    documento_id TEXT,
    criado_em    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transcricao_telefone ON transcricao (telefone, id);
CREATE TABLE IF NOT EXISTS documentos (
    id           TEXT PRIMARY KEY,
    telefone     TEXT NOT NULL,
    nome_arquivo TEXT NOT NULL,
    mime         TEXT NOT NULL,
    caminho      TEXT NOT NULL,
    criado_em    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS processadas (
    id_mensagem TEXT PRIMARY KEY
);
"""


def agora_utc() -> str:
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
        agora = agora_utc()
        self._db.execute(
            "INSERT OR IGNORE INTO conversas (telefone, nome_perfil, criado_em, atualizado_em) VALUES (?, ?, ?, ?)",
            (telefone, nome_perfil, agora, agora),
        )
        if nome_perfil:
            self._db.execute(
                "UPDATE conversas SET nome_perfil = ? WHERE telefone = ? AND nome_perfil = ''",
                (nome_perfil, telefone),
            )

    def _um(self, sql: str, *args: Any) -> sqlite3.Row | None:
        with self._trava:
            return self._db.execute(sql, args).fetchone()

    def marcar_processada(self, id_mensagem: str) -> bool:
        """Registra o id da mensagem do WhatsApp. Devolve False se já tinha sido vista
        (a Meta reenvia webhooks quando não recebe resposta a tempo)."""
        with self._trava, self._db:
            cur = self._db.execute("INSERT OR IGNORE INTO processadas VALUES (?)", (id_mensagem,))
            return cur.rowcount == 1

    # ---------- Histórico da API ----------

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
            self._db.execute("UPDATE conversas SET atualizado_em = ? WHERE telefone = ?", (agora_utc(), telefone))

    # ---------- Transcrição para a equipe ----------

    def registrar(self, telefone: str, autor: Autor, texto: str, documento_id: str | None = None, nome_perfil: str = "") -> None:
        agora = agora_utc()
        with self._trava, self._db:
            self._garantir_conversa(telefone, nome_perfil)
            self._db.execute(
                "INSERT INTO transcricao (telefone, autor, texto, documento_id, criado_em) VALUES (?, ?, ?, ?, ?)",
                (telefone, autor, texto, documento_id, agora),
            )
            extra = ", ultima_do_cliente = ?" if autor == "cliente" else ""
            args = (agora, agora, telefone) if autor == "cliente" else (agora, telefone)
            self._db.execute(f"UPDATE conversas SET atualizado_em = ?{extra} WHERE telefone = ?", args)

    def transcricao(self, telefone: str) -> list[dict[str, Any]]:
        with self._trava:
            linhas = self._db.execute(
                "SELECT autor, texto, documento_id, criado_em FROM transcricao WHERE telefone = ? ORDER BY id",
                (telefone,),
            ).fetchall()
        return [dict(l) for l in linhas]

    def ultima_do_cliente(self, telefone: str) -> datetime | None:
        linha = self._um("SELECT ultima_do_cliente FROM conversas WHERE telefone = ?", telefone)
        return datetime.fromisoformat(linha["ultima_do_cliente"]) if linha and linha["ultima_do_cliente"] else None

    # ---------- O que o agente precisa saber ao voltar a atender ----------

    def anotar_para_agente(self, telefone: str, linha: str) -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone)
            self._db.execute(
                "UPDATE conversas SET notas_para_agente = notas_para_agente || ? WHERE telefone = ?",
                (linha + "\n", telefone),
            )

    def retirar_notas_para_agente(self, telefone: str) -> str:
        with self._trava, self._db:
            linha = self._db.execute("SELECT notas_para_agente FROM conversas WHERE telefone = ?", (telefone,)).fetchone()
            self._db.execute("UPDATE conversas SET notas_para_agente = '' WHERE telefone = ?", (telefone,))
        return linha["notas_para_agente"].strip() if linha else ""

    # ---------- Documentos ----------

    def salvar_documento(self, id_documento: str, telefone: str, nome_arquivo: str, mime: str, caminho: Path) -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone)
            self._db.execute(
                "INSERT INTO documentos (id, telefone, nome_arquivo, mime, caminho, criado_em) VALUES (?, ?, ?, ?, ?, ?)",
                (id_documento, telefone, nome_arquivo, mime, str(caminho), agora_utc()),
            )

    def documentos(self, telefone: str) -> list[dict[str, Any]]:
        with self._trava:
            linhas = self._db.execute(
                "SELECT id, nome_arquivo, mime, criado_em FROM documentos WHERE telefone = ? ORDER BY criado_em",
                (telefone,),
            ).fetchall()
        return [dict(l) for l in linhas]

    def documento(self, id_documento: str) -> dict[str, Any] | None:
        linha = self._um("SELECT * FROM documentos WHERE id = ?", id_documento)
        return dict(linha) if linha else None

    # ---------- Status e ficha ----------

    def status(self, telefone: str) -> Status:
        linha = self._um("SELECT status FROM conversas WHERE telefone = ?", telefone)
        return linha["status"] if linha else "bot"

    def definir_status(self, telefone: str, status: Status, motivo_humano: str = "") -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone)
            self._db.execute(
                "UPDATE conversas SET status = ?, motivo_humano = ?, atualizado_em = ? WHERE telefone = ?",
                (status, motivo_humano, agora_utc(), telefone),
            )

    def ficha(self, telefone: str) -> Ficha | None:
        linha = self._um("SELECT ficha FROM conversas WHERE telefone = ?", telefone)
        if not linha or not linha["ficha"]:
            return None
        return Ficha.model_validate_json(linha["ficha"])

    def salvar_ficha(self, telefone: str, ficha: Ficha) -> None:
        with self._trava, self._db:
            self._garantir_conversa(telefone)
            self._db.execute(
                "UPDATE conversas SET ficha = ?, atualizado_em = ? WHERE telefone = ?",
                (ficha.model_dump_json(), agora_utc(), telefone),
            )

    def caso(self, telefone: str) -> dict[str, Any] | None:
        linha = self._um(
            "SELECT telefone, nome_perfil, status, motivo_humano, ficha, ultima_do_cliente, criado_em, atualizado_em "
            "FROM conversas WHERE telefone = ?",
            telefone,
        )
        if not linha:
            return None
        caso = dict(linha)
        caso["ficha"] = json.loads(linha["ficha"]) if linha["ficha"] else None
        return caso

    def listar_casos(self) -> list[dict[str, Any]]:
        with self._trava:
            telefones = [l["telefone"] for l in self._db.execute(
                "SELECT telefone FROM conversas ORDER BY atualizado_em DESC"
            ).fetchall()]
        return [c for t in telefones if (c := self.caso(t))]

    def apagar_conversa(self, telefone: str) -> list[str]:
        """Apaga tudo o que foi guardado sobre um contato (pedido de exclusão, LGPD).
        Devolve os caminhos dos arquivos de documentos, para apagar do disco."""
        with self._trava, self._db:
            caminhos = [l["caminho"] for l in self._db.execute(
                "SELECT caminho FROM documentos WHERE telefone = ?", (telefone,)
            ).fetchall()]
            for tabela in ("mensagens", "transcricao", "documentos", "conversas"):
                self._db.execute(f"DELETE FROM {tabela} WHERE telefone = ?", (telefone,))
        return caminhos
