"""Orquestra o atendimento: junta mensagens, chama o agente, responde e avisa a equipe."""

from __future__ import annotations

import asyncio
import base64
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from .agente import AgenteTriagem
from .avisos import Avisos
from .config import Horario
from .documentos import Arquivo
from .memoria import Memoria
from .whatsapp import MensagemRecebida, mascarar

log = logging.getLogger(__name__)

IMAGENS_ACEITAS = {"image/jpeg", "image/png", "image/gif", "image/webp"}
LIMITE_IMAGEM_BYTES = 5 * 1024 * 1024  # limite da API para cada imagem
LIMITE_PDF_BYTES = 20 * 1024 * 1024

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


class Canal(Protocol):
    async def enviar_texto(self, telefone: str, texto: str) -> None: ...
    async def baixar_midia(self, midia_id: str) -> tuple[bytes, str]: ...


async def transcrever_audio(conteudo: bytes, mime: str) -> str | None:
    """Ponto de integração para transcrever áudios (o Claude não recebe áudio).

    Ligue aqui um serviço de transcrição de fala para texto e devolva o texto.
    Enquanto devolver None, o agente pede gentilmente que a pessoa escreva.
    """
    return None


def dentro_do_horario(agora: datetime, horario: Horario) -> bool:
    inicio = time.fromisoformat(horario.inicio)
    fim = time.fromisoformat(horario.fim)
    return agora.weekday() in horario.dias and inicio <= agora.time() < fim


def mensagem_de_contexto(agora: datetime, horario: Horario, notas_da_equipe: str = "") -> str:
    situacao = "dentro" if dentro_do_horario(agora, horario) else "fora"
    texto = (
        f"Agora: {DIAS[agora.weekday()]}, {agora:%d/%m/%Y %H:%M}. "
        f"O escritório está {situacao} do horário de atendimento."
    )
    if notas_da_equipe:
        texto += (
            "\n\nEnquanto uma pessoa da equipe atendia este contato, a conversa foi esta:\n"
            f"{notas_da_equipe}\n"
            "Continue a partir daqui, sem repetir o que a equipe já resolveu."
        )
    return texto


@dataclass
class Recebido:
    """Uma mensagem do cliente já com a mídia baixada e guardada."""
    msg: MensagemRecebida
    conteudo: bytes | None = None
    mime: str = ""
    documento_id: str | None = None

    def descricao(self) -> str:
        if self.msg.tipo == "text":
            return self.msg.texto
        nome = self.msg.nome_arquivo or {"image": "foto", "document": "documento", "audio": "áudio"}.get(self.msg.tipo, self.msg.tipo)
        legenda = f" ({self.msg.texto})" if self.msg.texto else ""
        return f"[{nome}]{legenda}"


