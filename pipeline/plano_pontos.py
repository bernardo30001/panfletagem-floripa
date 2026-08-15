# -*- coding: utf-8 -*-
"""Blocos 2 e 3: fluxo estimado por ponto físico e índice de priorização.

Para cada ponto do catálogo (plano_config.PONTOS):
  1. FLUXO: panfletos/hora/pessoa estimados pelo modelo declarado no config
     (semáforo: ciclo/vermelho/aceite; pedestre: pedestres-hora × aceite).
  2. ENTORNO: locais de votação num raio de 1 km (haversine) e suas métricas
     ponderadas por eleitorado.
  3. ÍNDICE: 0.35·AFINIDADE + 0.20·LIBERAL + 0.25·FLUXO + 0.20·PERFIL, cada
     componente normalizado min-max. AFINIDADE = (2×%direita ver. 2024 +
     1×%direita dep. est. 2022)/3, ajustada pela tendência 2020→2024
     (soma de 0,5×Δ, que entra "só como tendência", conforme o pedido).
     LIBERAL = 0,50×%NOVO ver. 2024 + 0,25×%Bruno 2018 + 0,25×%Bruno fed. 2022.

A votação do Cadorin (84 votos) NÃO entra no índice — ver plano_config.
"""

import numpy as np
import pandas as pd

from . import config, plano_config


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def fluxo_estimado(p: dict) -> float:
    """Panfletos/hora/pessoa (ESTIMATIVA — método em plano_config)."""
    if p.get("inviavel"):
        return 0.0
    if p["tipo"] == "semaforo":
        ciclos_hora = 3600 / p["ciclo_s"]
        abordagens = p["vermelho_s"] / plano_config.SEGUNDOS_POR_ENTREGA
        bruto = ciclos_hora * abordagens * plano_config.TAXA_ACEITE["veiculo"]
    else:
        taxa = (plano_config.TAXA_ACEITE["feira"] if p["tipo"] == "feira"
                else plano_config.TAXA_ACEITE["pedestre"])
        bruto = p["ped_hora"] * taxa / 2  # 2 pessoas de referência
    return round(min(bruto, plano_config.TETO_ENTREGAS_HORA), 0)


