# Mapa de leitura por persona

A porta de entrada decide se a documentação é usada ou ignorada. Trilhas na ordem de leitura:

| Persona | Trilha | Tempo-alvo |
|---|---|---|
| Dev novo no time | [glossário](onboarding/glossario.md) → [ADRs 001–008](arquitetura/adr/) → [plano diretor §1](arquitetura/plano-diretor.md) (C4 + hexagonal) | 1º dia |
| Eng. de dados | [plano diretor §3](arquitetura/plano-diretor.md) → [catálogo de fontes](dados/catalogo-fontes.md) → catálogo de eventos (no plano, §3.1) | 1ª semana |
| Cientista de dados / ML | plano diretor §3 (feature store, anti-vazamento) → backtesting e precision@k (glossário + plano) | 1ª semana |
| Fiscal / órgão parceiro | plano diretor §5 (API) → §4 (papéis e escopo) → [PDF didático](apresentacao/plataforma-v1-didatico.pdf) | 1 tarde |
| DPO / jurídico | plano diretor §4 (LGPD, cofre, trilha de auditoria) → [ADR-004](arquitetura/adr/adr-004-cofre-de-identidade.md) e [ADR-005](arquitetura/adr/adr-005-score-restrito-a-orgaos.md) | 1 tarde |
| Gestor / orientador | [README](../README.md) → [PDF didático](apresentacao/plataforma-v1-didatico.pdf) → ADRs 001/005/006 | 1 hora |

Estrutura completa planejada do repositório de documentação: ver [plano diretor, §6](arquitetura/plano-diretor.md). Este repositório é a onda 1 dessa árvore (ADRs, glossário, catálogo de fontes) — as demais ondas entram conforme a implementação avança.
