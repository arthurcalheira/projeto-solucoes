# ADV01 — Gerador de minutas de petição

## Ideia

O que é "fixo" numa petição (estrutura, fundamentos recorrentes, estilo
do escritório) fica em **modelos**. O que muda (fatos, partes, pedidos)
vem de uma **ficha do caso** e dos **documentos do cliente**. A IA junta
as duas coisas e entrega uma minuta em Word para o advogado revisar.

## Fluxo

```
 ┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
 │ Ficha do caso│   │ Documentos do    │   │ Biblioteca do    │
 │ (formulário) │   │ cliente (PDF,    │   │ escritório:      │
 │              │   │ fotos, laudos)   │   │ modelos, teses,  │
 └──────┬───────┘   └────────┬─────────┘   │ jurisprudência   │
        │                    │ extração    └────────┬─────────┘
        └──────────┬─────────┘                      │
                   ▼                                │
          ┌──────────────────┐◄─────────────────────┘
          │ IA redige minuta │  (prompt base + modelo da peça)
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ Minuta .docx     │  citações marcadas para conferência
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ Advogado revisa  │  checklist-revisao.md
          │ e protocola      │
          └──────────────────┘
```

## O que é fixo × o que muda

| Fixo (montado uma vez por escritório) | Variável (por caso) |
|---|---|
| Estrutura de cada tipo de peça | Qualificação das partes |
| Teses e fundamentos que o escritório usa | Fatos |
| Jurisprudência selecionada e conferida | Documentos e provas |
| Estilo de escrita, cabeçalho, assinatura | Pedidos específicos, valor da causa |

A **biblioteca do escritório** é o seu diferencial: quanto melhor ela
estiver organizada, melhor a minuta. Montá-la faz parte da implantação.

## Stack sugerida para começar (simples)

- **Entrada:** formulário (Google Forms, Typeform ou página própria) ou
  envio pelo WhatsApp.
- **Orquestração:** n8n ou Make.
- **IA:** API de um modelo de linguagem forte em português e em textos
  longos (ex.: Claude).
- **Saída:** preenchimento de modelo .docx + envio por e-mail/Drive.
- **Biblioteca:** pasta organizada no Drive do escritório, por tipo de peça.

Comece simples. Só construa sistema próprio (painel, login, banco de
dados) quando tiver clientes pedindo e pagando.

## Implantação (resumo)

1. Coletar 3–5 petições-modelo boas de cada tipo que o escritório mais usa.
2. Extrair estrutura, teses e estilo → montar a biblioteca.
3. Adaptar [`templates/prompt-peticao.md`](templates/prompt-peticao.md) e
   [`templates/ficha-do-caso.md`](templates/ficha-do-caso.md) ao escritório.
4. Testar com 3 casos antigos já protocolados (comparar com o original).
5. Treinar a equipe e entregar o checklist de revisão.

## Métricas para provar resultado

- Tempo médio por peça (antes × depois)
- % da minuta aproveitada sem reescrita
- Nº de peças geradas por mês
