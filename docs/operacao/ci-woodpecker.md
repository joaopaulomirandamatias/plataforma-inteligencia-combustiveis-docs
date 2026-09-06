# CI da PIC com Woodpecker

Estado desta alteração: configuração candidata, sem corte de produção. Os workflows GitHub permanecem ativos até a validação independente e a confirmação dos requisitos abaixo. Nenhum deploy Railway, desativação de Actions, ativação de repositório ou alteração de proteção de branch é realizado por este documento.

O servidor Woodpecker 3.18.0 recebe eventos do GitHub. Agentes Linux/Docker executam os testes em redes e volumes temporários. As aplicações e os bancos de produção continuam no Railway. Os bancos dos testes são criados somente no ambiente descartável do job.

## Mapa de migração

| Repositório | Workflow anterior | Configuração candidata | Verificações e promoção preservadas |
|---|---|---|---|
| `plataforma-inteligencia-combustiveis` | `.github/workflows/ci.yml`: `validar`, `promover` | `.woodpecker/ci.yaml` | Python 3.13, uv 0.11.32, PostgreSQL 16, ruff, pytest JUnit, zero skips/zero coleta, teste explícito de conformidade; contrato pelo `.github/contrato.sha`, léxico canônico em main; promoção da main validada para deploy |
| `plataforma-inteligencia-combustiveis-web` | `.github/workflows/ci.yml`: `validar`, `promover` | `.woodpecker/ci.yaml` | Node 22, pnpm 9.15.9, lockfile congelado, testes, paridade do léxico canônico, auditoria de produção, build, pente no payload RSC; promoção da main validada para deploy |
| `plataforma-inteligencia-combustiveis-gestao` | `.github/workflows/ci.yml`: `backend` | `.woodpecker/backend.yaml` | Python 3.12, uv 0.11.32, lock/sync, PostgreSQL 16 e sete bancos isolados para dados, migração, projeção, IAM, convites e fronteiras; ruff/check+format, pytest JUnit sem skips, pip-audit de produção, compileall |
| `plataforma-inteligencia-combustiveis-gestao` | `.github/workflows/ci.yml`: `console` | `.woodpecker/console.yaml` | Node 24, npm ci sem scripts, typecheck, testes, build, npm audit de produção a partir de moderate; configuração fictícia de OIDC |
| `plataforma-inteligencia-combustiveis-gestao` | `.github/workflows/ci.yml`: `image` | `.woodpecker/image.yaml` | Imagem uma vez por execução, ID imutável, UID/GID 10001, comando e rótulos OCI, ausência de dependências dev, quatro entrypoints, migração e API com PostgreSQL descartável, saúde e OpenAPI 404; SBOM CycloneDX, Trivy 0.70.0, proveniência e política HIGH/CRITICAL com exceções estritas |
| `plataforma-inteligencia-combustiveis-docs` | `.github/workflows/contrato-openapi.yml`: `validar` | `.woodpecker/contrato-openapi.yaml` | Node 24.18.0, npm ci sem scripts, `npm run check`: regressões OpenAPI, léxico e lint do contrato |

## Eventos e identidade do código

Backend, web e docs validam pushes para main e PRs cuja base seja main. Gestão conserva PRs para qualquer base e pushes para main. Backend e web também aceitam execução manual, como os antigos `workflow_dispatch`. Não há cron novo.

No disparo manual, `CONTRACT_SHA` (backend) e `DOCS_SHA` (web) substituem os inputs anteriores e aceitam apenas SHA Git completo de 40 caracteres hexadecimais. Forneça-os nas variáveis da execução manual; pela CLI Woodpecker, use `pipeline create --var CONTRACT_SHA=<sha>` ou `--var DOCS_SHA=<sha>`, conforme o repositório. Sem override, permanecem respectivamente o contrato fixado e o léxico atual de main. Execução manual não promove deploy.

O plugin de clone 2.10.0 realiza a integração do PR com a branch de destino; conflito reprova. O script verifica que o SHA do evento é ancestral do checkout de integração e registra os dois SHAs. Em push/manual, exige igualdade exata de HEAD com o SHA do evento. O commit de merge temporário do Woodpecker pode ter SHA diferente do merge sintético do GitHub; o que se valida é a integração com a base. A proveniência da imagem usa o SHA efetivamente construído.

