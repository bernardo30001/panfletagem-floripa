# -*- coding: utf-8 -*-
"""Mapa do plano de panfletagem: heatmap eleitoral por ano (2018/2020/2022/
2024), pontos de panfletagem ranqueados e camadas de terminais/semáforos/
feiras. Reusa o padrão de heat adiado do mapa.py (leaflet.heat quebra em aba
sem layout se criado de forma síncrona)."""

import json

import branca.colormap as bcm
import folium
import pandas as pd

from . import config, plano_config

CAMADAS_HEAT = [
    ("2018 — voto liberal (Bruno + NOVO federal)",
     lambda t: t["votos_bruno_18"].fillna(0) + t["votos_novo_fed_18"].fillna(0), False),
    ("2020 — NOVO+PL vereador",
     lambda t: t["votos_direita_ver_20"].fillna(0), False),
    ("2022 — NOVO+PL dep. estadual",
     lambda t: t["votos_direita_dep_est_22"].fillna(0), False),
    ("2024 — NOVO+PL vereador",
     lambda t: t["votos_direita_ver_24"].fillna(0), True),
]

ICONES = {"semaforo": ("car", "red"), "terminal": ("bus", "blue"),
          "feira": ("shopping-basket", "green"), "calcadao": ("road", "orange"),
          "mercado": ("shopping-cart", "green"), "praca": ("tree", "green"),
          "universidade": ("graduation-cap", "purple"), "tech": ("laptop", "purple")}


def _popup_ponto(pid, r):
    fmt = lambda x, c=1: "—" if pd.isna(x) else f"{100*x:.{c}f}%".replace(".", ",")
    return (
        f"<b>{r['nome']}</b><br><small>{r['endereco']} — {r['regiao']}</small>"
        f"<hr style='margin:4px 0'><table style='font-size:12px'>"
        f"<tr><td><b>Índice</b></td><td align=right><b>{r['indice']:.1f}</b></td></tr>"
        f"<tr><td>Classe</td><td align=right>{r['classe']}</td></tr>"
        f"<tr><td>Fluxo estimado</td><td align=right>{r['fluxo_panfletos_hora']:.0f} panf/h/pessoa</td></tr>"
        f"<tr><td>Direita ver. 2024 (1 km)</td><td align=right>{fmt(r['pct_direita_ver24_1km'])}</td></tr>"
        f"<tr><td>NOVO ver. 2024 (1 km)</td><td align=right>{fmt(r['pct_novo_ver24_1km'])}</td></tr>"
        f"<tr><td>Tendência direita 20→24</td><td align=right>{fmt(r['tendencia_dir_20_24'])}</td></tr>"
        f"<tr><td>Voto liberal no entorno</td><td align=right>{fmt(r['liberal_raw'])}</td></tr>"
        f"<tr><td>Votos Matheus 2022 <i>(fora do índice)</i></td><td align=right>{int(r['votos_matheus_1km'])}</td></tr>"
        f"<tr><td>Superior completo (1 km)</td><td align=right>{fmt(r['pct_superior_1km'], 0)}</td></tr>"
        f"<tr><td>Eleitores no raio de 1 km</td><td align=right>{int(r['aptos_1km']):,}</td></tr>"
        f"</table><small>Equipe ideal: {int(r['pessoas_ideal'])} pessoa(s) · "
        f"janelas: {r['janelas']}</small>".replace(",", "."))


def gerar_mapa_plano(caminho):
    tab = pd.read_parquet(config.DIR_PROC / "plano_locais.parquet").dropna(subset=["lat", "lon"])
    pts = pd.read_parquet(config.DIR_PROC / "plano_pontos.parquet")

    m = folium.Map(location=config.MAPA_CENTRO, zoom_start=12,
                   tiles=None, control_scale=True)
    folium.TileLayer("openstreetmap", name="OpenStreetMap").add_to(m)
    folium.TileLayer("cartodbpositron", name="CARTO claro (padrão)").add_to(m)

    # ---- heatmaps por ano (criação adiada; ver comentário no mapa.py) ----
    grupos_js = []
    for nome, calc, mostrar in CAMADAS_HEAT:
        fg = folium.FeatureGroup(name=f"Heat {nome}", show=mostrar)
        fg.add_to(m)
        votos = calc(tab)
        vmax = float(votos.max()) or 1.0
        dados = [[round(r["lat"], 6), round(r["lon"], 6), round(v / vmax, 4)]
                 for (_, r), v in zip(tab.iterrows(), votos) if v > 0]
        grupos_js.append((fg.get_name(), dados))

    # ---- pontos de panfletagem ranqueados ----
    cmap = bcm.LinearColormap(["#2c7fb8", "#ffffb2", "#e31a1c"], vmin=0, vmax=100,
                              caption="Índice de priorização do ponto (0–100)")
    cmap.add_to(m)
    fg_pontos = folium.FeatureGroup(name="Pontos de panfletagem (cor = índice)", show=True)
    for pid, r in pts.iterrows():
        if r["inviavel"]:
            continue
        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=6 + 8 * (r["indice"] / 100),
            color="#333333", weight=0.8, fill=True,
            fill_color=cmap(float(r["indice"])), fill_opacity=0.9,
            tooltip=f"#{list(pts.index).index(pid)+1} {r['nome']} — índice {r['indice']:.0f}",
            popup=folium.Popup(_popup_ponto(pid, r), max_width=360),
        ).add_to(fg_pontos)
    fg_pontos.add_to(m)

    # ---- camadas por tipo (terminais / semáforos / feiras) ----
    for tipos, nome_camada in [(("terminal",), "Terminais de integração"),
                               (("semaforo",), "Semáforos priorizados"),
                               (("feira", "mercado"), "Feiras e mercados")]:
        fg = folium.FeatureGroup(name=nome_camada, show=False)
        for pid, r in pts[pts["tipo"].isin(tipos)].iterrows():
            icone, cor = ICONES[r["tipo"]]
            folium.Marker(
                location=[r["lat"], r["lon"]],
                icon=folium.Icon(color="lightgray" if r["inviavel"] else cor,
                                 prefix="fa", icon=icone),
                tooltip=r["nome"],
                popup=folium.Popup(_popup_ponto(pid, r), max_width=360),
            ).add_to(fg)
        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    heat_js = "\n".join(
        f"L.heatLayer({json.dumps(d)}, {{radius: 26, blur: 20, maxZoom: 13, max: 1.0}}).addTo({g});"
        for g, d in grupos_js)
    m.get_root().html.add_child(folium.Element(f"""
<script src="https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<script>
window.addEventListener("load", function () {{
  var mapa = {m.get_name()};
  function desenha() {{
    var s = mapa.getSize();
    if (s.x === 0 || s.y === 0) {{ setTimeout(desenha, 250); return; }}
    mapa.invalidateSize();
    {heat_js}
  }}
  desenha();
}});
</script>"""))

    titulo = ("<div style='position:fixed;top:10px;left:60px;z-index:9999;"
              "background:rgba(255,255,255,.92);padding:8px 14px;border-radius:6px;"
              "box-shadow:0 1px 4px rgba(0,0,0,.3);font-family:sans-serif'>"
              "<b>Plano de panfletagem 2026 — Florianópolis</b><br>"
              "<small>Heatmaps por ciclo (2018–2024) e pontos ranqueados — "
              "TSE / estimativas declaradas</small></div>")
    m.get_root().html.add_child(folium.Element(titulo))
    m.save(str(caminho))
    print(f"  mapa do plano salvo em {caminho}")