def montar_pontos() -> pd.DataFrame:
    tab = pd.read_parquet(config.DIR_PROC / "plano_locais.parquet")
    tab = tab.dropna(subset=["lat", "lon"])

    linhas = []
    for p in plano_config.PONTOS:
        d = _haversine_km(p["lat"], p["lon"], tab["lat"].values, tab["lon"].values)
        viz = tab[d <= plano_config.RAIO_ENTORNO_KM]
        raio_usado = plano_config.RAIO_ENTORNO_KM
        if viz.empty:
            # polos afastados de área residencial (ex.: Sapiens Parque) não
            # têm local de votação a 1 km — dobra o raio e registra
            raio_usado = 2 * plano_config.RAIO_ENTORNO_KM
            viz = tab[d <= raio_usado]
        peso = viz["aptos"].fillna(0)

        def wavg(col):
            v = viz[col]
            m = v.notna() & peso.gt(0)
            if not m.any():
                return np.nan
            return float((v[m] * peso[m]).sum() / peso[m].sum())

        dir24, dir22 = wavg("pct_direita_ver_24"), wavg("pct_direita_dep_est_22")
        tend = wavg("tendencia_20_24")
        afinidade_base = np.nanmean([2 * dir24, dir22]) * 3 / 3 if not np.isnan(dir24) else np.nan
        afinidade_base = (2 * dir24 + dir22) / 3 if not (np.isnan(dir24) or np.isnan(dir22)) else np.nan
        afinidade = afinidade_base + 0.5 * (tend if not np.isnan(tend) else 0)

        direita22_abs = viz["votos_direita_dep_est_22"].sum()
        matheus = viz["votos_matheus_22"].sum()  # só diagnóstico, fora do índice
        # LIBERAL: onde vive o eleitor-alvo, medido por amostras grandes —
        # NOVO vereador 2024 (metade do peso) e a referência Bruno Souza
        # (2018 estadual + 2022 federal, um quarto cada).
        nv24, br18, br22 = (wavg("pct_novo_ver_24"), wavg("pct_bruno_18"),
                            wavg("pct_bruno_fed_22"))
        partes = [(nv24, 0.50), (br18, 0.25), (br22, 0.25)]
        disp = [(v, p) for v, p in partes if not np.isnan(v)]
        liberal = (sum(v * p for v, p in disp) / sum(p for _, p in disp)
                   if disp else np.nan)

        linhas.append({
            "id": p["id"], "nome": p["nome"], "tipo": p["tipo"],
            "regiao": p["regiao"], "endereco": p["endereco"],
            "lat": p["lat"], "lon": p["lon"],
            "pessoas_ideal": p.get("pessoas_ideal", 2),
            "janelas": ",".join(p.get("janelas", [])),
            "dias_fixos": ",".join(p.get("dias", [])) or None,
            "coberto": bool(p.get("coberto", False)),
            "inviavel": bool(p.get("inviavel", False)),
            "fluxo_panfletos_hora": fluxo_estimado(p),
            "raio_km": raio_usado,
            "n_locais_1km": int(len(viz)),
            "aptos_1km": int(peso.sum()),
            "pct_direita_ver24_1km": dir24,
            "pct_direita_est22_1km": dir22,
            "pct_novo_ver24_1km": wavg("pct_novo_ver_24"),
            "tendencia_dir_20_24": tend,
            "tendencia_novo_20_24": wavg("tendencia_novo_20_24"),
            "pct_bruno18_1km": wavg("pct_bruno_18"),
            "pct_brunofed22_1km": wavg("pct_bruno_fed_22"),
            "votos_direita22_1km": int(direita22_abs),
            "votos_matheus_1km": int(matheus),
            "pct_superior_1km": wavg("pct_superior"),
            "pct_16a24_1km": wavg("pct_16a24"),
            "afinidade_raw": afinidade,
            "liberal_raw": liberal,
        })

    pts = pd.DataFrame(linhas).set_index("id")

    def minmax(s):
        s = s.astype(float)
        lo, hi = s.min(), s.max()
        return (s - lo) / ((hi - lo) or 1.0)

    validos = ~pts["inviavel"]
    perfil_raw = (minmax(pts["pct_superior_1km"]) * 0.7
                  + minmax(pts["pct_16a24_1km"]) * 0.3)
    pts["comp_afinidade"] = minmax(pts["afinidade_raw"].where(validos))
    pts["comp_liberal"] = minmax(pts["liberal_raw"].where(validos))
    pts["comp_fluxo"] = minmax(pts["fluxo_panfletos_hora"].where(validos))
    pts["comp_perfil"] = perfil_raw.where(validos)

    w = plano_config.PESOS_PONTO
    bruto = (w["afinidade"] * pts["comp_afinidade"]
             + w["liberal"] * pts["comp_liberal"]
             + w["fluxo"] * pts["comp_fluxo"] + w["perfil"] * pts["comp_perfil"])
    pts["indice"] = (100 * minmax(bruto.where(validos, 0))).fillna(0).round(1)

    # classificação estratégica pedida no Bloco 3
    p66f, p33f = pts.loc[validos, "comp_fluxo"].quantile([0.66, 0.33])
    p66a, p33a = pts.loc[validos, "comp_afinidade"].quantile([0.66, 0.33])
    def classe(r):
        if r["inviavel"]:
            return "inviável (rodovia — sem parada segura)"
        if r["comp_fluxo"] >= p66f and r["comp_afinidade"] <= p33a:
            return "alto fluxo / baixa afinidade — só reconhecimento de nome"
        if r["comp_afinidade"] >= p66a and r["comp_fluxo"] <= p33f:
            return "alta afinidade / baixo fluxo — porta a porta e eventos"
        if r["comp_fluxo"] >= p66f and r["comp_afinidade"] >= p66a:
            return "OURO — fluxo e afinidade altos"
        return "misto"
    pts["classe"] = pts.apply(classe, axis=1)

    pts = pts.sort_values("indice", ascending=False)
    pts.to_parquet(config.DIR_PROC / "plano_pontos.parquet")
    return pts


if __name__ == "__main__":
    pts = montar_pontos()
    cols = ["nome", "tipo", "regiao", "fluxo_panfletos_hora",
            "pct_direita_ver24_1km", "pct_novo_ver24_1km", "indice", "classe"]
    pd.set_option("display.width", 250)
    print(pts[cols].head(20).to_string())
    print("\n-- classes:")
    print(pts["classe"].value_counts().to_string())
