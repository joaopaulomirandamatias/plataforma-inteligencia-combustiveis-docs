# RIPD — Relatório de Impacto à Proteção de Dados Pessoais

> [!IMPORTANT]
> **Status: RASCUNHO TÉCNICO.** Pré-preenchido com o desenho técnico do sistema; **não é parecer jurídico**. Itens marcados `[PENDENTE]` exigem decisão institucional (encarregado/DPO, jurídico, instrumento com o órgão parceiro) **antes da primeira ingestão de dados de sócios**.

Fundamento: LGPD, art. 5º XVII e art. 38. Escopo: tratamentos de dados pessoais da Plataforma de Inteligência de Combustíveis, v1.

## 1. Identificação

| Campo | Valor |
|---|---|
| Controlador | `[PENDENTE — definir: instituição/empresa responsável]` |
| Encarregado (DPO) | `[PENDENTE — nomear antes da ingestão de QSA]` |
| Operadores | `[PENDENTE — infraestrutura contratada, se houver]` |

## 2. Descrição dos tratamentos

| # | Tratamento | Dados | Titulares | Origem |
|---|---|---|---|---|
| T1 | Ingestão do QSA (Dados Públicos CNPJ) | Nome do sócio, CPF **mascarado**, qualificação, datas | Sócios de empresas do setor | Fonte pública (RFB) |
| T2 | Pseudonimização e grafo societário | `pessoa_id` (HMAC), arestas T1–T4 | Sócios | Derivado de T1 |
| T3 | Cofre de identidade — resolução R1/R2/R3 | CPF completo (cifrado), metadados da resolução | Sócios em desambiguação | Órgão parceiro / instrumento legal |
| T4 | Consulta por fiscais (grafo com PF, dossiês) | Nome + vínculos societários | Sócios | T2/T3, sob escopo e finalidade |
| T5 | Trilha de auditoria | Identificação de operadores/fiscais (ator) | Usuários internos e de órgãos | Operação do sistema |
| T6 | Reclamações (Consumidor.gov/Procon) | Relatos possivelmente com dados do reclamante | Consumidores | Fonte pública — minimização na ingestão |

Detalhes técnicos: [cofre](../../seguranca/cofre-de-identidade.md) · [trilha](../../seguranca/trilha-de-auditoria.md) · [modelo bitemporal](../../dados/modelo-bitemporal.md).

## 3. Necessidade e proporcionalidade

- **Finalidade:** apoio à fiscalização do mercado de combustíveis e transparência ao consumidor — detecção de padrões societários (sucessão de fachada, reincidência) impossíveis de ver sem ligar registros públicos.
- **Minimização por desenho:** a base analítica opera **pseudonimizada** (`pessoa_id`); CPF completo existe em um único componente segregado; a visão pública **nunca** exibe pessoa física; payload de evento/webhook nunca carrega dado do cofre.
- **Alternativa menos invasiva considerada:** não tratar identidade PF — rejeitada porque mantém homônimos como vínculo falso e faz a priorização de fiscalização produzir injustiça (ADR-004, alternativas rejeitadas).

## 4. Bases legais por tratamento

| Tratamento | Base legal proposta | Fundamento | Status |
|---|---|---|---|
| T1, T2 | Legítimo interesse (art. 7º IX) sobre dado tornado público pelo titular/poder público (art. 7º §3º–§4º) | Finalidade de interesse público; expectativa razoável sobre QSA público | `[PENDENTE — teste de balanceamento formal (LIA) documentado]` |
| T3 | Conforme o instrumento: execução de política pública pelo órgão (art. 7º III, via R1) ou obrigação do convênio (R2) | O órgão é quem trata o sigilo | `[PENDENTE — instrumento assinado]` |
| T4 | Execução de políticas públicas / legítimo interesse com escopo | ABAC + finalidade logada | `[PENDENTE — revisão jurídica]` |
| T5 | Obrigação de auditoria e segurança (art. 7º II/IX; art. 46) | Integridade do sistema | Desenho pronto |
| T6 | Legítimo interesse com minimização agressiva | Relato é contexto, nunca indício | Desenho pronto |

## 5. Riscos e mitigações

| Risco | Sev. | Mitigação (já desenhada) |
|---|---|---|
| Exfiltração de CPF | Alta | Cofre segregado, envelope encryption, sal não-exportável — vazamento da zona 1 não reidentifica |
| Pessoa ligada indevidamente a "fraude" | **Crítica** | Arestas com nível/score, fila humana, política de linguagem, Guardião, visão pública sem PF |
| Homônimo → grupo falso → fiscalização indevida | Alta | T3 probabilístico nunca conclusivo; resolução por R1 antes de dossiê |
| Uso de finalidade desviada por usuário de órgão | Média | Escopo ABAC, finalidade obrigatória, trilha consultável por auditor |
| Reidentificação por cruzamento de saídas públicas | Média | Visão pública só empresa; agregados com supressão de célula pequena `[PENDENTE — definir k mínimo]` |
| Retenção excessiva | Média | Política de retenção + expurgo automatizado `[PENDENTE — prazos por classe]` |

## 6. Direitos dos titulares

Canal de atendimento `[PENDENTE — definir]`. Confirmação de tratamento, acesso e correção: viáveis por desenho (consulta por `pessoa_id` mediante identificação). Eliminação: ponderada contra obrigação de auditoria e interesse público — na trilha, integridade prevalece (documentado em [trilha, §retenção](../../seguranca/trilha-de-auditoria.md)); nos fatos societários, o dado é público de origem e a exclusão local não o torna inexistente — resposta padrão a definir com jurídico `[PENDENTE]`.

## 7. Medidas de segurança

Referência cruzada, sem duplicação: criptografia em trânsito/repouso, segregação do cofre, RBAC+ABAC, trilha encadeada com âncora externa, verificação agendada, controle duplo em lote, segregação de função admin/consulta — todas especificadas nos docs de segurança e no plano diretor §4.

## 8. Pendências institucionais (bloqueiam a ingestão de QSA)

1. `[PENDENTE]` Nomear controlador e encarregado (§1)
2. `[PENDENTE]` Teste de balanceamento (LIA) formal para T1/T2
3. `[PENDENTE]` Revisão jurídica das bases de T4
4. `[PENDENTE]` Política de retenção com prazos por classe de dado
5. `[PENDENTE]` k mínimo de supressão em agregados públicos
6. `[PENDENTE]` Canal de titular e fluxo de resposta

Enquanto a lista não zera, o conector F05 pode **arquivar** os dumps mensais (preservação sem tratamento analítico de PF — a janela de captura é irrecuperável) e o grafo opera apenas com T1/T2 (empresas), sem dimensão de pessoa física.
