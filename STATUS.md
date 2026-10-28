# Status do projeto

> **Leia isto primeiro ao retomar o trabalho.** Atualizado em 28/10/2026, no
> fim da primeira sessão de trabalho com o Claude. Atualize a cada sessão
> (decisões novas, o que mudou, próximos passos).

## Onde estamos, em uma frase

O produto está definido, a prospecção feita e o agente **pronto no código
para um piloto**. Ainda **não foi testado com a API do Claude nem com o
WhatsApp de verdade**, e **nenhum escritório foi contatado**.

## Decisões tomadas

| Decisão | Escolha | Onde está |
|---|---|---|
| Nicho | Escritórios de **advocacia previdenciária**, de pequeno e médio porte | [`00-estrategia/posicionamento.md`](00-estrategia/posicionamento.md) |
| Produto de entrada | **PREV01: atendimento e triagem no WhatsApp**. Depois: PREV02 (CNIS), PREV03 (petição), PREV04 (andamento) | [`02-verticais/advocacia/previdenciario/`](02-verticais/advocacia/previdenciario/) |
| Preço para testar | Piloto R$ 1.500; implantação R$ 2.500–6.000; mensalidade R$ 800–2.000 | [`previdenciario/README.md`](02-verticais/advocacia/previdenciario/README.md) |
| Nome da empresa | Sugestão **Antessala** (2ª: Arrimo, 3ª: Triali). **Não verificado** no INPI nem no Registro.br. A marca "Vitrinista" (domínio do e-mail) ficou em aberto | [`00-estrategia/marca.md`](00-estrategia/marca.md) |
| Modelo do agente | **Claude Haiku 5.5, esforço `high`** (~US$ 0,01 por triagem, estimativa). Comparar com o Opus 5.5 nas conversas de teste | [`agente/README.md`](agente/README.md) |
| Linguagem do agente | Python + FastAPI + SDK `anthropic` | [`agente/`](agente/) |
| Assinatura do Claude para os sócios | **Plano Team, 2 assentos Standard**. Nunca compartilhar uma conta (proibido pelos termos) | [`00-estrategia/ferramentas-e-workflow.md`](00-estrategia/ferramentas-e-workflow.md) |
| Chave da API | Criada em `platform.claude.com/settings/keys`, **sempre com workspace**. Pessoal para testes; de **conta de serviço** em produção | seção "Chave da API" abaixo |

## O que existe

| Área | Situação | Arquivos |
|---|---|---|
| Estratégia, catálogo, plano de 90 dias | Pronto | `00-estrategia/`, `01-catalogo/` |
| Guia de triagem por benefício | Pronto, **falta revisão de um advogado previdenciário** | `02-verticais/advocacia/previdenciario/triagem-por-beneficio.md` |
| Dados de mercado (negativas do INSS +70% no 1º sem./2026) | Pronto, com fontes | `07-prospeccao/mercado.md` |
| Lista de 68 escritórios priorizados (12 na prioridade A) | Pronta. Contatos e números **conferidos só nos sites** | `07-prospeccao/lista-prioritaria.md`, `prospects.csv` |
| Mensagens de abordagem (12 escritórios A + DFQS de Salvador) | Prontas; **nenhuma enviada** | `07-prospeccao/mensagens-abordagem.md`, `abordagens/` |
| Concorrentes | Mapeados | `07-prospeccao/concorrentes.md` |
| Demo clicável (modo previdenciário e modo com várias áreas) | Publicada. **Privada: liberar no menu Share antes de mandar** | link abaixo; arquivo `demo/triagem-previdenciaria.html` |
| Agente (WhatsApp + Claude + painel + avisos por e-mail + documentos) | Pronto no código, 33 testes passando **sem chamar a API** | `agente/` |
| Conversas de teste (20 cenários) | Prontas, **nunca rodadas** | `agente/avaliacao/` |
| Deploy (Docker) | Escrito, **build não testado** | `agente/Dockerfile`, `agente/DEPLOY.md` |
| Checklist do piloto e rascunho de contrato | Prontos; o contrato **precisa de revisão jurídica** | `04-entrega/checklist-piloto-prev01.md`, `05-compliance/contrato-piloto-rascunho.md` |

## Links

