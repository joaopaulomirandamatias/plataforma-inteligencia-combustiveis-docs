# Migração do CI de documentação para Woodpecker

## Estado

**Candidata; corte não realizado.**

Este repositório ainda usa `.github/workflows/contrato-openapi.yml` como CI vigente. A configuração `.woodpecker/contrato-openapi.yaml` reproduz o gate em paralelo para validação. A presença do arquivo, um PR aberto ou uma validação estática não comprovam que o Woodpecker esteja operacional.

Nenhum GitHub Actions foi desativado, nenhuma credencial foi criada e nenhum deploy foi alterado nesta proposta.

## Paridade planejada

| Aspecto | GitHub Actions vigente | Woodpecker candidato |
|---|---|---|
| Eventos | push para `main`; PR com base `main` | push para `main`; PR com base `main` |
| Runtime | Node.js 24.18.0 | `node:24.18.0-bookworm` |
| Checkout | credenciais não persistidas | clone isolado; nenhuma credencial entregue ao step |
| Integridade | checkout compatível com o SHA do evento | igualdade em push; ancestralidade do SHA do PR no checkout integrado |
| Dependências | `npm ci --ignore-scripts --no-audit` | mesmo comando |
| Gate | `npm run check` | mesmo comando |
| Limite | job de 10 minutos | `timeout 10m` envolvendo instalação e gate |
| Permissões | `contents: read` | não usa secrets nem escreve no GitHub |

`npm run check` preserva:

1. testes de regressão do gate OpenAPI;
2. testes do léxico;
3. lint de `docs/api/openapi.yaml` com Redocly.

## Evidências necessárias antes do corte

Todos os itens abaixo são obrigatórios:

- repositório ativado no Woodpecker e webhook do GitHub confirmado;
- agente compatível com os labels `backend=docker`, `platform=linux/amd64` e `pool=phn-test`;
- pipeline do Woodpecker executado no SHA exato desta branch, com checkout, instalação, testes e lint aprovados;
- novo PR ou novo commit comprovando que o webhook dispara novamente;
- execução aprovada após merge em `main`;
- contexto real do status Woodpecker registrado e configurado como verificação obrigatória;
- cancelamento de pipelines anteriores habilitado para `push` e `pull_request`, preservando o comportamento `cancel-in-progress`;
- comparação dos logs e códigos de saída entre Actions e Woodpecker;
- teste negativo demonstrando que contrato ou léxico inválido reprova no Woodpecker;
- plano de rollback verificado.

Até essas evidências existirem, o estado deve ser reportado como **não migrado**.

## Corte seguro

1. Revisar e aprovar a configuração candidata.
2. Executar os cenários positivos e negativos no agente real.
3. Fazer merge mantendo o GitHub Actions ativo.
4. Confirmar uma execução Woodpecker bem-sucedida em `main`.
5. Tornar o contexto Woodpecker obrigatório sem remover antecipadamente a proteção existente.
6. Em alteração separada e auditável, desativar o workflow antigo.
7. Registrar data, responsável, SHA, links dos pipelines e critérios observados.

Não remover o arquivo do GitHub Actions no mesmo commit que introduz o candidato.

## Rollback

Se webhook, agente, imagem, npm, testes, lint ou publicação de status falhar após o corte:

1. reativar `.github/workflows/contrato-openapi.yml`;
2. restaurar seu contexto obrigatório;
3. remover temporariamente a obrigatoriedade do contexto Woodpecker;
4. manter logs e SHAs da falha para diagnóstico;
5. corrigir em uma nova branch candidata.

A falha deste CI de documentação não autoriza qualquer alteração automática em aplicação, banco de dados, Railway ou Coolify.

## Sobre propostas simultâneas

O PR #18 contém a preparação técnica reutilizada por esta branch. Este PR padronizado acrescenta este registro de migração. Apenas uma das propostas deve ser integrada; manter as duas abertas é útil para revisão, mas fazer merge das duas é redundante.
