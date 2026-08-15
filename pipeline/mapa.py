# -*- coding: utf-8 -*-
"""Mapa interativo (Leaflet via folium) — entregável 1.

Camadas (alternáveis no controle no canto superior direito):
  1. Heatmap de votos absolutos da direita (NOVO+PL, dep. estadual 2022)
  2. Coroplético de % da direita por bairro (escala divergente centrada na
     média municipal — azul abaixo, vermelho acima)
  3. Coroplético do Índice de Prioridade por bairro
  4. Marcadores dos locais de votação (cor = score, raio = eleitorado)
  5. Pontos de fluxo de pedestres (terminais, feiras, mercados, calçadões)
"""

import json

import branca.colormap as bcm
import folium
import numpy as np
import pandas as pd

from . import config
from .metricas import bairros_ibge


def _fmt_pct(x, casas=1):
    return "—" if pd.isna(x) else f"{100 * x:.{casas}f}%".replace(".", ",")


def _fmt_int(x):
    return "—" if pd.isna(x) else f"{int(x):,}".replace(",", ".")


def _popup_local(chave, r) -> str:
    linhas = [
        f"<b>{r['nome']}</b><br>",
        f"<small>{r['endereco']} — {r['bairro_ibge']}</small><hr style='margin:4px 0'>",
        "<table style='font-size:12px'>",
        f"<tr><td>Eleitores aptos</td><td align=right><b>{_fmt_int(r['aptos'])}</b></td></tr>",
        f"<tr><td>NOVO dep. est. 2022</td><td align=right>{_fmt_int(r['votos_novo_dep_est_22'])} ({_fmt_pct(r['pct_novo_dep_est_22'])})</td></tr>",
        f"<tr><td>PL dep. est. 2022</td><td align=right>{_fmt_int(r['votos_pl_dep_est_22'])} ({_fmt_pct(r['pct_pl_dep_est_22'])})</td></tr>",
        f"<tr><td>Direita dep. est. 2022</td><td align=right><b>{_fmt_int(r['votos_direita_dep_est_22'])} ({_fmt_pct(r['pct_direita_dep_est_22'])})</b></td></tr>",
        f"<tr><td>Bolsonaro 2022 (teto)</td><td align=right>{_fmt_pct(r['pct_bolsonaro_22'])}</td></tr>",
        f"<tr><td>Direita vereador 2024</td><td align=right>{_fmt_int(r['votos_direita_ver_24'])} ({_fmt_pct(r['pct_direita_ver_24'])})</td></tr>",
        f"<tr><td>Votos Matheus 2022 <i>(fora do score)</i></td><td align=right>{_fmt_int(r['votos_matheus_22'])}</td></tr>",
        f"<tr><td>Abstenção 2022</td><td align=right>{_fmt_pct(r['abstencao_22'])}</td></tr>",
        f"<tr><td>Score de prioridade</td><td align=right><b>{r['score']:.1f}</b></td></tr>",
        "</table>",
    ]
    if isinstance(r.get("top3_vereadores_direita"), str):
        linhas.append("<hr style='margin:4px 0'><small><b>Vereadores NOVO/PL 2024 no local:</b><br>"
                      + r["top3_vereadores_direita"].replace(" | ", "<br>") + "</small>")
    if isinstance(r.get("prefeito_lider_24"), str):
        linhas.append(f"<br><small><b>Prefeito 2024 (líder no local):</b> {r['prefeito_lider_24']}</small>")
    linhas.append(f"<br><small>Local {chave} • {'só 2022' if r['so_2022'] else ('novo em 2024' if r['so_2024'] else '2022+2024')}</small>")
    return "".join(linhas)


def _coropletico(poligonos, agg, coluna, nome_camada, colormap, mostrar, fmt):
    """Camada GeoJson com estilo por valor do bairro."""
    dados = agg[coluna].to_dict()
    scores = agg["score"].to_dict()

    def estilo(feat):
        v = dados.get(feat["properties"]["NM_BAIRRO"])
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return {"fillColor": "#bbbbbb", "fillOpacity": 0.15,
                    "color": "#999999", "weight": 0.6}
        return {"fillColor": colormap(v), "fillOpacity": 0.65,
                "color": "#555555", "weight": 0.8}

    gj = json.loads(poligonos.to_json())
    for feat in gj["features"]:
        nm = feat["properties"]["NM_BAIRRO"]
        v = dados.get(nm)
        feat["properties"]["valor"] = (
            "sem local de votação" if v is None or pd.isna(v) else fmt(v))
        feat["properties"]["score_bairro"] = (
            "—" if nm not in scores or pd.isna(scores[nm])
            else f"{scores[nm]:.1f}".replace(".", ","))

    camada = folium.GeoJson(
        gj, name=nome_camada, style_function=estilo, show=mostrar,
        highlight_function=lambda f: {"weight": 2.5, "color": "#000000"},
        tooltip=folium.GeoJsonTooltip(
            fields=["NM_BAIRRO", "valor", "score_bairro"],
            aliases=["Bairro", nome_camada, "Score do bairro"]),
    )
    return camada


