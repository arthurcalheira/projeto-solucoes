# PREV01 — Atendimento e triagem previdenciária no WhatsApp

**Produto principal.** É por ele que a gente entra nos escritórios.

> O WhatsApp do escritório atende 24 horas, entende o caso do cliente,
> pede os documentos certos e entrega ao advogado um caso organizado e
> pronto para análise.

## Para quem

Escritórios de advocacia com foco em **direito previdenciário** que:

- têm de 1 a 10 advogados;
- recebem **50 ou mais contatos por mês** no WhatsApp (por indicação,
  Instagram ou anúncios);
- hoje fazem a triagem "na mão", com advogado ou secretária respondendo
  um por um.

Sinal de cliente ideal: "metade das pessoas que chamam no WhatsApp não
tem direito ou some antes de mandar os documentos".

## O que a solução faz

1. **Atende na hora**, de dia, de noite e no fim de semana, por texto ou
   áudio.
2. **Identifica o assunto**: aposentadoria, doença/incapacidade, BPC/LOAS,
   pensão por morte ou negativa do INSS.
3. **Faz as perguntas certas** de cada benefício
   (ver [`triagem-por-beneficio.md`](triagem-por-beneficio.md)).
4. **Pede e lê os documentos** (RG, CNIS, laudos, carta do INSS) e avisa o
   que ainda falta.
5. **Marca prioridade** (ex.: negativa do INSS com prazo de recurso
   correndo).
6. **Entrega ao advogado** uma ficha do caso com resumo, sinais
   encontrados e documentos.
7. **Passa para um humano** quando precisa
   (ver [`fluxo-atendimento.md`](fluxo-atendimento.md)).

**O que a solução nunca faz:** dizer se a pessoa tem direito, prometer
resultado, informar valor de benefício ou pedir senha do gov.br.

## O que está incluído

- Configuração do fluxo com as regras e o tom de voz do escritório
- Integração com o número de WhatsApp do escritório (API oficial)
- Pasta de documentos por cliente no Drive do escritório
- Planilha ou CRM com a fila de casos
- Aviso ao advogado quando um caso fica pronto
- Treinamento da equipe (1 sessão) e 30 dias de acompanhamento

**Não está incluído:** análise jurídica, cálculo de benefício, anúncios
(tráfego pago) e atendimento de clientes que já têm processo em andamento.
Esse último é o PREV04, oferecido como expansão.

## Preço sugerido (para testar)

| Item | Valor |
|---|---|
| Piloto de 30 dias | R$ 1.500 (abatido da implantação se fechar) |
| Implantação | R$ 2.500 – R$ 6.000 |
| Mensalidade até 300 conversas/mês | R$ 800 – R$ 1.200 |
| Mensalidade até 1.000 conversas/mês | R$ 1.500 – R$ 2.000 |

### Como justificar o preço

Faça a conta sempre com os números do escritório:

```
Contatos por mês no WhatsApp ................... 200
Tempo de triagem humana por contato ............ 10 min
Horas gastas por mês só filtrando .............. ~33 h
```

O argumento mais forte é a **receita**. Na advocacia previdenciária os
honorários costumam vir do êxito, então **um único caso a mais fechado
por mês** (por atender rápido, à noite ou no fim de semana) costuma pagar
a mensalidade.

## Caminho de expansão no mesmo cliente

| Código | Solução | Quando oferecer |
|---|---|---|
| PREV02 | Leitura e análise de CNIS e documentos | Depois de 1–2 meses de PREV01 |
| PREV03 | Minuta de petição a partir da ficha (= [ADV01](../solucao-peticoes.md)) | Quando o volume de casos aceitos crescer |
| PREV04 | Aviso de andamento do processo ao cliente | Quando o escritório reclamar de "cliente perguntando do processo" |

A triagem já produz a ficha do caso e os documentos organizados, que são
exatamente o que o gerador de petições precisa. Por isso o PREV03 é uma
venda natural para quem já usa o PREV01.

## Arquivos

- [`fluxo-atendimento.md`](fluxo-atendimento.md): etapas da conversa e
  regras de passagem para humano
- [`triagem-por-beneficio.md`](triagem-por-beneficio.md): perguntas,
  sinais e documentos por benefício
- [`prompt-agente.md`](prompt-agente.md): instruções do agente de IA
- [`implementacao-tecnica.md`](implementacao-tecnica.md): ferramentas,
  arquitetura e custos
- [`../../../demo/triagem-previdenciaria.html`](../../../demo/triagem-previdenciaria.html):
  demo para mostrar em reunião
