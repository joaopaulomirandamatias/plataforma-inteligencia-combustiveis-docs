# Inmetro e RBMLQ-I — o que é público, o que não é, e o que serve

*Verificado na fonte em 2026-09-14. Cada número abaixo foi medido no arquivo ou na consulta indicada, não lido de catálogo. Complementa o [catálogo de fontes](catalogo-fontes.md) (F08, F09 e a candidata F11).*

## Resposta curta

1. **O Inmetro serve como complemento, não como gabarito.** O que a plataforma mais precisa dele — erro medido por bico, aprovação/reprovação, lacres, autos de infração por estabelecimento — **não está aberto**: não está no dados.gov.br e não está na consulta pública do PSIE. Continua sendo a F09, por convênio.
2. **Quatro conjuntos servem de verdade**, e um deles é o único dado aberto do Inmetro no nível de estabelecimento: as **oficinas permissionárias** — quem tem autorização para intervir em bomba medidora, onde, até quando e com quais mecânicos.
3. O método de seleção de alvos praticado pelo Ipem-SP (seção final) coincide, critério a critério, com as fontes que a plataforma carrega, planeja ou já sabe que são restritas — e entrega a **métrica operacional de referência** que faltava ao [modelo de risco](../ml/modelos/risco-nao-conformidade.md).

## Como foi medido

- Organização **Inmetro** no dados.gov.br: 18 conjuntos abertos, 0 não abertos. O CKAN do portal (`ckan.dados.gov.br`) estava em 503 no início da verificação; a listagem veio pela API do próprio portal (`/api/publico/conjuntos-dados/buscar?idOrganizacao=a94e53da-6e60-4c32-8687-d1c910b908be`) e o detalhe de cada conjunto por `/api/publico/conjuntos-dados/{nome}`. A API pública documentada (`/dados/api/publico/...`) exige chave (401).
- **Plano de Dados Abertos 2024/2026** do Inmetro (inventário de bases, anexo I) e o **relatório parcial de execução** (publicado em 2026-07-27), ambos em `gov.br/inmetro/pt-br/acesso-a-informacao/dados-abertos`.
- Arquivos baixados e contados: `oficinas.json` de SP e mais cinco UFs, `veiculotanque.json` de nove UFs, `PT_OUTROS_2025_QTDE_uf.xml`, `SIL-PAM.csv`; consulta pública de instrumentos do PSIE (`servicos.rbmlq.gov.br/Instrumento`) inspecionada quanto aos tipos oferecidos.

## Os 18 conjuntos

| Conjunto (dados.gov.br) | Última alteração em arquivo | Serve? |
|---|---|---|
| **Portal de Serviços do Inmetro nos Estados – PSIE** | 2026-06-17 | **Sim** — oficinas permissionárias; veículo-tanque (cobertura parcial) |
| **Planejamento e Execução de Serviços Metrológicos** | 2026-04-07 | Como contexto — intensidade de fiscalização de bombas por UF |
| **Sistema Inmetro de Legislação (SIL)** | 2026-07-21 | **Sim** — Portarias de Aprovação de Modelo de bombas (dimensão marca/modelo); já previsto na F08 |
| Sistema Orquestra – Registro de Objetos (73 CSV) | 2026-07-21 | Marginal — não há bomba medidora; há tanque rodoviário de produtos perigosos, cilindro e instalação de GNV, ARLA 32 |
| Prodcert (certificados de produtos e serviços) | 2026-07-21 | Marginal |
| Organismos Acreditados (CADORG, RBC, RBLE) | 2023-05 | Não — recursos vazios na API do portal |
| Sinmac (acidentes de consumo) | 2026-09-08 | Não |
| PBE · PAP (descontinuado em 2019) · Agenda Regulatória · Cronotacógrafos · Certifiq (descontinuado em 2025) · TBT/OMC · CMC/BIPM · Pesquisas de opinião · Dissertações · Acordos de reconhecimento mútuo · Acordos de cooperação | — | Não |

O inventário do PDA marca o **SGI** (Sistema de Gestão Integrada — "planejamento e execução da fiscalização e arrecadação pelos órgãos delegados") como base aberta apontando para o conjunto *Planejamento e Execução*. Na prática, o que está aberto é o consolidado por UF e mês; para o SGI o próprio inventário registra *"possui conteúdo sigiloso: SIM"*.

## As fontes que servem

### PSIE · Oficinas permissionárias → candidata F11

