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
