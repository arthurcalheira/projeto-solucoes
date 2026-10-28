import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente_http(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "teste")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "verifica")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "segredo")
    monkeypatch.setenv("PAINEL_TOKEN", "painel")
    monkeypatch.setenv("BANCO", str(tmp_path / "teste.db"))
    monkeypatch.setenv("PASTA_DOCUMENTOS", str(tmp_path / "docs"))
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_verificacao_do_webhook(cliente_http):
    ok = cliente_http.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "verifica", "hub.challenge": "123"})
    assert ok.status_code == 200 and ok.text == "123"
    errado = cliente_http.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "123"})
    assert errado.status_code == 403


def test_webhook_sem_assinatura_valida_e_recusado(cliente_http):
    corpo = json.dumps({"entry": []}).encode()
    assert cliente_http.post("/webhook", content=corpo).status_code == 401
    assinatura = "sha256=" + hmac.new(b"segredo", corpo, hashlib.sha256).hexdigest()
    resposta = cliente_http.post("/webhook", content=corpo, headers={"X-Hub-Signature-256": assinatura})
    assert resposta.status_code == 200


def test_painel_exige_token(cliente_http):
    assert cliente_http.get("/casos").status_code == 401
    assert cliente_http.get("/casos", headers={"X-Painel-Token": "painel"}).json() == []


def _logar(c):
    r = c.post("/painel/entrar", content="senha=painel", headers={"Content-Type": "application/x-www-form-urlencoded"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/painel"


def test_painel_exige_login(cliente_http):
    r = cliente_http.get("/painel", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/painel/entrar"
    errado = cliente_http.post("/painel/entrar", content="senha=x", headers={"Content-Type": "application/x-www-form-urlencoded"}, follow_redirects=False)
    assert errado.headers["location"].startswith("/painel/entrar?erro")


def test_painel_mostra_caso_documento_e_envia_resposta(cliente_http):
    from tests.falsos import CanalFalso, turno

    app = cliente_http.app
    tel = "5571999990000"
    memoria = app.state.memoria
    memoria.registrar(tel, "cliente", "Oi, meu auxílio foi negado", nome_perfil="José")
    memoria.salvar_ficha(tel, turno(nome="José Souza", assunto="negativa", prioridade="alta",
                                    resumo_para_advogado="Auxílio negado há 10 dias.").ficha)
    doc_id = app.state.arquivo.salvar(tel, b"%PDF-1.7 carta", "application/pdf", "carta-inss.pdf")
    memoria.registrar(tel, "cliente", "[carta-inss.pdf]", doc_id)
    canal = CanalFalso()
    app.state.atendimento.canal = canal

    _logar(cliente_http)
    lista = cliente_http.get("/painel")
    assert "José Souza" in lista.text and "Alta" in lista.text

    pagina = cliente_http.get(f"/painel/caso/{tel}")
    assert "Auxílio negado há 10 dias." in pagina.text and "carta-inss.pdf" in pagina.text

    arquivo = cliente_http.get(f"/painel/documento/{doc_id}")
    assert arquivo.status_code == 200 and arquivo.content == b"%PDF-1.7 carta"

    r = cliente_http.post(f"/painel/caso/{tel}/responder", content="texto=Ol%C3%A1%2C+Jos%C3%A9%21",
                          headers={"Content-Type": "application/x-www-form-urlencoded"}, follow_redirects=False)
    assert r.status_code == 303
    assert canal.enviadas == [(tel, "Olá, José!")]
    assert memoria.status(tel) == "humano"

    cliente_http.post(f"/painel/caso/{tel}/devolver", follow_redirects=False)
    assert memoria.status(tel) == "bot"


def test_documento_exige_login(cliente_http):
    assert cliente_http.get("/painel/documento/qualquer", follow_redirects=False).status_code == 303
