from app.ficha import SCHEMA, Ficha, Resposta, Sinal, TurnoAgente


def _confere(schema: dict, modelo) -> None:
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"]) == set(modelo.model_fields)


def test_schema_igual_aos_modelos():
    _confere(SCHEMA, TurnoAgente)
    ficha = SCHEMA["properties"]["ficha"]
    _confere(ficha, Ficha)
    _confere(ficha["properties"]["respostas"]["items"], Resposta)
    _confere(ficha["properties"]["sinais"]["items"], Sinal)


def test_ficha_vazia_valida():
    assert Ficha.vazia().prioridade == ""
