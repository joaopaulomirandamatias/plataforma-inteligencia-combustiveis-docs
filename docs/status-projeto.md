# Status canônico do projeto

**Atualizado em:** 2026-10-19

**Escopo:** Plataforma de Inteligência de Combustíveis (PIC)

**Função deste documento:** ponto de entrada para saber o que existe, o que está
em produção e o que ainda depende de aceite. Documentos de cada frente continuam
sendo a fonte do detalhe técnico.

## Como interpretar o status

Os estados abaixo não são sinônimos e não devem ser promovidos por inferência:

1. **Implementado** — existe código, migração, contrato ou artefato executável.
2. **Validado tecnicamente** — os gates automatizados aplicáveis passaram em uma
   árvore identificável.
3. **Ativo em produção** — o componente foi observado executando no ambiente de
   produção na data da evidência.
4. **Aceito operacionalmente** — pessoas reais concluíram o fluxo acordado, com
   papéis, exceções e evidências registradas.

Um serviço `Online` prova o terceiro estado, não o quarto. Da mesma forma, uma
especificação aprovada não prova que o comportamento foi implementado.

## Topologia do projeto

O produto tem **três pilares**, mas quatro repositórios físicos porque a
plataforma pública separa núcleo/API e portal:

| Pilar | Repositório físico | Responsabilidade |
|---|---|---|
| Documentação e governança | `plataforma-inteligencia-combustiveis-docs` | Contratos, ADRs, status, backlogs e runbooks |
| Plataforma pública | `plataforma-inteligencia-combustiveis` | Ingestão, modelo bitemporal, resolução de entidades, geodados e API |
| Plataforma pública | `plataforma-inteligencia-combustiveis-web` | Portal público, busca, detalhe, mapa e indexação |
| Plataforma de gestão | `plataforma-inteligencia-combustiveis-gestao` | IAM, organizações, publicação, projeção, console e worker |

Essa separação física não cria um quarto produto. Contratos compartilhados e
critérios de promoção precisam, porém, considerar os dois repositórios da
plataforma pública.

## Quadro executivo

| Frente | Implementado | Validado tecnicamente | Ativo em produção | Aceito operacionalmente |
|---|---|---|---|---|
| Documentação canônica | Sim | Sim — gates de contrato e léxico | Não se aplica | Uso contínuo; revisão permanece obrigatória |
| Núcleo/API pública | Sim | Sim, com dívida localizada de branches/CI | **Sim** | Operação pública observada; não equivale a aceite institucional |
| Portal público | Sim | Sim — testes e build | **Sim** | Operação pública observada; melhorias antigas ainda requerem triagem |
| Gestão — G1 (tenant/IAM) | Sim | Sim | **Sim**, serviços observados | **Pendente** |
| Gestão — G2 (publicação) | Sim | Sim | **Sim**, serviços observados | **Pendente** |
| F1 — engenharia pré-rótulo | Sim | Sim | Sim | Validação empírica humana **pendente** |
| F09 — Inmetro/Ipem | Mapa e pedido documentados | Fontes públicas avaliadas | Não | Convênio e dados por bico **pendentes** |

## Evidência de produção em 2026-10-11

A verificação coordenada dos repositórios e do ambiente de produção encontrou:

- API pública respondendo `HTTP 200` e estado `pronto`;
- portal público e `sitemap` respondendo `HTTP 200`;
- `pic-api`, `pic-web`, pilha `pic-gestao-*`, bancos e migradores em estado
  operacional no Railway;
- snapshot público com 48.406 registros de cadastro, 128.618 registros PMQC e
  150.354 registros de preço;
- cargas F01 até 2026-10-10, F02 até 2026-10-09, F03 até 2026-10-03 e GEO-ANP
  até 2026-10-10.

Esses números são evidência datada, não SLO permanente. Para uma decisão
operacional atual, repetir o [runbook pós-deploy](operacao/runbooks/verificar-apos-deploy.md)
e consultar `/saude`.

## Onde cada pilar parou

### Documentação e governança

Os contratos, ADRs, catálogos de fontes e runbooks formam uma base ampla. A
pendência principal é manter o status sincronizado com os runtimes e evitar que
documentos de desenho sejam lidos como aceite de produto.

Em 2026-10-11, os schemas públicos de `GET /saude` e `GET /v1/precos`
passaram a recusar propriedades desconhecidas em todos os objetos, inclusive os
aninhados. Os campos tornados obrigatórios são os que o runtime sempre monta,
que a suíte de conformidade cobre e que foram observados em produção. O estado
de saúde é o literal `pronto`, não `ready`.

