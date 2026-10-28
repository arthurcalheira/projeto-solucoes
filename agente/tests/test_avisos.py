from app.avisos import montar_email
from tests.falsos import turno


def test_email_leva_link_e_nao_leva_resumo():
    ficha = turno(nome="Maria Aparecida", assunto="negativa", prioridade="alta",
                  resumo_para_advogado="Laudo psiquiátrico, CID F32").ficha
    msg = montar_email("concluido", "5519999998888", ficha, "", "https://agente.exemplo.com.br",
                       "agente@exemplo.com.br", ("adv@exemplo.com.br",))
    corpo = msg.get_content()
    assert "Maria Aparecida" in msg["Subject"] and "prioridade alta" in msg["Subject"]
    assert "https://agente.exemplo.com.br/painel/caso/5519999998888" in corpo
    assert "CID" not in corpo and "CID" not in msg["Subject"]


def test_email_de_passagem_para_humano():
    msg = montar_email("humano", "5519999998888", None, "Pediu para falar com alguém", "", "a@b.com", ("c@d.com",))
    assert msg["Subject"].startswith("Cliente precisa de atendimento")
    assert "Pediu para falar com alguém" in msg.get_content()