class Atendimento:
    def __init__(
        self,
        agente: AgenteTriagem,
        memoria: Memoria,
        canal: Canal,
        avisos: Avisos,
        horario: Horario,
        arquivo: Arquivo,
        agrupar_segundos: float = 4.0,
    ) -> None:
        self.agente = agente
        self.memoria = memoria
        self.canal = canal
        self.avisos = avisos
        self.horario = horario
        self.arquivo = arquivo
        self.agrupar_segundos = agrupar_segundos
        self._travas: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._pendentes: dict[str, list[MensagemRecebida]] = defaultdict(list)
        # Espera em andamento por contato (só enquanto ainda está "dormindo").
        self._esperas: dict[str, asyncio.Task] = {}
        self._tarefas: set[asyncio.Task] = set()

    # ---------- Entrada pelo webhook ----------

    async def receber(self, msg: MensagemRecebida) -> None:
        """Recebe uma mensagem do webhook. Mensagens seguidas do mesmo contato são
        juntadas por alguns segundos e respondidas de uma vez."""
        if not self.memoria.marcar_processada(msg.id):
            return
        self._pendentes[msg.telefone].append(msg)
        espera = self._esperas.pop(msg.telefone, None)
        if espera:
            espera.cancel()  # ainda não começou a processar: recomeça a contagem
        tarefa = asyncio.create_task(self._processar_depois(msg.telefone))
        self._esperas[msg.telefone] = tarefa
        self._tarefas.add(tarefa)
        tarefa.add_done_callback(self._tarefas.discard)

    async def aguardar(self) -> None:
        """Espera o processamento pendente terminar (usado no simulador e nos testes)."""
        while self._tarefas:
            await asyncio.gather(*list(self._tarefas), return_exceptions=True)

    async def _processar_depois(self, telefone: str) -> None:
        try:
            await asyncio.sleep(self.agrupar_segundos)
        except asyncio.CancelledError:
            return  # chegou outra mensagem; a nova espera cuida do lote
        if self._esperas.get(telefone) is asyncio.current_task():
            del self._esperas[telefone]  # daqui em diante não pode mais ser cancelada
        async with self._travas[telefone]:
            lote = self._pendentes.pop(telefone, [])
            if lote:
                try:
                    await self._processar(telefone, lote)
                except Exception:
                    log.exception("Erro ao processar mensagens de %s", mascarar(telefone))

    async def _processar(self, telefone: str, lote: list[MensagemRecebida]) -> None:
        recebidos = [await self._baixar_e_guardar(m) for m in lote]
        for r in recebidos:
            self.memoria.registrar(telefone, "cliente", r.descricao(), r.documento_id, nome_perfil=r.msg.nome_perfil)

        if self.memoria.status(telefone) == "humano":
            # Uma pessoa da equipe está atendendo: o agente não responde, só toma nota.
            for r in recebidos:
                self.memoria.anotar_para_agente(telefone, f"Cliente: {r.descricao()}")
            await self.avisos.notificar(telefone, "nova_mensagem", self.memoria.ficha(telefone))
            return

        entrada = await self._montar_entrada(recebidos)
        agora = datetime.now(ZoneInfo(self.horario.fuso))
        notas = self.memoria.retirar_notas_para_agente(telefone)
        resultado = await self.agente.responder(
            historico=self.memoria.historico(telefone),
            entrada=entrada,
            contexto=mensagem_de_contexto(agora, self.horario, notas),
            ficha_atual=self.memoria.ficha(telefone),
        )
        turno = resultado.turno
        self.memoria.acrescentar(telefone, resultado.novas_mensagens, nome_perfil=lote[0].nome_perfil)
        self.memoria.salvar_ficha(telefone, turno.ficha)
        log.info("Turno de %s: acao=%s uso=%s", mascarar(telefone), turno.acao, resultado.uso)

        for texto in turno.mensagens:
            if texto.strip():
                await self.canal.enviar_texto(telefone, texto)
                self.memoria.registrar(telefone, "agente", texto)

        status_anterior = self.memoria.status(telefone)
        if turno.acao == "humano":
            self.memoria.definir_status(telefone, "humano", turno.motivo_humano)
            await self.avisos.notificar(telefone, "humano", turno.ficha, turno.motivo_humano)
        elif turno.acao == "concluido" and status_anterior != "concluido":
            self.memoria.definir_status(telefone, "concluido")
            await self.avisos.notificar(telefone, "concluido", turno.ficha)

    # ---------- Ações da equipe (pelo painel) ----------

    async def responder_como_equipe(self, telefone: str, texto: str) -> None:
        """Uma pessoa da equipe responde ao cliente pelo mesmo número do WhatsApp."""
        async with self._travas[telefone]:
            await self.canal.enviar_texto(telefone, texto)
            self.memoria.registrar(telefone, "equipe", texto)
            self.memoria.anotar_para_agente(telefone, f"Equipe: {texto}")
            if self.memoria.status(telefone) != "humano":
                self.memoria.definir_status(telefone, "humano", "Assumido pela equipe")

    def assumir(self, telefone: str) -> None:
        self.memoria.definir_status(telefone, "humano", "Assumido pela equipe")

    def devolver_ao_agente(self, telefone: str) -> None:
        self.memoria.definir_status(telefone, "bot")

    # ---------- Mídias ----------

    async def _baixar_e_guardar(self, msg: MensagemRecebida) -> Recebido:
        if msg.tipo == "text" or not msg.midia_id:
            return Recebido(msg)
        try:
            conteudo, mime = await self.canal.baixar_midia(msg.midia_id)
        except Exception:
            log.exception("Falha ao baixar mídia")
            return Recebido(msg)
        mime = mime or msg.mime
        documento_id = self.arquivo.salvar(msg.telefone, conteudo, mime, msg.nome_arquivo)
        return Recebido(msg, conteudo, mime, documento_id)

    async def _montar_entrada(self, recebidos: list[Recebido]) -> list[dict[str, Any]]:
        """Transforma as mensagens do WhatsApp em blocos de conteúdo para o Claude."""
        blocos: list[dict[str, Any]] = []
        for r in recebidos:
            msg = r.msg
            if msg.tipo == "text":
                blocos.append({"type": "text", "text": msg.texto})
                continue
            if r.conteudo is None:
                if msg.tipo in ("image", "document", "audio"):
                    blocos.append({"type": "text", "text": "[A pessoa enviou um arquivo que não pôde ser baixado. Peça que envie de novo.]"})
                else:
                    blocos.append({"type": "text", "text": f"[A pessoa enviou uma mensagem do tipo '{msg.tipo}', que não é lida por aqui.]"})
            else:
                blocos.extend(await self._bloco_de_midia(msg, r.conteudo, r.mime))
            if msg.texto:
                blocos.append({"type": "text", "text": f"Legenda: {msg.texto}"})
        return blocos or [{"type": "text", "text": "[Mensagem vazia]"}]

    async def _bloco_de_midia(self, msg: MensagemRecebida, conteudo: bytes, mime: str) -> list[dict[str, Any]]:
        if mime in IMAGENS_ACEITAS and len(conteudo) <= LIMITE_IMAGEM_BYTES:
            dados = base64.standard_b64encode(conteudo).decode()
            return [{"type": "image", "source": {"type": "base64", "media_type": mime, "data": dados}}]
        if mime == "application/pdf" and len(conteudo) <= LIMITE_PDF_BYTES:
            dados = base64.standard_b64encode(conteudo).decode()
            bloco: dict[str, Any] = {"type": "document", "source": {"type": "base64", "media_type": mime, "data": dados}}
            if msg.nome_arquivo:
                bloco["title"] = msg.nome_arquivo
            return [bloco]
        if mime.startswith("audio/"):
            texto = await transcrever_audio(conteudo, mime)
            if texto:
                return [{"type": "text", "text": f"[Áudio transcrito] {texto}"}]
            return [{"type": "text", "text": "[A pessoa enviou um áudio, mas a transcrição ainda não está ligada. Peça com gentileza que escreva a mensagem.]"}]
        return [{"type": "text", "text": f"[A pessoa enviou um arquivo ({mime or 'tipo desconhecido'}) que não dá para ler. O arquivo foi guardado para a equipe. Peça uma foto ou um PDF.]"}]
