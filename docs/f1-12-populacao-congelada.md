# F1-12 — população candidata congelada e vinculada ao manifesto

## Problema que este card fecha

O F1-11 congela o protocolo do experimento — snapshots de fonte, hashes, cortes bitemporais, versões, seed e quotas. O F1-10 consegue transformar a fila F1-09 em amostra cega.

Ainda existia, porém, uma lacuna entre os dois artefatos: fornecer um `manifesto_sha256` válido à amostragem **não provava por si só que a população atualmente lida da fila havia sido produzida a partir daqueles snapshots e cortes**.

Essa lacuna é relevante para a validade experimental. Um mesmo protocolo não pode representar duas populações candidatas diferentes sem que essa diferença apareça no artefato auditável.

## Objetivo

F1-12 cria um gate antes da amostragem humana:

```text
manifesto F1-11 validado
        ↓
resolver exatamente snapshots F02/F03 declarados
        ↓
reexecutar F1-09 com os cortes bitemporais do manifesto
        ↓
coletar somente candidatos gerados nessa reexecução
        ↓
validar versões + proveniência por SHA-256
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

Nesta versão, o experimento aceita apenas a parte já executável do pipeline:

- F01 como universo cadastral conhecido no corte;
- F02 e/ou F03 como snapshots de pendências `cnpj_sem_posto`.

F05 continua fora até existir parser estruturado próprio. GEO-01 continua fora do ER enquanto coordenadas verificáveis não estiverem integradas ao contrato de representação.

### 2. Snapshot pendente resolve por fonte + SHA-256

Para cada F02/F03 declarado no manifesto, o ambiente precisa encontrar **exatamente uma** carga local com o mesmo par:

```text
fonte + hash_conteudo
```

Ausência falha alto. Ambiguidade também falha alto. `carga_id` continua sendo identificador local e não entra no hash do F1-11.

### 3. População é regenerada, não lida indiscriminadamente da fila

O F1-12 chama o pipeline F1-09 para os snapshots declarados e coleta apenas os `candidato_id` devolvidos por essas execuções.

Candidatos antigos ou de outro experimento que já existam em `identidade.candidato_ligacao` não entram na população apenas por estarem pendentes.

### 4. Proveniência factual precisa apontar para os snapshots declarados

O localizador da zona bruta já possui contrato formal:

```text
<arquivo>@sha256:<64-hex>[:linha]
```

O F1-12 extrai o SHA-256 de cada lado das evidências factuais e exige que cada par `fonte + hash` esteja declarado no manifesto F1-11.

Localizador abreviado, sem SHA completo ou com hash fora do manifesto é rejeitado.

### 5. Versões congeladas

O runtime usado para regenerar a população precisa coincidir com as versões declaradas no manifesto:

- codebook: versão carregada do F1-08a;
- normalizador: `f1-02-v1` nesta versão;
- blocking: `f1-03-v1` nesta versão;
- similaridade: `f1-04-v1` nesta versão;
- modelo: versão explícita do modelo fornecido; sem modelo, `f1-09-v1-sem-modelo`.

O envelope do candidato também precisa declarar o mesmo normalizador e a mesma versão do modelo.

Essas strings não significam que parâmetros estatísticos foram validados. Elas identificam a implementação que produziu a população.

## Fingerprint da população

O artefato `f1-12-v1` calcula `populacao_sha256` sobre uma representação canônica que inclui, por candidato:

- fontes e chaves do par;
- estrato primário e estratos internos;
- semântica da pontuação e valor, quando houver;
- versão do modelo;
- snapshots de origem por fonte + SHA-256.

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
- snapshots efetivamente usados.

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
- [x] pacote final continua estruturalmente cego;
- [x] suíte completa PostgreSQL 16, lint e contrato OpenAPI verdes no Railway CI Sandbox;
- [ ] merge/promoção continuam condicionados ao GitHub Actions oficial.

## Evidência de validação técnica

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

Esta evidência é **técnica suplementar**. O GitHub Actions oficial continua bloqueado por Billing & plans; portanto F1-12 não está promovida para `deploy` nem em produção.

## O que F1-12 não prova

`populacao_sha256` prova identidade do conjunto experimental e sua ligação ao protocolo. Ele **não prova**:

- que um par é ou não o mesmo posto;
- precisão ≥ 0,98;
- recall ≥ 0,95;
- qualidade do blocking;
- validade de parâmetros `m/u`;
- validade de thresholds de aceite/rejeição.

Essas propriedades só podem ser estimadas depois de revisão humana independente, adjudicação, auditoria de blocking e holdout final.
