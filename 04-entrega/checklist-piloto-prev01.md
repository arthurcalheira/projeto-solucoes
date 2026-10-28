# Checklist do piloto: PREV01 (triagem no WhatsApp)

Use no dia em que o escritório disser "sim". Mande a parte 1 para o
escritório no mesmo dia: a verificação da Meta é o que mais demora.

## 1. O que pedir ao escritório

### Dados para o agente
- [ ] Nome do escritório como deve aparecer para o cliente
- [ ] Horário de atendimento (dias e horas)
- [ ] Prazo de retorno ao cliente (ex.: "1 dia útil")
- [ ] O que o agente pode dizer sobre honorários (ex.: "a primeira análise é
      gratuita")
- [ ] Assuntos que o escritório **não** atende (o agente passa para a equipe)
- [ ] **Revisão do guia de triagem**
      ([`triagem-por-beneficio.md`](../02-verticais/advocacia/previdenciario/triagem-por-beneficio.md))
      por um advogado do escritório, com as mudanças anotadas

### WhatsApp (Meta)
- [ ] Número que será usado e se ele hoje está no app do WhatsApp
      (confirmar com a Meta se dá para manter no app ou se precisa de número
      novo)
- [ ] Acesso de administrador ao Gerenciador de Negócios da Meta (Business
      Manager) do escritório, ou criar um
- [ ] Documentos para a verificação da empresa: CNPJ, comprovante de endereço
      e site ou domínio
- [ ] Nome e foto do perfil do WhatsApp

### Equipe
- [ ] Quem recebe os avisos de caso pronto (e-mails)
- [ ] Quem assume quando o agente passa para uma pessoa, e em que horário
- [ ] Quem terá a senha do painel

### Contrato
- [ ] Contrato do piloto assinado (rascunho em
      [`05-compliance/contrato-piloto-rascunho.md`](../05-compliance/contrato-piloto-rascunho.md))
- [ ] Texto de privacidade que o agente mostra na primeira mensagem, aprovado
      pelo escritório

## 2. O que fazemos nós

| Quando | Tarefa |
|---|---|
| Dia 1 | Criar o workspace de produção no Console da Anthropic, com limite de gasto |
| Dia 1 | Preencher o `escritorio.json` com os dados do escritório |
| Dias 1–3 | Ajustar o guia de triagem com as mudanças do advogado e rodar as conversas de teste |
| Dias 2–5 | Colocar o servidor no ar ([`agente/DEPLOY.md`](../agente/DEPLOY.md)) e configurar e-mail e backup |
| Quando a Meta liberar | Ligar o webhook e testar com 3 celulares da equipe |
| Antes de abrir | Treinar a equipe no painel (30 min): ver casos, abrir documentos, responder, devolver ao agente |

## 3. Primeiras duas semanas

- [ ] **Semana 1:** agente ligado só à noite e nos fins de semana. A equipe
      olha o painel toda manhã.
- [ ] **Semana 2:** ligado o dia todo, se a semana 1 foi bem.
- [ ] Toda sexta: ler 10 conversas, anotar erros e ajustar o prompt (rodar as
      conversas de teste depois de cada ajuste).

## 4. Números para medir desde o início

| Número | Onde ver |
|---|---|
| Contatos atendidos (total e fora do horário) | painel / banco |
| Casos que chegaram a "pronto para análise" | painel |
| Casos passados para a equipe, e por quê | painel (motivo) |
| Tempo da primeira resposta ao cliente | logs |
| Custo de IA por conversa | Console da Anthropic |
| Clientes fechados vindos do agente | o escritório informa |

Esses números viram o relatório do fim do piloto e o argumento para o
contrato mensal.
