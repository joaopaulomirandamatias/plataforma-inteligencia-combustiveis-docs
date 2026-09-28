#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera docs/dados/mapa-de-integracoes.md E docs/apresentacao/mapa-de-integracoes.pdf
a partir da MESMA lista de linhas.

Por que um gerador, e não dois arquivos editados à mão: a página e o PDF dizem a
mesma coisa para públicos diferentes, e duas cópias editadas em paralelo divergem
sem que nada fique vermelho — foi exatamente o defeito que o léxico canônico já
corrigiu em outro lugar deste projeto.

    python3 scripts/gerar-mapa-de-integracoes.py          # md + pdf (precisa de weasyprint)
    python3 scripts/gerar-mapa-de-integracoes.py --so-md  # só a página

`DATA_VERIFICACAO` é a data em que a EXISTÊNCIA das fontes marcadas "ok" foi
conferida por HTTP. Ao acrescentar linha nova verificada em outra data, diga a
data na própria célula de acesso — não mexa nesta constante sem reverificar tudo.
"""
import sys, html, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
OUT_MD = RAIZ / "docs/dados/mapa-de-integracoes.md"
OUT_PDF = RAIZ / "docs/apresentacao/mapa-de-integracoes.pdf"
DATA_VERIFICACAO = "2026-09-14"

# símbolo no markdown, rótulo no PDF, classe CSS
STATUS = {
    "ok":      ("✔",  "verificado",  "ok"),
    "ver":     ("⚠",  "a verificar", "ver"),
    "res":     ("🔒", "restrito",    "res"),
    "publico": ("",   "público",     "pub"),
}

PERGUNTAS = [
  ('Quem é', 'identidade do posto e de quem o controla', 'ANP cadastro · Receita CNPJ · Juntas · GEO'),
  ('Quanto cobra', 'preço e sua posição na cadeia de custo', 'ANP SLP · produtores · distribuição · apps'),
  ('Quanto entrega', 'quantidade — metrologia e volume', 'Inmetro/Ipem · SEFAZ NF-e/NFC-e · cartões-frota · telemetria · automação'),
  ('O que entrega', 'qualidade do produto', 'ANP PMQC · auditorias das distribuidoras'),
  ('O que o Estado já constatou', 'conformidade e sanções', 'ANP fiscalização · Ipem autos · SEFAZ cassações · CGU · Procon'),
  ('Demanda e território', 'denominadores', 'SENATRAN frota · IBGE · ANP vendas'),
]

ESTADO = 'No ar, com API pública e site: F01 cadastro, F02 PMQC, F03 preços e GEO-ANP. Catalogadas sem conector: F04 fiscalização ANP, F07 IBGE, F08 normativo, F09 Ipem (convênio), F10 SEFAZ (fase 3). Conector pronto com carga desligada: F05 Receita. Quebrada: F06 Sindec (host fora do ar). Candidata: F11 oficinas permissionárias do Inmetro.'

PRIORIDADE = [
  ('Ipem/Inmetro por convênio (F09)', 'sem ele não há gabarito de quantidade; o pedido já está afiado no catálogo e escrito nos nomes do próprio SGI.'),
  ('SEFAZ: NF-e e NFC-e (F10)', 'a reconciliação comprado × vendido é o único fechamento volumétrico autoritativo; exige base legal antes do primeiro byte.'),
  ('Cartões-frota', 'o mesmo fechamento pelo lado privado, sem sigilo fiscal, com o sinal “acima da capacidade do tanque”; é também o setor de frotas pagando.'),
  ('ANP fiscalização e multas (F04), CGU CEIS/CNEP, SEFAZ-SP cassações', 'três rótulos públicos — os dois primeiros com páginas e recursos confirmados nesta verificação.'),
  ('SENATRAN frota por município', 'denominador de demanda; barato e público.'),
  ('consumidor.gov.br no lugar do Sindec; F11 oficinas como conector pequeno', 'restaura o sinal precoce e abre o único dado do Inmetro por estabelecimento.'),
  ('Distribuidoras', 'volume entregue e monitoramento da rede, por contrato.'),
  ('Telemetria e automação de pista', 'só com adesão real; é o gatilho de streaming previsto no ADR-006.'),
]

FILA = 'Itens ⚠ acima, na ordem em que valem o esforço: layout e granularidade por CNPJ dos dados de fiscalização e multas da ANP; lista de cassações da SEFAZ-SP (o endereço tentado respondeu 404); layout do consumidor.gov.br; CEIS/CNEP; frota SENATRAN; validação de certificado no PSIE; STD; preços de produtores; licenças ambientais. Cada item verificado sobe para o catálogo com data, como as fontes do Inmetro em [fontes-inmetro](fontes-inmetro.md).'

FINAL = 'Nenhuma fonte, pública ou restrita, autoriza a plataforma a afirmar conduta: ela mostra fato, fonte e data e recomenda verificação; quem conclui é o órgão competente ([ADR-005](../arquitetura/adr/), [política de linguagem](../agentes/politica-de-linguagem.md)). Fontes restritas entram só com base legal escrita e desenho de minimização antes do primeiro byte ([RIPD](../conformidade/lgpd/ripd.md)).'

GRUPOS = [
("1. Órgãos federais", [
  ('ANP', 'Cadastro de revendedores, PMQC (qualidade), SLP (preços semanais), georreferenciamento dos revendedores', 'Pull versionado de dados abertos', 'Público — em produção', 'ok', 'Identidade, preço e qualidade do posto', 'No ar: F01, F02, F03, GEO-ANP'),
  ('ANP', 'Ações de fiscalização do abastecimento (autos por agente econômico) e multas aplicadas', 'Dados abertos mensais, defasagem de 2 meses; arquivos brutos 1998–2018 e 2019–2025', 'Público — página e recursos existem; layout não lido', 'ok', 'Rótulo de conformidade e reincidência. Auto não é julgamento: registrar data do fato e da decisão', 'Catalogada (F04), sem conector'),
  ('ANP', 'Distribuidores autorizados (filiais), contratos de cessão de espaço, pontos de abastecimento, TRR', 'Dados abertos (CSV)', 'Público — recursos existem', 'ok', 'Cadeia de oferta: quem abastece quem', 'Não'),
  ('ANP', 'Vendas de derivados por UF e município; movimentação de derivados; preços de produtores e importadores', 'Dados abertos', 'Público — páginas existem; layout não lido', 'ok', 'Denominadores de volume e primeiro elo da cadeia de custo', 'Não'),
  ('ANP', 'Sistema de Transparência na Distribuição (STD, Decreto 12.930/2026): operações agregadas a cada 14 dias', 'Painel dinâmico', 'Público — página existe; dados brutos a confirmar', 'ver', 'Contexto de oferta sob regime emergencial', 'Não'),
  ('ANP', 'SIMP — movimentação de produtos declarada por cada agente', 'Convênio', 'Restrito', 'res', 'Volume por distribuidora e base; reconciliação com o varejo', 'Não'),
  ('ANP', 'Reclamações e denúncias contra postos (canal próprio)', 'Não estruturado; LAI agregada', 'Restrito', 'res', 'Sinal precoce', 'Não'),
  ('Inmetro / RBMLQ-I (Ipem)', 'Verificações de bomba por bico: erro, resultado, lacres, oficina executora, intervenções, ano de fabricação; autos de infração; preços de campo do SGI', 'Convênio; LAI agregada por CNPJ; consulta pública do PDA 2026–2028', 'Restrito — ausência do público confirmada duas vezes: na tela e na wiki do Inmetro', 'res', 'Gabarito metrológico — a fonte mais valiosa do sistema; o pedido já tem nomes de campo e de relatório (CPL5095, CVR5070, CVR5080, COF5010)', 'Catalogada (F09)'),
  ('Inmetro / RBMLQ-I', 'Oficinas permissionárias (JSON por UF); Portarias de Aprovação de Modelo (SIL-PAM); consolidado de execução por UF', 'Pull mensal / diário', 'Público — medido na fonte', 'ok', 'Quem intervém em bomba; dimensão marca/modelo; intensidade fiscalizatória', 'F11 candidata; F08'),
  ('Inmetro / RBMLQ-I — wiki', 'Base de conhecimento interna publicada: SGI, SGImóvel, Cronotacógrafo e PSIE tela a tela — campos, códigos e relatórios nomeados. Metadado, não dado: nenhum registro de estabelecimento', 'Leitura; API do MediaWiki', 'Público — verificado em 2026-09-28; GNU FDL 1.3', 'ok', 'Escreve o pedido da F09 no vocabulário do sistema e nomeia o que pedir como série; CPL5095 já compara a operação dirigida com o serviço subsequente do mesmo período, e OF2010 traz o CNPJ e o motivo do descredenciamento que faltam à F11', 'Referência (não vira conector)'),
  ('Inmetro / PSIE', 'Validação de certificado de verificação por número', 'Consulta pontual', 'Público — existe; comportamento não testado', 'ver', 'Posto idôneo sobe o próprio certificado e a plataforma confere — gabarito de baixo para cima', 'Não'),
  ('Receita Federal', 'Dados Públicos CNPJ: empresas, estabelecimentos, QSA, situação, CNAE, Simples/MEI', 'Dump mensal', 'Público', 'ok', 'Grafo societário — só o presente', 'Conector existe (F05); carga cheia desligada'),
  ('Receita Federal', 'CPF completo do sócio; NF-e modelo 55 (compras do posto à distribuidora)', 'Via órgão parceiro; base legal escrita', 'Restrito', 'res', 'Identidade da pessoa; volume comprado por posto', 'Não — o RIPD prevê a dimensão PF'),
  ('Senacon / MJ', 'Sindec (Procons) e consumidor.gov.br, por CNPJ', 'Pull do catálogo', 'Sindec: host não resolve. consumidor.gov.br: página existe; layout não lido', 'ver', 'Sinal precoce de reclamação', 'F06 quebrada; substituto a verificar'),
  ('CGU', 'CEIS, CNEP e CEPIM — empresas sancionadas ou inidôneas, por CNPJ', 'Dados abertos do Portal da Transparência', 'Público — página de download existe; layout não lido', 'ok', 'Flag de conformidade administrativa', 'Não'),
  ('SENATRAN', 'Frota de veículos por município e tipo', 'Dados abertos mensais', 'Público — página existe; layout não lido', 'ok', 'Denominador de demanda: litros esperados por município', 'Não'),
  ('IBGE', 'Malha municipal, população, renda, PIB municipal', 'Anual', 'Público', 'publico', 'Território; estratos de fairness', 'Catalogada (F07)'),
  ('Imprensa Nacional', 'Atos normativos ANP e Inmetro (DOU)', 'Varredura diária', 'Público', 'publico', 'RAG regulatório; vigência de cada regra', 'Catalogada (F08)'),
  ('CADE', 'Processos de cartel em revenda de combustíveis', 'Documental, não estruturado', 'Público', 'publico', 'Contexto de mercado local — preço uniforme não é concorrência', 'Não — contexto'),
]),
("2. Órgãos estaduais", [
  ('SEFAZ (cada UF)', 'NFC-e modelo 65 — cada venda na bomba: volume, produto, valor, hora', 'Base legal escrita (sigilo fiscal)', 'Restrito', 'res', 'Registro autoritativo de venda; reconciliação comprado × vendido × capacidade de tanque', 'Catalogada (F10, fase 3)'),
  ('SEFAZ-SP e congêneres', 'Cassação da inscrição estadual de postos por combustível fora de especificação (lei estadual)', 'DOE e lista pública', 'Público — endereço não localizado nesta verificação', 'ver', 'Rótulo público forte em SP, sem convênio', 'Não'),
  ('SEFAZ / Sintegra', 'Situação cadastral da inscrição estadual por CNPJ', 'Consulta pontual', 'Público por consulta', 'ver', 'Posto com IE suspensa ou cassada operando', 'Não'),
  ('Procons estaduais', 'Reclamações e rankings próprios', 'PDF / HTML', 'Público, pouco estruturado', 'publico', 'Complemento à F06', 'Não'),
  ('Órgãos ambientais (CETESB e congêneres)', 'Licença de operação; idade e troca de tanques subterrâneos', 'Consulta pública', 'Público', 'ver', 'Integridade física; posto operando sem licença', 'Não'),
  ('Corpo de Bombeiros', 'AVCB vigente', 'Consulta', 'Público', 'ver', 'Conformidade de segurança — baixa prioridade', 'Não'),
  ('Juntas Comerciais', 'Histórico societário — o que a Receita não dá (só o presente)', 'Certidão paga ou convênio', 'Pago', 'res', 'Rotatividade societária real', 'Não'),
]),
("3. Empresas do setor (por contrato)", [
  ('Distribuidoras / bandeiras', 'Contratos de bandeira e desembandeiramentos; volume entregue por posto; auditorias de qualidade da rede; lacres de tanque', 'API ou arquivo por contrato', 'Parceria — clientes pagantes no projeto v1', 'res', 'Volume do lado da oferta sem esperar a SEFAZ; monitoramento da rede', 'Não'),
  ('Cartões-frota (Ticket Log/Edenred, Sem Parar, Alelo Frota e outros)', 'Transações na bomba: litros, preço, CNPJ do posto, placa, hora', 'API por contrato', 'Parceria', 'res', 'O sinal privado mais rico de quantidade: abastecimento acima da capacidade do tanque do veículo é evidência direta de bomba fora de medida', 'Não'),
  ('Telemetria embarcada (Sascar, Omnilink e outros)', 'Nível de tanque e GPS por veículo', 'Stream por contrato', 'Parceria', 'res', 'Litros recebidos × litros pagos por abastecimento — gatilho do ADR-006 (streaming)', 'Não'),
  ('Instituto Combustível Legal, IBP, sindicatos', 'Estudos, canal de denúncia, estimativas setoriais', 'Documental; parceria', 'Misto', 'publico', 'Legitimidade setorial; calibração de estimativas', 'Não'),
  ('Petrobras e demais produtores', 'Preço de venda às distribuidoras por base e data', 'Página pública', 'Público — página existe; estrutura não lida', 'ver', 'Primeiro elo da cadeia de custo', 'Não'),
  ('Apps de preço e de mapas', 'Preço promocional relatado por consumidores', 'API comercial', 'Pago, termos restritivos', 'res', 'Terceiro critério do método de seleção de alvos do Ipem-SP', 'Lacuna registrada'),
]),
("4. Dado do próprio posto (por adesão)", [
  ('Automação de pista (Companytec, Sinergy, Gilbarco/Wayne e outros)', 'Encerrantes por bico, vendas por bico, alarmes', 'API ou exportação por adesão', 'Adesão do posto', 'res', 'Quantidade medida na origem; base do selo de transparência auditável', 'Não'),
  ('Medição eletrônica de tanque', 'Nível, entradas, perdas', 'Idem', 'Adesão do posto', 'res', 'Reconciliação estoque × entrada × venda', 'Não'),
  ('LMC — Livro de Movimentação de Combustíveis', 'Estoque diário, entradas e vendas por produto', 'Arquivo por adesão (ou via ANP)', 'Adesão do posto', 'res', 'Balanço volumétrico oficial do posto', 'Não'),
  ('Certificados de verificação do Inmetro em papel', 'Número, data, resultado', 'Upload + validação no PSIE', 'Adesão do posto', 'res', 'Gabarito parcial vindo do posto idôneo', 'Não'),
]),
("5. Referência e apoio", [
  ('OpenStreetMap / malha viária', 'Rotas e vias', 'Público (ODbL)', 'Público', 'publico', 'Setor de frotas: posto na rota', 'Não'),
  ('Base de CEP (ViaCEP / DNE)', 'Normalização de endereço', 'API pública ou base paga', 'Público / pago', 'publico', 'Resolução de entidade — a F11 não tem CNPJ', 'Não'),
  ('Catálogo de veículos', 'Capacidade de tanque por modelo', 'Referência', 'Público', 'ver', 'Regra: abasteceu mais que o tanque', 'Não'),
  ('RAIS / CAGED', 'Empregados por CNPJ', 'Agregado público; microdado restrito', 'Misto', 'publico', 'Porte do posto', 'Não'),
]),
]


# --------------------------------------------------------------------------
# Página Markdown
# --------------------------------------------------------------------------
def markdown() -> str:
    L = [f"# Mapa de integrações — o que falta, por órgão e empresa\n",
         f"*Verificação de existência na fonte em {DATA_VERIFICACAO}. Convenção do "
         f"[catálogo de fontes](catalogo-fontes.md): ✔ verificado na fonte (página ou recurso existe; "
         f"o layout só quando dito) · ⚠ conhecido, ainda não verificado · 🔒 restrito (convênio, contrato, "
         f"adesão ou base legal). Versão para compartilhar: [PDF](../apresentacao/mapa-de-integracoes.pdf). "
         f"Página e PDF saem do mesmo gerador: `scripts/gerar-mapa-de-integracoes.py`.*\n",
         "## As seis perguntas que uma plataforma completa responde\n",
         "| Pergunta | O que é | Quem detém o dado |\n|---|---|---|"]
    L += [f"| **{p}** | {d} | {q} |" for p, d, q in PERGUNTAS]
    L += ["", "Cada fonte abaixo serve a pelo menos uma dessas perguntas; o valor de uma integração é medido "
              "por quantas perguntas ela fecha para o mesmo `posto_id`.\n",
          "## Estado atual\n", ESTADO + "\n"]
    for titulo, linhas in GRUPOS:
        L += [f"## {titulo}\n",
              "| Órgão / empresa | Dados | Integração | Acesso | Destrava | Na plataforma hoje |\n|---|---|---|---|---|---|"]
        for org, dados, integ, acesso, st, destrava, pic in linhas:
            simbolo = STATUS[st][0]
            L.append(f"| **{org}** | {dados} | {integ} | {acesso} {simbolo} | {destrava} | {pic} |".replace("  |", " |"))
        L.append("")
    L.append("## Ordem de prioridade\n")
    L += [f"{i}. **{t}** — {d}" for i, (t, d) in enumerate(PRIORIDADE, 1)]
    L += ["", "## Fila de verificação na fonte\n", FILA + "\n",
          "## O que não muda com nenhuma integração\n", FINAL + "\n"]
    return "\n".join(L)


# --------------------------------------------------------------------------
# PDF (WeasyPrint) — o mesmo conteúdo, em página de apresentação
# --------------------------------------------------------------------------
CSS = """
@page { size: A4 landscape; margin: 14mm 12mm 16mm 12mm;
  @top-left { content: "Plataforma de Inteligência de Combustíveis — mapa de integrações"; font: 8pt 'Inter','DejaVu Sans',sans-serif; color:#6b7280; }
  @top-right { content: "Verificação de existência na fonte em DATA"; font: 8pt 'Inter','DejaVu Sans',sans-serif; color:#6b7280; }
  @bottom-right { content: "página " counter(page) " de " counter(pages); font: 8pt 'Inter','DejaVu Sans',sans-serif; color:#6b7280; }
  @bottom-left { content: "Documento de trabalho — nenhuma afirmação de conduta; fato, fonte e data."; font: 8pt 'Inter','DejaVu Sans',sans-serif; color:#6b7280; } }
@page :first { @top-left { content: none } @top-right { content: none } }
body { font-family:'Inter','DejaVu Sans',sans-serif; font-size:8.6pt; color:#111827; line-height:1.32; }
h1 { font-size:22pt; font-weight:600; color:#0f2a47; margin:0 0 3mm 0; letter-spacing:-0.01em; }
.sub { font-size:10.5pt; color:#374151; margin:0 0 5mm 0; max-width:220mm; }
.meta { font-size:8.5pt; color:#6b7280; margin-bottom:4mm; }
h2 { font-size:12.5pt; font-weight:600; color:#0f2a47; margin:5mm 0 2mm 0; page-break-after:avoid; border-bottom:1.2px solid #0f2a47; padding-bottom:1mm; }
table { width:100%; border-collapse:collapse; margin-bottom:3mm; table-layout:fixed; }
thead { display:table-header-group; }
th { text-align:left; font-weight:600; font-size:8pt; color:#0f2a47; background:#e8eef5; padding:1.6mm 1.8mm; border-bottom:1px solid #9fb3c8; }
td { padding:1.5mm 1.8mm; border-bottom:0.5px solid #d8dee6; vertical-align:top; }
tr { page-break-inside:avoid; }
tbody tr:nth-child(even) td { background:#f7f9fb; }
td.org { font-weight:600; color:#0f2a47; }
td.pic { color:#374151; }
.chip { display:inline-block; font-size:7pt; font-weight:600; padding:0.2mm 1.6mm; border-radius:2mm; margin-bottom:0.8mm; }
.chip.ok { background:#dcfce7; color:#14532d; } .chip.ver { background:#fef3c7; color:#78350f; }
.chip.res { background:#fee2e2; color:#7f1d1d; } .chip.pub { background:#e5e7eb; color:#1f2937; }
.perg { display:grid; grid-template-columns:repeat(3,1fr); gap:2.5mm; margin:2mm 0 4mm 0; }
.perg div { border:0.6px solid #c9d3de; border-left:3px solid #0f2a47; padding:2mm 2.5mm; background:#fbfcfd; }
.perg b { display:block; color:#0f2a47; font-size:9.5pt; margin-bottom:0.6mm; }
.perg small { color:#6b7280; display:block; margin-top:0.8mm; }
.legenda { margin:2mm 0 3mm 0; } .legenda .chip { margin-right:2mm; }
ol.prior { padding-left:5mm; margin:1mm 0 0 0; column-count:2; column-gap:8mm; }
ol.prior li { margin-bottom:1.6mm; break-inside:avoid; } ol.prior b { color:#0f2a47; }
.nota { page-break-inside:avoid; border:0.6px solid #c9d3de; background:#f7f9fb; padding:2.5mm 3mm; margin-top:3mm; }
.capa { page-break-after:always; } .capa .bloco { margin-top:16mm; }
"""

LARGURAS = ["17%", "25%", "14%", "14%", "19%", "11%"]


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def documento_html() -> str:
    H = ["<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>",
         "<title>Mapa de integrações — Plataforma de Inteligência de Combustíveis</title>",
         "<style>", CSS.replace("DATA", DATA_VERIFICACAO), "</style></head><body>",
         "<section class='capa'><div class='bloco'>",
         "<h1>Mapa de integrações</h1>",
         "<p class='sub'>Quais integrações e dados a Plataforma de Inteligência de Combustíveis precisa, "
         "por órgão e por empresa, para ficar completa — e o que já existe.</p>",
         f"<p class='meta'>Verificação de existência na fonte em {DATA_VERIFICACAO}. "
         "Documento de trabalho para discussão com parceiros institucionais.</p>",
         "<h2>As seis perguntas que uma plataforma completa responde</h2><div class='perg'>"]
    H += [f"<div><b>{esc(p)}</b>{esc(d)}<small>{esc(q)}</small></div>" for p, d, q in PERGUNTAS]
    H += ["</div>",
          "<div class='legenda'><b>Como ler o acesso:</b> <span class='chip ok'>verificado</span> página ou "
          "recurso existe na fonte nesta data (o layout, só quando dito) · <span class='chip ver'>a verificar</span> "
          "conhecido, ainda não verificado · <span class='chip res'>restrito / parceria / pago</span> convênio, "
          "contrato, adesão ou base legal · <span class='chip pub'>público</span> estável, sem verificação nova.</div>",
          "<div class='nota'>Cada fonte serve a pelo menos uma das seis perguntas. O valor de uma integração é "
          "medido por quantas perguntas ela fecha para o mesmo <code>posto_id</code> — e nenhuma fonte, pública ou "
          "restrita, autoriza a plataforma a afirmar conduta: ela mostra fato, fonte e data e recomenda verificação; "
          "quem conclui é o órgão competente.</div>",
          f"<div class='nota'><b>Estado atual.</b> {esc(ESTADO)}</div>",
          "</div></section>"]
    colgroup = "<colgroup>" + "".join(f"<col style='width:{w}'>" for w in LARGURAS) + "</colgroup>"
    for titulo, linhas in GRUPOS:
        H.append(f"<h2>{esc(titulo)}</h2><table>{colgroup}<thead><tr>"
                 "<th>Órgão / empresa</th><th>Dados</th><th>Integração</th><th>Acesso</th>"
                 "<th>Destrava</th><th>Na plataforma hoje</th></tr></thead><tbody>")
        for org, dados, integ, acesso, st, destrava, pic in linhas:
            _, rotulo, classe = STATUS[st]
            extra = "" if acesso.strip().lower() in ("restrito", "parceria", "pago", "público") else "<br>" + esc(acesso)
            H.append(f"<tr><td class='org'>{esc(org)}</td><td>{esc(dados)}</td><td>{esc(integ)}</td>"
                     f"<td><span class='chip {classe}'>{rotulo}</span>{extra}</td>"
                     f"<td>{esc(destrava)}</td><td class='pic'>{esc(pic)}</td></tr>")
        H.append("</tbody></table>")
    H.append("<h2>Ordem de prioridade</h2><ol class='prior'>")
    H += [f"<li><b>{esc(t)}</b> — {esc(d)}</li>" for t, d in PRIORIDADE]
    H += ["</ol>", f"<div class='nota'><b>Fila de verificação na fonte.</b> {esc(FILA)}</div>", "</body></html>"]
    return "".join(H)


if __name__ == "__main__":
    OUT_MD.write_text(markdown(), encoding="utf8")
    print(f"escrito {OUT_MD.relative_to(RAIZ)}")
    if "--so-md" not in sys.argv:
        from weasyprint import HTML
        HTML(string=documento_html()).write_pdf(OUT_PDF)
        print(f"escrito {OUT_PDF.relative_to(RAIZ)}")
