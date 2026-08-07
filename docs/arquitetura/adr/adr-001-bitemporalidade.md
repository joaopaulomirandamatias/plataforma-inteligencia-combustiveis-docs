# ADR-001 — Adotar bitemporalidade desde a fundação

**2026-08 · Aceito · Decisores: arquitetura + produto**

## Contexto
Postos mudam de dono, CNPJ e bandeira; normas mudam limite (E30/B15). Toda afirmação pública da plataforma precisa responder "sob qual dono e sob qual regra". Reconstruir histórico retroativamente com regras que já mudaram é inviável na prática — o custo de adiar é irreversível, não incremental.

## Decisão
Todo fato persiste com `tempo_validade` e `tempo_transacao`; escrita é sempre aditiva; toda consulta de produto é *as-of*; snapshots versionados materializam leituras quentes.

## Consequências
(+) Qualquer número publicado é reproduzível em qualquer data — é a defesa contra contestação e o controle anti-*repudiation*. (+) Detecção de sucessão de fachada vira consulta, não investigação. (−) Escrita e consulta mais complexas; exige disciplina de snapshot para custo de leitura. **(Proibido)** `UPDATE`/`DELETE` em tabela de fato; cache como fonte de verdade.

## Alternativas rejeitadas
- **Unitemporal (só validade):** não responde "o que sabíamos quando publicamos" — perde a defesa jurídica.
- **Event sourcing completo:** poder equivalente com custo operacional e curva de equipe muito maiores; bitemporal relacional entrega o mesmo requisito com SQL.

## Errata editorial (2026-08-07)
Os nomes `tempo_validade`/`tempo_transacao` usados neste ADR correspondem, no DDL e no restante da documentação, às colunas `validade` e `transacao` (ver `modelo-bitemporal.md`). Registro puramente editorial — a decisão permanece a aceita em 2026-08.
