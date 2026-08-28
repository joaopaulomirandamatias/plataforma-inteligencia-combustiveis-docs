# Plataforma de Inteligência de Combustíveis — Documentação

Documentação de arquitetura e engenharia da **Plataforma de Inteligência de Combustíveis**: um sistema que integra, reconcilia e versiona as fontes públicas e institucionais sobre o mercado brasileiro de combustíveis (ANP, Receita Federal, IPEM/Inmetro, Procon, corpus normativo), produzindo informação rastreável e inteligência acionável para órgãos fiscalizadores, distribuidoras, postos, frotas, consumidores e academia — com monitoramento contínuo por agentes de IA.

> **Status:** documentação viva da v1, com fundação de dados, API pública e site já implantados.
> Este repositório contém contratos e decisões; código e dados permanecem nos repositórios e ambientes próprios.

## O problema em uma frase

Os dados necessários para responder "este posto é confiável?" já existem — espalhados em seis órgãos, cada um identificando o mesmo posto de um jeito. A plataforma é a camada de verdade reconciliada que hoje não existe: cada posto com identidade única (`posto_id`), cada fato com fonte e data, cada número publicado reproduzível *as-of* qualquer data.

## Comece por aqui

| Você é... | Leia |
|---|---|
| Qualquer pessoa | [`docs/index.md`](docs/index.md) — mapa de leitura por persona |
| Quem quer o projeto completo | [`docs/projeto-v1.md`](docs/projeto-v1.md) — o documento de projeto v1 na íntegra (setores, fontes, IA, fases, riscos, decisões) |
| Arquiteto / dev | [`docs/arquitetura/plano-diretor.md`](docs/arquitetura/plano-diretor.md) — o plano diretor completo (C4, DDD, padrões, segurança, APIs) |
| Arquiteto de integração | [`docs/integracoes/interoperax.md`](docs/integracoes/interoperax.md) — fronteira de não interferência com o InteroperaX |
| Quem quer as decisões | [`docs/arquitetura/adr/`](docs/arquitetura/adr/) — os 8 ADRs fundadores |
| Eng. de dados | [`docs/dados/catalogo-fontes.md`](docs/dados/catalogo-fontes.md) — as 10 fontes, riscos e cuidados |
| Quem chegou agora | [`docs/onboarding/glossario.md`](docs/onboarding/glossario.md) — a linguagem ubíqua |
| Público não técnico | [`docs/apresentacao/plataforma-v1-didatico.pdf`](docs/apresentacao/plataforma-v1-didatico.pdf) — versão didática ilustrada |

## Princípios que regem tudo

1. **Bitemporalidade desde a fundação** — nada é sobrescrito; toda consulta é *as-of* (ADR-001).
2. **Identidade canônica** — contextos só se integram por `posto_id`/`pessoa_id` (ADR-003).
3. **Dado sensível segregado** — CPF completo só no cofre; a base analítica opera pseudonimizada (ADR-004).
4. **A plataforma nunca afirma fraude** — mostra fato, fonte e data; recomenda verificação; quem conclui é o órgão competente (ADR-005, ADR-008).
5. **Contrato antes de transporte** — batch-first com catálogo de eventos fixado; streaming quando houver telemetria (ADR-006).

## Licença e uso

Documentação de trabalho para discussão com parceiros institucionais. Nenhuma afirmação de desempenho deve ser citada antes da validação com dados históricos.
