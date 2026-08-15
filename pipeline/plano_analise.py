# -*- coding: utf-8 -*-
"""Bloco 1 do plano: consolida os 4 ciclos (2018/2020/2022/2024) por local de
votação e testa a hipótese do corredor universitário/tech.

Regras de agregação: SEMPRE por local (zona+nº do local) — as seções são
renumeradas entre ciclos. Fatos verificados nos dados e registrados aqui:
  - NOVO não lançou candidatos a dep. estadual em SC em 2018 (zero nominal e
    zero legenda) — a base "liberal 2018" é o Bruno Souza, que naquele ano
    concorreu pelo PSB (nº 40030) e se filiou ao NOVO em nov/2019.
  - Em 2022 Bruno Souza concorreu a dep. FEDERAL pelo NOVO (nº 3020).
"""

import json

import numpy as np
import pandas as pd

from . import config
from .util import chave_local, norm_txt

BRUNO_2018_NR = 40030   # dep. estadual 2018 (PSB à época; liberal de referência)
BRUNO_2022_NR = 3020    # dep. federal 2022 (NOVO)


def _carrega(ano):
    v = pd.read_parquet(config.DIR_PROC / f"votacao_{ano}.parquet")
    v["chave"] = chave_local(v)
    v["NR_VOTAVEL"] = pd.to_numeric(v["NR_VOTAVEL"], errors="coerce")
    return v[v["NR_TURNO"] == 1]


def _cargo(v, nome):
    return v[v["DS_CARGO"].map(norm_txt) == norm_txt(nome)]


def _soma(df, mask, nome):
    s = df[mask].groupby("chave")["QT_VOTOS"].sum()
    s.name = nome
    return s


def _partido_prop(df, nr):
    nv = df["NR_VOTAVEL"]
    nominal = ((nv >= 1000) & (nv <= 99999)
               & (nv.astype("Int64").astype(str).str[:2] == str(nr)))
    return nominal | (nv == nr)


def montar_plano_locais() -> pd.DataFrame:
    """Tabela final por local: métricas 2022/2024 já existentes + 2018/2020."""
    base = pd.read_parquet(config.DIR_PROC / "tabela_locais_final.parquet")

    # ---- 2018 (geral): NOVO federal, Bruno estadual, válidos ----
    v18 = _carrega(2018)
    est18, fed18 = _cargo(v18, "Deputado Estadual"), _cargo(v18, "Deputado Federal")
    m18 = pd.concat([
        _soma(est18, ~est18["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS), "validos_est_18"),
        _soma(est18, est18["NR_VOTAVEL"] == BRUNO_2018_NR, "votos_bruno_18"),
        _soma(fed18, ~fed18["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS), "validos_fed_18"),
        _soma(fed18, _partido_prop(fed18, 30), "votos_novo_fed_18"),
    ], axis=1)

    # ---- 2020 (municipal): NOVO e PL vereador ----
    v20 = _carrega(2020)
    ver20 = _cargo(v20, "Vereador")
    m20 = pd.concat([
        _soma(ver20, ~ver20["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS), "validos_ver_20"),
        _soma(ver20, _partido_prop(ver20, 30), "votos_novo_ver_20"),
        _soma(ver20, _partido_prop(ver20, 22), "votos_pl_ver_20"),
    ], axis=1)

    # ---- Bruno federal 2022 (referência liberal mais recente) ----
    v22 = _carrega(2022)
    fed22 = _cargo(v22, "Deputado Federal")
    m22x = _soma(fed22, fed22["NR_VOTAVEL"] == BRUNO_2022_NR, "votos_bruno_fed_22").to_frame()

    tab = base.join(m18, how="left").join(m20, how="left").join(m22x, how="left")

    for c in m18.columns.tolist() + m20.columns.tolist() + ["votos_bruno_fed_22"]:
        tab[c] = pd.to_numeric(tab[c], errors="coerce").astype("float64")

    tab["pct_bruno_18"] = tab["votos_bruno_18"] / tab["validos_est_18"]
    tab["pct_novo_fed_18"] = tab["votos_novo_fed_18"] / tab["validos_fed_18"]
    tab["pct_bruno_fed_22"] = tab["votos_bruno_fed_22"] / tab["validos_dep_fed_22"]
    tab["votos_direita_ver_20"] = tab["votos_novo_ver_20"] + tab["votos_pl_ver_20"]
    tab["pct_direita_ver_20"] = tab["votos_direita_ver_20"] / tab["validos_ver_20"]
    tab["pct_novo_ver_20"] = tab["votos_novo_ver_20"] / tab["validos_ver_20"]
    tab["pct_novo_ver_24"] = tab["votos_novo_ver_24"] / tab["validos_ver_24"]

    # tendência da direita 2020 -> 2024 (pontos percentuais)
    tab["tendencia_20_24"] = tab["pct_direita_ver_24"] - tab["pct_direita_ver_20"]
    # tendência do voto LIBERAL (só NOVO), para separar do efeito PL/bolsonarista
    tab["tendencia_novo_20_24"] = tab["pct_novo_ver_24"] - tab["pct_novo_ver_20"]

    tab.to_parquet(config.DIR_PROC / "plano_locais.parquet")
    return tab


def testar_hipotese(tab: pd.DataFrame) -> dict:
    """Hipótese: o eleitorado natural do Cadorin é o corredor universitário/
    tech, não o bairro mais rico. Testa com os dados e devolve os achados."""
    b = tab.groupby("bairro_ibge").agg(
        aptos=("aptos", "sum"),
        novo24=("votos_novo_ver_24", "sum"), val24=("validos_ver_24", "sum"),
        novo22=("votos_novo_dep_est_22", "sum"), val22=("validos_dep_est_22", "sum"),
        matheus=("votos_matheus_22", "sum"),
        bruno18=("votos_bruno_18", "sum"), val18=("validos_est_18", "sum"),
        brunofed22=("votos_bruno_fed_22", "sum"), valfed22=("validos_dep_fed_22", "sum"),
        superior=("pct_superior", "mean"), jovem=("pct_16a24", "mean"),
    )
    b = b[b["aptos"] >= 1500]
    b["pct_novo24"] = b["novo24"] / b["val24"]
    b["pct_novo22"] = b["novo22"] / b["val22"]
    b["pct_bruno18"] = b["bruno18"] / b["val18"]
    b["pct_brunofed22"] = b["brunofed22"] / b["valfed22"]

    corr_sup = float(b["pct_novo24"].corr(b["superior"]))
    corr_jov = float(b["pct_novo24"].corr(b["jovem"]))

    achados = {
        "corr_novo24_superior": round(corr_sup, 3),
        "corr_novo24_jovem": round(corr_jov, 3),
        "top_novo24": (b["pct_novo24"].nlargest(10) * 100).round(1).to_dict(),
        "top_bruno18": (b["pct_bruno18"].nlargest(10) * 100).round(1).to_dict(),
        "top_brunofed22": (b["pct_brunofed22"].nlargest(10) * 100).round(1).to_dict(),
        "matheus_por_bairro": b[b["matheus"] > 0]["matheus"].astype(int)
                               .sort_values(ascending=False).to_dict(),
    }
    (config.DIR_PROC / "plano_achados.json").write_text(
        json.dumps(achados, ensure_ascii=False, indent=1, default=str))
    return achados


if __name__ == "__main__":
    t = montar_plano_locais()
    a = testar_hipotese(t)
    print(json.dumps(a, ensure_ascii=False, indent=1, default=str))
