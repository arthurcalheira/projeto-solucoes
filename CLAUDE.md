# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Projeto de dois sócios que vendem soluções de IA para escritórios de
advocacia previdenciária. Produto principal: agente de triagem no WhatsApp
(pasta `agente/`). O resto do repositório é documentação de negócio.

## Ao começar e ao terminar uma sessão

Leia o [`STATUS.md`](STATUS.md): decisões tomadas, o que está pronto, o que
falta e os próximos passos. Ao terminar, atualize esse arquivo (data no topo,
o que mudou e uma linha no histórico).

## Idioma e estilo

- Escreva sempre em português do Brasil: documentos, comentários e nomes no
  código, mensagens de commit e PRs.
- Documentos curtos e diretos, com tabelas quando ajudam. Não invente
  números: cite a fonte ou marque como estimativa.

## Onde fica cada coisa

- `00-estrategia/`: posicionamento, preços, plano de 90 dias, marca e forma de trabalhar
- `01-catalogo/`: soluções vendidas, com código (PREV01, ADV01...)
- `02-verticais/advocacia/previdenciario/`: o produto PREV01 e o guia de triagem
- `03-comercial/` e `07-prospeccao/`: material de venda e lista de escritórios
- `04-entrega/`, `05-compliance/`, `06-clientes/`: implantação, LGPD e clientes
- `agente/`: código Python do agente, painel e conversas de teste (ver `agente/README.md` e `agente/DEPLOY.md`)
- `demo/`: demo clicável usada nas reuniões (um HTML só, publicado como artifact; o link está no `STATUS.md`)

## Comandos (`agente/`)

Python 3.11+, FastAPI, SDK `anthropic`. Todos os comandos rodam de dentro de
`agente/`, com o venv ativo.

```bash
cd agente
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

pytest                                         # todos os testes; não chamam a API
pytest tests/test_agente.py                    # um arquivo
pytest tests/test_agente.py -k recusa          # um teste, pelo nome

uvicorn app.main:app --port 8000               # servidor (webhook, /painel, /casos, /saude)
python simulador.py                            # conversa pelo terminal (PAGO)
python -m avaliacao.rodar --cenario pede-humano   # conversas de teste (PAGO)
```

- Rode `pytest` antes de cada commit. Não há linter nem formatador
  configurado.
- `simulador.py` e `avaliacao.rodar` fazem **chamadas pagas** à API e precisam
  de `ANTHROPIC_API_KEY` no `agente/.env`. Não rode sem o usuário pedir, e
  não use `--confirmar` (pula a confirmação de gasto) por conta própria.
- Docker: o contexto do build é a **raiz do repositório**, não `agente/`
  (`docker build -f agente/Dockerfile -t agente-triagem .`), porque a imagem
  copia o guia de triagem de `02-verticais/`.
- `agente/dados/` (banco, documentos recebidos, resultados da avaliação),
  `agente/.env` e `agente/escritorio.json` ficam fora do git. Sem
  `escritorio.json`, o código usa o `escritorio.example.json`.

## Arquitetura do agente

O diagrama e a tabela de arquivos estão no `agente/README.md`. O que só
aparece lendo vários arquivos:

**Caminho de uma mensagem.** `main.py` (webhook, assinatura da Meta) →
`Atendimento.receber` → `AgenteTriagem.responder` → `Memoria`. O
`Atendimento` ignora mensagens repetidas (tabela `processadas`), espera
`AGRUPAR_SEGUNDOS` para juntar mensagens seguidas do mesmo telefone numa
chamada só e usa uma trava por telefone.

**Cada chamada ao Claude** envia `[*histórico, mensagem do cliente, mensagem
de contexto]`. A mensagem de contexto tem papel `system`, vai no fim e leva
tudo o que varia: data, hora, se o escritório está aberto e as notas da
equipe. Se a chamada dá certo, as três mensagens (cliente, contexto,
resposta) entram no histórico. Se falha (erro da API, recusa, corte por
`max_tokens`, JSON fora do formato), só a mensagem do cliente entra, o caso
vai para um humano e a ficha anterior é mantida.

