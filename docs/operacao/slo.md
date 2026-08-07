# SLOs — Objetivos de Nível de Serviço

*(especificação inicial — números da proposta do plano diretor §3.3; calibrar com medição real no piloto)*. Princípio: prometer o que a v1 sustenta. SLO inflado não protege usuário — só queima credibilidade na primeira medição.

## Disponibilidade

| Serviço | SLO | Janela de medição | Observação |
|---|---|---|---|
| Ficha pública | **99,9%** | 28 dias | SSG atrás de CDN — a promessa alta é barata aqui |
| Portal do órgão | **99,5%** | 28 dias, horário estendido (6h–24h) | Fora da janela: melhor esforço |
| API autenticada | **99,5%** | 28 dias | SLI: fração de respostas válidas (não-5xx, < 2s p95) |
| Webhooks | 99% de entregas ≤ 1h do evento | 28 dias | O retry de 24h cobre o resto |

## Dados — SLOs de completude, não de latência

Pipelines batch não têm SLO de latência de requisição; têm **prazo de processamento**:

| Pipeline | SLO |
|---|---|
| Dump mensal RFB | Arquivado em ≤ 24h da publicação *(inegociável — janela irrecuperável)*; processado em ≤ 72h |
| Fontes ANP | Processadas em ≤ 72h da publicação |
| Varredura DOU | Diária, com atraso máximo de 1 dia útil |
| Fila de revisão humana (identidade) | Idade máxima do par: 7 dias |
| Snapshot | Novo snapshot em ≤ 24h após carga relevante |

## Recuperação

| Métrica | Alvo |
|---|---|
| RPO (perda máxima de dados) | 1h (WAL contínuo) |
| RTO (retorno após desastre) | 4h |
| Zona bruta | Réplica geográfica; perda inaceitável por definição (é a fonte de reprocessamento eterno) |

## Error budget e consequência

Cada SLO define orçamento de erro (ex.: 99,5%/28d ≈ 3,4h). **Orçamento estourado → congela release do serviço afetado** até voltar ao verde; exceções exigem registro na trilha com justificativa. Sem consequência declarada, SLO é decoração.

## Integridade — SLOs que não aparecem em dashboards de uptime

| Verificação | Cadência | Falha = |
|---|---|---|
| Corrente de auditoria (incremental) | Diária | [Incidente maior](runbooks/corrente-de-auditoria-quebrada.md) |
| Corrente completa | Semanal | idem |
| Âncora externa | Diária | Alerta imediato |
| Invariante zero-bypass do Guardião | Contínua (auditada) | Incidente maior |
| Reprodutibilidade amostral (nº publicado × recomputado as-of) | Semanal, amostra | Investigação obrigatória |

A última linha é o SLO mais característico do sistema: sortear números publicados e recomputá-los as-of. É o teste de que a promessa central — todo número reproduzível — continua verdadeira em produção, não só no desenho.
