# -*- coding: utf-8 -*-
"""Entregáveis 2, 3 e 4: ranking_panfletagem.csv, top20_roteiro.md e
relatorio.md (leitura analítica + extras)."""

import pandas as pd

from . import config
from .metricas import AVISOS
from .util import norm_txt


def _pct(x, casas=1):
    return "—" if pd.isna(x) else f"{100 * x:.{casas}f}%".replace(".", ",")


def _int(x):
    return "—" if pd.isna(x) else f"{int(round(x)):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Entregável 2 — ranking em CSV
# ---------------------------------------------------------------------------

COLUNAS_CSV = [
    # identificação
    "nome", "endereco", "bairro_tse", "bairro_ibge", "regiao", "cep",
    "lat", "lon",
    # bloco 3
    "aptos", "aptos_2022", "aptos_2024", "n_secoes_2022",
    "comparecimento_22", "abstencao_22",
    # bloco 1 — 2022
    "validos_dep_est_22", "votos_novo_dep_est_22", "pct_novo_dep_est_22",
    "votos_pl_dep_est_22", "pct_pl_dep_est_22",
    "votos_direita_dep_est_22", "pct_direita_dep_est_22",
    "validos_dep_fed_22", "votos_novo_dep_fed_22", "pct_novo_dep_fed_22",
    "votos_pl_dep_fed_22", "pct_pl_dep_fed_22",
    "votos_direita_dep_fed_22", "pct_direita_dep_fed_22",
    "votos_bolsonaro_22", "pct_bolsonaro_22",
    "votos_gov_novo_22", "pct_gov_novo_22", "votos_gov_pl_22", "pct_gov_pl_22",
    # bloco 1 — 2024
    "validos_ver_24", "votos_novo_ver_24", "pct_novo_ver_24",
    "votos_pl_ver_24", "pct_pl_ver_24",
    "votos_direita_ver_24", "pct_direita_ver_24",
    "top3_vereadores_direita", "prefeito_lider_24", "prefeito_2024_pct",
    # bloco 2
    "votos_matheus_22", "penetracao_matheus",
    # perfil
    "pct_16a24", "pct_60mais", "pct_superior", "pct_feminino",
    # índice
    "comp_potencial", "comp_liberal", "comp_densidade", "comp_consistencia",
    "flag_pequeno", "score",
]


def gerar_ranking_csv(tab: pd.DataFrame, caminho):
    cols = [c for c in COLUNAS_CSV if c in tab.columns]
    out = tab[cols].sort_values("score", ascending=False)
    # utf-8-sig -> abre com acentos corretos direto no Excel
    out.to_csv(caminho, encoding="utf-8-sig", sep=";", decimal=",",
               float_format="%.4f")
    print(f"  ranking salvo em {caminho}")


# ---------------------------------------------------------------------------
# Entregável 3 — roteiro dos 20 locais prioritários por região
# ---------------------------------------------------------------------------

def _justificativa(r) -> str:
    partes = [f"{_int(r['votos_direita_dep_est_22'])} votos de direita em 2022 "
              f"({_pct(r['pct_direita_dep_est_22'])} dos válidos)"]
    if pd.notna(r.get("pct_novo_ver_24")):
        partes.append(f"NOVO com {_pct(r['pct_novo_ver_24'])} em 2024")
    partes.append(f"{_int(r['aptos'])} eleitores no local")
    if pd.notna(r["abstencao_22"]) and r["abstencao_22"] > 0.22:
        partes.append(f"abstenção alta ({_pct(r['abstencao_22'])})")
    return "; ".join(partes) + "."


ORDEM_REGIOES = ["Centro", "Continente", "Norte da Ilha", "Sul da Ilha",
                 "Leste/Lagoa", "Outros"]