| Campo | Valor |
|---|---|
| O que traz | Por UF: razão social, endereço, CEP, município, telefone, e-mail, número de autorização, **credenciamentos (tipo de serviço + data de validade)** e **nomes dos mecânicos** |
| Cadência | Mensal (metadados); arquivos regenerados em 2026-06-17 |
| Formato | JSON e XML — `https://servicos.rbmlq.gov.br/dados-abertos/{UF}/oficinas.json` |
| Acesso | Público, sem chave. O diretório não lista (403), mas o arquivo responde para toda UF testada (SP, MG, RJ, PR, RS, BA) |
| Medido (SP) | 881 oficinas; **137 credenciadas em "BOMBA MEDIDORA DE COMBUSTÍVEIS LÍQUIDOS"** em 54 municípios; validades vencendo em 2026 (50) e 2027 (87). Demais tipos: balanças 630, esfigmomanômetro 101, taxímetro 64, medidor de velocidade 15, GNV 4 |
| Papel | Universo, geografia e vigência de quem pode intervir em bomba; quando a F09 chegar, cruzar posto ↔ oficina executora |
| Riscos | **Sem CNPJ** — a chave é número de autorização + razão social + endereço, o que exige resolução de entidade por nome e endereço; nomes de mecânicos são dado pessoal (finalidade pública, mas minimizar: não expor na borda pública) |
| Cuidados | Snapshot mensal bitemporal: validade muda e a oficina some da lista quando a autorização é cassada — a **ausência** é o sinal; guardar o JSON bruto com `sha256`, como nas demais fontes |

### PSIE · Veículo-tanque (anexo)

| Campo | Valor |
|---|---|
| O que traz | Por veículo: validade do certificado, data da última verificação, regional, número Inmetro, série, placa, chassi, ano; proprietário (nome, município, UF) |
| Formato | `https://servicos.rbmlq.gov.br/dados-abertos/{UF}/veiculotanque.json` |
| Medido | Só parte dos órgãos delegados publica: GO 11 MB, PR 26 MB, RS 18 MB, PE 8 MB, SC 5 MB; **SP, MG, RJ e BA respondem `[]`** |
| Papel | Lado da distribuição (frota de TRR e distribuidoras verificada), não do posto |
| Riscos | Cobertura desigual por UF — vazio não significa "sem frota" |

### Planejamento e Execução de Serviços Metrológicos (contexto)

| Campo | Valor |
|---|---|
| O que traz | Por UF e mês, previsto × realizado por grupo de serviço; o grupo **"Bombas medidoras para combustíveis"** existe para 26 UFs (o DF não aparece) |
| Formato | XML — `https://dados.inmetro.gov.br/plan_exec_serv_metrologicos/PT_OUTROS_2025_QTDE_uf.xml` (2025); por UF só há 2019 |
| Medido | Apesar do nome, o arquivo de 2025 é o bloco `G_FINANCEIRO` (**R$**, previsto × realizado), e não quantidades como descreve o guia de 2019 — SP: R$ 25,3 mi previstos, R$ 10,3 mi realizados em bombas |
| Papel | Covariável de intensidade fiscalizatória por UF (quanto do planejado se executou). Nunca feature por posto |

### SIL · Portarias de Aprovação de Modelo (dimensão para F08 e F09)

| Campo | Valor |
|---|---|
| O que traz | Todas as PAM do Inmetro: tipo de ato, número, data, situação, ementa, link do PDF |
| Formato | CSV **UTF-16, separador `;`**, 18,9 MB — `https://dados.inmetro.gov.br/sil/SIL-PAM.csv` (diário). O RMAC está em `SIL.csv` |
| Medido | 8.344 portarias; **664 sobre bombas medidoras** (273 em vigor, 291 revistas, 99 revogadas); 2023–2026: 8, 10, 8, 5 por ano; inclui atos sobre "sistema de gerenciamento" e "concentrador de bombas" |
| Papel | Tabela de marca/modelo aprovado — o que dá sentido a "modelo do instrumento" quando a F09 trouxer o instrumento verificado |

## O que não está público (verificado, não presumido)