O trabalho de recuperação hierárquica com PageIndex pertence ao runtime
**PHN/ReguHub (harmonização normativa)**. É uma experiência adjacente, em POC,
e não uma dependência nem uma prioridade automática do núcleo PIC. Veja o
[épico do POC](arquitetura/epico-poc-pageindex-recuperacao-hierarquica.md) e o
[ADR-011](arquitetura/adr/adr-011-recuperacao-documental-hierarquica-pageindex.md).

### Plataforma pública

O núcleo, a API e o portal estão implantados e processam dados reais. O bloco
PMQC estruturado da ficha foi concluído em produção. O ponto de retomada da
estabilização é executar com segurança o saneamento das evidências GEO antes de
impor a nova restrição de unicidade e migrar a configuração Railway antes da
descontinuação do Config as Code atual.

Em 2026-10-11 foi registrada uma nova decisão de produto para a
[ficha pública](produto/ficha-publica.md): preço não pode ser sua única dimensão
principal. Cadastro, amostras PMQC, cada ensaio/resultado/unidade, atos públicos,
frescor e metodologia devem ser organizados por seção. Isso é **especificação
alvo**, não evidência de disponibilidade em produção.

Em 2026-10-19, a camada visual desse primeiro bloco foi promovida ao portal
público. Os PRs #35 e #36 do portal foram mesclados; as branches `main` e
`deploy` ficaram alinhadas em
`d9b93a36e5f0afb1b2f2eb43a274b3496e577bc9`; o pipeline Woodpecker #47 concluiu
CI e promoção; e o deployment Railway
`c8513d09-6802-440a-bee7-a31368e2fd74` terminou com `SUCCESS`. O smoke retornou
`HTTP 200` e a ficha do posto `304d2b1e-e655-5f50-8db9-b8445179ce25` foi
verificada visualmente. A seção **Qualidade do combustível** está, portanto,
ativa no portal.

Na sequência, o PR #72 do núcleo isolou PMQC das migrações GEO 023/024, migrou o
CI para o Woodpecker compartilhado e foi mesclado. O pipeline de PR #10 e o
pipeline de `main` #11 passaram; este último promoveu `main` e `deploy` para
`8f46c869bcd956dab30ec903d24da8cbfddfebb3`. A suíte do runner executou 788
testes com PostgreSQL, nenhum ignorado, e mais 25 testes dedicados de contrato.

No Railway, o Migrator `11efd3fe-c865-4ed6-a921-3c4e1bba2f1e` concluiu com
`SUCCESS` e registrou “nada pendente (22 migrações já aplicadas)”; portanto não
houve DDL. A API `33982e35-b1ec-4344-b5af-c1a2cb547903` foi então implantada
com `SUCCESS`, sem redeploy do worker. `/saude` respondeu `HTTP 200`. O smoke da
ficha `00097ff8-98c0-5d16-823e-66edb77c334c` confirmou 6 agrupamentos e 48
ensaios PMQC, e a verificação visual no portal mostrou data, fonte, contagens,
resultado, unidade e classificação sem erros no console. O schema PMQC pode,
assim, ser consumido em produção; ausência de agrupamentos continua significando
somente ausência de resultado público vinculado no recorte.

O PR #73 fixou o núcleo no contrato documental de produção
`46b4f535462e44edf79a5e3c0c2bb5cffe6dd8fa`. Os pipelines Woodpecker #12 e
#13 passaram e promoveram `main`/`deploy` para
`09b02acebaa7e583495678a083e8cfb13bad0772`. Como esse movimento alterou apenas
o lock reprodutível do contrato, não houve novo deployment Railway da API.

Também em 2026-10-19, a agenda automática do `pic-worker`
(`7b607d55-fb96-4af4-928b-da4f3a9d730d`) foi pausada de forma deliberada: o
cron `0 4 * * *` passou a `null`, com pós-condição confirmada. Não houve
redeploy; o deployment `28bccddb-af92-4f99-b8c6-3e385159e59e` permaneceu em
`SUCCESS`, com restart `NEVER` e volume `/data`. A pausa evita novas tentativas
diárias da F06 em `NXDOMAIN` e novas reingestões GEO antes do saneamento — estas
foram observadas em 13, 15, 17 e 19/10. API e portal continuam servindo o
snapshot publicado, mas os dados não recebem atualização diária automática
enquanto esse estado durar.

As fontes ANP podem ser atualizadas de modo controlado pelo one-shot
`/railway.worker-anp.json`, após prova do SHA, Migrator e contagens. A F06 fica
isolada em `/railway.worker-f06.json`. A agenda completa só volta depois de uma
prova F06 bem-sucedida no runtime Railway e de um ciclo completo sem erros. O
one-shot não remove o NO-GO das migrações GEO 023/024 nem substitui o backup
restaurável e o saneamento exigidos para elas.

