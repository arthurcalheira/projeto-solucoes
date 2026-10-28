# Agente de triagem previdenciária

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
                app/memoria.py (SQLite: histórico, conversa, ficha, status)
                app/documentos.py (fotos e PDFs guardados no disco)
                  │
                  ├─► responde no WhatsApp
                  └─► ação "humano" ou "concluido" → app/avisos.py (e-mail e/ou webhook)

Advogado ──► /painel (app/painel.py): casos, ficha, documentos, conversa,
             resposta pelo WhatsApp do escritório e devolução ao agente
```

| Arquivo | O que faz |
|---|---|
| `prompts/sistema.md` | Instruções do agente. Os `{{...}}` vêm do `escritorio.json` e o guia de triagem é incluído automaticamente |
| `escritorio.example.json` | Dados de cada escritório: nome, prazo de retorno, honorários, horário e guia de triagem |
| `app/ficha.py` | Formato da ficha do caso e da resposta do agente |
| `app/agente.py` | Chamada ao Claude, com cache, saída estruturada e tratamento de recusa e erro |
| `app/atendimento.py` | Fluxo da conversa, agrupamento de mensagens, mídias e passagem para humano |
| `app/whatsapp.py` | Webhook, envio de mensagens e download de mídias da Cloud API |
| `app/memoria.py` | Banco SQLite: histórico da API, conversa legível, documentos, ficha e status |
| `app/documentos.py` | Guarda no disco as fotos e PDFs recebidos |
| `app/avisos.py` | Avisa a equipe por e-mail (SMTP) e/ou webhook |
| `app/painel.py` | Painel web do advogado |
| `app/main.py` | Servidor HTTP: `/webhook`, `/painel` e a API `/casos` |
| `simulador.py` | Conversa pelo terminal, sem WhatsApp |
| `avaliacao/` | 20 conversas de teste e o script que confere as regras |
| `Dockerfile`, `DEPLOY.md` | Como colocar no ar |

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
3. Suba o servidor num endereço com HTTPS (passo a passo em
   [`DEPLOY.md`](DEPLOY.md)).
4. No painel da Meta, cadastre o webhook `https://SEU-ENDERECO/webhook` com
   o mesmo `WHATSAPP_VERIFY_TOKEN` e assine o campo `messages`.

## Painel do advogado

Abra `https://SEU-ENDERECO/painel` e entre com a senha `PAINEL_TOKEN`. O
painel mostra:
- a **lista de casos**, primeiro os que estão com a equipe, depois os prontos
  para análise;
- em cada caso: ficha, resumo, sinais, respostas, **arquivos recebidos**
  (abrem no navegador), documentos pendentes e a **conversa completa**;
- uma caixa para **responder pelo WhatsApp do escritório**. Ao responder, o
  agente para de atender aquele contato. O botão **Devolver ao agente** faz
  ele voltar, já sabendo o que a equipe conversou.

O WhatsApp só permite mensagens livres até 24 h depois da última mensagem do
cliente. Depois disso, é preciso uma mensagem de modelo aprovada pela Meta
(o painel avisa).

## Avisos para a equipe

- **E-mail:** preencha `SMTP_*`, `AVISO_EMAIL_DE` e `AVISO_EMAIL_PARA`. O
  e-mail chega quando um caso fica pronto ou precisa de humano, com o nome, o
  assunto, a prioridade e o link do caso. Por segurança, não leva o resumo
  nem dados de saúde.
- **Webhook:** preencha `AVISO_WEBHOOK_URL` para receber a ficha completa
  (n8n, Make, Slack).

## Conversas de teste

```bash
python -m avaliacao.rodar                       # usa o modelo do .env
python -m avaliacao.rodar --modelo claude-opus-5-5 --esforco medium
```

São 20 cenários: os 5 assuntos, óbito recente, pedido de humano, cliente
irritado, cliente que já tem processo, assunto trabalhista, "eu tenho
direito?", "quanto vou receber?", oferta de senha, tentativa de mudar as
regras, honorários e áudio. O script confere se alguma resposta quebra as
regras e se a ação, o assunto e a prioridade batem. **Faz chamadas pagas**
(com o Haiku, menos de US$ 1 por rodada) e pede confirmação antes. Leia
algumas conversas salvas em `dados/` para julgar o tom, que o script não mede.

## API para integrações

Todas as chamadas exigem o cabeçalho `X-Painel-Token`.

- `GET /casos`: lista os casos com ficha, status (`bot`, `humano` ou
  `concluido`) e motivo.
- `POST /casos/{telefone}/devolver-ao-agente`: o agente volta a responder o
  contato.
- `DELETE /casos/{telefone}`: apaga tudo do contato, inclusive os arquivos
  (pedido de exclusão pela LGPD).

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

Pronto no código: painel, documentos, resposta da equipe pelo mesmo número,
avisos por e-mail, Docker e conversas de teste. Falta:

- [ ] **Rodar as conversas de teste com a chave da API** e ajustar o prompt
      (depende da chave).
- [ ] **Colocar no ar** seguindo o [`DEPLOY.md`](DEPLOY.md) (depende de
      escolher o provedor). O build do Docker ainda não foi testado.
- [ ] **WhatsApp do escritório** na API oficial e verificação da empresa na
      Meta (depende do escritório).
- [ ] **Transcrição de áudio:** ligar um serviço de fala para texto em
      `transcrever_audio()` (`app/atendimento.py`). Depende de escolher o
      serviço. Hoje o agente pede que a pessoa escreva.
- [ ] **Lembrete de documentos pendentes** depois de 48 h. Exige uma
      mensagem de modelo aprovada pela Meta.
- [ ] **Cópia dos documentos para o Drive do escritório** (opcional; hoje
      ficam no servidor e abrem pelo painel).
- [ ] **Banco:** trocar o SQLite por Postgres quando houver vários
      escritórios. Em qualquer caso, disco criptografado, backup e política
      de retenção (há dados de saúde).
