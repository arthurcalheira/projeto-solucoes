# Colocar o agente no ar

O agente é um servidor web que precisa de três coisas:
1. um endereço público com **HTTPS** (a Meta só envia webhooks para HTTPS);
2. um **disco persistente** para o banco e os documentos (`/app/agente/dados`);
3. as **variáveis de ambiente** do `.env.example`.

Qualquer provedor que rode um container Docker com volume persistente serve:
Railway, Render, Fly.io ou um servidor próprio. Os passos abaixo valem para
todos. Os nomes dos menus mudam de um provedor para outro.

## 1. Subir o container

- **Origem:** este repositório no GitHub, com o `Dockerfile` em
  `agente/Dockerfile` e o **contexto de build na raiz do repositório** (o
  build copia o guia de triagem de `02-verticais/`).
- **Porta:** o container escuta na variável `PORT` (padrão 8000).
- **Volume:** monte um disco persistente em `/app/agente/dados`. Sem isso,
  conversas e documentos somem a cada nova versão.
- **Região:** prefira São Paulo, quando o provedor tiver, pela LGPD e pela
  latência.

Para testar o build no seu computador:

```bash
docker build -f agente/Dockerfile -t agente-triagem .
docker run --env-file agente/.env -p 8000:8000 -v "$PWD/agente/dados:/app/agente/dados" agente-triagem
```

## 2. Variáveis de ambiente

Cadastre no provedor (nunca no repositório) as variáveis do
[`.env.example`](.env.example). Obrigatórias para produção:

| Variável | O que é |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API (de preferência de conta de serviço, num workspace de produção) |
| `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` | Dados do app na Meta |
| `PAINEL_TOKEN` | Senha do painel: texto longo e aleatório |
| `PAINEL_URL` | O endereço público, ex.: `https://agente.seudominio.com.br` |
| `ESCRITORIO_CONFIG` | Caminho do JSON do escritório (veja abaixo) |

Opcionais: avisos por e-mail (`SMTP_*`, `AVISO_EMAIL_*`) e por webhook
(`AVISO_WEBHOOK_URL`).

**Configuração do escritório:** copie `escritorio.example.json`, ajuste os
dados e coloque no volume (ex.: `/app/agente/dados/escritorio.json`), com
`ESCRITORIO_CONFIG=dados/escritorio.json`. Se não encontrar o arquivo, o
agente usa o exemplo.

## 3. Conferir

- `https://SEU-ENDERECO/saude` deve responder `{"ok": true}`.
- `https://SEU-ENDERECO/painel` deve pedir a senha.

## 4. Ligar o webhook na Meta

No app da Meta, em **WhatsApp → Configuração**:
- **URL de retorno:** `https://SEU-ENDERECO/webhook`
- **Token de verificação:** o mesmo `WHATSAPP_VERIFY_TOKEN`
- Assine o campo **messages**.

Mande um "oi" de outro celular para o número do escritório e acompanhe pelo
painel.

## 5. Antes de abrir para os clientes

- [ ] Backup diário do volume (banco + documentos), guardado de forma
      criptografada.
- [ ] Limite de gasto mensal no workspace de produção do Console da
      Anthropic.
- [ ] Primeira semana só à noite e nos fins de semana, com a equipe
      olhando o painel.
- [ ] Rodar as conversas de teste ([`avaliacao/`](avaliacao/)) depois de
      qualquer mudança no prompt.
