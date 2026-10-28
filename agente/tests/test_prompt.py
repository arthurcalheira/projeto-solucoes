from app.config import RAIZ, carregar_escritorio
from app.prompt import montar_prompt_sistema


def test_prompt_preenche_marcadores_com_o_escritorio_exemplo():
    escritorio = carregar_escritorio(RAIZ / "escritorio.example.json")
    texto = montar_prompt_sistema(escritorio)
    assert escritorio.nome in texto
    assert "<guia_de_triagem>" in texto and "BPC/LOAS" in texto
    assert "{{" not in texto


def test_guia_encontrado_com_config_dentro_de_dados(tmp_path):
    import json
    import shutil

    from app.config import carregar_escritorio

    # Imita o container: config em dados/, guia relativo à pasta do agente.
    destino = RAIZ / "dados" / "teste-config"
    destino.mkdir(parents=True, exist_ok=True)
    try:
        dados = json.loads((RAIZ / "escritorio.example.json").read_text(encoding="utf-8"))
        (destino / "escritorio.json").write_text(json.dumps(dados), encoding="utf-8")
        escritorio = carregar_escritorio(destino / "escritorio.json")
        assert escritorio.guia_triagem.is_file()
    finally:
        shutil.rmtree(destino)