Os nomes esperados dos workflows são `ci`, `contrato-openapi`, `backend`, `console` e `image`. Os contextos completos de status dependem da configuração real do servidor; capture-os no primeiro PR antes de substituir verificações obrigatórias. Não invente nomes em rulesets.

## Executor e limites

Todos os workflows exigem `backend=docker` e `platform=linux/amd64`. As suítes comuns exigem `pool=phn-test`, destinado ao daemon Docker rootless separado do Docker de produção. A configuração inicial prevista limita o daemon dos jobs a 6 GiB e 1,5 CPU no total, mais 256 MiB para o agente, com uma execução por vez; a aplicação desses limites precisa ser confirmada no servidor. A imagem da Gestão exige `ci-docker-build=true` e aprovação de repositório confiável para serviços privilegiados. O executor comum mantém `ci-docker-build=false`; não atribua `true` a ele. DIND privilegiado continua tendo risco de acesso ao kernel do host: ele deve executar em máquina dedicada a builds ou VM descartável, sem acesso aos serviços ou credenciais de produção.

O daemon `docker:28.5.1-dind` pertence à execução, não monta socket, volume ou porta do host. O serviço PostgreSQL da prova de imagem roda dentro desse daemon; `--network host` nesse script significa a rede interna do DIND, não a rede do servidor Coolify. O daemon é destruído quando o workflow termina. A porta 2375 sem TLS fica apenas na rede privada da execução; não publique essa porta nem conecte a rede do job às redes de produção.

Configure concorrência inicial do agente em 1; meça memória e espaço antes de ampliar. Configure timeout do repositório em 30 minutos para conter instalação e upload: os scripts mantêm limites de 20 minutos para backend/web/imagem, 15 minutos para console, 10 minutos para docs e 5 minutos para promoção. Configure cancelamento de execuções obsoletas para reproduzir `cancel-in-progress`; não cancele um upload em andamento durante o corte.

## Credenciais e artefatos

| Secret Woodpecker | Repositório/evento | Requisito |
|---|---|---|
| `github_deploy_token` | Backend e web, somente push | Token próprio por repositório com Contents:write; nunca disponível em PR/manual nem variável global. A branch main continua protegida. A promoção captura o lease de deploy antes de conferir a main atual e só escreve deploy depois das verificações. Uma promoção concorrente invalida esse lease. |
| `ci_artifacts_endpoint` | Gestão, somente push até revisão do uploader | Endpoint HTTPS do armazenamento S3 compatível privado, restrito ao plugin `woodpeckerci/plugin-s3:1.3.2`. |
| `ci_artifacts_bucket` | Gestão, somente push até revisão do uploader | Bucket privado com expiração de 30 dias e política de leitura controlada. |
| `ci_artifacts_access_key`, `ci_artifacts_secret_key` | Gestão, somente push até revisão do uploader | Credenciais limitadas ao prefixo PIC Gestão, restritas ao plugin S3 exato; nunca disponíveis aos scripts de build, nem com acesso a outros buckets. Não liberar estes secrets a YAML controlado por PR. |

Não copiar credenciais de banco, owner, OIDC, Railway ou Coolify de produção. As senhas literais nos workflows são exclusivamente das fixtures descartáveis, iguais às anteriores. O checkout de docs e léxico é público e dispensa PAT.

O arquivo compactado `supply-chain.tar.gz` contém a mesma allowlist de oito evidências do job anterior e seu SHA-256 é registrado no log. O target configurado é `pic-gestao/<sha-evento>/<pipeline>/<inicio>/`; o plugin acrescenta `/` ao início da chave, que deve ser considerado na política real do bucket. O arquivo de proveniência identifica o SHA testado. Reruns usam o início da execução para separar as tentativas. O upload usa ACL privada e `overwrite: false`, mas essa opção faz HEAD seguido de PUT e não garante escrita atômica nem imutabilidade. A credencial precisa poder consultar a existência dos objetos no seu prefixo; versionamento, retenção e prevenção de sobrescrita exigem política comprovada do armazenamento. O upload acontece antes do gate de vulnerabilidades para conservar a evidência de reprovações HIGH/CRITICAL. A vida útil de 30 dias deve ser configurada e comprovada no bucket; YAML não configura lifecycle de S3.

