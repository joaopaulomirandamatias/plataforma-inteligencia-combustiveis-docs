# Runbook — Desligar e religar a plataforma inteira

**Gatilho:** decisão do dono de parar o custo de compute por um período declarado. **Não é incidente** — é operação planejada, e é exatamente por isso que ela é perigosa: ninguém está de plantão, ninguém está desconfiado, e o modo de falha é silencioso. O erro típico não é derrubar demais; é **religar o binário errado e acreditar no `SUCCESS`**.

**Episódio catalogado:** desligado em 2026-08-20, religado em 2026-08-28 — 12 serviços no projeto Railway `Plataforma Combustível`, environment `production`. Tudo abaixo é o que aquele episódio ensinou; os números entre parênteses são as medições daquela execução, não promessas.

## Quando desligar — e quando não

Desligar é legítimo quando há pausa longa e declarada do projeto, compute sem contrapartida de uso e nenhum compromisso de disponibilidade vigente. Só que a plataforma tem uma assimetria que a maioria dos sistemas não tem: **parar de servir é reversível; parar de capturar nem sempre é.**

- **Não desligue atravessando a janela do dump mensal da Receita (F05).** A fonte é retrato do presente: mês não capturado é história societária perdida em caráter irreversível, e o [SLO do dump](../slo.md) é inegociável por escrito (arquivado em ≤ 24h da publicação). Se a parada cruza a janela, existem três saídas honestas — ingerir antes de desligar, marcar o religar para dentro da janela, ou registrar por escrito que o mês foi abandonado. Não existe a quarta, que é desligar e torcer. O tratamento da janela perdida é o [runbook do dump](dump-mensal-ausente-ou-anomalo.md).
- **Não desligue por conta própria com órgão parceiro ou piloto em uso.** Tirar do ar o que já foi mostrado a um parceiro é decisão de quem responde pelo compromisso, não de quem opera.
- **Se o objetivo é só reduzir custo, meça antes de derrubar tudo.** Migradores já são one-shot e não custam parados; o worker roda por cron e vive minutos por dia. O que custa continuamente são API, web e os bancos. Desligar a plataforma inteira para economizar o que o worker gasta é pagar caro em risco por pouco em fatura.

## O que se apaga, o que nunca se apaga

O verbo do desligamento é `railway down --service <nome> --yes`, um serviço de cada vez. Ele **remove o deployment, não o serviço**: variáveis, domínios, cron, watch paths, ligação com o repositório e volume continuam existindo. É por isso que ele é o verbo certo — o religar vira *redeploy*, não *reprovisionamento*.

**Os três volumes nunca são destruídos**, e ficam `Ready` guardando tudo:

| Volume | Tamanho medido | O que guarda |
|---|---|---|
| `postgres-volume` | ~1,7 GB | todos os fatos, a trilha de auditoria e o histórico bitemporal |
| `pic-worker-volume` (montado em `/data`) | ~965 MB | a **zona bruta** — inclusive o dump mensal da Receita |
| `pic-gestao-projection-db-data` | ~1,1 GB | a projeção da PIC Gestão |

O porquê precisa estar escrito, e não na cabeça de quem desligou: a zona bruta é a fonte de reprocessamento eterno ([ADR-002](../../arquitetura/adr/adr-002-zona-bruta-imutavel.md)), declarada no [SLO](../slo.md) como perda inaceitável por definição, e nela mora o dump da Receita — cuja perda é irreversível em um sentido em que a perda de um banco não é. **O custo residual de armazenamento é o preço de não perder história.** Quem abrir a fatura do mês seguinte vai perguntar "e esses volumes parados?"; a resposta é esta linha, e ela tem de estar num documento versionado para sobreviver à pergunta.

Pela mesma razão não se apagam serviços, variáveis nem domínios, e **nunca se faz `wipe` de volume** — wipe leva os backups junto (ver `docs/operacao-backup-restore-railway.md` no repositório do backend).

## Desligar — a ordem e o que ela protege

