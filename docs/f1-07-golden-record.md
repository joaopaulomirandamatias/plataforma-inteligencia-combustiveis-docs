# F1-07 — Golden record com proveniência campo a campo

## Princípio

O golden record é uma **projeção explicável** sobre um snapshot de cluster. Ele não corrige a fonte, não sobrescreve fatos, não move `posto_id` e não transforma divergência em consenso artificial.

Para cada campo exibido como “melhor valor disponível”, o sistema precisa conseguir responder:

1. qual valor foi escolhido;
2. de qual fonte veio;
3. qual localizador permite voltar ao byte/linha/documento de origem;
4. em que validade e tempo de transação esse valor estava disponível;
5. qual versão da política escolheu o valor;
6. quais valores concorrentes foram descartados e por quê.

Sem essas respostas, não existe golden record auditável — existe apenas uma cópia de dados com perda de proveniência.

---

## Entrada

A entrada é um **snapshot já resolvido da F1-06** e candidatos de campo obtidos somente de fatos associados aos `posto_id` membros daquele snapshot.

Cada candidato tem, no mínimo:

```text
campo
valor
fonte
localizador
posto_id_origem
validade_inicio
validade_fim
transacao_inicio
```

`valor = ausente` não participa da seleção. Valor vazio não ganha precedência sobre valor preenchido.

A camada nunca consulta registros que não pertençam ao snapshot de cluster escolhido no corte temporal solicitado.

---

## Política versionada

A seleção é configuração, não `if/else` espalhado no código.

Estrutura conceitual:

```text
PoliticaGoldenRecord
  versao
  campos[]
    nome
    precedencia_fontes[]
    criterio_temporal
    desempate
```

### Critérios temporais permitidos na v1

- `precedencia_depois_recencia`: primeiro escolhe a fonte de maior precedência disponível; dentro da mesma fonte usa a versão válida mais recente;
- `mais_recente`: ignora precedência de fonte e escolhe o fato válido mais recente;
- `fonte_exclusiva`: o campo só pode ser afirmado por uma determinada fonte; ausência permanece ausência.

Nenhum campo pode receber política desconhecida em runtime.

### Desempate obrigatório

Quando dois candidatos continuam empatados, a ordem final é determinística:

1. maior `transacao_inicio`;
2. `fonte` em ordem C;
3. `localizador` em ordem C;
4. `posto_id_origem` em ordem C.

O desempate não implica que a última chave seja semanticamente “melhor”; serve apenas para tornar reprocessamento reproduzível.

---

## Política inicial proposta

A tabela abaixo é **configuração inicial de engenharia**, não evidência de que todas as fontes já estejam ingeridas.

| Campo | Política v1 | Observação |
|---|---|---|
| `razao_social` | precedência F05 → F01 | Receita é autoridade cadastral da pessoa jurídica quando F05 estiver estruturada; até lá F01 é o disponível |
| `cnpj` | fonte exclusiva do vínculo empresarial vigente | nunca inferir CNPJ por similaridade textual |
| `endereco` | precedência F01 → F05 | F01 descreve o ponto autorizado; F05 serve como evidência complementar |
| `bairro` | precedência F01 → F05 | idem |
| `cep` | precedência F01 → F05 | somente valor normalizado/validado participa |
| `municipio` | precedência F01 → F05 | normalização territorial separada continua sendo F07 |
| `uf` | precedência F01 → F05 | idem |
| `bandeira` | mais recente entre fontes autorizadas | muda ao longo do tempo; não tratar como identidade estática |
| `autorizacao` | fonte exclusiva F01 | fato regulatório da ANP |

A inclusão real de F05 na seleção só ocorre quando o parser estruturado correspondente existir. O arquivamento bruto de F05 não autoriza inventar valores que ainda não foram extraídos.

---

## Saída

Para cada campo:

```text
CampoGolden
  campo
  valor
  fonte
  localizador
  posto_id_origem
  validade_inicio
  validade_fim
  transacao_inicio
  politica_versao
  regra_aplicada
  alternativas[]
```

`alternativas` preserva candidatos válidos que perderam a seleção. A UI pode ocultá-las por padrão, mas a API interna e a auditoria não podem descartá-las.

O registro agregado contém também:

```text
GoldenRecord
  cluster_id
  cluster_versao
  validade_em
  transacao_em
  politica_versao
  campos{}
  campos_sem_cobertura[]
```

`campos_sem_cobertura` diferencia “não há fato disponível” de “o sistema esqueceu de calcular o campo”.

---

## Regras de segurança semântica

1. **LLM não escolhe precedência.** Golden record é determinístico.
2. **Similaridade não vira valor.** Um nome parecido pode ajudar entity resolution, mas não autoriza copiar o nome de outro registro.
3. **Ausência permanece ausência.** Não completar CEP, CNPJ, endereço ou bandeira por adivinhação.
4. **Fonte original permanece consultável.** O golden record nunca substitui `fatos.*`.
5. **Política muda por versão.** Alterar precedência cria outra versão de política; resultados históricos podem ser reconstruídos com a versão anterior.
6. **Corte temporal é obrigatório.** O mesmo cluster pode produzir golden records diferentes para tempos do mundo/transação diferentes.

---

## Implementação proposta

### F1-07a — motor puro

- dataclasses de candidato, política e saída;
- seleção determinística por campo;
- alternativas preservadas;
- cobertura ausente explícita;
- testes sem banco para precedência, recência, empate e ausência.

### F1-07b — adaptador PostgreSQL

- recebe `cluster_id`, `validade_em`, `transacao_em`;
- usa F1-06 para obter membros do snapshot correto;
- consulta fatos permitidos por campo;
- transforma linhas em candidatos sem perder `fonte/localizador`;
- chama o motor puro;
- nenhum SQL de `UPDATE`/`DELETE`.

### F1-07c — exposição

Só depois do contrato interno ficar estável:

- endpoint interno/administrativo primeiro;
- contrato OpenAPI atualizado antes do endpoint público;
- ficha pública continua distinguindo fato, interpretação e ausência de cobertura.

---

## Critérios de aceite

- [ ] mesma entrada + mesma política + mesmo corte temporal produz saída idêntica;
- [ ] toda afirmação selecionada possui `fonte` e `localizador`;
- [ ] nenhum valor é criado quando não existe candidato;
- [ ] alternativas divergentes permanecem auditáveis;
- [ ] troca da ordem da entrada não muda o resultado;
- [ ] versão da política aparece em todos os resultados;
- [ ] mudança de política não altera fatos anteriores;
- [ ] consulta usa somente membros válidos do snapshot F1-06 no corte solicitado;
- [ ] F05 não participa como dado estruturado antes de seu parser existir;
- [ ] testes e lint verdes antes de promoção para `deploy`.
