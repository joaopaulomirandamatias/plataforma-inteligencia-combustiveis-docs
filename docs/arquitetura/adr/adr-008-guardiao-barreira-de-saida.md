# ADR-008 — Guardião como barreira de saída dos agentes

**2026-08 · Aceito · Decisores: arquitetura + jurídico**

## Contexto
Agentes LLM leem conteúdo externo (reclamações, PDFs, atos) — vetor de prompt injection — e podem formular além do que a evidência sustenta, que é o risco jurídico central do produto.

## Decisão
Nenhuma saída de agente persiste ou publica sem passar pelo Guardião (verificação de política de linguagem + limites de afirmação); conteúdo externo é sempre tratado como dado, nunca como instrução; agentes não têm acesso ao cofre.

## Consequências
(+) A política de linguagem é aplicada por software, não por convenção. (−) Latência e custo extras por saída — aceitos. **(Proibido)** canal de publicação que contorne o Guardião, inclusive "só desta vez".

## Alternativas rejeitadas
- **Confiar no prompt de cada agente:** falha silenciosa e não auditável.
- **Revisão humana universal:** não escala e vira o gargalo que os agentes existem para eliminar — humano revisa o dossiê final, não cada saída intermediária.
