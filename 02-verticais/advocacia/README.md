# Vertical: Advocacia

## Para quem vender

Priorize escritórios **pequenos e médios** (1 a 20 advogados), com
volume em áreas de muita repetição:

- previdenciário (aposentadoria, BPC/LOAS, auxílio-doença)
- trabalhista
- consumidor / bancário (revisionais, negativação indevida)
- família (divórcio, alimentos)
- cível de massa

Quanto mais repetitivo o tipo de peça, maior o ganho e mais fácil a venda.

## Dores típicas → solução do catálogo

| Dor do escritório | Solução |
|---|---|
| "Perco horas montando petição parecida com a anterior" | ADV01 — Gerador de minutas |
| "O WhatsApp não para, metade é curioso" | ADV02 — Triagem de clientes |
| "Preciso ler um processo de 400 páginas" | ADV03 — Resumo de processos |
| "Tenho medo de perder prazo" | ADV04 — Prazos e publicações |
| "Cliente liga toda hora perguntando do processo" | ADV05 — Comunicação de andamento |

## ⚠️ Limites que você precisa respeitar

1. **Você vende a ferramenta para o advogado, não a petição para o
   cliente final.** Postular em juízo e dar consultoria jurídica são
   atividades privativas de advogado (Estatuto da Advocacia, Lei
   8.906/1994, art. 1º). Nunca ofereça "petição pronta" direto para
   pessoa física.
2. **Revisão humana obrigatória.** Todo documento gerado é *minuta*. O
   advogado revisa, ajusta e assina. Isso deve estar no contrato e na
   própria interface da solução.
3. **Jurisprudência inventada é o maior risco.** IA pode citar decisões
   que não existem — já houve advogados multados por isso. A solução
   deve: (a) usar só jurisprudência que o escritório fornecer ou que
   venha de fonte verificável, e (b) marcar toda citação para conferência.
4. **Sigilo e LGPD.** Dados de processos são sensíveis. Ver
   [`05-compliance/lgpd-e-seguranca.md`](../../05-compliance/lgpd-e-seguranca.md).
5. **Orientações da OAB.** O Conselho Federal da OAB publicou
   recomendações sobre uso de IA generativa na advocacia (transparência,
   supervisão humana, sigilo). Leia a versão vigente e use isso a seu
   favor na venda: "a solução já segue as recomendações da OAB".

## Arquivos desta pasta

- **[`previdenciario/`](previdenciario/): foco atual.** Produto PREV01,
  a triagem no WhatsApp para escritórios previdenciários.

- [`solucao-peticoes.md`](solucao-peticoes.md) — como funciona o ADV01
- [`templates/ficha-do-caso.md`](templates/ficha-do-caso.md) — formulário de entrada
- [`templates/prompt-peticao.md`](templates/prompt-peticao.md) — prompt base do gerador
- [`checklist-revisao.md`](checklist-revisao.md) — checklist que o advogado usa antes de protocolar
