# ADR-002 — Zona bruta imutável

**2026-08 · Aceito · Decisores: arquitetura**

## Contexto
Fontes públicas mudam formato sem aviso; bugs de parser são descobertos meses depois.

## Decisão
Todo arquivo baixado é preservado como chegou, com data e hash; transformação lê a zona bruta, nunca a altera.

## Consequências
(+) Qualquer bug de normalização é corrigível retroativamente reprocessando; linhagem completa do número publicado ao byte de origem. (−) Armazenamento só cresce — aceito, é barato. **(Proibido)** transformação in-place; descarte de download "redundante".

## Alternativas rejeitadas
- **Guardar só o normalizado:** perde a correção retroativa — o erro do parser vira erro permanente.
- **Deduplicação agressiva por conteúdo:** economiza pouco e complica a trilha de auditoria.
