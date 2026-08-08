# F1-08 — operação reproduzível da revisão humana

Este documento descreve a interface operacional da validação de Entity Resolution. Ele complementa `f1-08-validacao-entity-resolution.md`: a metodologia define **o que medir**; este contrato define **como transportar, revisar e registrar** a amostra sem revelar o score ao revisor nem perder a trilha técnica.

## Princípio de separação

Dois artefatos são gerados no mesmo instante e nunca devem ser confundidos:

1. **pacote cego do revisor** — pode ser entregue ao revisor; contém ID opaco, estratos e evidências factuais com proveniência, mas não contém referência interna, score, peso, limiar ou destino do modelo;
2. **manifesto interno de reconciliação** — fica sob controle da equipe; relaciona `item_id` opaco à referência técnica usada para persistir e reconciliar o resultado.

A existência do manifesto interno não autoriza acrescentar essas chaves ao pacote cego.

## Executável

A implementação em validação disponibiliza um executável separado do CLI F0:

```text
pic-er
```

Ele permanece separado de `pic` enquanto a F1 não fechar todos os gates de CI.

### 1. Gerar amostra

```bash
pic-er amostrar \
  --entrada candidatos.json \
  --pacote pacote-revisor.json \
  --interno manifesto-interno.json
```

`--pacote` e `--interno` precisam ser arquivos diferentes.

Entrada mínima:

```json
{
  "experimento_id": "er-2026-001",
  "manifesto_sha256": "<64 hex>",
  "seed": "seed-publicada-no-protocolo",
  "quotas": {
    "facil": 50,
    "dificil": 100
  },
  "candidatos": [
    {
      "referencia_interna": "candidato-tecnico-001",
      "fonte_a": "F01",
      "chave_a": "...",
      "fonte_b": "F03",
      "chave_b": "...",
      "estrato_primario": "dificil",
      "estratos": ["F01xF03", "dificil", "sem_identificador_forte"],
      "evidencias": [
        {
          "nome": "endereco",
          "valor_a": "...",
          "valor_b": "...",
          "fonte_a": "F01",
          "localizador_a": "...",
          "fonte_b": "F03",
          "localizador_b": "..."
        }
      ]
    }
  ]
}
```

A quota é exata. Se um estrato não tiver candidatos suficientes, o comando deve falhar; ele não reduz quota nem repõe com outro estrato em silêncio.

## 2. Registrar o experimento

O manifesto interno gerado na etapa anterior é persistido uma única vez de forma idempotente:

```bash
pic-er registrar --interno manifesto-interno.json
```

O banco registra:

- `experimento_id`;
- hash do manifesto;
- versão do codebook;
- seed da amostragem;
- `item_id` opaco;
- referência técnica interna;
- estrato primário e estratos adicionais.

Reutilizar o mesmo ID de experimento com manifesto/configuração diferente deve falhar.

## 3. Importar rótulos independentes

Cada revisor entrega um lote próprio:

```json
{
  "experimento_id": "er-2026-001",
  "revisor_id": "revisor-a",
  "rotulos": [
    {
      "item_id": "<uuid-opaco>",
      "rotulo": "MESMO_PONTO",
      "justificativa": "opcional"
    }
  ]
}
```

Importação:

```bash
pic-er importar-rotulos --entrada rotulos-revisor-a.json
```

Rótulos permitidos são somente:

- `MESMO_PONTO`;
- `PONTOS_DIFERENTES`;
- `INDETERMINADO`.

O mesmo revisor não pode reenviar/alterar o próprio rótulo. Correção futura precisa ser outro evento explicitamente modelado; nunca `UPDATE` silencioso.

## 4. Adjudicar somente divergências

Quando dois ou mais revisores divergem, a adjudicação é outro evento:

```json
{
  "experimento_id": "er-2026-001",
  "adjudicador_id": "adjudicador-a",
  "adjudicacoes": [
    {
      "item_id": "<uuid-opaco>",
      "rotulo_final": "INDETERMINADO",
      "justificativa": "evidência factual insuficiente para resolver a divergência"
    }
  ]
}
```

```bash
pic-er adjudicar --entrada adjudicacoes.json
```

A regra “adjudicação exige divergência humana prévia” existe em duas camadas:

1. domínio Python;
2. trigger no PostgreSQL.

Assim, INSERT direto não deve conseguir contornar a regra.

## 5. Exportar estado do experimento

```bash
pic-er status \
  --experimento er-2026-001 \
  --saida status-er-2026-001.json
```

Estados esperados:

- `SEM_REVISAO`;
- `UMA_REVISAO`;
- `CONCORDANTE`;
- `DIVERGENTE`;
- `ADJUDICADO`.

`DIVERGENTE` não recebe rótulo final automaticamente. `INDETERMINADO` continua sendo um resultado legítimo e não é convertido para `PONTOS_DIFERENTES`.

## Transação e falha

Os comandos de escrita usam uma transação por lote. Se qualquer item do lote falhar, a operação deve propagar o erro e a transação deve ser revertida pelo contexto da conexão. Não existe modo “best effort” silencioso para rótulos científicos.

## Dados e segurança

- pacote cego não contém score, pesos, thresholds nem destino do modelo;
- manifesto interno não é material de revisão externa;
- `revisor_id` e `adjudicador_id` são identificadores opacos; CPF/e-mail não são necessários;
- tabelas de experimento, item, rótulo e adjudicação são append-only para a aplicação;
- `UPDATE` e `DELETE` permanecem negados;
- nenhuma operação F1-08 altera fatos, `posto_id`, clusters ou `posto_chave_fonte`.

## Estado de implementação em 2026-08-08

- F1-08a: validada e em `deploy`;
- F1-08b: implementada em `main`, aguardando CI;
- F1-08c: migração 012 + domínio + barreira SQL implementados em `main`, aguardando CI;
- F1-08d: relatório de holdout isolado na PR #1, aguardando CI;
- F1-08e: CLI operacional isolada em branch/PR própria até os gates voltarem.

O GitHub Actions está temporariamente impedido de iniciar jobs por billing/spending limit da conta. Enquanto isso, `deploy` deve permanecer no último SHA verde e a migração 012 não deve ser aplicada manualmente em produção.
