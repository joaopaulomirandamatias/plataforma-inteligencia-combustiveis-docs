# ADR-006 — Batch-first; streaming só quando telemetria existir

**2026-08 · Aceito · Decisores: arquitetura**

## Contexto
Volumes reais da v1: fontes públicas mensais/semanais; o maior fluxo é o dump da Receita — grande *em lote*, não contínuo. O único fluxo genuinamente streaming (telemetria de frota) pertence à fase 2. Kafka na v1 seriam três brokers operados para dados que chegam uma vez por mês.

## Decisão
Orquestração batch (Dagster) + padrão Outbox no Postgres para eventos de domínio. O **contrato** de evento (CloudEvents + JSON Schema versionado, catálogo próprio) é fixado agora; o transporte é detalhe substituível declarado em documento de extensão.

## Consequências
(+) Operação mínima; zero infraestrutura ociosa. (+) Migração para Kafka/Redpanda na fase 2 não toca produtores nem consumidores — só o adaptador de transporte. (−) Latência de entrega de evento em segundos/minutos — adequada à v1, insuficiente para telemetria (gatilho explícito da migração). **(Proibido)** consumidor que dependa de ordem global ou de deduplicação pelo transporte.

## Alternativas rejeitadas
- **Kafka desde já:** custo operacional sem carga que o justifique; risco de a equipe desenhar para a ferramenta e não para o domínio.
- **RabbitMQ:** resolve fila, não resolve replay/retenção que o reprocessamento bitemporal aproveita; se streaming vier, log distribuído serve melhor.
- **Polling sem eventos:** acopla consumidores ao esquema interno dos produtores — exatamente o que o context map proíbe.
