# F1-09 — Pipeline executável de candidatos de Entity Resolution

## Objetivo

Fechar a lacuna entre os componentes já implementados da F1 e a fila auditável de revisão:

```text
representação normalizada
        ↓
blocking mensurável
        ↓
vetor de similaridade
        ↓
Fellegi–Sunter opcional
        ↓
fila candidato_ligacao
        ↓
revisão F1-08
```

O pipeline **termina na fila**. Ele não contém threshold, auto-match, auto-reject, merge de cluster, alteração de `posto_id` ou remapeamento de fatos.

## Escala de pontuação

A F1-01 original criou `score` limitado a `[0,1]`. Isso não comporta o peso Fellegi–Sunter `log2(m/u)`. A decisão normativa está no ADR-009.

A migração 013, em validação, preserva o legado e adiciona:

- `pontuacao_escala`;
- `pontuacao_valor`;
- `calibracao_id`.

Escalas:

- `legado_score_01`;
- `similaridade_01`;
- `peso_log2`;
- `probabilidade_01`;
- `sem_modelo`.

`probabilidade_01` exige `calibracao_id` no domínio e no PostgreSQL. Peso log₂ nunca sofre sigmoid/min-max implícito para parecer probabilidade.

## Envelope de entrada

`RepresentacaoIdentidade` contém apenas a projeção comparável. Para revisão humana isso não basta, pois a evidência precisa ser citável.

A F1-09 usa `RegistroComparavel`:

- `representacao`: projeção F1-02;
- `localizador`: origem factual verificável;
- `campos_revisao`: valores factuais que podem ser exibidos posteriormente.

Localizador é obrigatório. O pipeline não fabrica proveniência.

## Envelope de evidências

Novos candidatos F1-09 gravam JSON versionado `f1-09-v1` com quatro blocos:

1. `normalizacao` — versão de normalização de cada lado;
2. `blocking` — motivos pelos quais o par foi comparado;
3. `similaridade` — vetor e estados discretizados;
4. `pontuacao` — escala, valor, versão do modelo e contribuições quando houver;
5. `revisao` — campos factuais com fonte e localizador de A/B.

Esse envelope é **interno**. Score/peso, motivo de blocking e estratos não devem ser enviados automaticamente ao revisor. O ADR-010 determina que estratos de amostragem ficam fora do pacote cego `f1-08a-v2`.

## Modo sem modelo

Sem parâmetros Fellegi–Sunter validados, o pipeline ainda pode produzir pares auditáveis:

```text
pontuacao_escala = sem_modelo
pontuacao_valor  = NULL
```

Isso permite construir a primeira amostra humana sem inventar parâmetros `m/u` ou probabilidade.

## Modo Fellegi–Sunter

Quando um `ModeloFellegiSunter` explicitamente versionado é fornecido:

```text
pontuacao_escala = peso_log2
pontuacao_valor  = soma log2(m/u)
```

As contribuições por campo/estado ficam no envelope interno. Parâmetro ausente faz a execução falhar antes do INSERT.

## Integração com F02/F03

### Por que reler a zona bruta

F02 e F03 armazenam em `ingestao.pendencia_vinculo` apenas a chave tentada, motivo, contagem e um localizador de exemplo. Isso é suficiente para operar o vínculo determinístico, mas não preserva no registro agregado todos os campos de nome/endereço necessários para Entity Resolution.

Os bytes originais permanecem na zona bruta imutável. A F1-09 usa essa fonte como evidência, sem alterar os fatos F02/F03.

### Recorte inicial

A implementação em validação aceita somente:

```text
motivo = cnpj_sem_posto
fonte ∈ {F02, F03}
```

O fluxo recebe um `carga_id` explícito:

1. lê `ingestao.carga`;
2. seleciona as chaves `cnpj_sem_posto` da mesma carga;
3. abre `caminho_bruto`;
4. confere manifesto e SHA-256;
5. usa o **parser original do conector** para determinar quais linhas eram válidas;
6. relê somente essas linhas para recuperar nome/endereço e demais evidências;
7. aplica validação de dígitos verificadores da F1-02;
8. compara as observações contra F01.

CNPJ de 14 dígitos que passa pelo parser antigo mas falha no DV da F1 é contabilizado e não usado como identificador forte.

## Chave da observação pendente

Uma mesma carga pode repetir o posto em vários produtos/ensaios. Para não gerar uma entidade por linha nem colapsar diferenças factuais em silêncio, a chave interna da observação usa:

```text
cnpj:<cnpj>:obs:<sha256-da-identidade-factual>
```

Linhas com identidade factual idêntica colapsam; alteração factual produz outra observação. Essa chave serve apenas ao pipeline/fila e não cria `posto_id` nem alias.

## F01 bitemporal

O universo F01 é consultado com dois cortes obrigatórios:

- `validade_em` — quando o dado deveria valer no mundo;
- `transacao_em` — o que a plataforma já sabia naquele instante de conhecimento.

Nenhum `now()` escondido define o resultado da comparação.

## Casos ainda fora do escopo

### `cnpj_ausente`

Pode exigir matching apenas por nome/endereço/geografia. Ainda não existe uma chave de entidade publicada pela fonte que permita agrupar observações sem risco de sobreagrupar.

### `cnpj_invalido`

Pode representar erro recuperável, mas a reconstrução precisa ser evidenciada. O pipeline não corrige dígitos automaticamente.

Esses dois motivos serão tratados em card posterior com chave de observação e política próprias.

## Critérios de aceite da PR #4

- [ ] migração 013 passa PostgreSQL 16 real;
- [ ] cliente F1-01 antigo continua conseguindo inserir `score` legado;
- [ ] `similaridade_01`/`probabilidade_01` não aceitam valor NULL por efeito de `CHECK UNKNOWN`;
- [ ] `peso_log2` aceita real finito negativo/positivo;
- [ ] NaN/infinito são rejeitados;
- [ ] probabilidade exige calibração explícita;
- [ ] pipeline sem modelo grava NULL, não score fictício;
- [ ] modelo incompleto falha antes de enfileirar;
- [ ] evidências de revisão preservam valores, fontes e localizadores;
- [ ] F02/F03 são relidos da zona bruta com hash conferido;
- [ ] teste integração F01→F03 pendente→fila não cria alias F03 nem posto novo;
- [ ] lint, suíte completa e contrato OpenAPI verdes;
- [ ] nenhum merge enquanto a Issue #2 de billing impedir o CI.

## Dependência de blindagem

A PR #4 não exporta pacote para revisor. Quando a ponte fila→F1-08 for implementada, ela deverá usar `f1-08a-v2` (PR #5) ou versão posterior, em que estratos internos não aparecem no artefato cego.
