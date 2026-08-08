# F1-15 — particionamento treino/calibração/teste por grupos estruturais

## Problema

A validação formal F1-08 exige que o teste final não participe da estimação de parâmetros, treinamento ou escolha de thresholds. O relatório F1-08d já rejeita registros marcados como `treino` ou `calibracao` quando executa o holdout, mas ainda faltava o artefato que **congela a partição antes da rotulagem humana**.

Dividir pares aleatoriamente por linha não é suficiente: dois pares podem compartilhar o mesmo registro de origem. Se um deles cair em treino e outro em teste, o experimento contém vazamento direto de informação sobre aquele registro.

## Objetivo

F1-15 congela um split reprodutível antes do primeiro rótulo:

```text
itens cegos do experimento
        ↓
resolver candidato_ligacao de cada item
        ↓
representar cada par como aresta entre registros (fonte, chave)
        ↓
componentes conectados
        ↓
grupo estrutural indivisível
        ↓
alocação determinística por seed + pesos explícitos
        ↓
treino | calibração | teste
        ↓
artefato canônico + SHA-256 + persistência append-only
```

Nenhum rótulo humano, score, threshold ou resultado de avaliação participa da alocação.

## Unidade de agrupamento

Cada item de revisão aponta internamente para `candidato_ligacao:<id>`. O candidato possui dois extremos:

```text
(fonte_a, chave_a) ↔ (fonte_b, chave_b)
```

Esses extremos são nós de um grafo não direcionado e cada item é uma aresta. Todas as arestas conectadas formam um **grupo estrutural indivisível**.

Consequência: se dois itens compartilham qualquer registro de origem, direta ou transitivamente, ficam na mesma partição.

### Limite

Esse grupo é uma barreira estrutural disponível **antes** do ground truth. Ele não afirma que um componente conectado seja a identidade física verdadeira do posto, nem prova que dois componentes distintos não pertençam ao mesmo ponto físico. O isolamento por identidade verdadeira só pode ser auditado depois que existir evidência humana real.

## Protocolo explícito

A geração exige:

- `experimento_id`;
- `manifesto_sha256`;
- `populacao_sha256`;
- `seed_particao`;
- `pesos_particao` com exatamente:
  - `treino`;
  - `calibracao`;
  - `teste`.

Os pesos precisam ser inteiros positivos. Não existe proporção padrão escondida no código.

O experimento precisa possuir pelo menos três grupos estruturais independentes. Caso contrário, o sistema falha em vez de quebrar um grupo para preencher artificialmente uma partição.

## Alocação determinística

1. cada grupo recebe `grupo_id` derivado por SHA-256 do conjunto canônico de registros que o compõem;
2. grupos são ordenados determinística e independentemente da ordem física das tabelas;
3. os três primeiros grupos garantem que treino, calibração e teste sejam não vazios;
4. grupos restantes são atribuídos considerando déficit relativo aos pesos explícitos;
5. empates usam SHA-256 de seed + grupo + partição;
6. um grupo nunca é dividido.

Mesmas entradas, mesma seed e mesmos pesos produzem o mesmo artefato.

## Artefato

Schema: `f1-15-v1`.

Contém:

- experimento;
- hashes do manifesto e da população;
- seed;
- pesos declarados;
- total de itens;
- contagem por partição;
- grupos estruturais, partição e `item_id` cegos;
- `particionamento_sha256` canônico.

O hash muda quando muda seed, pesos, população ou composição/alocação dos grupos.

## Persistência

Migração `016_particionamento_entity_resolution.sql` adiciona:

### `identidade.particionamento_er`

Cabeçalho append-only do split, um por experimento.

### `identidade.particao_grupo_er`

Grupo estrutural e sua partição.

### `identidade.particao_item_er`

Mapa `item_id` → grupo.

O papel da aplicação possui `SELECT` e `INSERT`, sem `UPDATE`/`DELETE`.

## Defesa em profundidade no PostgreSQL

O banco verifica no `COMMIT`:

1. todos os itens do experimento foram mapeados;
2. nenhum item extra foi introduzido;
3. contagem declarada por grupo coincide com o mapa;
4. todos os itens possuem referência interna válida `candidato_ligacao:<id>`;
5. treino, calibração e teste são não vazios;
6. o mesmo registro de origem `(fonte, chave)` não aparece em mais de uma partição.

Assim, um `INSERT` SQL manual não consegue contornar a principal barreira de leakage apenas escolhendo `grupo_id` arbitrários.

O split também precisa ser registrado antes do primeiro rótulo humano. Depois disso, criar outro particionamento para o mesmo experimento é bloqueado.

## Operação

O módulo operacional recebe um JSON completo; não escolhe pesos ou seed pelo usuário:

```text
python -m pic.operacao_particionamento_entity_resolution \
  --entrada protocolo-particao.json \
  --saida particionamento.json
```

O comando gera, persiste e exporta o artefato canônico.

## Critérios de aceite

- [x] alocação não usa rótulos humanos;
- [x] itens que compartilham registro ficam na mesma partição;
- [x] conectividade transitiva mantém o componente inteiro unido;
- [x] mesma entrada/seed/pesos gera o mesmo split;
- [x] seed, pesos ou população diferentes alteram o hash do artefato;
- [x] nenhuma partição fica vazia;
- [x] menos de três grupos independentes falha alto;
- [x] persistência é idempotente apenas para o mesmo artefato;
- [x] tabelas são append-only para a aplicação;
- [x] split precisa ser congelado antes do primeiro rótulo;
- [x] SQL direto não pode colocar um mesmo registro em partições diferentes;
- [x] operação exige parâmetros metodológicos explícitos;
- [ ] lint, PostgreSQL 16, suíte completa e OpenAPI verdes no Railway CI Sandbox após a operação final;
- [ ] merge/promoção condicionados ao GitHub Actions oficial.

## O que F1-15 não prova

F1-15 não prova independência por **identidade verdadeira** antes do ground truth, nem produz qualquer resultado científico. Ele não mede:

- precisão;
- recall;
- blocking recall;
- concordância/Kappa;
- qualidade dos rótulos;
- parâmetros `m/u`;
- thresholds.

Seu papel é impedir uma classe observável de vazamento experimental e congelar o split antes que os resultados humanos possam influenciá-lo.
