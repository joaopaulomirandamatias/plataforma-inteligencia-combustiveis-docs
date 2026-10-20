# F1-10 — Ponte da fila de candidatos para a amostra cega

## Objetivo

Conectar a saída auditável da F1-09 à amostragem F1-08 sem permitir que metadados do classificador contaminem a revisão humana.

```text
F1-09 candidato_ligacao
        ↓
validar envelope interno
        ↓
extrair somente revisao.campos
        ↓
ItemRevisao interno + estratos
        ↓
amostragem estratificada F1-08b
        ↓
codebook cego F1-08a-v2
        ↓
pacote do revisor
```

A ponte não decide identidade e não usa o rótulo histórico F1-01 como verdade de referência.

## Candidatos elegíveis

Por padrão, somente candidatos sem decisão e pertencentes a um dos contratos
F1-09 reconhecidos:

- `blocking-similaridade-f1-09` ↔ `f1-09-v1`;
- `blocking-similaridade-f1-09-f02-contexto-v1` ↔
  `f1-09-f02-contexto-v1`;
- **sem decisão em `identidade.decisao_ligacao`**.

Método e schema formam um par fechado: misturá-los ou apresentar um método
desconhecido falha alto. A inclusão do contrato F02 é aditiva e não altera nem
regrava candidatos F03 do contrato-base.

> O suporte ao par F02 contextual é experimental. O F1-12 v2 já fecha os gates
> estruturais de manifesto homogêneo, proveniências GEO e digest do envelope,
> mas a geração produtiva de pacote continua bloqueada até o dry-run integral
> das 801 pendências descrito no
> [F1-09](f1-09-pipeline-candidatos.md#gate-das-801-pendências-f02-de-maio2026).

A exclusão da decisão F1-01 evita que a nova avaliação independente reutilize, por padrão, pares já tratados por um fluxo humano anterior. A leitura com `somente_pendentes=false` existe para auditoria, não como padrão de desenho experimental.

## Verificação de coerência

Antes de converter um candidato, a ponte exige que banco e envelope concordem em:

- `pontuacao_escala`;
- `pontuacao_valor`;
- `versao_modelo`;
- `fonte_a` / `fonte_b` de cada campo factual.

Divergência faz o processo falhar. O sistema não escolhe qual versão “parece mais correta”.

## O que vira evidência de revisão

Somente:

```text
evidencias.revisao.campos[]
```

Cada campo contém:

- nome;
- valor A/B;
- fonte A/B;
- localizador A/B.

Não são convertidos para `EvidenciaRevisao`:

- pontuação;
- peso log₂;
- contribuição Fellegi–Sunter;
- motivo de blocking;
- estados de similaridade;
- versão do modelo;
- threshold/destino.

Esses elementos continuam no artefato interno para auditoria e análise posterior.

No contrato contextual F02, `revisao.campos` recebe apenas uma projeção factual
para a revisão humana:

- contagens de cobertura geográfica e razões de presença/ausência;
- um resumo por comparação F01×F02, somente quando ambos os lados possuem
  ponto válido, com coordenadas, tipo, fonte, hash e distância;
- um resumo das datas cadastrais F01, da data de coleta F02 e das razões
  temporais.

Essa projeção **não é o envelope geoespacial completo**. Um ponto existente em
apenas um lado não vira campo de comparação. Também não atravessam para o
pacote cego o localizador próprio do ponto GEO, `localizador_vinculo`, as três
datas de cada ponto (`validade_inicio`, `coletado_em`, `observado_em`) nem a
estrutura bruta de `contexto_f02`. Os localizadores A/B de cada campo da revisão
continuam sendo os localizadores factuais dos registros F01/F02 comparados.

O contexto completo permanece no envelope interno, participa de
`evidencias_sha256`/`populacao_sha256` e fica disponível para auditoria. Score,
threshold e destino sugerido continuam proibidos no pacote humano. Para as 801
pendências, o runtime F02 recusa modelo explícito e exige `sem_modelo` com valor
nulo antes de produzir a população experimental.

## Estratificação interna

A ponte cria estratos internos determinísticos a partir de informação metodológica, sem inventar faixas numéricas de score:

- par de fontes;
- escala de pontuação;
- famílias de blocking;
- combinação fonte × famílias de blocking como estrato primário.

Exemplo:

```text
fontes:F01xF03|blocking:cnpj_raiz+nome_tokens
```

Não são criados rótulos arbitrários como `score_alto`/`score_baixo` nesta etapa. Se o protocolo futuro usar faixas de score, os limites precisam ser definidos e versionados antes de abrir a amostra.

## Gate duplo de blindagem

A geração do pacote final exige duas condições:

1. versão do codebook explicitamente reconhecida como sem estratos (`f1-08a-v2` inicialmente);
2. inspeção estrutural do artefato depois de gerado.

A inspeção recusa o pacote se encontrar:

- chaves `estratos`, `estrato_primario` ou `referencia_interna`;
- qualquer valor de estrato interno selecionado para os candidatos.

Portanto, apenas renomear um codebook inseguro para “v2” não libera o pacote.

## Dependências de merge

A implementação F1-10 fica em PR encadeada sobre a F1-09 para manter o diff isolado.

Ordem necessária:

1. validar/mesclar PR #4 — F1-09;
2. validar/mesclar PR #5 — codebook `f1-08a-v2`;
3. rebase/retarget da F1-10 para `main` já contendo as duas dependências;
4. CI completo;
5. somente então liberar geração fila→pacote.

Enquanto a PR #5 não estiver integrada, a função de geração termina com erro explícito de codebook inseguro. A conversão fila→`ItemRevisao` pode ser testada isoladamente.

## Critérios de aceite

- [ ] somente candidatos de contratos F1-09 reconhecidos entram por padrão;
- [ ] método/schema incompatíveis ou desconhecidos falham alto;
- [ ] candidatos com decisão F1-01 ficam fora por padrão;
- [ ] banco/envelope divergentes falham alto;
- [ ] fonte do campo factual precisa corresponder ao par da fila;
- [ ] pontuação e blocking não entram nas evidências do revisor;
- [ ] estratos permanecem internos;
- [ ] codebook v1 é bloqueado;
- [ ] inspeção estrutural detecta vazamento mesmo com versão nominalmente segura;
- [ ] quotas continuam a cargo da F1-08b e falham se insuficientes;
- [ ] CI PostgreSQL 16 + suíte + contrato verdes antes de merge;
- [ ] nenhum efeito sobre `posto_id`, fatos ou clusters.
