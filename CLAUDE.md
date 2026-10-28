# Instruções para o Claude neste repositório

Projeto de dois sócios que vendem soluções de IA para escritórios de
advocacia previdenciária. Produto principal: agente de triagem no WhatsApp
(pasta `agente/`).

## Idioma e estilo

- Escreva sempre em português do Brasil: documentos, comentários de código,
  mensagens de commit e PRs.
- Documentos curtos e diretos, com tabelas quando ajudam. Não invente
  números: cite a fonte ou marque como estimativa.

## Onde fica cada coisa

- `00-estrategia/`: posicionamento, preços, plano de 90 dias, marca e forma de trabalhar
- `01-catalogo/`: soluções vendidas, com código (PREV01, ADV01...)
- `02-verticais/advocacia/previdenciario/`: o produto PREV01 e o guia de triagem
- `03-comercial/` e `07-prospeccao/`: material de venda e lista de escritórios
- `04-entrega/`, `05-compliance/`, `06-clientes/`: implantação, LGPD e clientes
- `agente/`: código Python do agente (ver `agente/README.md`)
- `demo/`: demo clicável usada nas reuniões

## Código (`agente/`)

- Python 3.11+, FastAPI, SDK `anthropic`. Instale com
  `pip install -r agente/requirements-dev.txt` dentro de um venv.
- Rode os testes antes de cada commit: `cd agente && pytest`. Os testes não
  chamam a API.
- O formato da ficha está em `agente/app/ficha.py` (SCHEMA e modelos
  Pydantic). Mudou um, mude o outro.
- O histórico das conversas só cresce: nunca edite nem apague mensagens
  antigas antes de enviar à API.
- O prompt de sistema (`agente/prompts/sistema.md`) precisa ficar fixo.
  Nada de data, hora ou dado variável nele, para não quebrar o cache.

## Regras que não podem ser quebradas

- Nunca coloque senhas, chaves de API ou tokens no repositório.
- Nunca use dados reais de clientes dos escritórios em testes, exemplos ou
  documentos. Use casos fictícios.
- O agente nunca diz se a pessoa tem direito, nunca promete resultado e
  nunca pede senha do gov.br. Mudanças no prompt não podem enfraquecer
  essas regras.
- Não faça commit direto no `main`: trabalhe numa branch e abra um PR.
