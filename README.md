# Projeto Soluções — IA para negócios

Base de organização para vender soluções com IA: de agentes de automação
a produtos verticais (começando por escritórios de advocacia).

A ideia central: **não vender "IA", vender um resultado repetível**.
Cada solução vira um *pacote* com escopo, preço, processo de entrega e
materiais de venda prontos — assim o segundo cliente custa muito menos
esforço que o primeiro.

## Foco atual

**Advocacia previdenciária**, entrando pela **PREV01: atendimento e
triagem no WhatsApp**. Veja
[`02-verticais/advocacia/previdenciario/`](02-verticais/advocacia/previdenciario/)
e a demo [`demo/triagem-previdenciaria.html`](demo/triagem-previdenciaria.html).

## Como esta pasta está organizada

| Pasta | Para que serve |
|---|---|
| [`00-estrategia/`](00-estrategia/) | Posicionamento, precificação e plano dos primeiros 90 dias |
| [`01-catalogo/`](01-catalogo/) | O catálogo de soluções padronizadas (o que você vende) |
| [`02-verticais/`](02-verticais/) | Material específico por nicho — começa por [`advocacia/`](02-verticais/advocacia/) |
| [`03-comercial/`](03-comercial/) | Roteiro de diagnóstico, modelo de proposta, objeções |
| [`04-entrega/`](04-entrega/) | Processo de implantação e onboarding do cliente |
| [`05-compliance/`](05-compliance/) | LGPD, segurança e pontos do contrato |
| [`06-clientes/`](06-clientes/) | Uma pasta por cliente (copie `_modelo/`) |
| [`07-prospeccao/`](07-prospeccao/) | Dados de mercado, lista de escritórios para abordar e concorrentes |

## Ordem sugerida de leitura

1. [`00-estrategia/posicionamento.md`](00-estrategia/posicionamento.md)
2. [`01-catalogo/catalogo.md`](01-catalogo/catalogo.md)
3. [`02-verticais/advocacia/README.md`](02-verticais/advocacia/README.md)
4. [`00-estrategia/plano-90-dias.md`](00-estrategia/plano-90-dias.md)

## Regras da casa

- Toda solução nova entra primeiro no catálogo, com escopo fechado.
- Nada vai para cliente sem passar pelo checklist de entrega.
- Dados de cliente **nunca** entram neste repositório — só configuração,
  modelos e documentação (ver [`05-compliance/lgpd-e-seguranca.md`](05-compliance/lgpd-e-seguranca.md)).
