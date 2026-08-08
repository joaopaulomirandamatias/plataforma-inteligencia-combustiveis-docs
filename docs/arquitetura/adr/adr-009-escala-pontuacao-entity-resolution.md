# ADR-009 — Escala explícita de pontuação no Entity Resolution

**Status:** aceito  
**Data:** 2026-08-08

## Contexto

A fila F1-01 nasceu antes do classificador probabilístico e registra `score` limitado ao intervalo `[0,1]`. A F1-04 passou a implementar Fellegi–Sunter de forma correta e explicável, produzindo **peso de evidência em `log2(m/u)`**. Esse peso é um número real não limitado a `[0,1]` e pode ser negativo.

Converter implicitamente esse peso para `[0,1]` por sigmoid, min-max ou outra transformação produziria um número com aparência de probabilidade sem que exista calibração empírica que sustente essa semântica. Similaridade, peso de evidência e probabilidade são grandezas distintas.

A F1-05 implementa a mecânica de calibração, mas parâmetros e limiares de produção continuam dependentes da F1-08 e de rótulos humanos independentes.

## Decisão

Toda pontuação de Entity Resolution passa a declarar **valor + escala** explicitamente.

Escalas reconhecidas inicialmente:

- `legado_score_01` — compatibilidade com a F1-01 existente; valor histórico em `[0,1]` sem nova interpretação;
- `similaridade_01` — similaridade determinística em `[0,1]`; não significa probabilidade;
- `peso_log2` — peso de evidência Fellegi–Sunter em `log2(m/u)`, número real finito;
- `probabilidade_01` — probabilidade calibrada em `[0,1]`; só pode ser usada quando houver artefato de calibração/versionamento que justifique a semântica;
- `sem_modelo` — candidato criado para revisão sem pontuação de classificador.

Não existe conversão implícita entre escalas.

## Persistência

A migração de evolução deve ser **aditiva e compatível com dados já publicados**:

1. preservar a coluna histórica `score` e seu conteúdo;
2. permitir que novos candidatos não dependam dela;
3. adicionar campos canônicos de escala/valor para F1-09+;
4. dados históricos passam a ser interpretados explicitamente como `legado_score_01`;
5. novas restrições do banco validam a coerência entre escala e valor;
6. `NaN` e infinito não são pontuações válidas.

A coluna histórica não será reinterpretada retroativamente como probabilidade.

## Pipeline

O pipeline executável F1-09 pode produzir candidato em duas modalidades:

- sem modelo estatístico: vetor de similaridade + motivos de blocking + proveniência, escala `sem_modelo`;
- com um `ModeloFellegiSunter` explicitamente versionado: as mesmas evidências + contribuições por campo, escala `peso_log2`.

O pipeline **não** decide `aceitar`/`rejeitar`, não aplica limiares de produção e não remapeia identidade. Seu destino é a fila de candidatos/revisão.

## Evidência para revisão humana

O JSON `evidencias` da fila passa a usar um envelope versionado para novos candidatos. Ele deve separar:

- `blocking`: motivos que fizeram o par ser comparado;
- `similaridade`: vetor e estados discretizados;
- `pontuacao`: escala, versão do modelo e contribuições, quando existirem;
- `revisao`: fatos que podem ser mostrados ao revisor, com `fonte` e `localizador` de cada lado.

`score`, peso e destino automático não são exportados para o pacote cego F1-08a.

## Proveniência

`RepresentacaoIdentidade` é uma projeção comparável e não contém, por si só, o localizador da evidência original. O pipeline deve receber um envelope enriquecido com proveniência; ele não pode fabricar localizadores.

## Consequências

### Positivas

- elimina a falsa equivalência entre peso log₂ e probabilidade;
- permite conectar F1-04 à F1-01 sem adulterar semântica;
- mantém compatibilidade com candidatos históricos;
- torna experimentos e calibração reproduzíveis;
- prepara o pacote cego da F1-08 com proveniência estruturada.

### Custos

- a fila terá temporariamente coluna histórica e representação canônica lado a lado;
- consumidores internos precisam preferir os campos canônicos em novas implementações;
- `probabilidade_01` permanecerá indisponível até existir calibração empírica válida.

## Invariantes

- peso `log2` nunca é chamado de probabilidade;
- ausência de modelo nunca recebe score fictício;
- candidato não altera `posto_id`, fatos ou clusters;
- escala e valor são parte da identidade semântica do resultado do modelo;
- rótulos humanos continuam independentes da pontuação mostrada internamente.
