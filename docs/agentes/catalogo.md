# Catálogo de Agentes

*(especificação inicial)* — os sete agentes: gatilho, entradas, saídas, acessos **e acessos negados**. Regra que governa todos: [ADR-008](../arquitetura/adr/adr-008-guardiao-barreira-de-saida.md) — conteúdo externo é dado, nunca instrução; nenhum agente acessa o cofre; nenhuma saída publica sem o Guardião.

| Agente | Gatilho | Cadência |
|---|---|---|
| Sentinela | Eventos de domínio cruzando limiares declarados | Contínuo |
| Investigador | `CasoAberto` (via Sentinela) | Por caso |
| Refutador | Caso montado pelo Investigador | Por caso |
| Relator | Caso sobrevivente ao Refutador, validado | Sob demanda |
| Curador de dados | Agenda + anomalias de ingestão | Diário |
| Analista regulatório | Varredura do DOU e portais | Diário |
| Guardião | **Toda** saída de qualquer agente | Por saída |

## Fichas

### Sentinela
- **Entradas:** fluxo de eventos ([catálogo](../dados/eventos/README.md)); limiares versionados (mudança de limiar segue o rito de [governança](../ml/governanca-de-modelo.md)).
- **Saídas:** `CasoAberto` com o gatilho anexado. Não analisa — despacha.
- **Negado:** abrir caso sem evento gatilho identificável; qualquer chamada a LLM (Sentinela é regra, não modelo — determinismo aqui é feature).

### Investigador
- **Entradas:** caso + consultas as-of + [RAG normativo](../arquitetura/c4/conteineres.md) + grafo (pseudonimizado).
- **Saídas:** linha do tempo do caso, evidências com localizador, corroborações cruzadas.
- **Negado:** cofre; conclusão ("é fraude") — monta, não julga; evidência sem localizador verificável.

### Refutador
- **Entradas:** o caso montado — que ele trata como adversário.
- **Saídas:** `CasoRefutado` (com motivo — sucesso do sistema) ou caso sobrevivente com as refutações tentadas anexadas.
- **Roteiro mínimo de ataque:** dono mudou? norma mudou na janela? amostra pequena? erro de reconciliação plausível? explicação legítima (manutenção, aferição recente, lote)? cobertura suficiente?
- **Negado:** aprovar por omissão — cada item do roteiro exige resposta registrada.

### Relator
- **Entradas:** caso sobrevivente + refutações tentadas.
- **Saídas:** dossiê ([pipeline](pipeline-do-caso.md) define as seções obrigatórias).
- **Negado:** afirmar além do template da [política de linguagem](politica-de-linguagem.md); omitir hipótese alternativa testada.

### Curador de dados
- **Entradas:** telemetria de ingestão, cobertura, filas, deriva.
- **Saídas:** alertas internos; anotação de cobertura que acompanha scores e agregados.
- **Negado:** tocar dado — observa e reporta.

### Analista regulatório
- **Entradas:** DOU e portais das fontes (F08).
- **Saídas:** `AtoNormativoPublicado` com análise de impacto preliminar; atualização da fila de reindexação do RAG.
- **Negado:** interpretar juridicamente — detecta e encaminha; consolidar vigência sem revisão humana do encadeamento.

### Guardião
- **Entradas:** toda saída de agente destinada a persistência ou publicação.
- **Verificações:** léxico proibido; compatibilidade afirmação×evidência; **resolução de cada citação contra a base** (localizador existe e diz o que o texto afirma — anti-alucinação); presença das seções obrigatórias; escopo do destinatário.
- **Saídas:** aprovação, ou veto com motivo (vai à trilha).
- **Negado a todos os outros:** qualquer caminho de publicação que o contorne. A invariante "zero-bypass" é auditada, não prometida.

## Telemetria comum

Por agente: latência, custo por execução, taxa de veto do Guardião (por agente emissor — Relator com veto alto é sintoma de prompt ruim, não de Guardião rígido), taxa de refutação (baixa demais = Refutador fraco; investigar antes de comemorar).
