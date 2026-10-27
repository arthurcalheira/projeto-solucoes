# Implementação técnica

> O código do agente está em [`agente/`](../../../agente/): servidor em
> Python, ligado direto à API do WhatsApp e à API do Claude. O caminho com
> n8n ou Make descrito abaixo continua valendo como alternativa sem código.

Comece com ferramentas prontas e ligadas entre si. Só construa um sistema
próprio quando tiver vários clientes pedindo a mesma coisa.

## Arquitetura

```
 Cliente no WhatsApp
        │  texto, áudio, fotos, PDF
        ▼
 WhatsApp Business Platform (API oficial)
        │
        ▼
 Orquestrador (n8n ou Make) ─────────────────────────────┐
   │   1. áudio? → transcrição                           │
   │   2. envia histórico + prompt ao modelo de IA       │
   │   3. imagem/PDF? → IA identifica o documento        │
   │   4. lê o JSON de saída (acao + ficha)              │
   │                                                     │
   ├──► responde ao cliente no WhatsApp                  │
   ├──► salva documentos no Drive DO ESCRITÓRIO          │
   │      /Clientes/<nome>-<telefone>/                   │
   ├──► atualiza a fila de casos (planilha ou CRM)       │
   └──► acao = humano/concluido → avisa o advogado ──────┘
             (e-mail, WhatsApp interno ou Slack)
```

## Escolhas e por quê

| Peça | Recomendação | Observação |
|---|---|---|
| WhatsApp | **API oficial** (Meta Cloud API ou um parceiro oficial da Meta) | APIs não oficiais são mais baratas, mas o número pode ser **bloqueado**. Para escritório de advocacia, não vale o risco. |
| Atendimento humano no mesmo número | Plataforma de atendimento multiusuário compatível com a API oficial | Permite que o advogado assuma a conversa e o agente pare de responder. |
| Orquestração | n8n (pode ser auto-hospedado, o que ajuda na LGPD) ou Make | Um fluxo por cliente, criado a partir de um modelo seu. |
| IA | Modelo forte em português, que leia imagens e PDFs (ex.: Claude via API) | Use contrato/API empresarial em que os dados **não** treinam modelos. |
| Áudio | Serviço de transcrição de fala (speech-to-text) | Essencial: muita gente desse público manda áudio. |
| Fila de casos | Google Sheets no começo; CRM quando o escritório já tiver um | Uma linha por caso, preenchida com a ficha. |
| Documentos | Google Drive ou OneDrive **do escritório** | Você não guarda documentos de clientes no seu ambiente. |

## Regras da Meta para IA no WhatsApp (acompanhar)

Desde 15/01/2026, a Meta proíbe na API do WhatsApp os **assistentes de
IA de uso geral** (como o ChatGPT dentro do WhatsApp). A própria Meta diz
que **bots de atendimento ao cliente da empresa continuam permitidos**, e
esse é o nosso caso: o agente atende os clientes do escritório.

No Brasil, o CADE obrigou a Meta a manter a IA de terceiros liberada. Em
março de 2026 a Meta disse que passaria a cobrar por "mensagens não
padronizadas" nesses casos. Confira a regra e a tabela vigentes antes de
cada implantação.

Fontes:
- [Canaltech (mar/2026)](https://canaltech.com.br/mercado/whatsapp-libera-ia-de-terceiros-novamente-no-brasil-apos-nova-decisao-do-cade/)
- [Exame (jan/2026)](https://exame.com/tecnologia/whatsapp-volta-atras-e-deixa-que-empresas-brasileiras-usem-ias-para-atender-clientes/)

## Custos a medir no piloto

- **WhatsApp:** a Meta não cobra as respostas enviadas dentro de 24 h
  depois da mensagem do cliente; mensagens de modelo (templates) são
  cobradas. Confira a tabela vigente.
- **IA:** cobrada por uso. Uma triagem costuma custar centavos ou poucos
  reais. Meça o custo real no piloto e precifique com margem de 3 a 5
  vezes.
- **Transcrição de áudio:** por minuto de áudio.
- **Orquestrador e plataforma de atendimento:** mensalidade fixa.

Registre o custo de cada cliente em `06-clientes/<cliente>/README.md`.

## Do modelo padrão ao cliente novo

1. Duplique o fluxo-modelo no orquestrador.
2. Preencha os campos `{{...}}` do [`prompt-agente.md`](prompt-agente.md).
3. Revise a [`triagem-por-beneficio.md`](triagem-por-beneficio.md) com o
   advogado do escritório.
4. Conecte o número do escritório, o Drive e a planilha.
5. Teste com 10 conversas simuladas: os 5 assuntos, áudio, foto ruim,
   pedido de humano e cliente irritado.
6. Ligue em horário reduzido (ex.: só à noite) na primeira semana.

## Segurança (resumo)

- Credenciais no gerenciador de senhas, nunca no fluxo em texto aberto.
- Não deixe documentos ou conversas completas nos logs do orquestrador.
- Acesso ao Drive do escritório só com a permissão necessária.
- Detalhes em [`05-compliance/lgpd-e-seguranca.md`](../../../05-compliance/lgpd-e-seguranca.md).
  Laudos médicos são **dados sensíveis** pela LGPD.