O PR #74 corrigiu o falso verde da agenda no código: falhas estruturadas fecham
com exit `1`, F06 em `NXDOMAIN` fecha com `5`, F02/F03 sem publicação esperada
continuam em `0` e status desconhecido falha fechado. Os pipelines Woodpecker
#14 e #15 passaram sem skips e promoveram
`main == deploy == 51eb12dd8ba95fc3eb90832287d3f58c83928b77`. O serviço
`pic-worker` não foi reimplantado nem executado; continua no deployment anterior
com cron `null`. O primeiro one-shot controlado desse SHA ainda deve provar a
propagação do exit code no runtime, e logs, resumos e deltas continuam
obrigatórios. O procedimento detalhado está em
`docs/operacao-migracoes.md` no repositório do núcleo, e a interpretação da
pausa no runbook de [desligar/religar](operacao/runbooks/desligar-e-religar-a-plataforma.md#cron).

No PR #70 do núcleo, as migrações 023 e 024 implementam o invariante geográfico
correto: no máximo uma evidência com transação viva por posto+fonte cobrindo o
mesmo instante D, admitindo segmentos de validade disjuntos. A 024 é o
forward-fix que preserva a matriz C×D — A `[D1,D3)` e B `[D3,∞)` no conhecimento
corrente, sem apagar A `[D1,∞)` do histórico anterior — e serializa a origem F01
contra o refresh cadastral. Em 2026-10-11, a suíte completa em PostgreSQL e o
CI remoto do PR estavam aprovados. Em 2026-10-19, o PR permanecia sem
implantação por **NO-GO operacional**: não havia cobertura atual de backup/PITR
para executar com segurança a sequência das migrações 023/024. O contrato e o
core não estão comprovados como mesclados, migrados ou ativos em produção. O
saneamento, o backup restaurável, a decisão de PITR e os gates do runbook
continuam obrigatórios.

O [status de F1](status-f1-implementacao.md) registra a engenharia pré-rótulo.
Seu próximo avanço não é fabricar mais resultados sintéticos: requer snapshots
reais, dois revisores humanos independentes, adjudicação e abertura única do
holdout.

### Plataforma de gestão

G1 e G2 possuem implementação, testes e serviços implantados. Permanecem
**abertos para aceite operacional**. O aceite mínimo deve registrar:

Em 2026-10-15, a conta piloto foi auditada contra a configuração do serviço e
foi confirmado drift entre o e-mail esperado e a identidade já persistida no
Keycloak. O cadastro persistido foi reconciliado em produção; sujeito, nome de
usuário, senha e TOTP foram preservados, a conta permaneceu ativa e uma
verificação posterior confirmou a ausência de ações obrigatórias. O utilitário
e o runbook desse diagnóstico foram integrados no repositório de gestão com CI
verde. Essa correção restabelece o identificador de acesso esperado, mas não
substitui o aceite G1/G2 abaixo.

1. dois atores OIDC reais, com papéis diferentes;
2. duas organizações e a matriz negativa de acesso cruzado;
3. publicação e suspensão refletidas na projeção em até 60 segundos;
4. alerta e tratamento de falha/dead-letter;
5. decisão de produto/jurídico para a atuação do Guardião.

Até essas evidências existirem, não escrever “G1/G2 concluídos” sem o
qualificador **tecnicamente**.

## Próxima rodada recomendada

1. **Estabilização:** preservar trabalho local, reconciliar branches e PRs,
   recuperar gates de CI e concluir a migração de configuração do Railway para
   `.railway/railway.ts` antes de 2026-12-01.
2. **Piloto de gestão:** executar o aceite G1/G2 com 2–5 unidades reais e guardar
   as evidências do fluxo e das falhas.
3. **Frente institucional em paralelo:** iniciar o pedido F09 ao Inmetro/Ipem,
   sem bloquear o piloto por um calendário externo.
4. **Evidência científica:** depois de estabilizar o núcleo, executar a fase
   empírica humana de F1.

Aplicativo, telemetria, SEFAZ completa e novas frentes de IA não são o próximo
gate do PIC enquanto estabilização e piloto permanecerem abertos.

## Regra de manutenção

- Atualizar este arquivo somente com evidência identificável e datada.
- Manter o detalhe no documento da frente e trazer para cá apenas a conclusão.
- Ao mudar um estado, registrar separadamente implementação, validação técnica,
  produção e aceite operacional.
- Tratar `Online`, teste verde e documento aprovado como evidências diferentes.
- Não copiar para cá métricas de F1 antes do protocolo humano descrito no
  [status de F1](status-f1-implementacao.md).
