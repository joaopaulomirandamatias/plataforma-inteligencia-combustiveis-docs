# F1-11 — Manifesto reproduzível do experimento de Entity Resolution

## Objetivo

Substituir o campo manual `manifesto_sha256` por um artefato calculado a partir do protocolo efetivamente congelado. O mesmo conjunto lógico de evidências e configurações deve produzir o mesmo SHA-256 independentemente da ordem de entrada ou do ambiente em que a validação for reproduzida.

## Conteúdo hashado

O manifesto `f1-11-v1` contém:

- `experimento_id`;
- snapshots das fontes identificados por `fonte + hash_conteudo` e competência opcional;
- commit exato do código;
- versões de codebook, normalizador, blocking, similaridade e modelo;
- seed da amostragem;
- quotas por estrato;
- corte de validade;
- corte de transação.

Todos os timestamps são normalizados para UTC (`Z`) antes do hash.

## O que deliberadamente não define o hash

`carga_id` é um identificador local do banco. A mesma carga de bytes pode receber IDs diferentes em desenvolvimento, teste e produção.

Por isso:

- o protocolo pode informar `carga_id` para validação operacional;
- o valor precisa ser inteiro positivo se informado;
- **`carga_id` não é serializado no manifesto canônico e não altera o SHA-256**;
- a identidade portável da fonte é `fonte + SHA-256 dos bytes`.

Essa escolha permite reconstruir o mesmo experimento em outro ambiente sem produzir um hash artificialmente diferente.

## Código

`codigo_commit` precisa ser um hash Git hexadecimal explícito de 40 a 64 caracteres. Nomes como `main`, `latest` ou `deploy` não são aceitos porque mudam de significado com o tempo.

## Plano de amostragem

O manifesto congela:

```json
{
  "seed": "seed-publicada",
  "quotas": {
    "estrato-a": 100,
    "estrato-b": 200
  }
}
```

Ordem de chaves não altera o hash. Alterar seed ou qualquer quota altera o hash.

## Cortes bitemporais

O protocolo exige timezone explícito para:

```text
validade_em
transacao_em
```

Por exemplo, `2026-08-08T03:00:00-03:00` é normalizado para `2026-08-08T06:00:00Z`.

## CLI

Na implementação em validação:

```bash
pic-er manifesto \
  --entrada protocolo.json \
  --saida manifesto.json
```

O comando é offline e não exige credenciais de banco.

O artefato possui:

```json
{
  "manifesto_sha256": "<sha256>",
  "manifesto": { "...": "conteúdo canônico" }
}
```

## Vínculo com a amostra

`pic-er amostrar` recebe opcionalmente o manifesto:

```bash
pic-er amostrar \
  --entrada candidatos.json \
  --manifesto manifesto.json \
  --pacote pacote-revisor.json \
  --interno manifesto-interno.json
```

Antes de amostrar, o executável verifica:

- `experimento_id`;
- seed;
- quotas;
- versão do codebook carregado no runtime;
- SHA-256 do próprio artefato.

O hash correto é então injetado na entrada da amostragem. Se a entrada já trouxer `manifesto_sha256`, ele precisa coincidir exatamente.

Manifesto adulterado ou plano divergente falha antes da criação dos arquivos de revisão.

## Determinismo

Não alteram o hash:

- ordem dos snapshots;
- ordem das quotas;
- timezone equivalente depois de normalização UTC;
- `carga_id` local.

Alteram o hash:

- bytes-fonte diferentes;
- versão de qualquer componente;
- commit de código;
- seed;
- quotas;
- cortes temporais;
- experimento.

## Dependência

A F1-11 está encadeada sobre a PR operacional F1-08e. Depois que o GitHub Actions voltar:

1. validar/mesclar codebook v2 quando aplicável;
2. validar F1-08e;
3. validar F1-11;
4. tornar `--manifesto` obrigatório em um card posterior depois que todos os consumidores tiverem migrado.

Enquanto isso, o parâmetro permanece opcional para compatibilidade, mas novos experimentos devem usar o manifesto calculado.
