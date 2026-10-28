"""Painel web do advogado: lista de casos, ficha, documentos e resposta ao cliente.

Acesso por senha (PAINEL_TOKEN). Depois do login, um cookie HttpOnly mantém a
sessão. Páginas em HTML simples, sem JavaScript, para funcionar em qualquer
navegador, inclusive no celular.
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response

from .ficha import ASSUNTOS, CASO_DE

router = APIRouter(prefix="/painel")

COOKIE = "painel_sessao"
STATUS = {"bot": "Com o agente", "humano": "Com a equipe", "concluido": "Pronto para análise"}
PRIORIDADE = {"alta": "Alta", "media": "Média", "baixa": "Baixa", "": "—"}
AUTOR = {"cliente": "Cliente", "agente": "Agente", "equipe": "Equipe"}
JANELA_WHATSAPP = timedelta(hours=24)

ESTILO = """
:root { --bg:#eef1f4; --sup:#fff; --tinta:#15202b; --suave:#5a6776; --linha:#d5dce4; --marca:#1b4d6b;
  --alta:#a8261b; --alta-f:#f8e1de; --media:#8f5a00; --media-f:#f7ead2; --baixa:#3b6446; --baixa-f:#e0eee3; }
@media (prefers-color-scheme: dark) { :root { --bg:#0f151b; --sup:#17202a; --tinta:#e6ecf2; --suave:#9aa8b7;
  --linha:#2b3946; --marca:#6fb0d6; --alta:#f08a7e; --alta-f:#3a1d1a; --media:#e5b45c; --media-f:#352813;
  --baixa:#8fc79c; --baixa-f:#1b2e20; color-scheme: dark; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--tinta); font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1000px; margin: 0 auto; padding: 20px 16px 40px; display: grid; gap: 16px; }
h1 { font-size: 1.3rem; margin: 0; } h2 { font-size: 1rem; margin: 0 0 8px; }
a { color: var(--marca); }
.card { background: var(--sup); border: 1px solid var(--linha); border-radius: 12px; padding: 16px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--linha); vertical-align: top; }
th { color: var(--suave); font-size: 0.75rem; text-transform: uppercase; letter-spacing: .05em; }
.pill { display: inline-block; padding: 1px 9px; border-radius: 99px; font-size: .78rem; font-weight: 700; background: var(--bg); }
.alta { background: var(--alta-f); color: var(--alta); } .media { background: var(--media-f); color: var(--media); }
.baixa { background: var(--baixa-f); color: var(--baixa); }
.topo { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; justify-content: space-between; }
.grade { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; margin: 0; }
dt { color: var(--suave); } dd { margin: 0; overflow-wrap: anywhere; }
ul { margin: 0; padding-left: 18px; }
.msg { padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; background: var(--bg); }
.msg small { color: var(--suave); }
.msg.equipe { border-left: 3px solid var(--marca); }
textarea { width: 100%; min-height: 80px; font: inherit; padding: 8px; border-radius: 8px; border: 1px solid var(--linha); background: var(--sup); color: var(--tinta); }
input[type=password] { font: inherit; padding: 8px; border-radius: 8px; border: 1px solid var(--linha); width: 100%; max-width: 320px; }
button { font: inherit; font-weight: 600; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--marca); background: var(--marca); color: #fff; cursor: pointer; }
button.sec { background: transparent; color: var(--marca); }
.acoes { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.aviso { color: var(--media); font-size: .9rem; }
"""


def _sessao(token: str) -> str:
    return hmac.new(token.encode(), b"painel", hashlib.sha256).hexdigest()


def _logado(request: Request) -> bool:
    token = request.app.state.cfg.painel_token
    cookie = request.cookies.get(COOKIE, "")
    return bool(token) and hmac.compare_digest(cookie, _sessao(token))


def _exigir(request: Request) -> None:
    if not _logado(request):
        raise HTTPException(status_code=303, headers={"Location": "/painel/entrar"})


async def _formulario(request: Request) -> dict[str, str]:
    dados = parse_qs((await request.body()).decode())
    return {k: v[0] for k, v in dados.items()}


def _pagina(titulo: str, corpo: str) -> HTMLResponse:
    html = (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{escape(titulo)}</title><style>{ESTILO}</style></head>"
        f"<body><main>{corpo}</main></body></html>"
    )
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


def _pill_prioridade(p: str) -> str:
    return f"<span class='pill {escape(p)}'>{PRIORIDADE.get(p, '—')}</span>"


def _hora(iso: str | None) -> str:
    if not iso:
        return "—"
    return datetime.fromisoformat(iso).astimezone().strftime("%d/%m %H:%M")


# ---------- Login ----------

@router.get("/entrar")
async def tela_entrar(erro: str = "") -> HTMLResponse:
    msg = "<p class='aviso'>Senha incorreta.</p>" if erro else ""
    return _pagina("Entrar no painel", f"""
      <div class='card'><h1>Painel do escritório</h1>{msg}
      <form method='post' action='/painel/entrar'>
        <p><label for='senha'>Senha do painel</label><br><input id='senha' name='senha' type='password' autofocus></p>
        <button type='submit'>Entrar</button>
      </form></div>""")


@router.post("/entrar")
async def entrar(request: Request) -> Response:
    senha = (await _formulario(request)).get("senha", "")
    token = request.app.state.cfg.painel_token
    if not token or not hmac.compare_digest(senha, token):
        return RedirectResponse("/painel/entrar?erro=1", status_code=303)
    resposta = RedirectResponse("/painel", status_code=303)
    resposta.set_cookie(
        COOKIE, _sessao(token), httponly=True, samesite="strict",
        secure=request.url.scheme == "https", max_age=12 * 3600,
    )
    return resposta


@router.post("/sair")
async def sair() -> Response:
    resposta = RedirectResponse("/painel/entrar", status_code=303)
    resposta.delete_cookie(COOKIE)
    return resposta


# ---------- Lista de casos ----------

@router.get("")
async def lista(request: Request) -> HTMLResponse:
    _exigir(request)
    casos = request.app.state.memoria.listar_casos()
    ordem = {"humano": 0, "concluido": 1, "bot": 2}
    casos.sort(key=lambda c: ordem.get(c["status"], 3))
    linhas = []
    for c in casos:
        f = c["ficha"] or {}
        nome = f.get("nome") or c["nome_perfil"] or "Sem nome"
        linhas.append(
            f"<tr><td><a href='/painel/caso/{quote(c['telefone'])}'>{escape(nome)}</a></td>"
            f"<td>{escape(ASSUNTOS.get(f.get('assunto', ''), '') or '—')}</td>"
            f"<td>{_pill_prioridade(f.get('prioridade', ''))}</td>"
            f"<td>{STATUS.get(c['status'], c['status'])}</td>"
            f"<td>{_hora(c['atualizado_em'])}</td></tr>"
        )
    tabela = "".join(linhas) or "<tr><td colspan='5'>Nenhum caso ainda. Eles aparecem aqui quando alguém escrever no WhatsApp.</td></tr>"
    return _pagina("Casos", f"""
      <div class='topo'><h1>Casos</h1>
        <form method='post' action='/painel/sair'><button class='sec' type='submit'>Sair</button></form></div>
      <div class='card'><table>
        <thead><tr><th>Cliente</th><th>Assunto</th><th>Prioridade</th><th>Situação</th><th>Atualizado</th></tr></thead>
        <tbody>{tabela}</tbody></table></div>""")


# ---------- Um caso ----------

@router.get("/caso/{telefone}")
async def ver_caso(telefone: str, request: Request, erro: str = "") -> HTMLResponse:
    _exigir(request)
    memoria = request.app.state.memoria
    caso = memoria.caso(telefone)
    if not caso:
        raise HTTPException(status_code=404)
    f = caso["ficha"] or {}
    nome = f.get("nome") or caso["nome_perfil"] or "Sem nome"

    dados = [
        ("Telefone", telefone), ("Situação", STATUS.get(caso["status"], caso["status"])),
        ("Caso de", CASO_DE.get(f.get("caso_de", ""), "") or "—"), ("Assunto", ASSUNTOS.get(f.get("assunto", ""), "") or "—"),
        ("Benefício negado", f.get("beneficio_negado") or "—"), ("Cidade", f.get("cidade_uf") or "—"),
    ]
    if caso["motivo_humano"]:
        dados.append(("Motivo", caso["motivo_humano"]))
    dl = "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in dados)
    respostas = "".join(f"<dt>{escape(r['pergunta'])}</dt><dd>{escape(r['resposta'])}</dd>" for r in f.get("respostas", []))
    sinais = "".join(f"<li>{_pill_prioridade(s['nivel'])} {escape(s['texto'])}</li>" for s in f.get("sinais", []))

    docs = memoria.documentos(telefone)
    lista_docs = "".join(
        f"<li><a href='/painel/documento/{d['id']}' target='_blank' rel='noopener'>{escape(d['nome_arquivo'])}</a> <small>{_hora(d['criado_em'])}</small></li>"
        for d in docs
    ) or "<li>Nenhum arquivo recebido.</li>"
    pendentes = "".join(f"<li>{escape(d)}</li>" for d in f.get("documentos_pendentes", [])) or "<li>Nenhum.</li>"

    conversa = "".join(
        f"<div class='msg {m['autor']}'><small>{AUTOR.get(m['autor'], m['autor'])} · {_hora(m['criado_em'])}</small><br>"
        + (f"<a href='/painel/documento/{m['documento_id']}' target='_blank' rel='noopener'>{escape(m['texto'])}</a>" if m["documento_id"] else escape(m["texto"]))
        + "</div>"
        for m in memoria.transcricao(telefone)
    )

    ultima = memoria.ultima_do_cliente(telefone)
    fora_da_janela = ultima is None or datetime.now(timezone.utc) - ultima > JANELA_WHATSAPP
    aviso_janela = (
        "<p class='aviso'>Já se passaram mais de 24 h desde a última mensagem do cliente. "
        "O WhatsApp só permite responder com uma mensagem de modelo aprovada pela Meta.</p>"
        if fora_da_janela else ""
    )
    aviso_erro = "<p class='aviso'>A mensagem não foi enviada. Confira a conexão com o WhatsApp e tente de novo.</p>" if erro else ""
    tel = quote(telefone)
    if caso["status"] == "humano":
        botao_status = f"<form method='post' action='/painel/caso/{tel}/devolver'><button class='sec' type='submit'>Devolver ao agente</button></form>"
    else:
        botao_status = f"<form method='post' action='/painel/caso/{tel}/assumir'><button class='sec' type='submit'>Assumir o atendimento</button></form>"

    return _pagina(nome, f"""
      <div class='topo'><h1>{escape(nome)} {_pill_prioridade(f.get('prioridade', ''))}</h1>
        <a href='/painel'>← Todos os casos</a></div>
      <div class='grade'>
        <div class='card'><h2>Dados</h2><dl>{dl}</dl></div>
        <div class='card'><h2>Resumo para o advogado</h2><p>{escape(f.get('resumo_para_advogado') or 'A triagem ainda não terminou.')}</p>
          <h2>Sinais para análise</h2><ul>{sinais or '<li>Nenhum ainda.</li>'}</ul></div>
        <div class='card'><h2>Respostas da triagem</h2><dl>{respostas or '<dd>Nenhuma ainda.</dd>'}</dl></div>
        <div class='card'><h2>Arquivos recebidos</h2><ul>{lista_docs}</ul>
          <h2 style='margin-top:12px'>Documentos pendentes</h2><ul>{pendentes}</ul></div>
      </div>
      <div class='card'><h2>Conversa</h2>{conversa or '<p>Sem mensagens.</p>'}</div>
      <div class='card'><h2>Responder pelo WhatsApp do escritório</h2>{aviso_janela}{aviso_erro}
        <form method='post' action='/painel/caso/{tel}/responder'>
          <label for='texto' class='aviso' style='color:var(--suave)'>Ao responder, o agente para de atender este contato até você devolver.</label>
          <textarea id='texto' name='texto' required></textarea>
          <div class='acoes'><button type='submit'>Enviar</button></div>
        </form>
        <div class='acoes'>{botao_status}</div></div>""")


@router.post("/caso/{telefone}/responder")
async def responder(telefone: str, request: Request) -> Response:
    _exigir(request)
    texto = (await _formulario(request)).get("texto", "").strip()
    destino = f"/painel/caso/{quote(telefone)}"
    if texto:
        try:
            await request.app.state.atendimento.responder_como_equipe(telefone, texto)
        except Exception:
            return RedirectResponse(destino + "?erro=1", status_code=303)
    return RedirectResponse(destino, status_code=303)


@router.post("/caso/{telefone}/assumir")
async def assumir(telefone: str, request: Request) -> Response:
    _exigir(request)
    request.app.state.atendimento.assumir(telefone)
    return RedirectResponse(f"/painel/caso/{quote(telefone)}", status_code=303)


@router.post("/caso/{telefone}/devolver")
async def devolver(telefone: str, request: Request) -> Response:
    _exigir(request)
    request.app.state.atendimento.devolver_ao_agente(telefone)
    return RedirectResponse(f"/painel/caso/{quote(telefone)}", status_code=303)


@router.get("/documento/{id_documento}")
async def documento(id_documento: str, request: Request) -> Response:
    _exigir(request)
    doc = request.app.state.memoria.documento(id_documento)
    if not doc or not Path(doc["caminho"]).is_file():
        raise HTTPException(status_code=404)
    return FileResponse(
        doc["caminho"], media_type=doc["mime"], filename=doc["nome_arquivo"],
        content_disposition_type="inline", headers={"Cache-Control": "no-store"},
    )