def gerar_mapa(tab: pd.DataFrame, agg: pd.DataFrame, caminho):
    # tiles=None + camadas explícitas: a última base adicionada fica ativa,
    # então o positron (mais limpo p/ dados) entra por último
    m = folium.Map(location=config.MAPA_CENTRO, zoom_start=config.MAPA_ZOOM,
                   tiles=None, control_scale=True)
    folium.TileLayer("openstreetmap", name="OpenStreetMap").add_to(m)
    folium.TileLayer("cartodbpositron", name="CARTO claro (padrão)").add_to(m)

    poligonos = bairros_ibge()

    # ------ 1. heatmap de votos absolutos da direita ------------------------
    # A camada de calor é criada DEPOIS do load da página, com retry até o
    # container ter tamanho real: o leaflet.heat desenha o canvas de forma
    # síncrona no onAdd e estoura IndexSizeError se a aba ainda estiver
    # oculta/sem layout (o que também abortaria o resto da inicialização).
    # Pesos normalizados para 0–1: o plugin trata intensidade nessa escala;
    # votos brutos saturariam tudo no vermelho máximo.
    pontos = tab.dropna(subset=["lat", "lon"])
    votos = pontos["votos_direita_dep_est_22"].fillna(0)
    vmax = float(votos.max()) or 1.0
    heat = [[round(r["lat"], 6), round(r["lon"], 6), round(v / vmax, 4)]
            for (_, r), v in zip(pontos.iterrows(), votos) if v > 0]
    fg_heat = folium.FeatureGroup(name="Heatmap — votos absolutos da direita (2022)",
                                  show=True)
    fg_heat.add_to(m)
    # o src fica aqui no corpo (e não no header) para garantir que carregue
    # DEPOIS do leaflet.js — o folium só anexa os JS padrão no render()
    heat_js = f"""
<script src="https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<script>
window.addEventListener("load", function () {{
  var mapa = {m.get_name()};
  function desenhaHeat() {{
    var s = mapa.getSize();
    if (s.x === 0 || s.y === 0) {{ setTimeout(desenhaHeat, 250); return; }}
    mapa.invalidateSize();
    L.heatLayer({json.dumps(heat)},
                {{radius: 28, blur: 22, maxZoom: 13, max: 1.0}})
     .addTo({fg_heat.get_name()});
  }}
  desenhaHeat();
}});
</script>"""
    m.get_root().html.add_child(folium.Element(heat_js))

    # ------ 2. coroplético % direita por bairro (escala divergente) ---------
    media = float(tab["votos_direita_dep_est_22"].sum()
                  / tab["validos_dep_est_22"].sum())
    lo, hi = float(agg["pct_direita_22"].min()), float(agg["pct_direita_22"].max())
    amplitude = max(media - lo, hi - media)
    cmap_pct = bcm.LinearColormap(
        ["#2166ac", "#f7f7f7", "#b2182b"],
        vmin=media - amplitude, vmax=media + amplitude,
        caption=f"% NOVO+PL dep. estadual 2022 (branco = média municipal, {100*media:.1f}%)")
    _coropletico(poligonos, agg, "pct_direita_22",
                 "% direita por bairro (2022)", cmap_pct, False,
                 lambda v: f"{100*v:.1f}%".replace(".", ",")).add_to(m)
    cmap_pct.add_to(m)

    # ------ 3. coroplético do índice de prioridade --------------------------
    cmap_score = bcm.LinearColormap(
        ["#ffffcc", "#fd8d3c", "#bd0026"],
        vmin=float(agg["score"].min()), vmax=float(agg["score"].max()),
        caption="Índice de Prioridade de Panfletagem (média ponderada do bairro)")
    _coropletico(poligonos, agg, "score",
                 "Índice de prioridade por bairro", cmap_score, False,
                 lambda v: f"{v:.1f}".replace(".", ",")).add_to(m)
    cmap_score.add_to(m)

    # ------ 4. marcadores dos locais de votação -----------------------------
    fg_loc = folium.FeatureGroup(name="Locais de votação (cor = score)", show=True)
    cmap_marc = bcm.LinearColormap(["#2c7fb8", "#ffffb2", "#e31a1c"],
                                   vmin=0, vmax=100)
    aptos_max = float(pontos["aptos"].max())
    for chave, r in pontos.iterrows():
        raio = 4 + 9 * float((r["aptos"] or 0) / aptos_max) ** 0.5
        folium.CircleMarker(
            location=[r["lat"], r["lon"]], radius=raio,
            color="#333333", weight=0.8,
            fill=True, fill_color=cmap_marc(float(r["score"])), fill_opacity=0.85,
            popup=folium.Popup(_popup_local(chave, r), max_width=340),
            tooltip=f"{r['nome']} — score {r['score']:.0f}",
        ).add_to(fg_loc)
    fg_loc.add_to(m)

    # ------ 5. pontos de fluxo de pedestres ---------------------------------
    fg_fluxo = folium.FeatureGroup(name="Pontos de fluxo (terminais, feiras…)",
                                   show=False)
    icones = {"terminal": "bus", "feira": "shopping-basket", "mercado": "shopping-cart",
              "calcadao": "road", "praca": "tree"}
    for p in config.PONTOS_FLUXO:
        folium.Marker(
            location=[p["lat"], p["lon"]],
            icon=folium.Icon(color="darkgreen", prefix="fa",
                             icon=icones.get(p["tipo"], "info-sign")),
            popup=folium.Popup(
                f"<b>{p['nome']}</b><br><small>{p['tipo'].title()} — {p['regiao']}"
                f"<br><b>Quando:</b> {p['dias_horarios']}</small>", max_width=280),
            tooltip=p["nome"],
        ).add_to(fg_fluxo)
    fg_fluxo.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    titulo = ("<div style='position:fixed;top:10px;left:60px;z-index:9999;"
              "background:rgba(255,255,255,.92);padding:8px 14px;border-radius:6px;"
              "box-shadow:0 1px 4px rgba(0,0,0,.3);font-family:sans-serif'>"
              "<b>Panfletagem Florianópolis 2026</b><br>"
              "<small>Desempenho da direita (NOVO+PL) e prioridade por local de votação "
              "— TSE 2022/2024</small></div>")
    m.get_root().html.add_child(folium.Element(titulo))

    m.save(str(caminho))
    print(f"  mapa salvo em {caminho}")