- **Verificações de bombas por estabelecimento.** A consulta pública do PSIE oferece oito tipos de instrumento — balança dinâmica, balança rodoferroviária, esfigmomanômetro, etilômetro, medidor de umidade de grãos, medidor de velocidade, taxímetro, veículo-tanque. **Bomba medidora não está entre eles**, e nenhum nome plausível de arquivo (`bomba*.json`, `instrumentos.json`, `verificacoes.json`) existe no host de dados abertos.
- **Autos de infração e fiscalizações por estabelecimento**: SGI, sigiloso pelo inventário do próprio PDA.
- **Histórico de intervenções por instrumento** e **relação posto ↔ oficina executora**: SGI.
- **Preços registrados manualmente pelas equipes de campo no SGI**: existem e não são explorados nem internamente (seção seguinte).

Três caminhos, não excludentes:

1. **F09 por convênio**, como já está no catálogo — com o pedido afiado pela seção seguinte.
2. **Pedido via LAI** de extração agregada por CNPJ (resultado, data, instrumento) — testa a tese antes do convênio.
3. **Consulta pública do próximo PDA.** O relatório parcial de 2026-07-27 informa que o PDA **dez/2026 – dez/2028** já está em elaboração; o PDA tem consulta pública de priorização (a de 2024 teve 23 bases votadas). É a janela institucional para pedir a abertura das verificações de bombas medidoras.

## Leitura de campo: o método de seleção de alvos do Ipem-SP

Esboço de candidatura ao Prêmio de Inovação da RBMLQ-I (Ipem-SP, com o GAESI-USP), compartilhado com o projeto em 2026-09. O método cruza seis fontes para escolher os postos das ações especiais de fiscalização metrológica. Cada critério, e onde ele está na plataforma:

| Critério do método | Fonte na plataforma | Estado |
|---|---|---|
| Preço significativamente abaixo da média local, por combustível (ANP e sites de preço) | **F03** SLP + contexto regional | Em produção (`/contexto-regional`) |
| Outros estabelecimentos dos mesmos sócios de postos já autuados (Junta Comercial) | **F05** Receita Federal (QSA) | Conector existe; a Junta Comercial não é aberta em lote — a Receita é o substituto público |
| Preços promocionais informados por consumidores em aplicativos de mapas | — | Sem fonte aberta; APIs comerciais são pagas e com termos de uso restritivos. Lacuna registrada |
| Reclamações reincidentes na ouvidoria do órgão | **F06** | Sindec/MJ fora do ar; `consumidor.gov.br` é o candidato a substituto; a ouvidoria do Ipem não é pública |
| Número de intervenções no instrumento em relação ao ano de fabricação | **F09** (convênio) | Restrito. Molda o esquema-alvo: `ano_fabricacao` e contagem de intervenções por instrumento |
| Uso das mesmas oficinas permissionárias já associadas a autuações | **F11** (público) + **F09** (executora por posto) | Metade aberta — ficha acima |

O que o esboço acrescenta à plataforma, além de confirmar as prioridades:

- **Métrica operacional de referência.** Na fiscalização de rotina, **0,17 auto de infração por posto fiscalizado**; nas operações com seleção de alvos, **1,81** — cerca de dez vezes. É o "precision@k contra o critério atual" que o projeto v1 pede para o primeiro slide, agora com os dois números de chão. O modelo de risco passa a ser medido contra essas duas referências, e não contra métricas de classificação sem correspondência operacional.
- **Premissas de dimensionamento** usadas pelo próprio órgão: cerca de 8.500 postos autorizados em SP; venda média de 12.000 L/dia por posto; 10 % como fração média de desvio nos casos com apreensão; ~350 estabelecimentos com apreensão acumulada. Servem para estimativas de impacto — sempre citadas como premissas do esboço, não como medição da plataforma.
- **Lição declarada pelo próprio órgão**: o gargalo é a integração entre fontes e sistemas — exatamente o que a plataforma é.
- **Reciprocidade para o convênio F09**: o SGI guarda preços coletados em campo que nem o Ipem explora; a plataforma já entrega o comparativo regional. É argumento de mão dupla.

## Decisões em aberto

1. Abrir a **F11 (oficinas permissionárias)** como conector em v1 — JSON por UF, mensal, bitemporal, sem CNPJ.
2. **SIL-PAM** como tabela de dimensão de bombas, junto com a F08 ou como carga própria.
3. **Substituir a F06** pelo `consumidor.gov.br` — verificar layout e granularidade por CNPJ antes de prometer.
4. Afiar o **pedido do convênio F09** com os campos do método: erro por bico, resultado, data, oficina executora, ano de fabricação, intervenções, e os preços registrados no SGI.
5. Entrar na **consulta pública do PDA 2026–2028** pedindo a abertura das verificações de bombas medidoras.