A preservação dos artefatos de PR permanece bloqueada. A revisão de Segurança identificou que a restrição por imagem de plugin não impede um PR de mudar os parâmetros do uploader: pode trocar o endpoint e mapear a chave secreta para o identificador de acesso, expondo-a na autenticação da requisição. Não liberar secrets S3 a esses PRs. Antes do corte, implementar uploader com configuração fora do controle do PR e credencial efêmera de escopo estrito, com revisão independente. Enquanto isso, `image` de PR deve falhar sem credenciais ou ficar sem executor; não remover upload nem tornar o gate opcional. A restrição de imagem é defesa adicional, não prova de que um YAML não confiável pode usar secrets com segurança.

Fixar os digests verificados de `aquasec/trivy:0.70.0` e `woodpeckerci/plugin-s3:1.3.2` é requisito antes do corte: as tags da configuração candidata ainda são mutáveis, enquanto os Actions anteriores eram fixados por commit. Registrar os digests usados no run e conferir a correspondência com as versões esperadas.

O SBOM, limites de 50 MiB, freshness da base Trivy de até 48 horas, manifesto e política versionados, hashes e detector de padrões de credenciais continuam obrigatórios. A evidência permanece não assinada e não prova igualdade com imagem reconstruída pelo Railway.

## Corte e rollback

1. Revisão independente de QA e Segurança dos arquivos, conforme AGENTS.md da Gestão; conferir se main avançou desde a preparação e integrar mudanças.
2. Validar executor comum, executor de imagem dedicado e bucket privado/lifecycle; resolver o uploader de PR fora do controle do YAML não confiável, fixar os digests e cadastrar secrets com escopo e eventos da tabela.
3. Ativar os repositórios no Woodpecker e validar webhooks/status. Rodar os candidatos em PR; não enviar token de promoção em PR.
4. Provar as suítes e a captura dos artefatos em sucesso e em gate de vulnerabilidade reprovado. Conferir cancelamento, timeout, descarte de bancos e indisponibilidade de secrets para comandos de PR.
5. Integrar a configuração aprovada, executar main e verificar que somente o SHA aprovado promove deploy. Backend/web mantêm o mecanismo de branch deploy existente; Gestão/docs não recebem um deploy automático novo nesta migração.
6. Revisar Railway: não basta push em main nem adicionar um webhook para garantir gate. Conferir que cada serviço continua no gatilho/branch acordado e registrar os status obrigatórios reais. A ordem Migrator COMPLETED antes de API/worker continua exigida pelo runbook operacional.
7. Somente após essas evidências, substituir as verificações obrigatórias dos PRs e desativar os workflows antigos com registro da data, responsável e último run. Deixar os arquivos antigos preservados para rollback; não remover proteção sem substituição equivalente.

Rollback: interromper a promoção Woodpecker, reabilitar os workflows antigos e restaurar seus contextos obrigatórios. Não executar ambos os promotores simultaneamente. Falha de CI não implica rollback ou migração de banco de produção automático.

## Evidências desta preparação

Foram comparados os quatro workflows da main, preservados seus comandos de validação e conferidos os YAMLs com o JSON Schema oficial do Woodpecker 3.18.0. Os scripts são validados por Bash; cenários locais conferem rejeição de checkout incorreto, evento indevido de promoção e overrides inválidos. A revisão independente de Segurança identificou e orientou a correção da ordem do lease de deploy e bloqueou a liberação de secrets S3 aos PRs. A regressão de promoção usa repositório bare local e reproduz uma promoção concorrente entre o fetch e o push: o deploy mais novo é preservado e o lease antigo reprova. Rode `python3 .ci/woodpecker/test-promote.py` no backend ou web; não exige token nem conexão GitHub. As suítes completas, DIND, S3, status, PRs e deploy ainda exigem prova no executor: validação estática não substitui essa prova.

Referências: [sintaxe 3.18.0](https://github.com/woodpecker-ci/woodpecker/blob/v3.18.0/docs/docs/20-usage/20-workflow-syntax.md), [secrets](https://github.com/woodpecker-ci/woodpecker/blob/v3.18.0/docs/docs/20-usage/40-secrets.md), [serviços](https://github.com/woodpecker-ci/woodpecker/blob/v3.18.0/docs/docs/20-usage/60-services.md), [plugin git](https://github.com/woodpecker-ci/plugin-git/blob/main/docs.md), [plugin S3](https://github.com/woodpecker-ci/plugin-s3/tree/v1.3.2).