def gerar_top20(tab: pd.DataFrame, caminho):
    top = tab[~tab["flag_pequeno"]].nlargest(20, "score")
    linhas = [
        "# Top 20 locais prioritários para panfletagem — Florianópolis 2026",
        "",
        f"Critério: Índice de Prioridade (pesos: potencial "
        f"{config.PESOS_INDICE['potencial']:.2f}, liberal {config.PESOS_INDICE['liberal']:.2f}, "
        f"densidade {config.PESOS_INDICE['densidade']:.2f}, consistência "
        f"{config.PESOS_INDICE['consistencia']:.2f}). Fonte: TSE 2022/2024. "
        f"A votação do Matheus em 2022 não entra no cálculo.",
        "",
    ]
    for regiao in ORDEM_REGIOES:
        grupo = top[top["regiao"] == regiao]
        if grupo.empty:
            continue
        linhas.append(f"## {regiao} ({len(grupo)} locais)")
        linhas.append("")
        for chave, r in grupo.iterrows():
            pos = int(top.index.get_loc(chave)) + 1
            linhas += [
                f"**{pos}º — {r['nome']}** (score {r['score']:.1f})  ",
                f"{r['endereco']} — {r['bairro_ibge']}  ",
                f"_{_justificativa(r)}_",
                "",
            ]
    caminho.write_text("\n".join(linhas), encoding="utf-8")
    print(f"  roteiro salvo em {caminho}")


# ---------------------------------------------------------------------------
# Entregável 4 — relatório analítico
# ---------------------------------------------------------------------------

def _tabela_md(df, colunas, cabecalhos, formatos):
    linhas = ["| " + " | ".join(cabecalhos) + " |",
              "|" + "|".join("---" for _ in cabecalhos) + "|"]
    for idx, r in df.iterrows():
        cels = [str(idx)]
        for c, f in zip(colunas, formatos):
            cels.append(f(r[c]))
        linhas.append("| " + " | ".join(cels) + " |")
    return linhas


def _eleitos_direita_por_bairro(tab: pd.DataFrame) -> pd.Series:
    """Votos (por bairro) dos vereadores NOVO/PL ELEITOS em 2024 — base da
    análise de 'voto órfão'."""
    res = pd.read_parquet(config.DIR_PROC / "resultado_vereador_2024.parquet")
    eleitos = res[res["DS_SIT_TOT_TURNO"].map(norm_txt)
                  .isin({"ELEITO", "ELEITO POR QP", "ELEITO POR MEDIA"})]
    eleitos = eleitos[eleitos["NR_PARTIDO"].isin(config.PARTIDOS_DIREITA)]
    if eleitos.empty:
        return pd.Series(dtype=float)
    nums = set(eleitos["NR_CANDIDATO"].astype(int))

    from .util import chave_local
    v24 = pd.read_parquet(config.DIR_PROC / "votacao_2024.parquet")
    v24 = v24[(v24["DS_CARGO"].map(norm_txt) == "VEREADOR")
              & (v24["NR_TURNO"] == 1)]
    v24 = v24[pd.to_numeric(v24["NR_VOTAVEL"], errors="coerce").isin(nums)]
    v24["chave"] = chave_local(v24)
    por_local = v24.groupby("chave")["QT_VOTOS"].sum()
    bairro = tab["bairro_ibge"]
    return por_local.groupby(por_local.index.map(bairro)).sum()


