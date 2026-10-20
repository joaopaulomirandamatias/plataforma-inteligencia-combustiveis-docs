# F1-12 v2 — população candidata congelada e vinculada ao manifesto

> **Estado:** o contrato estrutural `f1-12-v2` está implementado e mantém
> compatibilidade de leitura com os candidatos F1-09 reconhecidos. Os gates
> estruturais F02 recusam modelo explícito, vinculam o hash ao localizador GEO e
> exigem igualdade entre snapshots GEO declarados e usados. A população F02
> continua experimental; seu único gate operacional de promoção restante é o
> dry-run das 801 pendências e a revisão do relatório.

## Problema que este card fecha

O F1-11 congela o protocolo do experimento — snapshots de fonte, hashes, cortes bitemporais, versões, seed e quotas. O F1-10 consegue transformar a fila F1-09 em amostra cega.

Ainda existia, porém, uma lacuna entre os dois artefatos: fornecer um `manifesto_sha256` válido à amostragem **não provava por si só que a população atualmente lida da fila havia sido produzida a partir daqueles snapshots e cortes**.

Essa lacuna é relevante para a validade experimental. Um mesmo protocolo não pode representar duas populações candidatas diferentes sem que essa diferença apareça no artefato auditável.

## Objetivo

F1-12 cria um gate antes da amostragem humana:

```text
manifesto F1-11 validado
        ↓
resolver exatamente o snapshot F02 ou F03 declarado
        ↓
reexecutar F1-09 com os cortes bitemporais do manifesto
        ↓
coletar somente candidatos gerados nessa reexecução
        ↓
validar versões + todas as proveniências por SHA-256
        ↓
calcular fingerprint canônico da população
        ↓
selecionar quotas/seed do próprio manifesto
        ↓
gate estrutural F1-10 / codebook v2
        ↓
pacote cego + reconciliação interna
```

O card **não** cria rótulos, não estima `m/u`, não escolhe thresholds, não liga identidades e não altera clusters.

## Contratos

### 1. Fontes suportadas

Nesta versão, cada experimento aceita apenas um contrato de entidades:

- F01 como universo cadastral conhecido no corte;
- F02 **ou** F03 como snapshot de pendências `cnpj_sem_posto`;
- GEO-01 e GEO-ANP somente como snapshots de proveniência geográfica, quando
  suas evidências forem usadas por um candidato F01↔F02.

F05 continua fora até existir parser estruturado próprio. GEO-01 e GEO-ANP
participam do ER como **evidência**, com coordenada, fonte, localizador e hash;
não são entidades candidatas e não ampliam o lote de comparação.

Para F02, as fontes de **entidade** do manifesto e do lote são exatamente
`{F01, F02}`. F03 no mesmo manifesto falha antes de gerar candidatos, porque o
F1-12 congela uma única versão de modelo por experimento. Snapshots GEO
adicionais são permitidos exclusivamente para provar as evidências usadas. Um
experimento F03 separado continua no contrato-base `f1-09-v1`. Para GEO, o
conjunto declarado precisa coincidir exatamente com o conjunto efetivamente
referenciado pelos candidatos; não se aceitam snapshots ausentes nem
declarados em excesso.

### 2. Snapshot pendente resolve por fonte + SHA-256

Para cada F02/F03 declarado no manifesto, o ambiente precisa encontrar **exatamente uma** carga local com o mesmo par:

```text
fonte + hash_conteudo
```

Ausência falha alto. Ambiguidade também falha alto. `carga_id` continua sendo identificador local e não entra no hash do F1-11.

### 3. População é regenerada, não lida indiscriminadamente da fila

O F1-12 chama o pipeline F1-09 para os snapshots declarados e coleta apenas os `candidato_id` devolvidos por essas execuções.

Candidatos antigos ou de outro experimento que já existam em `identidade.candidato_ligacao` não entram na população apenas por estarem pendentes.

### 4. Toda proveniência precisa apontar para os snapshots declarados

O localizador da zona bruta já possui contrato formal:

```text
<arquivo>@sha256:<64-hex>[:linha]
```

O F1-12 extrai o SHA-256 de cada lado das evidências factuais e também de cada
ponto GEO contido em `contexto_f02.geoespacial.pontos_f01/pontos_f02`. Todo par
`fonte + hash_conteudo` usado precisa estar declarado no manifesto F1-11. Para
GEO, o SHA-256 embutido no `localizador` também precisa coincidir com o
`hash_conteudo` declarado no próprio ponto.

