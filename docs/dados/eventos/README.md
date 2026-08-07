# Catálogo de Eventos de Domínio

Contrato dos eventos — fixado antes do transporte ([ADR-006](../../arquitetura/adr/adr-006-batch-first.md)): o transporte troca na fase 2; estes contratos, não. Envelope [CloudEvents 1.0](https://cloudevents.io/); payload validado por JSON Schema versionado.

## Convenções

- `type`: `br.combustiveis.<contexto>.<evento>.v1` (prefixo provisório até o domínio institucional existir; a troca será mudança de major).
- Nome no passado — evento é fato consumado.
- **Payload nunca carrega dado do cofre** (nem pseudonimizado quando o evento é assinável por webhook externo).
- Identificadores sempre canônicos (`posto_id`/`pessoa_id`), jamais chave de fonte.
- Deduplicação é obrigação do consumidor, pela chave de idempotência — o transporte não deduplica.
- Mudança aditiva não gera versão; remoção/renomeação/semântica gera `.v2` com convivência declarada.

## Eventos

| Evento | Contexto | Chave de idempotência | Ordem | Arquivo |
|---|---|---|---|---|
| FonteColetada | ingestao | `(fonte, url, hash_conteudo)` | por fonte | [fonte-coletada.md](fonte-coletada.md) |
| ColetaPMQCRegistrada | qualidade | `(posto_id, amostra_id)` | por posto | [coleta-pmqc-registrada.md](coleta-pmqc-registrada.md) |
| PrecoSemanalRegistrado | precos | `(posto_id, semana, produto)` | por posto | [preco-semanal-registrado.md](preco-semanal-registrado.md) |
| IdentidadeReconciliada | identidade | `(cluster_id, versao)` | global (por versão) | [identidade-reconciliada.md](identidade-reconciliada.md) |
| LigacaoIdentidadeRevisada | identidade | `(par_id, decisao_id)` | por par | [ligacao-identidade-revisada.md](ligacao-identidade-revisada.md) |
| MudancaSocietariaDetectada | societario | `(cnpj, competencia_dump)` | por CNPJ | [mudanca-societaria-detectada.md](mudanca-societaria-detectada.md) |
| LimiarDeRiscoCruzado | risco | `(posto_id, modelo, versao, janela)` | por posto | [limiar-de-risco-cruzado.md](limiar-de-risco-cruzado.md) |
| CasoAberto / CasoRefutado / CasoPublicado | investigacao | `(caso_id, transicao)` | por caso | [caso-transicoes.md](caso-transicoes.md) |
| AtoNormativoPublicado | normativo | `(orgao, ato_id, versao)` | por órgão | [ato-normativo-publicado.md](ato-normativo-publicado.md) |
| SnapshotPublicado | entrega | `(versao_snapshot)` | global | [snapshot-publicado.md](snapshot-publicado.md) |
