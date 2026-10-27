from app.config import RAIZ, carregar_escritorio
from app.prompt import montar_prompt_sistema


def test_prompt_preenche_marcadores_com_o_escritorio_exemplo():
    escritorio = carregar_escritorio(RAIZ / "escritorio.example.json")
    texto = montar_prompt_sistema(escritorio)
    assert escritorio.nome in texto
    assert "<guia_de_triagem>" in texto and "BPC/LOAS" in texto
    assert "{{" not in texto
