# Modelo de ameaças — PIC Verifica, manifestações e integração metrológica

**Versão:** proposta 0.1 — 12/11/2026.  
**Estado:** análise de projeto, **não** auditoria de segurança nem certificação; controles aqui descritos **não estão implementados** por este documento.  
**Referências internas:** [PIC Verifica](../produto/pic-verifica-app.md), [ADR-012](../arquitetura/adr/adr-012-app-bluetooth-e-manifestacoes.md), [contrato conceitual](../arquitetura/contrato-evento-bomba-e-relato.md), [RIPD](../conformidade/lgpd/ripd.md), [trilha existente](trilha-de-auditoria.md).

## 1. Ativos, fronteiras e modelo de ameaça

**Ativos a proteger:** identidade/contato do reportante; anexos e localização; texto livre; número de protocolo; credenciais de analistas; pacotes brutos de bombas; chaves/certificados e status de assinatura; `posto_id` e vínculo instrumento/posto; decisões e histórico de triagem; auditoria e eventual comunicação a órgãos.

| Fronteira | Origem → destino | Ameaça principal | Regra de projeto |
| --- | --- | --- | --- |
| Mobile → bomba | Bluetooth físico, perfil/modelo a confirmar | Dispositivo impostor, replay, pareamento indevido, tentativa de comando de escrita, leitura de instrumento errado | Pareamento explícito, identificação independente, allowlist de comandos **read-only**, tempo/nonce quando disponível, tratar assinatura e certificado como propriedades distintas |
| Controlador de pista → integração | API/IFSF/ERP por adesão | Controle não autorizado, credencial privilegiada, movimento lateral OT/IT | Canal segregado, credencial por instalação e permissão mínima; **nenhum controle da bomba** no app |
| Mobile → gateway de manifestações | Rede pública / upload | Token roubado, spam, replay, XSS/SQLi, upload malicioso, protocolo enumerável | Rate limit, idempotência, autenticação/antibot proporcional, análise de arquivos em quarentena, protocolos opacos, testes de enumeração |
| Gateway → cofre privado | Serviço de ingresso → armazenamento | Vazamento de contato e anexos, escopo cruzado, retenção indefinida | Separar identidade e evidência, criptografar, restringir chaves, política de retenção aprovada e trilha de leitura |
| Consoles → manifestações | Analistas, supervisores, órgão | Escalada de privilégio, acesso sem finalidade, vazamento por export, busca global não autorizada | RBAC + ABAC por papel/caso/finalidade/prazo; auditoria de **leitura e export**; concessão revogável |
| Evidência → agentes de IA | Texto, PDF, foto, descrição de terceiros | Prompt injection, alucinação de fraude, vazamento por ferramentas/RAG | Dados externos não são instruções; sanitizar, não executar comandos, Guardião; humano decide e valida fontes |
| Dados privados → portal/fatos oficiais | Projeções e relatórios | Denúncia virar fato público ou score; associação incorreta | Default-deny por classe de dado; testes negativos; nenhuma mutação automática de F02/F04 ou rótulo de fraude |
| Operação → CI/backup | Logs, cadeia de software, restauração | Segredos em builds, supply chain, perda de evidência, backup corrompido | SBOM e verificação de dependências, assinatura de artefatos quando suportada, restauração testada, segregação de segredos e retenção |

## 2. Riscos priorizados e aceite mínimo

| ID | Severidade inicial | Controle recomendado | Evidência antes do piloto |
| --- | --- | --- | --- |
| SEC-01 | **P0** | Proteção de identidade do reportante, inclusive contra operador técnico e gestor do posto | Matriz de acessos negativos, logs de leitura, auditoria de exportação, revisão RIPD |
| SEC-02 | **P0** | Verificação de identidade **real** do instrumento antes de correlacionar registros | Testes de BLE/SPP, dispositivo falso, troca de serial/QR, replay e falha de certificado |
| SEC-03 | **P0** | Cofre de evidências segregado, hashes do original e manifestos de cadeia de custódia | Testes de upload, preservação/recuperação do original, controle de retenção e verificação de integridade |
| SEC-04 | **P0** | Proteção antiabuso e quarentena de anexos | Testes de malware/EICAR apropriados, arquivos grandes, duplicação, links perigosos, rate limit |
| SEC-05 | **P1** | Defesa de agentes contra instruções em textos e anexos | Injeções simuladas e prova de que nenhuma ferramenta sensível executou |
| SEC-06 | **P1** | Segurança mobile conforme OWASP MASVS e testes com MASTG | Perfil de requisitos e relatório por versão/aparelho/plataforma |
| SEC-07 | **P1** | Isolamento OT/IT e adaptadores sem escrita | Revisão técnica do fabricante, testes de comandos negados e segregação de rede |
| SEC-08 | **P1** | Recuperação testada, dependências/artefatos verificáveis | Exercício de restore, matriz RPO/RTO, SBOM e verificação de releases |

