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

Por padrão, somente candidatos com:

- `metodo = blocking-similaridade-f1-09`;
- envelope `schema_versao = f1-09-v1`;
- **sem decisão em `identidade.decisao_ligacao`**.

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

- [ ] somente candidatos F1-09 entram por padrão;
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