Localizador abreviado, sem SHA completo ou com hash fora do manifesto é rejeitado.

O artefato `f1-12-v2` publica `proveniencias_usadas` em ordem canônica. Cada
item contém:

- `fonte`;
- `localizador` completo;
- `hash_conteudo` SHA-256.

Para F01/F02/F03, um candidato não pode misturar dois hashes da mesma fonte.
Fontes GEO podem contribuir com mais de um snapshot real; cada um precisa ser
declarado, efetivamente usado e fica visível separadamente. A comparação final
é por igualdade de conjuntos: snapshot GEO usado e não declarado, ou declarado
e não usado, falha alto. No adaptador PostgreSQL, o hash GEO vem de
`cache_geocodificacao.resultado_sha256`, não do cadastro F01 nem do localizador
do vínculo.

### 5. Semântica temporal das evidências geográficas

Cada ponto geográfico separa três datas opcionais:

- `validade_inicio`: quando o fato geográfico começa a valer na camada
  bitemporal;
- `coletado_em`: quando o resultado foi coletado/persistido pela plataforma;
- `observado_em`: quando a própria fonte declara que a posição foi obtida.

GEO-ANP usa `metadados.data_obtencao` em `observado_em`. GEO-01 mantém
`observado_em = null`; sua validade e coleta não são convertidas em observação.
No ponto F02, `observado_em` é a data de coleta PMQC e `coletado_em` é a data do
depósito bruto. Ausência continua `null`, sem imputação.

### 6. Versões congeladas

O runtime usado para regenerar a população precisa coincidir com as versões declaradas no manifesto:

- codebook: versão carregada do F1-08a;
- normalizador: `f1-02-v1` nesta versão;
- blocking: `f1-03-v1` nesta versão;
- similaridade: `f1-04-v1` nesta versão;
- modelo: versão explícita do modelo fornecido; sem modelo,
  `f1-09-v1-sem-modelo` no contrato-base ou
  `f1-09-f02-contexto-v1-sem-modelo` para a população exclusiva F01↔F02.

O contrato-base F01↔F03 continua aceitando um modelo explicitamente versionado.
Já a presença de F02 no manifesto fecha o protocolo em
`f1-09-f02-contexto-v1-sem-modelo`: fornecer um modelo é erro de contrato antes
da execução do pipeline.

O envelope do candidato também precisa declarar o mesmo normalizador e a mesma versão do modelo.

Essas strings não significam que parâmetros estatísticos foram validados. Elas identificam a implementação que produziu a população.

O manifesto não converte um contrato no outro. Populações F01↔F03 continuam
sob `f1-09-v1`; a população F01↔F02 contextual usa schema e método próprios,
preserva os candidatos legados e exige o protocolo sem modelo. Nesta versão,
cada população/manifesto deve ser homogêneo; coexistência append-only na fila
não autoriza misturar contratos no mesmo artefato experimental.

Além dos localizadores factuais F01/F02, cada ponto GEO usado em distância
resolve para fonte e SHA-256 declarados no manifesto, aparece em
`proveniencias_usadas` e participa do fingerprint da população.

## Fingerprint da população

O artefato `f1-12-v2` calcula `populacao_sha256` sobre uma representação
canônica que inclui, por candidato:

- fontes e chaves do par;
- estrato primário e estratos internos;
- semântica da pontuação e valor, quando houver;
- versão do modelo;
- snapshots de origem por fonte + SHA-256;
- proveniências completas por fonte + localizador + SHA-256;
- `evidencias_sha256`, o SHA-256 da serialização JSON canônica do **envelope
  completo** de evidências.

O envelope é serializado com chaves ordenadas, separadores compactos, UTF-8 e
proibição de NaN. Portanto, qualquer alteração em campo factual, ponto,
distância, razão de ausência, data ou metadado temporal muda
`evidencias_sha256` e, por consequência, `populacao_sha256`.

O payload também incorpora o `manifesto_sha256`. Portanto, a mesma lista de pares sob outro protocolo não representa a mesma população experimental.

A ordenação é canônica para evitar que ordem de consulta ou ordem física da tabela altere o hash.