0. **Registre o inventário antes de derrubar qualquer coisa.** `list-services` e `list-deployments`, salvos com nome de serviço, id do deployment ativo e commit. Em 2026-08-20 eram 12 serviços; a lista muda com o projeto, e a lista **do dia** é a única referência contra a qual o religar pode ser conferido. Sem ela, "voltou tudo?" é uma pergunta sem resposta.
1. **Aplicações primeiro** — `pic-web`, `pic-api`, `pic-worker` e a pilha `pic-gestao-*`. Derrubar o banco antes deixa a API viva batendo em banco morto: 5xx, retentativas, healthcheck em laço e páginas de log que ninguém vai ler depois. Pior, o worker no meio de uma carga perde o meio de uma carga, em vez de simplesmente não começar.
2. **Se o worker estiver ingerindo, espere terminar.** A agenda é orientada a vencimento e retomável — o que não rodou continua vencido —, mas terminar o arquivo em curso é mais barato que reprocessá-lo.
3. **Bancos por último** — `Postgres` e `pic-gestao-projection-db`.
4. **Confirme pelo resultado, não pelo comando:** zero serviços rodando e os endereços públicos respondendo **404**. O 404 é o resultado esperado, não sintoma: significa que não há roteamento para coisa alguma. Um 502 no lugar dele diria que ainda existe algo de pé para o roteador tentar alcançar.

## Religar — ordem inversa, e as duas armadilhas

A ordem é `Postgres` → `pic-gestao-projection-db` → aplicações (`pic-api`, `pic-web`, `pic-worker`). O banco vem primeiro porque o healthcheck da API é `/saude`, que **consulta o banco**: subir a API antes derruba o próprio rollout com 503 `banco_indisponivel` e queima as três tentativas da política de restart antes de o banco existir. O rollout falha por ordem, e o diagnóstico aponta para o lugar errado.

### Armadilha 1 — o CLI recusa, a MCP religa

`railway redeploy` **recusa** um deployment removido: *"cannot be redeployed... or was removed"*. A conclusão fácil, e errada, é que só o painel resolve. O `redeploy` **da MCP da Railway religa**, reaproveitando o build. Isso não é só conveniência: religar o mesmo deployment devolve **exatamente o binário que estava no ar**, sem rebuild, sem SHA novo e sem um rollout que passa por gates de novo. É o que "voltar ao estado anterior" deveria significar — e é a diferença entre retomar e reimplantar.

### Armadilha 2 — o status mente sobre qual é o último deployment

Esta é a que mais engana. No religar de 2026-08-28, o `get-status` do `pic-api` apresentava como último deployment um de **08/08 em `FAILED`**, quando o mais recente era o de **20/08, com o commit correto**. Deployments removidos ficam **ocultos numa visão e visíveis na outra**: `get-status` esconde, `list-deployments` mostra.

Quem religa pelo status volta o binário errado — e o status novo dirá `SUCCESS`, porque de fato subiu. Só não subiu o que devia. Daí as duas regras:

- **Antes de religar, `list-deployments` do serviço.** Escolha o deployment por data e commit, não pelo que a interface chama de "último".
- **Depois de religar, verifique comportamento, não status.** Status diz que subiu; não diz *o quê* subiu.

E a regra permanente do pipeline continua valendo no religar: produção acompanha a branch `deploy`, nunca `main` ([backlog de CI](../../backlog-ci.md)).

## Provar que voltou — por comportamento

Cada sonda abaixo existe porque prova uma coisa que as outras não provam. Use fetch único gravado em arquivo e conte com `grep -o … | wc -l`, pelas razões do [runbook do deploy em transição](verificar-apos-deploy.md).