**P0/P1 são prioridades de engenharia**, não avaliações quantitativas de risco realizadas. Uma liberação de produção requer análise de probabilidade, impacto, responsável e risco residual.

## 3. Requisitos verificáveis

### 3.1 Denúncia e dados pessoais
- **SEC-R01:** sem permissão por **ator, caso, finalidade, escopo e prazo**, qualquer leitura de relato, anexos, identidade ou histórico é negada. Administração da infraestrutura não concede permissão sobre conteúdo.
- **SEC-R02:** identidade do reportante, anexos e texto livre são armazenados em domínios/chaves separados; acesso a cada domínio é rastreado.
- **SEC-R03:** dados de relato **não** são indexados publicamente, publicados por webhook, propagados para analytics/LLM ou associados ao score de posto; auditoria prova a negativa.
- **SEC-R04:** relato pode ser submetido sem Bluetooth; token de protocolo é opaco, resistente a enumeração e com proteção contra acesso de terceiros; status externo não revela investigação protegida.
- **SEC-R05:** anexos não são processados como executáveis; MIME detectado, tamanho limitado, armazenamento em quarentena, remoção de metadados excessivos na cópia destinada à análise quando apropriado. Original preservado segundo política.
- **SEC-R06:** a equipe jurídica/DPO define base legal por finalidade, retenção, canais de direitos, comunicação de incidente e compartilhamento antes do piloto real; nenhum prazo é presumido.

### 3.2 Evidência metrológica
- **SEC-R07:** identidade Bluetooth sozinha ou QR apresentado pelo dispositivo não autentica o instrumento. Vinculação exige associação verificável com o cadastro físico e documentação aplicável.
- **SEC-R08:** assinatura inválida, não verificada ou ausente é resultado explícito; assinatura válida **não** equivale a verificação física do volume entregue.
- **SEC-R09:** registros brutos, hash, método de verificação, versão de parser, instante de evento e de recebimento permanecem distintos; relógios conflitantes não são corrigidos silenciosamente.
- **SEC-R10:** app e gateway de laboratório só recebem permissões de leitura previamente aprovadas; alteração de firmware, calibração, parâmetros e operação é proibida.
- **SEC-R11:** dados em tempo real são canal opcional separado (controlador com contrato); não presumir streaming pelo Bluetooth de verificação metrológica.

### 3.3 Auditoria, IA e continuidade
- **SEC-R12:** toda atribuição de caso, leitura sensível, exportação, encaminhamento, suspensão e mudança de política gera trilha com ator, finalidade, objeto, tempo, decisão e resultado, sem expor conteúdo em logs.
- **SEC-R13:** falha de verificação de integridade do log aciona incidente; âncoras externas devem ser independentes do domínio de escrita. Considerar WORM/assinatura e cadeia de custódia sem obrigatoriedade de blockchain.
- **SEC-R14:** documentos e anexos de terceiros são **dados não confiáveis** para agentes, sem execução de instruções; validação humana obrigatória para ação de consequência.
- **SEC-R15:** testes automatizados cobrem isolamento multi-tenant, isolamento multi-caso, papéis revogados, expiração de concessão, indisponibilidade de rede e recuperação após falha.
- **SEC-R16:** build/release com inventário de dependências/SBOM, checagem de vulnerabilidades, segredos fora do repositório e rollback comprovado.

## 4. Bases de referência de segurança

- [OWASP MASVS](https://mas.owasp.org/MASVS/) / [MASTG](https://mas.owasp.org/MASTG/) — controles e testes mobile.
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — API/backend/console; identificar edição e perfil em cada avaliação.
- [NIST SP 800-218 (SSDF)](https://csrc.nist.gov/pubs/sp/800/218/final) — desenvolvimento seguro.
- [NIST SP 800-82 Rev. 3 (final)](https://csrc.nist.gov/pubs/sp/800/82/r3/final) e [Rev. 4 (minuta pública em setembro de 2026)](https://csrc.nist.gov/pubs/sp/800/82/r4/ipd) — segregação de sistemas operacionais; **não** tratar a minuta como final.
- [ANPD — comunicação de incidentes](https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/comunicado-de-incidente-de-seguranca-cis) — definir rito jurídico e prazos conforme caso concreto.

## 5. Gates de segurança

1. **G-S0 — modelo de ameaças aprovado:** fronteiras, responsabilidades, controlador, instituição de triagem e possíveis impactos.
2. **G-S1 — proteção de relatos:** matriz de autorização, anexos, protocolo, privacidade e testes de abuso; nenhum acesso de posto.
3. **G-S2 — metrologia em laboratório:** compatibilidade por marca/modelo, comandos apenas de leitura, identidade, assinatura, segurança em área apropriada.
4. **G-S3 — operação:** auditoria independente, backup/restauração, incidentes, monitoramento, revisão jurídica e aceite institucional.

**Ainda pendente:** definição de donos dos gates, acordos com fabricantes/órgãos e verificação do risco residual. Requisitos não devem ser confundidos com controles implantados.