- **Demo:** https://claude.ai/artifact/F6cMDPLxtpidu3ykCvDDLj
  (com `#varias-areas` no fim, abre o modo para escritórios com várias áreas)
- **Repositório:** https://github.com/arthurcalheira/projeto-solucoes, branch
  `claude/intelligent-knuth-anwbj7`. **Ainda não foi feito o merge para o
  `main`** (abrir um PR quando quiserem consolidar).

## Próximos passos

### Vendas (prioridade)
1. [ ] Verificar o nome (INPI, Registro.br, redes) e criar o WhatsApp Business da empresa
2. [ ] Liberar a demo no menu Share (ou gravar um vídeo de 2 min)
3. [ ] Enviar as 12 mensagens da prioridade A e anotar no `prospects.csv` quem respondeu e em quanto tempo
4. [ ] Reuniões de diagnóstico com quem responder (`03-comercial/roteiro-diagnostico.md`)
5. [ ] DFQS (Salvador): confirmar o contato no site e decidir entre a versão previdenciária e a de várias áreas da mensagem

### Agente (depende de vocês)
1. [ ] Criar a chave da API e colocar créditos no Console
2. [ ] Rodar `python simulador.py` e `python -m avaliacao.rodar` dentro de `agente/` (menos de US$ 1 com o Haiku); mandar o resultado para ajustar o prompt
3. [ ] Escolher a hospedagem e seguir o `agente/DEPLOY.md` (testar o build do Docker)
4. [ ] Escolher o serviço de transcrição de áudio
5. [ ] Quando houver um escritório: WhatsApp na API oficial, verificação na Meta e revisão do guia de triagem (`04-entrega/checklist-piloto-prev01.md`)

### Se um escritório fechar
Prometa o início do piloto para **2 a 3 semanas**. Siga o
`04-entrega/checklist-piloto-prev01.md` e peça os dados da Meta no mesmo
dia.

## Informações importantes para lembrar

### Regras do agente (inegociáveis)
Nunca diz se a pessoa tem direito, nunca promete resultado nem valor, nunca
pede senha do gov.br, passa para uma pessoa quando precisa. Quem analisa é
sempre o advogado. Mais detalhes no `CLAUDE.md`.

### Chave da API
- Console: `platform.claude.com/settings/keys` → **Create key**.
- **Sempre escolher um workspace**, senão o código do agente não funciona
  (faltaria o cabeçalho de workspace).
- A chave aparece uma vez só: guardar no cofre de senhas e no `agente/.env`
  (que nunca vai para o repositório).
- A API é paga à parte da assinatura do Claude (pré-paga, em Billing).

### WhatsApp e a Meta
- Usar a **API oficial**. APIs não oficiais podem bloquear o número.
- Regra da Meta desde 15/01/2026: proibidos assistentes de IA de uso geral;
  **bots de atendimento da própria empresa são permitidos** (o nosso caso).
  No Brasil, o CADE obrigou a liberar a IA de terceiros. Pode haver cobrança
  por mensagem: conferir antes de cada implantação.
- Mensagem livre só até 24 h depois da última mensagem do cliente. Depois
  disso, só com modelo aprovado pela Meta.

### O que o agente ainda não faz
- **Áudio:** pede para a pessoa escrever.
- **Lembrete automático de documentos.**
- **Cópia dos documentos para o Drive:** hoje eles abrem pelo painel.
- **Roteiro detalhado de trabalhista e consumidor:** existe só na demo. No
  agente real, essas áreas passam para uma pessoa.

### Rodar o agente no computador (resumo)
Instalar Python e VS Code, baixar o ZIP da branch, criar o `agente/.env`
com a chave e, no terminal do VS Code:
- **Mac:** `cd agente`, `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, `python simulador.py`
- **Windows:** `cd agente`, `py -m venv .venv`, `.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`, `python simulador.py`

## Histórico

| Data | O que aconteceu |
|---|---|
| 27–28/10/2026 | Primeira sessão: estrutura do projeto, escolha do nicho e do produto, demo, pesquisa de mercado, prospecção de 68 escritórios, mensagens de abordagem, sugestão de nome, agente completo no código (painel, avisos, documentos, deploy, conversas de teste), checklist do piloto e rascunho de contrato |
