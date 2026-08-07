# Mapa de leitura por persona

A porta de entrada decide se a documentação é usada ou ignorada. Trilhas na ordem de leitura:

| Persona | Trilha | Tempo-alvo |
|---|---|---|
| Dev novo no time | [glossário](onboarding/glossario.md) → [ADRs 001–008](arquitetura/adr/) → [C4 contexto](arquitetura/c4/contexto.md) → [C4 contêineres](arquitetura/c4/conteineres.md) | 1º dia |
| Eng. de dados | [modelo bitemporal](dados/modelo-bitemporal.md) → [catálogo de fontes](dados/catalogo-fontes.md) → [entity resolution](dados/entity-resolution.md) → catálogo de eventos ([plano diretor §3.1](arquitetura/plano-diretor.md)) | 1ª semana |
| Cientista de dados / ML | [modelo bitemporal](dados/modelo-bitemporal.md) (armadilha nº 3!) → plano diretor §3 (feature store, anti-vazamento) → [context map](dominio/context-map.md) (invariantes de Risco) | 1ª semana |
| Fiscal / órgão parceiro | plano diretor §5 (API) → §4 (papéis e escopo) → [PDF didático](apresentacao/plataforma-v1-didatico.pdf) | 1 tarde |
| DPO / jurídico | **[RIPD](conformidade/lgpd/ripd.md)** (pendências no §8) → [cofre](seguranca/cofre-de-identidade.md) → [trilha de auditoria](seguranca/trilha-de-auditoria.md) → [ADR-004](arquitetura/adr/adr-004-cofre-de-identidade.md) e [ADR-005](arquitetura/adr/adr-005-score-restrito-a-orgaos.md) | 1 tarde |
| Gestor / orientador | [README](../README.md) → [projeto v1](projeto-v1.md) → [PDF didático](apresentacao/plataforma-v1-didatico.pdf) → ADRs 001/005/006 | 1 hora |

## O que já existe, por onda

| Onda | Artefatos | Status |
|---|---|---|
| 1 | [ADRs 001–008](arquitetura/adr/) · [glossário](onboarding/glossario.md) · [catálogo de fontes](dados/catalogo-fontes.md) | ✅ |
| 2 | [C4 contexto](arquitetura/c4/contexto.md) · [C4 contêineres](arquitetura/c4/conteineres.md) · [context map](dominio/context-map.md) · [modelo bitemporal](dados/modelo-bitemporal.md) | ✅ |
| 3 | [entity resolution](dados/entity-resolution.md) · [cofre](seguranca/cofre-de-identidade.md) · [trilha de auditoria](seguranca/trilha-de-auditoria.md) · [RIPD](conformidade/lgpd/ripd.md) *(rascunho técnico)* | ✅ |
| 4 | OpenAPI · catálogo de eventos (arquivos próprios) · runbooks de fonte | — |
| 5 | ml/ · agentes/ · SLOs | — |

Estrutura completa planejada: [plano diretor, §6](arquitetura/plano-diretor.md).
