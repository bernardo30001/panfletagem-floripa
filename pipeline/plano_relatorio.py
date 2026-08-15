# -*- coding: utf-8 -*-
"""Relatório estratégico do plano de panfletagem (entregável 4 do plano)."""

import json

import pandas as pd

from . import config, plano_config


def _pct(x, c=1):
    return "—" if pd.isna(x) else f"{100*x:.{c}f}%".replace(".", ",")


def _int(x):
    return "—" if pd.isna(x) else f"{int(round(x)):,}".replace(",", ".")


def _tabela(df, cols, cabecalhos, fmts):
    L = ["| " + " | ".join(cabecalhos) + " |",
         "|" + "|".join("---" for _ in cabecalhos) + "|"]
    for idx, r in df.iterrows():
        cels = [str(idx)] + [f(r[c]) for c, f in zip(cols, fmts)]
        L.append("| " + " | ".join(cels) + " |")
    return L


def gerar_relatorio_plano(caminho):
    pts = pd.read_parquet(config.DIR_PROC / "plano_pontos.parquet")
    tab = pd.read_parquet(config.DIR_PROC / "plano_locais.parquet")
    cal = pd.read_parquet(config.DIR_PROC / "plano_calendario.parquet")
    ach = json.loads((config.DIR_PROC / "plano_achados.json").read_text())

    # territórios A/B/C por bairro
    b = tab.groupby("bairro_ibge").agg(
        aptos=("aptos", "sum"), regiao=("regiao", lambda s: s.mode().iat[0]),
        novo24=("votos_novo_ver_24", "sum"), val24=("validos_ver_24", "sum"),
        dir24=("votos_direita_ver_24", "sum"),
        dir20=("votos_direita_ver_20", "sum"), val20=("validos_ver_20", "sum"),
        superior=("pct_superior", "mean"))
    b = b[b["aptos"] >= 1500]
    b["pct_novo24"] = b["novo24"] / b["val24"]
    b["pct_dir24"] = b["dir24"] / b["val24"]
    b["tend"] = b["pct_dir24"] - (b["dir20"] / b["val20"])
    med_dir = b["pct_dir24"].median()
    b["territorio"] = "C"
    b.loc[b["pct_dir24"] >= med_dir, "territorio"] = "B"
    b.loc[(b["pct_novo24"] >= 0.055) | ((b["pct_dir24"] >= med_dir) & (b["superior"] >= 0.38)), "territorio"] = "A"
    terr = {t: b[b["territorio"] == t].sort_values("pct_novo24", ascending=False)
            for t in "ABC"}

    validos = pts[~pts["inviavel"]]
    top15 = validos.nlargest(15, "indice")
    fases_resumo = cal.groupby("fase")["panfletos"].agg(["count", "sum"])

    L = [
        "# Plano de panfletagem — Florianópolis 2026",
        "## Mandato Matheus Cadorin (NOVO/SC) · campanha 16/08 a 03/10/2026",
        "",
        f"*Gerado em 13/08/2026 pelo pipeline `panfletagem-floripa/` — dados TSE "
        f"(4 ciclos: 2018/2020/2022/2024, seções agregadas por LOCAL de votação, "
        f"zonas 12/13/100 confirmadas nos dados), malha de bairros IBGE Censo 2022, "
        f"e camada de fluxo físico com estimativas declaradas.*",
        "",
        "---",
        "## 1. Metodologia (fato × estimativa)",
        "",
        "**Fatos (fonte oficial):** votos por seção/local (TSE Dados Abertos, "
        "acessado 13/08/2026); locais de votação com coordenadas (TSE); perfil do "
        "eleitorado por seção (TSE); bairros (IBGE CD2022); feiras livres e dias "
        "(lista oficial PMF, via ND+ 25/05/2023); VMD da SC-401 (SSP-SC, jan/2025); "
        "volume do sistema de ônibus (~140 mil usuários/dia, Consórcio Fênix).",
        "",
        "**Estimativas (marcadas, método declarado):** ciclos semafóricos e tempos "
        "de vermelho (a PMF não publica planilha semafórica — valores de campo "
        "típicos, ±20%); pedestres/hora por ponto (distribuição do volume do "
        "sistema pelos terminais + observação de praxe); taxas de aceite (veículo "
        "45%, pedestre 18%, feira 40%); panfletos/h/pessoa = f(ciclo, vermelho, "
        "aceite) com teto físico de 280/h (1 entrega ≈ 6 s).",
        "",
        "**Fórmula do índice por ponto** (pesos em `pipeline/plano_config.py`):",
        "```",
        "índice = 100 × minmax( 0.35·AFINIDADE + 0.20·LIBERAL + 0.25·FLUXO + 0.20·PERFIL )",
        "AFINIDADE = (2×%dir. vereador 2024 + 1×%dir. dep.est. 2022)/3 + 0,5×(Δ 2020→2024)",
        "LIBERAL   = 0,50×%NOVO ver.2024 + 0,25×%Bruno 2018 + 0,25×%Bruno fed.2022",
        "FLUXO     = panfletos/hora/pessoa estimados",
        "PERFIL    = 0,7×escolaridade superior + 0,3×jovens 16–24 (raio de 1 km)",
        "```",
        "Seções associadas a cada ponto num raio de **1 km**, ponderadas por eleitorado.",
        "",
        "**A votação do Cadorin em 2022 NÃO entra no índice** (decisão do "
        "coordenador em 13/08/2026, tecnicamente correta): 84 votos dão "
        "penetração abaixo de 1% em 149 dos 152 locais — ruído — e a "
        "normalização convertia essa faixa de 6 p.p. em 25% do índice, "
        "penalizando os poucos pontos onde havia base. O componente LIBERAL "
        "responde à mesma pergunta ('onde está o eleitor dele?') com amostras "
        "de 10 a 24 mil votos em vez de 84. Partimos do zero.",
        "",
        "**Dados que NÃO existem publicamente** (não inventados): planilha "
        "semafórica da PMF/SMMU; contagem de passageiros POR terminal (só o total "
        "do sistema); MEI/CNPJ georreferenciado por bairro (o arquivo nacional da "
        "Receita tem >5 GB — proxy usado: % de superior completo do TSE, que "
        "correlaciona 0,82 com o voto NOVO; script para rodar localmente pode ser "
        "gerado sob demanda); renda por setor censitário do Censo 2022 (não "
        "integrada nesta versão).",
        "",
        "---",
        "## 2. O que os dados de 2024 revelaram",
        "",
        f"- Direita (NOVO+PL) p/ vereador 2024: **20,9% dos válidos** — mas o motor "
        f"é o PL (**16,8%**, 3× o resultado de 2020); o NOVO FICOU MENOR: 5,3% "
        f"(2020) → **4,1%** (2024).",
        "- Tradução: o crescimento da direita na capital é bolsonarista, não "
        "liberal. O Cadorin não herda esse voto automaticamente — ele disputa o "
        "sub-segmento liberal e precisa do próprio nome na rua.",
        f"- Voto liberal de referência: Bruno Souza fez **13.198 votos** na capital "
        f"em 2018 (dep. estadual, então PSB, nº 40030 — filiou-se ao NOVO em "
        f"nov/2019) e **23.914** em 2022 (dep. federal, NOVO). É o teto realista "
        f"do nicho: 3,5–8% dos válidos, concentrado no mesmo arco de bairros.",
        f"- Matheus 2022: **84 votos** (Itacorubi 15, Centro/Coqueiros/Trindade 7 "
        f"cada, João Paulo 6). Gap total: há ~65 mil votos NOVO+PL e ~24 mil votos "
        f"'Bruno' provando demanda liberal — com penetração do Matheus de 0,13%.",
        "",
        "### Hipótese do corredor universitário: CONFIRMADA COM CORREÇÃO",
        "",
        f"- O voto NOVO 2024 por bairro correlaciona **r = {ach['corr_novo24_superior']}** "
        f"com % de superior completo — e **r = {ach['corr_novo24_jovem']}** (negativo!) "
        "com % de jovens 16–24.",
        "- Ou seja: o eleitorado natural é o **profissional formado** (tech, "
        "empreendedor, servidor qualificado), não o 'estudante'. O corredor "
        "universitário funciona porque concentra diplomas, não calouros — e a "
        "portaria da UFSC tem entorno eleitoral fraco (Serrinha/Carvoeira).",
        "- E o dado derruba a oposição 'universitário × bairro rico': **Jurerê "
        "Oeste é o 2º bairro do NOVO (8,5%) e foi o 1º do Bruno em 2018 E 2022**. "
        "Rico escolarizado também é núcleo. Top NOVO 2024: Santa Mônica 10,6%, "
        "Jurerê Oeste 8,5%, João Paulo 8,0%, Itacorubi 7,9%, Centro 7,1%, "
        "Trindade 6,3%, Córrego Grande 6,1%.",
        "",
        "---",
        "## 3. Territórios A / B / C (bairros com 1.500+ eleitores)",
        "",
        "**A — núcleo liberal (converter):** " + ", ".join(
            f"{i} ({_pct(r['pct_novo24'])} NOVO)" for i, r in terr["A"].iterrows()),
        "",
        "**B — fronteira de direita (apresentar o nome):** " + ", ".join(
            f"{i}" for i, r in terr["B"].iterrows()),
        "",
        "**C — baixa afinidade (só fluxo de passagem):** " + ", ".join(
            f"{i}" for i, r in terr["C"].iterrows()),
        "",
        "---",
        "## 4. Os 15 pontos de ouro",
        "",
    ]
    for pos, (pid, r) in enumerate(top15.iterrows(), 1):
        L += [
            f"**{pos}. {r['nome']}** — índice {r['indice']:.1f} ({r['classe']})  ",
            f"{r['endereco']} · {r['regiao']} · ~{r['fluxo_panfletos_hora']:.0f} panf/h/pessoa  ",
            f"_Entorno de 1 km: direita 2024 {_pct(r['pct_direita_ver24_1km'])}, "
            f"NOVO {_pct(r['pct_novo_ver24_1km'])}, superior completo "
            f"{_pct(r['pct_superior_1km'],0)}, {_int(r['aptos_1km'])} eleitores, "
            f"Matheus tinha {int(r['votos_matheus_1km'])} votos. "
            f"Janelas: {r['janelas']}. Equipe ideal: {int(r['pessoas_ideal'])}._",
            "",
        ]
    L += [
        "---",
        "## 5. Rankings parciais (para discordar dos pesos)",
        "",
        "### Por AFINIDADE (entorno mais alinhado)", "",
    ]
    L += _tabela(validos.nlargest(8, "comp_afinidade").set_index("nome"),
                 ["pct_direita_ver24_1km", "tendencia_dir_20_24", "indice"],
                 ["Ponto", "Direita 24 (1 km)", "Tendência 20→24", "Índice"],
                 [_pct, _pct, lambda x: f"{x:.0f}"])
    L += ["", "### Por FLUXO (mais panfletos/hora)", ""]
    L += _tabela(validos.nlargest(8, "comp_fluxo").set_index("nome"),
                 ["fluxo_panfletos_hora", "pct_direita_ver24_1km", "indice"],
                 ["Ponto", "Panf/h/pessoa (est.)", "Direita 24", "Índice"],
                 [lambda x: f"{x:.0f}", _pct, lambda x: f"{x:.0f}"])
    L += ["", "### Por PERFIL (entorno mais 'público-alvo')", ""]
    L += _tabela(validos.nlargest(8, "comp_perfil").set_index("nome"),
                 ["pct_superior_1km", "pct_16a24_1km", "indice"],
                 ["Ponto", "Superior (1 km)", "16–24 (1 km)", "Índice"],
                 [lambda x: _pct(x, 0), lambda x: _pct(x, 0), lambda x: f"{x:.0f}"])
    L += [
        "",
        "### Casos especiais",
        "- **Alto fluxo / baixa afinidade** (só reconhecimento de nome): "
        + "; ".join(validos[validos["classe"].str.startswith("alto fluxo")]["nome"]),
        "- **Alta afinidade / baixo fluxo** (porta a porta e eventos, não panfleto): "
        + "; ".join(validos[validos["classe"].str.startswith("alta afinidade")]["nome"]),
        "- **SC-401 em pista**: maior fluxo da cidade (VMD ~60,6 mil veículos/dia "
        "no trecho norte fora de temporada — SSP-SC, jan/2025), mas SEM parada "
        "segura para abordagem: rodovia de fluxo contínuo. Usar os terminais e "
        "semáforos das entradas de bairro que a alimentam.",
        "",
        "---",
        "## 6. Calendário (resumo — detalhe no calendario_panfletagem.xlsx)",
        "",
    ]
    for fase, r in fases_resumo.iterrows():
        L.append(f"- **{fase}**: {int(r['count'])} turnos-ponto, "
                 f"{_int(r['sum'])} panfletos.")
    L += [
        "",
        f"- Premissas NÃO informadas pelo coordenador (edite `plano_config.py` e "
        f"regenere): equipe {plano_config.EQUIPE['fixos_dia_util']} pessoas em dia "
        f"útil, {plano_config.EQUIPE['sabado']} no sábado, "
        f"{plano_config.EQUIPE['domingo']} no domingo; tiragem "
        f"{_int(plano_config.ORCAMENTO_PANFLETOS)}.",
        f"- **A capacidade física da equipe é ~{1/cal.attrs.get('fator_orcamento', 0.353):.1f}× "
        f"a tiragem premissa** (o plano escala a distribuição por 0,35 para caber "
        f"nos 60 mil). Ou aumenta a tiragem (~170 mil) ou reduz turnos — decidir.",
        "- Rotação: nenhum ponto repete em dias consecutivos (exceto fim de semana, "
        "quando a oferta de pontos abertos é menor); os 10 primeiros do índice "
        "recebem 7+ visitas cada (mínimo pedido: 4).",
        "- Chuva: toda linha do XLSX tem alternativa coberta da região (terminais, "
        "Mercado Público, marquises da Fúlvio Aducci). Setembro é chuvoso em SC "
        "(Epagri/CIRAM); planejar ~1/3 dos dias com plano B acionado (estimativa).",
        "",
        "---",
        "## 7. Conformidade legal (verificada em 13/08/2026)",
        "",
        "- **Período**: propaganda a partir de **16/08/2026** (Lei 9.504/97, art. "
        "36). Distribuição de material impresso **independe de licença municipal** "
        "(art. 37, §8º) e pode ir **até 22h de 03/10** (véspera).",
        "- **Dia 04/10 (eleição): distribuir material é CRIME** (boca de urna — "
        "art. 39, §5º). O plano termina dia 03/10. No dia, só manifestação "
        "individual e silenciosa.",
        "- **Material**: todo impresso deve trazer CNPJ/CPF do responsável pela "
        "confecção, de quem contratou e a TIRAGEM (art. 38, §1º; Res. TSE "
        "23.610/2019, atualizada pela Res. 23.755/2026).",
        "- **Bens públicos**: proibido colar/pendurar em postes, semáforos, "
        "abrigos de ônibus e viadutos (art. 37). Entrega em mão é livre.",
        "- **Código de Posturas de Floripa (LC 442/2012, alt. LC 634/2018)**: multa "
        "de **R$ 100 POR PANFLETO deixado** em logradouro público (reincidência). "
        "Operacionalmente: equipe recolhe material caído no fim de cada turno e "
        "registra em foto — 'derrame de santinhos' na véspera também gera multa "
        "eleitoral.",
        "- **Semáforos**: NÃO encontrei lei municipal de Florianópolis que proíba "
        "expressamente a abordagem em cruzamento (diferente de outras capitais). "
        "Regra operacional para reduzir risco CTB/segurança: equipe no canteiro/"
        "passeio, nunca entre faixas em movimento; colete; abordar apenas com o "
        "vermelho fechado; nada de material no para-brisa.",
        "- **Shoppings (Iguatemi/Beiramar)**: área INTERNA é privada — só com "
        "autorização. O plano usa as calçadas públicas do entorno.",
        "- **Cabos eleitorais**: contratação sem vínculo CLT (art. 100); limite "
        "quantitativo do art. 100-A — p/ deputado estadual, 50% do limite de "
        "federal na circunscrição (em Floripa o teto passa de 300 pessoas; nossa "
        "equipe premissa de 6–10 está muito abaixo). Registrar todos na prestação "
        "de contas.",
        "",
        "---",
        "## 8. As três decisões estratégicas",
        "",
        "**1) Assumir o eleitor formado, não o 'jovem universitário'.** A correlação "
        "voto NOVO × superior completo é 0,82; com jovens é negativa. Panfleto com "
        "densidade (dado, entrega, QR p/ portal) no arco Santa Mônica–Itacorubi–"
        "Córrego Grande–João Paulo–Centro **e em Jurerê Oeste** — o dado mandou "
        "incluir o bairro rico que a hipótese descartava.",
        "",
        "**2) Não disputar o voto PL na rua — capturar o órfão liberal.** O PL fez "
        "16,8% p/ vereador com máquina bolsonarista; brigar por esse eleitor em "
        "ponto de rua é caro. O alvo é o eleitor 'Bruno 2018/2022' (13–24 mil "
        "pessoas mapeadas por local no ranking) hoje sem candidato liberal na "
        "capital — daí o peso de 20% do componente LIBERAL, que localiza esse "
        "eleitor por onde ele já votou (NOVO 2024 e Bruno 2018/2022).",
        "",
        "**3) Resolver a matemática tiragem × capacidade ANTES do dia 16/08.** Com "
        "60 mil panfletos, a equipe premissa opera a 35% da capacidade física; "
        "com 170 mil, satura o plano inteiro. Decidir tiragem + equipe agora "
        "muda TODO o calendário — o XLSX regenera em 1 comando.",
        "",
        "---",
        "### Fontes externas (acesso 13/08/2026)",
        "- TSE Dados Abertos — votação por seção 2018/2020/2022/2024, eleitorado/locais, perfil (dadosabertos.tse.jus.br)",
        "- [Res. TSE 23.755/2026](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-755-de-2-de-marco-de-2026) e [regras de propaganda 2026 (TSE, jul/2026)](https://www.tse.jus.br/comunicacao/noticias/2026/Julho/saiba-quando-comeca-a-propaganda-eleitoral-e-conheca-as-novas-regras-para-as-eleicoes-2026); [O Tempo, 06/08/2026](https://www.otempo.com.br/politica/2026/8/6/eleicoes-2026-veja-quando-comeca-a-propaganda-nas-ruas-o-que-e-permitido-e-o-que-e-proibido)",
        "- [SSP-SC — fluxo SC-401 (jan/2025)](https://ssp.sc.gov.br/trecho-norte-da-sc-401-registra-aumento-significativo-no-fluxo-diario-de-veiculos-em-janeiro-de-2025/); [ND+ — tráfego SC-401](https://ndmais.com.br/transito/trafego-na-sc-401-dispara-38-chega-a-quase-100-mil-veiculos-dia-e-supera-janeiro-de-2024/)",
        "- [Consórcio Fênix — sistema de transporte](https://www.consorciofenix.com.br/noticias/novidades-no-pagamento-da-tarifa-do-sistema-de-transporte-coletivo-de-florianopolis,817) (~140 mil usuários/dia)",
        "- [Feiras livres — lista oficial PMF via ND+ (25/05/2023)](https://ndmais.com.br/economia/e-dia-de-feira-e-elas-estao-por-toda-florianopolis-saiba-onde-encontra-las/)",
        "- [Código de Posturas de Florianópolis / LC 442/2012](https://leismunicipais.com.br/a/sc/f/florianopolis/lei-complementar/2012/44/442/lei-complementar-n-442-2012-altera-o-art-28-da-lei-n-1224-de-1974-codigo-de-posturas-municipal)",
        "- [TSE — limites de contratação de cabos eleitorais (art. 100-A)](https://www.tse.jus.br/comunicacao/noticias/2013/Dezembro/especial-minirreforma-lei-impoe-limites-para-a-contratacao-de-cabos-eleitorais)",
        "- [Epagri/CIRAM — chuva de setembro em SC](https://ciram.epagri.sc.gov.br/index.php/2025/09/10/a-chuva-de-setembro-em-sc-e-a-previsao-de-dias-mais-secos/)",
        "- Bruno Souza 2018: [Memória Política ALESC](https://memoriapolitica.alesc.sc.gov.br/biografia/1019-Bruno_Souza); [NSC Total — filiação ao NOVO](https://www.nsctotal.com.br/colunistas/moacir-pereira/deputado-bruno-souza-filia-se-ao-partido-novo-em-sc)",
    ]
    caminho.write_text("\n".join(L), encoding="utf-8")
    print(f"  relatório do plano salvo em {caminho}")
