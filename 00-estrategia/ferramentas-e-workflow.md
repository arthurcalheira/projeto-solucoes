# Ferramentas e forma de trabalhar em dupla

> Pesquisa de outubro de 2026. Os preços são em dólares, sem impostos, e
> mudam com frequência. Confira em [claude.com/pricing](https://claude.com/pricing)
> antes de assinar.

## 1. Claude: uma assinatura para cada um, no plano Team

**Não usem a mesma conta.** Os termos de uso da Anthropic para planos
individuais proíbem compartilhar login e deixar outra pessoa usar a conta. A
conta pode ser suspensa sem reembolso. Além disso, os dois dividiriam o
mesmo limite de uso e o mesmo histórico de conversas.

A forma certa de "usar a mesma assinatura" é o **plano Team**: uma
organização, uma fatura e um assento para cada pessoa. Segundo a página
oficial de preços, o Team **começa em 2 assentos**.

| Opção | Custo para 2 pessoas | Quando faz sentido |
|---|---|---|
| **Team, 2 assentos Standard** | US$ 40/mês no plano anual (US$ 50 no mensal) | **Recomendado para começar** |
| Team, 1 Standard + 1 Premium | US$ 120/mês no anual (US$ 150 no mensal) | Quando quem programa bater no limite de uso do Claude Code |
| 2 contas Pro separadas | US$ 40/mês no mensal (US$ 34 no anual) | Mais barato, mas sem projetos compartilhados nem fatura única |

Segundo a página de preços, o Team inclui:
- **Claude Code** em todos os assentos;
- **projetos compartilhados**: os arquivos e as instruções de um projeto
  ficam disponíveis para os dois, mas as conversas de cada um continuam
  privadas;
- fatura centralizada, administração de conectores e skills para a
  organização, e instruções comuns para todos;
- créditos de API compartilhados de até US$ 500 por mês. Confirme as
  condições antes de contar com isso.

O assento Premium dá cerca de 5 vezes mais uso que o Standard. Comecem com
dois Standard e só subam quem realmente bater no limite.

### Atenção: a API do produto é cobrada à parte

O agente que atende os clientes no WhatsApp usa a **API da Anthropic**, que
**não faz parte da assinatura**. A API é paga por uso no
[Console](https://platform.claude.com) da Anthropic.

- Criem **uma organização no Console** e convidem os dois.
- Usem **uma chave para desenvolvimento e outra para produção**, e coloquem
  um **limite de gasto mensal**.
- Com o Haiku 5.5, o custo estimado é de cerca de US$ 0,01 por triagem.

## 2. A stack

| Para quê | Ferramenta | Custo |
|---|---|---|
| Conversar, escrever propostas e pesquisar | Claude (app e web), plano Team | ver acima |
| Programar e mexer no repositório | Claude Code (terminal, app ou web) | incluso no Team |
| Código e documentos do projeto | **GitHub** (este repositório, privado) | grátis |
| Tarefas | **GitHub Projects** (quadro ligado às issues do repo) | grátis |
| Revisão automática de código | Claude Code GitHub Action (o Claude comenta nos PRs) | usa a API |
| Contratos, propostas e planilhas para cliente | Google Drive (Docs e Sheets) | grátis ou Workspace |
| Lista de prospecção | Google Sheets (importem o `07-prospeccao/prospects.csv`) | grátis |
| Senhas e chaves (WhatsApp, Meta, API) | Bitwarden (organização gratuita para 2 pessoas) ou 1Password | grátis ou pago |
| Conversa do dia a dia | Grupo de WhatsApp só de vocês dois | grátis |
| Servidor do agente | Um provedor simples com HTTPS (ex.: Railway, Render ou Fly.io) | ~US$ 5–20/mês no começo |

**Por que não Notion, Slack ou Jira agora:** com duas pessoas, cada
ferramenta a mais é um lugar a mais para procurar as coisas. O GitHub
guarda código, documentos e tarefas num lugar só, e o Claude Code trabalha
direto nele. Adicionem ferramentas quando sentirem falta, não antes.

## 3. O fluxo de trabalho

### Divisão de papéis

Sugestão: um cuida mais de **vendas e clientes** (prospecção, reuniões,
implantação) e o outro mais de **produto e tecnologia** (agente, servidor,
qualidade). Os dois usam o Claude para tudo, e as decisões importantes são
tomadas juntos.

### No repositório

1. **O `main` é protegido.** Ninguém faz commit direto nele.
2. **Cada tarefa tem uma issue** no GitHub Projects, com responsável e prazo.
3. **Cada tarefa vira uma branch e um pull request** (PR). O Claude Code
   cria a branch, faz a mudança, roda os testes e abre o PR.
4. **O outro sócio revisa o PR.** A GitHub Action do Claude também comenta.
   Só então o PR é mesclado.
5. **O `CLAUDE.md` na raiz** traz as regras do projeto: idioma, onde fica
   cada coisa, como rodar os testes, o que nunca fazer. Os dois Claudes
   leem o mesmo arquivo e trabalham do mesmo jeito. Quando o Claude errar
   algo repetidamente, corrijam a regra no `CLAUDE.md` via PR.

### No Claude (app e web)

- Criem um **projeto compartilhado "Antessala"** com os documentos
  principais: posicionamento, catálogo, preços, triagem e mensagens de
  abordagem. Assim os dois pedem propostas e respostas a clientes com o
  mesmo contexto.
- Conversa que gerou uma decisão importante vira documento no repositório
  ou no projeto. As conversas não são compartilhadas entre vocês.

### Ritmo

- **Segunda, 30 minutos:** revisar os números da semana (conversas,
  propostas, pilotos, receita) e escolher as 3 prioridades.
- **Sexta, 15 minutos:** o que foi feito, o que travou e o que muda no
  quadro.
- **No dia a dia,** o grupo de WhatsApp. O que for decisão vai para uma
  issue ou para um documento.

## 4. Segurança e dados

- Nada de senha ou chave no repositório, no WhatsApp ou em conversas com o
  Claude. Use o gerenciador de senhas.
- **Dados reais de clientes dos escritórios não entram no repositório nem
  nas conversas do Claude** usadas para desenvolver. Testem com casos
  fictícios.
- Ativem a verificação em duas etapas no GitHub, no Google, na Meta e no
  Console da Anthropic.

## 5. Primeiros passos (uma tarde)

- [ ] Assinar o Claude Team com 2 assentos Standard e convidar o sócio
- [ ] Criar a organização no Console da Anthropic, gerar a chave de
      desenvolvimento e definir o limite de gasto
- [ ] Dar acesso ao sócio no GitHub e proteger o `main`
- [ ] Criar o quadro no GitHub Projects com as tarefas de
      [`plano-90-dias.md`](plano-90-dias.md)
- [ ] Criar o projeto compartilhado no Claude com os documentos principais
- [ ] Criar o cofre de senhas compartilhado
- [ ] Importar o `prospects.csv` no Google Sheets e dividir os 12
      escritórios da prioridade A

## Fontes

- [Planos e preços do Claude (página oficial)](https://claude.com/pricing)
- [Termos de uso para consumidores da Anthropic](https://www.anthropic.com/legal/consumer-terms)
- [Resumo sobre compartilhamento de contas em assinaturas de IA](https://www.rupt.dev/blog/ai-subscription-account-sharing-policies/)
- [Projetos compartilhados no plano Team](https://kissmyskills.com/es/blogs/news/claude-team-plan-shared-projects)