| Sonda | Esperado | O que prova — e o que não prova |
|---|---|---|
| `GET /saude` | 200 com `versao`, `versao_snapshot`, `contagens` por conjunto e `cargas` por fonte | Processo vivo **e** banco alcançável pelo papel de leitura — sem banco o endpoint responde 503 `banco_indisponivel`. **Não prova qual binário subiu.** |
| `GET /v1/postos/mapa?…&limit=500` | 500 itens = **500 postos distintos, zero `posto_id` repetido** | Esta é a prova de binário. O colapso por `posto_id` dentro da consulta entrou em 20/08; antes disso o `limit` contava evidências, e a viewport cheia devolvia cerca de um terço dos postos que cabiam. Ponto repetido — ou menos itens que o `limit` com `truncado: true` — é o binário velho de volta, não problema de dado. |
| `GET /v1/postos/{id}/contexto-regional` | 200 | Que a rota mais nova da ficha está no ar. Rota ausente devolve 404 com o serviço inteiro em `SUCCESS`. |
| `robots.txt` e `sitemap.xml` do portal | 200, índice com **28 fatias** (1 de páginas fixas + 27 UFs) | Que o web subiu **com `PIC_API_URL`**. Sem a variável as fatias nascem vazias e são servidas vazias — e nada no status acusa. |
| Ficha renderizada | **0** ocorrências de `sha256`, `localizador` e `.csv` no HTML (`scripts/verificar-payload.mjs`) | Que a barreira de saída voltou junto ([ADR-008](../../arquitetura/adr/adr-008-guardiao-barreira-de-saida.md)). Procedência vaza pelo payload de flight mesmo sem pintar na tela. |

## O efeito colateral esperado — e o que ele significa

Ao subir, o worker roda a agenda e **ingere o atraso acumulado de uma vez**. A agenda é orientada a vencimento: oito dias parados são oito dias vencidos. Em 2026-08-28 o cadastro foi de **45.762 para 46.510 postos**.

**Isso é o desenho funcionando, não anomalia** — e precisa estar previsto aqui para ninguém abrir incidente de "carga duplicada" em cima do comportamento correto. O sinal preocupante é o oposto: contagem **parada** depois do religar, que aponta worker sem cron, worker que subiu com papel de leitura, ou volume não montado.

Um ressalva: o gate de volume anômalo do dump mensal continua valendo durante a recuperação do atraso. Salto grande **na F05** não é este efeito colateral — é o [runbook do dump](dump-mensal-ausente-ou-anomalo.md).

## Cron

O worker roda por cron (`0 6 * * *`, com o volume em `/data`). O agendamento é configuração de serviço e sobrevive ao `down`, mas **conferir é obrigatório**, porque a falha é muda: worker sem cron não gera erro nenhum — só nunca mais ingere, e o sintoma aparece dias depois como "os dados estão velhos", longe da causa. A confirmação real não é ver o cron na tela; é a contagem andar no dia seguinte.

## Se algo não voltar

1. **A MCP também recusa religar o deployment** → o build se perdeu. Aí sim vale um deploy novo, do SHA da branch `deploy`, passando pelo gate. Nunca apontando produção para `main` para "destravar".
2. **API ou worker sobem e caem em laço** → leia o log de arranque antes de qualquer hipótese. O contêiner imprime o modo e a **origem** dele (`[iniciar] modo: agenda (de $PIC_MODO)`); worker que subiu como `servir` é uma segunda API silenciosa, e o sintoma seria a F01 parar de ingerir. URL de banco é **por serviço**: worker que recebeu o papel de leitura recusa subir e diz qual papel recebeu e qual variável corrigir.
3. **Nada disso resolve** → pare e escale. A linha que não se cruza sozinho: não destruir volume e não reprovisionar serviço "para começar limpo". Reprovisionar perde variável, domínio, cron e a ligação de volume, e troca um problema de dez minutos por um dia de reconstrução.

## A pilha da PIC Gestão não voltou — e isso não é regressão do religar

Registrado aqui para que ninguém confunda **"não religou"** com **"quebrou ao religar"**: a pilha `pic-gestao-*` **nunca esteve operacional**. `pic-gestao-api` falha desde 11/08, e idp, console e migradores só têm deployments `SKIPPED`. Não há estado bom anterior para o qual voltar, e tentar consertá-la durante uma retomada é abrir um projeto de implantação no meio de uma operação de emergência. Quem religar deve registrar a pilha como fora do escopo, com esta frase, e seguir.

## O que NÃO fazer

- **Apagar volume porque "o serviço está parado".** É a única ação desta página sem volta.
- **Religar pelo que o `get-status` chama de último deployment.** Confira sempre por `list-deployments`.
- **Concluir de um `SUCCESS` que a plataforma voltou.** Ele prova que algo subiu.
- **Subir aplicações antes dos bancos** e depois diagnosticar o healthcheck.
- **Apontar produção para `main`** para acelerar o religar.
- **Desligar atravessando a janela do dump da Receita** sem uma decisão registrada de que o mês foi abandonado.
