# Catálogo de soluções

Cada item aqui é um **produto**: escopo fechado, preço de referência,
prazo de entrega. Use a [ficha padrão](#ficha-padrão-de-solução) para
cadastrar soluções novas.

## Soluções horizontais (qualquer empresa)

| Código | Solução | O que faz | Prazo típico |
|---|---|---|---|
| H01 | Atendimento WhatsApp com IA | Responde dúvidas frequentes, qualifica e agenda, passa para humano quando precisa | 2–3 semanas |
| H02 | Leitura e extração de documentos | Lê PDFs/fotos (contratos, notas, RG/CPF) e preenche planilha ou sistema | 1–2 semanas |
| H03 | Gerador de documentos a partir de modelo | Preenche modelos .docx com dados + texto redigido por IA | 1–2 semanas |
| H04 | Triagem de e-mails | Classifica, resume e rascunha respostas | 1 semana |
| H05 | Relatório automático | Junta dados de várias fontes e envia resumo semanal | 1–2 semanas |
| H06 | Agente interno de conhecimento | Responde perguntas da equipe com base nos documentos da empresa | 2–3 semanas |

## Soluções verticais — Advocacia

Montadas a partir dos blocos horizontais. Detalhes em
[`02-verticais/advocacia/`](../02-verticais/advocacia/).

| Código | Solução | Blocos usados | Prazo típico |
|---|---|---|---|
| ADV01 | Gerador de minutas de petição | H02 + H03 + H06 | 2–4 semanas |
| ADV02 | Triagem e atendimento inicial de clientes | H01 + H02 | 2–3 semanas |
| ADV03 | Resumo e análise de processos/documentos | H02 + H06 | 1–2 semanas |
| ADV04 | Acompanhamento de prazos e publicações | H05 | 2–3 semanas |
| ADV05 | Comunicação de andamento ao cliente | H01 + H05 | 1–2 semanas |

## Ficha padrão de solução

Copie este bloco ao criar uma nova solução:

```markdown
### <CÓDIGO> — <Nome>

**Problema que resolve:**
**Para quem:**
**Entrada (o que o cliente fornece):**
**Saída (o que a solução entrega):**
**Fora do escopo:**
**Ferramentas/stack:**
**Prazo de implantação:**
**Preço de referência:** setup R$ ___ + R$ ___/mês
**Métrica de sucesso:** (ex.: horas economizadas, tempo de resposta)
**Riscos e cuidados:**
```
