# Agente de triagem previdenciária (esqueleto)

Atende clientes de escritórios previdenciários pelo WhatsApp, faz a triagem
por benefício, lê fotos e PDFs de documentos, monta a ficha do caso e passa
para uma pessoa da equipe quando precisa. Implementa o produto descrito em
[`02-verticais/advocacia/previdenciario/`](../02-verticais/advocacia/previdenciario/).

## Como funciona

```
WhatsApp (cliente)
   │ webhook da Meta (assinatura conferida)
   ▼
app/main.py ──► app/atendimento.py
                  │ junta mensagens seguidas (ex.: 3 fotos) numa resposta só
                  │ baixa fotos e PDFs; áudio → transcrição (ponto a ligar)
                  ▼
                app/agente.py ──► API do Claude
                  │   prompt do escritório (em cache) + histórico + data/hora
                  │   resposta estruturada: mensagens + ação + ficha do caso
                  ▼
                app/memoria.py (SQLite: histórico, ficha, status)
                  │
                  ├─► responde no WhatsApp
                  └─► ação "humano" ou "concluido" → app/avisos.py (avisa a equipe)
```

| Arquivo | O que faz |
|---|---|
| `prompts/sistema.md` | Instruções do agente. Os `{{...}}` vêm do `escritorio.json` e o guia de triagem é incluído automaticamente |
| `escritorio.example.json` | Dados de cada escritório: nome, prazo de retorno, honorários, horário e guia de triagem |
| `app/ficha.py` | Formato da ficha do caso e da resposta do agente |
| `app/agente.py` | Chamada ao Claude, com cache, saída estruturada e tratamento de recusa e erro |
| `app/atendimento.py` | Fluxo da conversa, agrupamento de mensagens, mídias e passagem para humano |
| `app/whatsapp.py` | Webhook, envio de mensagens e download de mídias da Cloud API |
| `app/memoria.py` | Banco SQLite |
| `app/main.py` | Servidor HTTP: `/webhook` e a API do painel (`/casos`) |
| `simulador.py` | Conversa pelo terminal, sem WhatsApp |

## Rodar no seu computador

```bash
cd agente
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env               # preencha pelo menos ANTHROPIC_API_KEY
cp escritorio.example.json escritorio.json   # ajuste para o escritório

pytest                             # testes (não chamam a API)
python simulador.py                # converse com o agente pelo terminal
```

No simulador, envie documentos com `/foto caminho.jpg` ou `/pdf caminho.pdf`,
veja a ficha com `/ficha` e saia com `/sair`. **Cada mensagem no simulador é
uma chamada paga à API.**

## Ligar no WhatsApp

1. Crie um app na Meta com o produto WhatsApp e um número da WhatsApp
   Business Platform (API oficial).
2. Preencha no `.env`: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`,
   `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` (um texto que você inventa)
   e `PAINEL_TOKEN`.
3. Suba o servidor num endereço com HTTPS:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
4. No painel da Meta, cadastre o webhook `https://SEU-ENDERECO/webhook` com
   o mesmo `WHATSAPP_VERIFY_TOKEN` e assine o campo `messages`.

## API do painel

Todas as chamadas exigem o cabeçalho `X-Painel-Token`.

- `GET /casos`: lista os casos com ficha, status (`bot`, `humano` ou
  `concluido`) e motivo.
- `POST /casos/{telefone}/devolver-ao-agente`: o agente volta a responder o
  contato.
- `DELETE /casos/{telefone}`: apaga tudo do contato (pedido de exclusão pela
  LGPD).

Para receber avisos (caso pronto, precisa de humano, nova mensagem durante o
atendimento humano), preencha `AVISO_WEBHOOK_URL`. Pode ser um webhook do
n8n, do Make ou do Slack.

## Decisões técnicas

- **Modelo:** `claude-haiku-5-5`, com esforço `high`. Ele custa cerca de 40
  vezes menos que o Opus 5.5 (estimativa: ~US$ 0,01 por triagem, contra ~US$
  0,25), e a triagem é uma tarefa relativamente simples. Os dois valores são
  configuráveis no `.env` (`CLAUDE_MODELO`, `CLAUDE_ESFORCO`). Antes do
  piloto, compare com o `claude-opus-5-5` num conjunto de conversas de teste,
  principalmente na leitura de fotos ruins de documentos.
- **Saída estruturada:** a API devolve sempre um JSON no formato de
  `app/ficha.py`, com as mensagens, a ação e a ficha completa. Se vier algo
  fora do formato, o caso vai para um humano.
- **Cache de prompt:** o prompt do escritório, com cerca de 2.700 tokens, é
  fixo e fica em cache para todas as conversas. O histórico de cada conversa
  também usa cache. Data e hora vão numa mensagem de sistema no fim, para não
  quebrar o cache.
- **O histórico só cresce.** Mensagens antigas nunca são editadas, porque
  isso invalidaria o cache e os blocos de raciocínio do modelo. Para
  conversas muito longas, o próximo passo é ativar a compactação de contexto
  da API.
- **Recusas:** se o modelo recusar uma mensagem, o caso vai para um humano.
  Com Opus ou Sonnet, antes disso o servidor da Anthropic tenta outro modelo
  automaticamente (`fallbacks="default"`, um recurso em beta). O Haiku 5.5
  não tem esse recurso, então o código só envia o parâmetro para os modelos
  que aceitam.
- **Segurança:** o webhook confere a assinatura da Meta, as mensagens
  repetidas são ignoradas, os logs mostram o telefone mascarado e nunca o
  conteúdo das conversas, e o prompt instrui o agente a tratar o que o
  cliente escreve como dado, não como ordem.

## O que falta para produção

- [ ] **Transcrição de áudio:** ligar um serviço de fala para texto em
      `transcrever_audio()` (`app/atendimento.py`). Hoje o agente pede que a
      pessoa escreva.
- [ ] **Atendimento humano no mesmo número:** integrar com uma plataforma de
      atendimento multiusuário compatível com a API oficial, para a equipe
      responder pelo mesmo WhatsApp.
- [ ] **Documentos no Drive do escritório:** copiar fotos e PDFs para a pasta
      do cliente.
- [ ] **Banco:** trocar o SQLite por Postgres quando houver mais de um
      escritório ou servidor. Em qualquer caso, use disco criptografado,
      backup e uma política de retenção (há dados de saúde).
- [ ] **Painel visual** para o advogado, em cima de `GET /casos`.
- [ ] **Lembrete de documentos pendentes** depois de 48 h, fora da janela de
      24 h só com mensagem de modelo (template) aprovada pela Meta.
- [ ] **Avaliação:** um conjunto de conversas de teste (os 5 assuntos,
      áudio, foto ruim, pedido de humano, tentativa de mudar as regras) para
      medir a qualidade antes de cada mudança no prompt.
