# Cofre de Identidade

Implementação do [ADR-004](../arquitetura/adr/adr-004-cofre-de-identidade.md): o único componente do sistema autorizado a conter CPF completo. Zona 2 do [C4 contexto](../arquitetura/c4/contexto.md) — segregação **física**, não lógica.

## Por que existe

O CPF vem mascarado (`***XXXXXX**`) na base pública da Receita, por decisão deliberada do controlador. Vínculos por sócio PF (T3) são portanto probabilísticos, e homônimo gera grupo societário falso — que gera fiscalização indevida. Desambiguar exige o dado real em algum ponto; o cofre existe para que esse ponto seja **um só**, mínimo, cifrado e auditado.

## Arquitetura

```
┌─ ZONA 2 ─────────────────────────────────────────────────┐
│  Postgres dedicado · rede segregada · sem rota de saída   │
│                                                           │
│  cpf_cifrado      ← envelope encryption (DEK por registro,│
│                     KEK no KMS)                           │
│  pessoa_id        ← HMAC-SHA256(sal_do_cofre, CPF)        │
│  meta_resolucao   ← rota (R1/R2/R3), data, instrumento    │
│  log_finalidade   ← ator, papel, caso, justificativa      │
└──────────────────┬────────────────────────────────────────┘
                   │  única saída: pessoa_id
                   ▼
              ZONA 1 (base analítica — nunca vê CPF)
```

**Propriedade central:** o sal do HMAC nunca sai do cofre. Vazamento completo da base analítica não expõe CPF **por construção** — `pessoa_id` não é reversível sem o sal.

## O que o cofre contém — e o que é proibido de conter

| Contém | Proibido |
|---|---|
| CPF cifrado | Qualquer dado de negócio (fatos, scores, casos) |
| `pessoa_id` e sal | Nome além do necessário à desambiguação |
| Metadados da resolução (rota, instrumento legal, data) | Cópia de documento além do previsto no instrumento |
| Log de finalidade de cada consulta | Qualquer API de leitura em lote sem controle duplo |

## Fluxos de resolução

### Emissão de `pessoa_id` (ingestão)
CPF mascarado + nome geram **cluster candidato** com score (raridade do nome, corroboração T4, coerência temporal). Sem resolução: o candidato circula na zona 1 com `pessoa_id` provisório marcado como não-confirmado — e o [context map](../dominio/context-map.md) exige que aresta T3 carregue exatamente essa confiança.

### R1 — o órgão confirma *(rota recomendada da v1)*
1. Plataforma monta o pacote: cluster candidato + evidências (nome, CPF parcial, empresas, coerências).
2. Órgão confirma/refuta com seus meios legais (convênio Receita próprio).
3. Resposta (confirmado/refutado + CPF quando o instrumento permitir) entra pelo fluxo do cofre; `pessoa_id` definitivo é emitido; evento de revisão atualiza as arestas.
A plataforma **nunca toca sigilo fiscal** — a etapa sensível fica com quem tem competência legal.

### R2 — convênio próprio
Igual ao R1 com consulta direta pela plataforma, **somente** se o instrumento jurídico o contemplar expressamente. Pré-condições: RIPD atualizado, base legal escrita, revisão do DPO.

### R3 — requisição em caso concreto
Resolução pontual dentro de procedimento administrativo/judicial identificado. O `caso_id` do procedimento é obrigatório no log de finalidade.

### Vedado — sem exceção
Serviços de "consulta CPF" de mercado, bases vazadas, e **reconstrução técnica dos dígitos mascarados**. A viabilidade técnica da reconstrução é conhecida e irrelevante: contorná-la é tratamento incompatível com a finalidade (LGPD) e destrói a credibilidade institucional que torna a plataforma útil. Não existe rota R4.

## Controle de acesso

- mTLS obrigatório; credenciais de curta duração; **nenhuma** credencial de aplicação da zona 1 alcança o cofre.
- Finalidade é campo obrigatório de toda consulta — sem finalidade, sem resposta.
- Operação em lote (export, migração) exige **controle duplo** (duas pessoas, papéis distintos, registrado).
- Quem administra o cofre não consulta identidades (segregação de função — mesma regra da matriz IAM).

## Gestão de chaves

| Chave | Rotação | Observação |
|---|---|---|
| KEK (KMS) | Anual + saída de qualquer operador | Padrão envelope: re-cifra DEKs, não os dados |
| DEK (por registro) | Na re-cifragem | — |
| **Sal do HMAC** | **Não rotaciona** | Rotacionar mudaria todo `pessoa_id` do sistema. Comprometimento do sal = incidente maior com plano próprio: re-pseudonimização completa (evento de identidade em massa, versionado) |

## Falhas e degradação

| Cenário | Efeito | Resposta |
|---|---|---|
| Cofre indisponível | Degrada **apenas** a desambiguação de homônimos — ingestão, análise e portais seguem | Fila de resolução acumula; nada bloqueia |
| Comprometimento suspeito | — | Rotação de KEK, verificação da trilha, comunicação conforme RIPD; a zona 1 permanece pseudônima |
| Corrente de auditoria do cofre quebrada | Incidente de segurança maior | Runbook próprio (`operacao/runbooks/`) |

## Auditoria

Toda consulta grava na [trilha de auditoria](trilha-de-auditoria.md) com ator, papel, finalidade e resultado (sem o CPF). O log de finalidade do cofre é espelhado na corrente central — o auditor verifica o cofre **sem entrar nele**.