def gerar_relatorio(tab: pd.DataFrame, agg: pd.DataFrame, caminho):
    w = config.PESOS_INDICE
    total_dir = tab["votos_direita_dep_est_22"].sum()
    total_val = tab["validos_dep_est_22"].sum()
    media_pct = total_dir / total_val
    ativos = agg[agg["aptos"] >= 1000]

    # clusters de bairro por % direita 2022
    p75 = ativos["pct_direita_22"].quantile(0.75)
    nucleo = ativos[ativos["pct_direita_22"] >= p75].sort_values(
        "pct_direita_22", ascending=False)
    fronteira = ativos[(ativos["pct_direita_22"] >= media_pct)
                       & (ativos["pct_direita_22"] < p75)].sort_values(
        "votos_direita_22", ascending=False)
    fraco = ativos[ativos["pct_direita_22"] < media_pct]

    # base do Matheus
    com_matheus = tab[tab["votos_matheus_22"] > 0].sort_values(
        "votos_matheus_22", ascending=False)

    # abstenção alta + potencial alto
    p75_abst = tab["abstencao_22"].quantile(0.75)
    abst_pot = tab[(tab["abstencao_22"] > p75_abst)
                   & (tab["score"] > tab["score"].median())
                   & (~tab["flag_pequeno"])].nlargest(8, "score")

    # voto órfão
    votos_eleitos = _eleitos_direita_por_bairro(tab)
    agg2 = agg.copy()
    agg2["votos_eleitos_direita"] = votos_eleitos.reindex(agg2.index).fillna(0)
    agg2["share_eleitos"] = (agg2["votos_eleitos_direita"]
                             / agg2["votos_direita_24"].replace(0, pd.NA))
    med24 = agg2["pct_direita_24"].median()
    orfaos = agg2[(agg2["pct_direita_24"] > med24)
                  & (agg2["share_eleitos"].fillna(0) < 0.35)
                  & (agg2["aptos"] >= 1000)].sort_values(
        "votos_direita_24", ascending=False)

    L = []
    L += [
        "# Relatório — Inteligência eleitoral para panfletagem",
        "## Florianópolis, ciclo 2026 · Mandato Matheus Cadorin (NOVO/SC)",
        "",
        f"*Gerado pelo pipeline em `panfletagem-floripa/` com dados abertos do "
        f"TSE (votação por seção 2022/2024, locais de votação, perfil do "
        f"eleitorado) e malha de bairros do Censo 2022 (IBGE).*",
        "",
        "---",
        "## 1. Números de partida",
        "",
        f"- **{len(tab)}** locais de votação analisados; **{_int(tab['aptos'].sum())}** eleitores aptos.",
        f"- Direita (NOVO+PL) p/ **dep. estadual 2022**: **{_int(total_dir)}** votos = **{_pct(media_pct)}** dos válidos "
        f"(NOVO {_pct(tab['votos_novo_dep_est_22'].sum()/total_val)}, PL {_pct(tab['votos_pl_dep_est_22'].sum()/total_val)}).",
        f"- Teto da direita (Bolsonaro 1º turno 2022): **{_pct(tab['votos_bolsonaro_22'].sum()/tab['validos_pres_22'].sum())}** — "
        "a distância entre o voto proporcional da direita e esse teto é eleitor alcançável.",
        f"- Direita p/ **vereador 2024**: {_pct(tab['votos_direita_ver_24'].sum()/tab['validos_ver_24'].sum())} dos válidos.",
        f"- **Matheus em 2022**: **{_int(tab['votos_matheus_22'].sum())} votos** na capital, presentes em "
        f"{len(com_matheus)} dos {len(tab)} locais — penetração média de "
        f"{_pct(tab['votos_matheus_22'].sum()/total_dir, 2)} sobre o voto de direita. "
        "Na prática, a capital é campo aberto: quase todo o voto de direita está disponível.",
        "",
        "---",
        "## 2. Como o Índice de Prioridade é calculado",
        "",
        "```",
        "score = 100 × minmax( 0.40·POTENCIAL + 0.25·LIBERAL + 0.20·DENSIDADE + 0.15·CONSISTÊNCIA )",
        "",
        "POTENCIAL    = votos absolutos NOVO+PL, dep. estadual 2022 (min-max)",
        "LIBERAL      = média do %NOVO p/ vereador 2024 e dep. estadual 2022 (min-max)",
        "DENSIDADE    = eleitores aptos do local (min-max)",
        "CONSISTÊNCIA = 1 − |%direita 2022 − %direita 2024| (min-max)",
        "```",
        "",
        f"Pesos e método de normalização em `pipeline/config.py` "
        f"(`PESOS_INDICE`, `NORMALIZACAO='{config.NORMALIZACAO}'`). Locais com "
        f"menos de {config.MIN_ELEITORES_LOCAL} eleitores recebem score 0 "
        "(`flag_pequeno`) — não valem hora de equipe.",
        "",
        "**A votação do Matheus em 2022 NÃO entra no score.** O componente "
        "anterior (GAP = 1 − penetração dele) foi removido: com 84 votos, a "
        "penetração fica abaixo de 1% em 149 dos 152 locais — é ruído — e a "
        "normalização esticava essa faixa de 6 p.p. para 0..1, transformando "
        "ruído em 35% do score e penalizando justamente os poucos locais onde "
        "havia base. No lugar entrou LIBERAL, que mede onde vive o eleitor-alvo "
        "com uma amostra ~700× maior. Os votos dele seguem no CSV e nos popups "
        "como diagnóstico, sem efeito no ranking. Premissa: começamos do zero.",
        "",
        "---",
        "## 3. Núcleo duro da direita (quartil superior de % NOVO+PL, bairros com 1.000+ eleitores)",
        "",
    ]
    L += _tabela_md(
        nucleo.head(12),
        ["regiao", "aptos", "votos_direita_22", "pct_direita_22",
         "pct_novo_22", "pct_pl_22", "votos_matheus_22", "score"],
        ["Bairro", "Região", "Aptos", "Votos direita 22", "% direita",
         "% NOVO", "% PL", "Matheus", "Score"],
        [str, _int, _int, _pct, _pct, _pct, _int,
         lambda x: f"{x:.1f}"])
    L += [
        "",
        "É onde a mensagem já tem audiência: material de reforço e recrutamento "
        "de voluntários rendem mais que persuasão.",
        "",
        "## 4. Fronteira competitiva (acima da média municipal, abaixo do núcleo)",
        "",
    ]
    L += _tabela_md(
        fronteira.head(12),
        ["regiao", "aptos", "votos_direita_22", "pct_direita_22",
         "abstencao_22", "score"],
        ["Bairro", "Região", "Aptos", "Votos direita 22", "% direita",
         "Abstenção 22", "Score"],
        [str, _int, _int, _pct, _pct, lambda x: f"{x:.1f}"])
    L += [
        "",
        "Volume alto e % intermediário = melhor custo-benefício de persuasão. "
        "É o coração do roteiro de panfletagem.",
        "",
        f"## 5. Onde o Matheus já tem base (e onde está zerado)",
        "",
        f"Os {_int(tab['votos_matheus_22'].sum())} votos de 2022 caíram assim:",
        "",
    ]
    if len(com_matheus):
        L += _tabela_md(
            com_matheus.head(10).set_index("nome"),
            ["bairro_ibge", "votos_matheus_22", "votos_direita_dep_est_22",
             "penetracao_matheus"],
            ["Local", "Bairro", "Votos Matheus", "Direita no local", "Penetração"],
            [str, _int, _int, lambda x: _pct(x, 2)])
    zerados = int((tab["votos_matheus_22"] == 0).sum())
    sem_dado = int(tab["votos_matheus_22"].isna().sum())
    L += [
        "",
        f"**{zerados} locais ({_pct(zerados/len(tab))}) estão zerados**"
        + (f" (outros {sem_dado} são locais criados em 2024, sem dado de 2022)."
           if sem_dado else ".")
        + " O voto "
        "existente concentra-se no eixo Centro–UFSC–Itacorubi (perfil "
        "universitário/liberal, aderente ao NOVO). A leitura estratégica: não há "
        "reduto a defender — TODO local de score alto é terreno de conquista.",
        "",
        "## 6. Perfil demográfico dos clusters (para calibrar linguagem do panfleto)",
        "",
    ]
    for nome, cluster in [("Núcleo duro", nucleo), ("Fronteira", fronteira),
                          ("Abaixo da média", fraco)]:
        if cluster.empty:
            continue
        pesos_b = cluster["aptos"]
        mede = lambda c: (cluster[c] * pesos_b).sum() / pesos_b.sum()
        L.append(f"- **{nome}** ({len(cluster)} bairros): "
                 f"{_pct(mede('pct_16a24'))} jovens (16–24), "
                 f"{_pct(mede('pct_60mais'))} com 60+, "
                 f"{_pct(mede('pct_superior'))} com superior completo, "
                 f"{_pct(mede('pct_feminino'))} mulheres.")
    L += [
        "",
        "Recomendações práticas:",
        "- Onde **superior completo** é alto (Centro, Itacorubi, Coqueiros): panfleto de dados — "
        "emendas, economia gerada, fiscalização; QR code para o portal do mandato.",
        "- Onde **60+** pesa (Estreito, Balneário, Canto): fonte maior, foco em saúde, "
        "segurança e previsibilidade; linguagem direta sem jargão liberal.",
        "- Onde **jovens** pesam (Trindade, Pantanal, Ingleses): estética de rede social, "
        "pauta de oportunidade/empreendedorismo, link para Instagram do mandato.",
        "",
        "---",
        "## 7. Abstenção alta + potencial alto (abordagem diferenciada)",
        "",
        f"Locais no quartil superior de abstenção 2022 (>{_pct(p75_abst)}) e score acima da mediana — "
        "aqui o panfleto precisa primeiro convencer a VOTAR:",
        "",
    ]
    L += _tabela_md(
        abst_pot.set_index("nome"),
        ["bairro_ibge", "abstencao_22", "votos_direita_dep_est_22", "score"],
        ["Local", "Bairro", "Abstenção 22", "Votos direita 22", "Score"],
        [str, _pct, _int, lambda x: f"{x:.1f}"])
    L += [
        "",
        "---",
        "## 8. Voto órfão (bairro forte em NOVO/PL sem vereador local eleito em 2024)",
        "",
        "Bairros acima da mediana de % direita p/ vereador em 2024 onde os "
        "vereadores ELEITOS de NOVO/PL captaram menos de 35% do voto de direita "
        "local — eleitor habituado a votar na sigla, sem 'dono' político no território:",
        "",
    ]
    if len(orfaos):
        L += _tabela_md(
            orfaos.head(10),
            ["regiao", "votos_direita_24", "pct_direita_24", "share_eleitos"],
            ["Bairro", "Região", "Votos direita ver. 24", "% direita 24",
             "% capturado por eleitos"],
            [str, _int, _pct, lambda x: _pct(x)])
    else:
        L.append("*Nenhum bairro se qualificou no corte atual (ajuste o limiar de 35% no código).*")
    L += [
        "",
        "---",
        "## 9. Pontos de fluxo × locais prioritários (rendimento por hora de equipe)",
        "",
        "Panfletagem em ponto de fluxo rende mais contatos/hora que porta a porta. "
        "Sugestão de alocação, cruzando os pontos com o score da região:",
        "",
        "| Ponto | Tipo | Região | Quando |",
        "|---|---|---|---|",
    ]
    for p in config.PONTOS_FLUXO:
        L.append(f"| {p['nome']} | {p['tipo'].title()} | {p['regiao']} | {p['dias_horarios']} |")
    L += [
        "",
        "Regras de bolso:",
        "- **Terminais no pico da manhã (7h–9h)**: maior volume bruto de contatos/hora; "
        "material curto, entrega rápida. TICEN e TITRI primeiro — concentram baldeações "
        "das regiões de maior score.",
        "- **Feiras e mercados no sábado de manhã**: menos volume, muito mais tempo de "
        "conversa; ideal para material denso e presença do deputado.",
        "- **Calçadões no almoço (11h30–14h)**: público economicamente ativo do Centro; "
        "bom para pauta de economia/impostos.",
        "- **Praças de bairro no fim de tarde**: famílias e 60+; pauta local (saúde, segurança).",
        "",
        "---",
        "## 10. Avisos de qualidade de dados",
        "",
    ]
    for a in (AVISOS or ["(nenhum)"]):
        L.append(f"- {a}")
    L += [
        "- Votação por local ≠ residência do eleitor: o eleitor vota onde tem título, "
        "que costuma acompanhar a residência, mas há defasagem (mudanças sem transferência).",
        "- % calculados sobre votos válidos (exclui brancos 95 e nulos 96).",
        "- Comparecimento estimado pela soma de todos os votos do cargo de dep. estadual "
        "(inclui brancos/nulos) — o TSE não publica comparecimento por local diretamente.",
        "",
        "## 11. Para recalcular com outros parâmetros",
        "",
        "Edite `pipeline/config.py` (pesos, partidos, candidato, mínimo de eleitores, "
        "normalização) e rode `python3 run_pipeline.py`. Os downloads ficam em cache "
        "em `data/raw/`; para forçar rebaixamento, apague o arquivo correspondente.",
    ]
    caminho.write_text("\n".join(L), encoding="utf-8")
    print(f"  relatório salvo em {caminho}")