## Saídas

### Artefato de população

Contém:

- `schema_versao`;
- `manifesto_sha256`;
- `populacao_sha256`;
- total de candidatos;
- contagem por estrato primário;
- snapshots efetivamente usados;
- `proveniencias_usadas` com fonte, localizador e SHA-256.

### Pacote cego

Continua obedecendo ao codebook v2. O revisor não recebe:

- fingerprint da população;
- estratos;
- referência interna;
- score;
- contribuições Fellegi–Sunter;
- motivos de blocking;
- thresholds ou destino esperado.

### Manifesto interno de reconciliação

Passa a registrar também:

- `populacao_schema_versao`;
- `populacao_sha256`;
- contagem completa da população por estrato.

Esses campos são de auditoria interna, não de revisão cega.

## Operação

A CLI adiciona o comando:

```text
pic-er preparar-experimento \
  --manifesto manifesto.json \
  --populacao populacao.json \
  --pacote pacote-cego.json \
  --interno reconciliacao.json
```

Os três destinos precisam ser distintos. A população e a reconciliação são artefatos internos; o pacote cego continua sem fingerprint, referência interna e estratos.

## Critérios de aceite

- [x] mesmo manifesto + mesmos bytes + mesmo código produz o mesmo `populacao_sha256`;
- [x] repetição idempotente do pipeline não duplica a população lógica;
- [x] candidato de fila não gerado pelos snapshots declarados não entra silenciosamente;
- [x] hash factual fora do manifesto falha alto;
- [x] F02/F03 declarado sem carga exata falha alto;
- [x] versão de runtime/modelo divergente falha alto;
- [x] fonte ainda não suportada falha alto;
- [x] população F02 contextual prova hashes de todas as evidências GEO;
- [x] `proveniencias_usadas` preserva fonte, localizador e hash de cada entrada;
- [x] localizador GEO contém SHA-256 completo e igual ao `hash_conteudo` do ponto;
- [x] snapshots GEO declarados e usados coincidem exatamente, sem sobras;
- [x] manifesto/população F02 rejeitam modelo explícito antes de gerar candidatos;
- [x] manifesto misto F02/F03 é rejeitado antes de gerar candidatos;
- [x] digest canônico do envelope completo participa de `populacao_sha256`;
- [x] validade, coleta e observação geográfica permanecem semanticamente
      separadas;
- [x] pacote final continua estruturalmente cego;
- [x] suíte completa PostgreSQL 16, lint e contrato OpenAPI verdes no Railway CI Sandbox;
- [ ] dry-run das 801 pendências F02 e revisão do relatório antes de produção.

## Evidência histórica de validação técnica do v1

PR draft: `#8` — `work/f1-12-populacao-congelada`.

Branch real validada no commit:

`c3ca708c7029cee73ebeff686b9c900c79747e4a`

Railway CI Sandbox, deployment:

`9764f690-6db0-474c-8817-1beb76d734ad`

Resultado:

- `ruff check .`: PASS;
- suíte completa: **338 passed, 1 skipped, 2 deselected**;
- testes F1-12 de população/CLI: **6 passed**;
- isolamento contra candidato antigo da fila: **1 passed**;
- contrato OpenAPI: **8/8 passed**;
- `CI_RESULT=PASS`.

O sandbox também detectou um `ruff I001` no primeiro run que incluiu o teste de isolamento. A correção foi aplicada na branch real antes da repetição do gate; o erro não foi ignorado nem corrigido apenas na branch temporária de CI.

Esta evidência é **técnica suplementar e anterior ao `f1-12-v2`**. Ela não
substitui os testes atuais do contrato v2 nem o dry-run das 801 pendências. O
GitHub Actions oficial estava bloqueado por Billing & plans naquela rodada;
portanto, os números acima não constituem promoção do contrato atual.

## O que F1-12 não prova

`populacao_sha256` prova identidade do conjunto experimental e sua ligação ao protocolo. Ele **não prova**:

- que um par é ou não o mesmo posto;
- precisão ≥ 0,98;
- recall ≥ 0,95;
- qualidade do blocking;
- validade de parâmetros `m/u`;
- validade de thresholds de aceite/rejeição.

Essas propriedades só podem ser estimadas depois de revisão humana independente, adjudicação, auditoria de blocking e holdout final.
