# Mapa de leitura por persona

A porta de entrada decide se a documentação é usada ou ignorada. Trilhas na ordem de leitura:

| Persona | Trilha | Tempo-alvo |
|---|---|---|
| Dev novo no time | [glossário](onboarding/glossario.md) → [ADRs 001–008](arquitetura/adr/) → [C4 contexto](arquitetura/c4/contexto.md) → [C4 contêineres](arquitetura/c4/conteineres.md) | 1º dia |
| Eng. de dados | [modelo bitemporal](dados/modelo-bitemporal.md) → [catálogo de fontes](dados/catalogo-fontes.md) → [entity resolution](dados/entity-resolution.md) → catálogo de eventos ([plano diretor §3.1](arquitetura/plano-diretor.md)) | 1ª semana |
| Cientista de dados / ML | [backtesting](ml/backtesting.md) → [governança de modelo](ml/governanca-de-modelo.md) → [model cards](ml/modelos/README.md) → [modelo bitemporal](dados/modelo-bitemporal.md) (armadilha nº 3!) | 1ª semana |
| Fiscal / órgão parceiro | [guia de consumo da API](api/guia-de-consumo.md) → [webhooks](api/webhooks.md) → plano diretor §4 (papéis e escopo) → [PDF didático](apresentacao/plataforma-v1-didatico.pdf) | 1 tarde |
| Integrador / consumidor da API | [guia de consumo](api/guia-de-consumo.md) → [openapi.yaml](api/openapi.yaml) → [webhooks](api/webhooks.md) → [catálogo de eventos](dados/eventos/README.md) | 1 tarde |
| DPO / jurídico | **[RIPD](conformidade/lgpd/ripd.md)** (pendências no §8) → [cofre](seguranca/cofre-de-identidade.md) → [trilha de auditoria](seguranca/trilha-de-auditoria.md) → [ADR-004](arquitetura/adr/adr-004-cofre-de-identidade.md) e [ADR-005](arquitetura/adr/adr-005-score-restrito-a-orgaos.md) | 1 tarde |
| Gestor / orientador | [README](../README.md) → [projeto v1](projeto-v1.md) → [PDF didático](apresentacao/plataforma-v1-didatico.pdf) → ADRs 001/005/006 | 1 hora |

## O que já existe, por onda

| Onda | Artefatos | Status |
|---|---|---|
| 1 | [ADRs 001–008](arquitetura/adr/) · [glossário](onboarding/glossario.md) · [catálogo de fontes](dados/catalogo-fontes.md) | ✅ |
| 2 | [C4 contexto](arquitetura/c4/contexto.md) · [C4 contêineres](arquitetura/c4/conteineres.md) · [context map](dominio/context-map.md) · [modelo bitemporal](dados/modelo-bitemporal.md) | ✅ |
| 3 | [entity resolution](dados/entity-resolution.md) · [cofre](seguranca/cofre-de-identidade.md) · [trilha de auditoria](seguranca/trilha-de-auditoria.md) · [RIPD](conformidade/lgpd/ripd.md) *(rascunho técnico)* | ✅ |
| 4 | [openapi.yaml](api/openapi.yaml) · [guia de consumo](api/guia-de-consumo.md) · [webhooks](api/webhooks.md) · [catálogo de eventos](dados/eventos/README.md) (11 arquivos) · [runbooks](../docs/operacao/runbooks/) (formato · dump RFB · corrente quebrada · [pós-deploy](operacao/runbooks/verificar-apos-deploy.md) · [desligar/religar](operacao/runbooks/desligar-e-religar-a-plataforma.md)) | ✅ |
| 5 | [backtesting](ml/backtesting.md) · [governança de modelo](ml/governanca-de-modelo.md) · [model cards](ml/modelos/README.md) · [catálogo de agentes](agentes/catalogo.md) · [pipeline do caso](agentes/pipeline-do-caso.md) · [política de linguagem](agentes/politica-de-linguagem.md) · [SLOs](operacao/slo.md) | ✅ *(especificação inicial)* |

**As cinco ondas estão completas.** Os docs da onda 5 nasceram como *especificação inicial* — contratos que a implementação deve honrar — e serão promovidos a documentação de sistema real conforme o código existir. O que resta da [árvore completa](arquitetura/plano-diretor.md) (hexagonal por contexto, `dominio/contextos/`, modelo de ameaças detalhado, observabilidade, IaC, onboarding executável) entra junto com a implementação, porque documentar antes seria inventar.
