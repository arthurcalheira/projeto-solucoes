import asyncio

from app.agente import AgenteTriagem
from app.atendimento import Atendimento, dentro_do_horario
from app.config import Horario
from app.memoria import Memoria
from app.whatsapp import MensagemRecebida
from tests.falsos import AvisosFalsos, CanalFalso, ClienteFalso, resposta_api, turno

HORARIO = Horario((0, 1, 2, 3, 4), "08:00", "18:00", "America/Sao_Paulo")
TEL = "5519999998888"


def _montar(respostas, midias=None):
    cliente = ClienteFalso(respostas)
    memoria = Memoria(":memory:")
    canal = CanalFalso(midias)
    avisos = AvisosFalsos()
    agente = AgenteTriagem(cliente, "claude-opus-5-5", "medium", "PROMPT")
    return Atendimento(agente, memoria, canal, avisos, HORARIO, agrupar_segundos=0.05), cliente, memoria, canal, avisos


def _texto(id_, texto):
    return MensagemRecebida(id=id_, telefone=TEL, tipo="text", texto=texto)


def _rodar(atendimento, *mensagens):
    async def fluxo():
        for m in mensagens:
            await atendimento.receber(m)
        await atendimento.aguardar()
    asyncio.run(fluxo())


def test_junta_mensagens_seguidas_numa_chamada():
    atendimento, cliente, memoria, canal, _ = _montar([resposta_api(turno(mensagens=["Olá, Maria!"]))])
    _rodar(atendimento, _texto("1", "Oi"), _texto("2", "Meu nome é Maria"))
    assert len(cliente.chamadas) == 1
    entrada = cliente.chamadas[0]["messages"][0]["content"]
    assert [b["text"] for b in entrada] == ["Oi", "Meu nome é Maria"]
    assert canal.enviadas == [(TEL, "Olá, Maria!")]
    assert len(memoria.historico(TEL)) == 3


def test_ignora_webhook_repetido():
    atendimento, cliente, *_ = _montar([resposta_api(turno())])
    _rodar(atendimento, _texto("1", "Oi"), _texto("1", "Oi"))
    assert len(cliente.chamadas) == 1


def test_imagem_e_pdf_viram_blocos_para_o_claude():
    midias = {"m1": (b"\xff\xd8foto", "image/jpeg"), "m2": (b"%PDF-1.7", "application/pdf")}
    atendimento, cliente, *_ = _montar([resposta_api(turno())], midias)
    _rodar(
        atendimento,
        MensagemRecebida(id="1", telefone=TEL, tipo="image", midia_id="m1", texto="carta do INSS"),
        MensagemRecebida(id="2", telefone=TEL, tipo="document", midia_id="m2", nome_arquivo="cnis.pdf"),
    )
    tipos = [b["type"] for b in cliente.chamadas[0]["messages"][0]["content"]]
    assert tipos == ["image", "text", "document"]


def test_passa_para_humano_e_para_de_responder():
    atendimento, cliente, memoria, canal, avisos = _montar([resposta_api(turno("humano", ["Já chamei a equipe."]))])
    _rodar(atendimento, _texto("1", "Quero falar com uma pessoa"))
    assert memoria.status(TEL) == "humano"
    assert avisos.eventos == [(TEL, "humano")]

    _rodar(atendimento, _texto("2", "Alô?"))
    assert len(cliente.chamadas) == 1  # o agente não foi chamado de novo
    assert canal.enviadas == [(TEL, "Já chamei a equipe.")]
    assert avisos.eventos[-1] == (TEL, "nova_mensagem")


def test_concluido_avisa_uma_vez():
    respostas = [resposta_api(turno("concluido", assunto="bpc")), resposta_api(turno("concluido", assunto="bpc"))]
    atendimento, _, memoria, _, avisos = _montar(respostas)
    _rodar(atendimento, _texto("1", "Pronto"))
    _rodar(atendimento, _texto("2", "Mandei mais um documento"))
    assert memoria.status(TEL) == "concluido"
    assert avisos.eventos == [(TEL, "concluido")]
    assert memoria.ficha(TEL).assunto == "bpc"


def test_horario_de_atendimento():
    from datetime import datetime

    assert dentro_do_horario(datetime(2026, 10, 26, 10, 0), HORARIO)  # segunda, 10h
    assert not dentro_do_horario(datetime(2026, 10, 26, 19, 0), HORARIO)  # segunda, 19h
    assert not dentro_do_horario(datetime(2026, 10, 25, 10, 0), HORARIO)  # domingo
