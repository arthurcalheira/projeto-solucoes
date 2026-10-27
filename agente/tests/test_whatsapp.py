import hashlib
import hmac
import json

from app.whatsapp import assinatura_valida, extrair_mensagens, mascarar

PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "changes": [{
            "value": {
                "contacts": [{"wa_id": "5519999998888", "profile": {"name": "Maria"}}],
                "messages": [
                    {"from": "5519999998888", "id": "wamid.1", "type": "text", "text": {"body": "Oi, o INSS negou meu auxílio"}},
                    {"from": "5519999998888", "id": "wamid.2", "type": "image",
                     "image": {"id": "midia-1", "mime_type": "image/jpeg", "caption": "carta do INSS"}},
                    {"from": "5519999998888", "id": "wamid.3", "type": "document",
                     "document": {"id": "midia-2", "mime_type": "application/pdf", "filename": "cnis.pdf"}},
                ],
            }
        }]
    }],
}


def test_extrai_texto_imagem_e_documento():
    msgs = extrair_mensagens(PAYLOAD)
    assert [m.tipo for m in msgs] == ["text", "image", "document"]
    assert msgs[0].texto == "Oi, o INSS negou meu auxílio"
    assert msgs[0].nome_perfil == "Maria"
    assert msgs[1].midia_id == "midia-1" and msgs[1].texto == "carta do INSS"
    assert msgs[2].nome_arquivo == "cnis.pdf"


def test_ignora_avisos_de_entrega():
    payload = {"entry": [{"changes": [{"value": {"statuses": [{"id": "wamid.x", "status": "read"}]}}]}]}
    assert extrair_mensagens(payload) == []


def test_assinatura():
    corpo = json.dumps(PAYLOAD).encode()
    assinatura = "sha256=" + hmac.new(b"segredo", corpo, hashlib.sha256).hexdigest()
    assert assinatura_valida(corpo, assinatura, "segredo")
    assert not assinatura_valida(corpo, assinatura, "outro")
    assert not assinatura_valida(corpo, None, "segredo")
    assert not assinatura_valida(corpo, assinatura, "")


def test_mascara_telefone():
    assert mascarar("5519999998888") == "5519****88"