**O prompt de sistema é montado uma vez**, na inicialização (`app/prompt.py`):
`prompts/sistema.md` + os campos do `escritorio.json` + o guia de triagem.
O guia é o arquivo `02-verticais/advocacia/previdenciario/triagem-por-beneficio.md`,
fonte única: **editar esse documento muda o comportamento do agente**.

**Dois registros de cada conversa** em `app/memoria.py` (SQLite):
`mensagens` é o histórico no formato da API, que só cresce; `transcricao` é
a conversa legível que o painel mostra (cliente, agente e equipe). Quem
escreve numa nem sempre escreve na outra.

**Status do caso:** `bot` → `humano` ou `concluido`. Em `humano` o agente
não responde: as mensagens do cliente e da equipe se acumulam em
`notas_para_agente` e são entregues na mensagem de contexto quando o caso é
devolvido ao agente (painel ou `POST /casos/{telefone}/devolver-ao-agente`).

**Ficha:** o modelo devolve a ficha completa a cada turno e ela substitui a
anterior. O formato está em `app/ficha.py` duas vezes: o `SCHEMA` (vai para
a API) e os modelos Pydantic (validam a resposta). Mudou um, mude o outro;
`tests/test_ficha.py` confere. `painel.py` e `avisos.py` leem os campos pelo
nome.

**Testes:** os dublês ficam em `tests/falsos.py` (`ClienteFalso` imita
`client.beta.messages.create` e guarda os argumentos; `CanalFalso`;
`AvisosFalsos`) e o banco é `Memoria(":memory:")`. `tests/test_avaliacao.py`
exige exatamente 20 cenários em `avaliacao/cenarios.json`: ao criar ou tirar
um cenário, ajuste o teste e os textos que citam "20 cenários".

## Cuidados ao mexer no código

- **O histórico só cresce.** Nunca edite nem apague mensagens antigas antes
  de enviar à API: isso invalida o cache e os blocos de raciocínio.
- **O prompt de sistema precisa ficar fixo.** Nada de data, hora ou dado
  variável em `prompts/sistema.md` nem no que `montar_prompt_sistema`
  preenche. O que varia vai na mensagem de contexto.
- **A chamada em `app/agente.py` nunca rodou contra a API de verdade** (ver
  `STATUS.md`) e usa recursos recentes: saída estruturada em `output_config`,
  mensagem `system` dentro de `messages`, `fallbacks` em beta só para os
  modelos de `MODELOS_COM_FALLBACK`. Antes de "corrigir" algo ali de memória,
  confira a documentação atual da API (skill `claude-api`).
- **Privacidade nos logs e avisos:** telefone sempre por `mascarar()`, nunca
  o conteúdo das conversas. O e-mail de aviso não leva resumo nem dados de
  saúde; a ficha completa só vai no webhook.
- **Há dois prompts:** `agente/prompts/sistema.md` é o que o código usa;
  `02-verticais/advocacia/previdenciario/prompt-agente.md` é a versão
  documentada para a implantação sem código. Mudança de regra vale para os
  dois.
- **Depois de mudar o prompt ou o guia de triagem,** as conversas de teste
  precisam ser rodadas de novo. Como são pagas, avise o usuário em vez de
  rodar.
- O painel é HTML gerado no servidor, sem JavaScript, de propósito (funciona
  em qualquer celular). Texto que vem do cliente ou do modelo entra na
  página sempre por `escape()`.

## Regras que não podem ser quebradas

- Nunca coloque senhas, chaves de API ou tokens no repositório.
- Nunca use dados reais de clientes dos escritórios em testes, exemplos ou
  documentos. Use casos fictícios.
- O agente nunca diz se a pessoa tem direito, nunca promete resultado ou
  valor e nunca pede senha do gov.br. Mudanças no prompt não podem
  enfraquecer essas regras, nem as expressões de
  `proibido_em_qualquer_resposta` em `avaliacao/cenarios.json` que as
  conferem.
- Não faça commit direto no `main`: trabalhe numa branch e abra um PR.
