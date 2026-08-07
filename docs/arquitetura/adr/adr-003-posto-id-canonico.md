# ADR-003 — `posto_id` canônico como chave universal

**2026-08 · Aceito · Decisores: arquitetura**

## Contexto
A mesma entidade física aparece sob cinco identificadores diferentes; sem chave única não há junção confiável entre contextos.

## Decisão
O contexto de Identidade produz `posto_id` estável e versionado; contextos só se integram por ele (e por `pessoa_id`).

## Consequências
(+) Toda junção do produto é confiável e auditável. (−) O pipeline de identidade vira dependência central — mitigado por versionamento de cluster, fila humana e reversão *as-of*. **(Proibido)** join por CNPJ, nome ou chave de fonte entre contextos.

## Alternativas rejeitadas
- **CNPJ como chave:** quebra em sucessão, baixa e reabertura — exatamente os casos que mais importam.
- **Chave da fonte:** acopla todos os contextos ao esquema de um terceiro.
