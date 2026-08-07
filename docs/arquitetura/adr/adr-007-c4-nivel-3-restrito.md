# ADR-007 — C4 nível 3 apenas para Identidade, Agentes e Cofre

**2026-08 · Aceito · Decisores: arquitetura**

## Contexto
Diagrama de componente apodrece mais rápido do que ajuda; manter todos atualizados é custo sem retorno.

## Decisão
Nível 3 é obrigatório e mantido apenas onde o risco técnico e legal se concentra: Identidade, Agentes, Cofre. Demais contêineres param no nível 2.

## Consequências
(+) O que existe está atualizado — confiança na documentação. (−) Dev de outro contêiner desce ao código direto do nível 2 — aceitável com hexagonal documentado. **(Proibido)** diagrama binário sem fonte-texto versionada (Mermaid).

## Alternativas rejeitadas
- **Nível 3 universal:** vira arqueologia em seis meses.
- **Nenhum nível 3:** os três contêineres críticos são exatamente onde um erro de componente custa reputação ou processo.
