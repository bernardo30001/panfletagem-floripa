# -*- coding: utf-8 -*-
"""Dashboard único (saida/index.html) para publicação no GitHub Pages.

Junta os quatro entregáveis numa página só, com abas:
  Visão geral (tiles + tabela interativa) · Mapa (iframe) · Roteiro · Relatório
Tudo autocontido: dados do ranking embutidos como JSON, markdown convertido
para HTML aqui no build (sem CDN além dos tiles do próprio mapa).
"""

import html
import json
import re
from datetime import date

import pandas as pd

from . import config

# ---------------------------------------------------------------------------
# Conversor de markdown minimalista (cobre só o que os nossos .md usam:
# títulos, tabelas, listas, negrito, itálico, código, hr, links)
# ---------------------------------------------------------------------------

def _inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"(?<![\w])_([^_]+)_(?![\w])", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md_para_html(texto: str) -> str:
    linhas = texto.split("\n")
    saida, i = [], 0
    while i < len(linhas):
        l = linhas[i]
        if l.startswith("```"):
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(html.escape(linhas[i]))
                i += 1
            saida.append("<pre><code>" + "\n".join(bloco) + "</code></pre>")
        elif l.startswith("|"):
            tab = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tab.append(linhas[i])
                i += 1
            i -= 1
            cab = [c.strip() for c in tab[0].strip("|").split("|")]
            corpo = tab[2:] if len(tab) > 2 else []
            t = ["<div class='tabela-md'><table><thead><tr>"]
            t += [f"<th>{_inline(c)}</th>" for c in cab]
            t.append("</tr></thead><tbody>")
            for linha in corpo:
                cels = [c.strip() for c in linha.strip("|").split("|")]
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cels) + "</tr>")
            t.append("</tbody></table></div>")
            saida.append("".join(t))
        elif l.startswith("- "):
            itens = []
            while i < len(linhas) and linhas[i].startswith("- "):
                itens.append(f"<li>{_inline(linhas[i][2:])}</li>")
                i += 1
            i -= 1
            saida.append("<ul>" + "".join(itens) + "</ul>")
        elif l.startswith("## "):
            saida.append(f"<h3>{_inline(l[3:])}</h3>")
        elif l.startswith("# "):
            saida.append(f"<h2>{_inline(l[2:])}</h2>")
        elif l.strip() == "---":
            saida.append("<hr>")
        elif l.strip():
            saida.append(f"<p>{_inline(l)}</p>")
        i += 1
    return "\n".join(saida)


# ---------------------------------------------------------------------------
# Dados do ranking para a tabela interativa
# ---------------------------------------------------------------------------

def _dados_ranking(tab: pd.DataFrame) -> list[dict]:
    regs = []
    orden = tab.sort_values("score", ascending=False)
    for pos, (chave, r) in enumerate(orden.iterrows(), 1):
        regs.append({
            "pos": pos,
            "nome": (r["nome"] or "").title(),
            "endereco": (r["endereco"] or "").title(),
            "bairro": r["bairro_ibge"] or "",
            "regiao": r["regiao"] or "",
            "aptos": None if pd.isna(r["aptos"]) else int(r["aptos"]),
            "direita22": None if pd.isna(r["votos_direita_dep_est_22"]) else int(r["votos_direita_dep_est_22"]),
            "pctDireita": None if pd.isna(r["pct_direita_dep_est_22"]) else round(100 * r["pct_direita_dep_est_22"], 1),
            "matheus": None if pd.isna(r["votos_matheus_22"]) else int(r["votos_matheus_22"]),
            "abstencao": None if pd.isna(r["abstencao_22"]) else round(100 * r["abstencao_22"], 1),
            "score": round(r["score"], 1),
            "pequeno": bool(r["flag_pequeno"]),
        })
    return regs


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------

def gerar_dashboard(tab: pd.DataFrame, caminho):
    roteiro_html = md_para_html((config.DIR_SAIDA / "top20_roteiro.md").read_text(encoding="utf-8"))
    relatorio_html = md_para_html((config.DIR_SAIDA / "relatorio.md").read_text(encoding="utf-8"))
    dados = _dados_ranking(tab)

    total_aptos = int(tab["aptos"].sum())
    total_dir = int(tab["votos_direita_dep_est_22"].sum())
    pct_dir = 100 * tab["votos_direita_dep_est_22"].sum() / tab["validos_dep_est_22"].sum()
    votos_mat = int(tab["votos_matheus_22"].sum())
    regioes = sorted({d["regiao"] for d in dados if d["regiao"]})

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Panfletagem Florianópolis 2026 — Inteligência eleitoral</title>
<style>
:root {{
  --fundo:#f7f7f5; --superficie:#ffffff; --tinta:#1c1c1a; --tinta2:#5f5e59;
  --borda:#e4e3de; --acento:#c2410c; --acento-claro:#fdba74; --barra:#f97316;
  --zebra:#fafaf8;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --fundo:#161615; --superficie:#211f1e; --tinta:#f0efeb; --tinta2:#a6a49c;
    --borda:#3a3835; --acento:#fb923c; --acento-claro:#7c2d12; --barra:#ea580c;
    --zebra:#262422;
  }}
}}
* {{ box-sizing:border-box; margin:0; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
       background:var(--fundo); color:var(--tinta); line-height:1.55; }}
header {{ background:var(--superficie); border-bottom:1px solid var(--borda);
          padding:20px 24px 0; position:sticky; top:0; z-index:50; }}
header h1 {{ font-size:1.25rem; }}
header p.sub {{ color:var(--tinta2); font-size:.85rem; margin:2px 0 14px; }}
nav {{ display:flex; gap:4px; flex-wrap:wrap; }}
nav button {{ border:none; background:none; color:var(--tinta2); font-size:.95rem;
  padding:10px 14px; cursor:pointer; border-bottom:2.5px solid transparent; }}
nav button.ativo {{ color:var(--acento); border-bottom-color:var(--acento); font-weight:600; }}
main {{ max-width:1180px; margin:0 auto; padding:24px; }}
section {{ display:none; }} section.ativa {{ display:block; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
          gap:12px; margin-bottom:22px; }}
.tile {{ background:var(--superficie); border:1px solid var(--borda);
         border-radius:10px; padding:14px 16px; }}
.tile .num {{ font-size:1.7rem; font-weight:700; letter-spacing:-.02em; }}
.tile .rot {{ color:var(--tinta2); font-size:.8rem; margin-top:2px; }}
.controles {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }}
.controles input, .controles select {{ padding:8px 12px; border:1px solid var(--borda);
  border-radius:8px; background:var(--superficie); color:var(--tinta); font-size:.9rem; }}
.controles input {{ flex:1; min-width:220px; }}
.tabela-wrap {{ background:var(--superficie); border:1px solid var(--borda);
  border-radius:10px; overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:.85rem; }}
th, td {{ padding:8px 10px; text-align:right; white-space:nowrap; }}
th:nth-child(2), td:nth-child(2), th:nth-child(3), td:nth-child(3),
th:nth-child(4), td:nth-child(4) {{ text-align:left; }}
thead th {{ position:sticky; top:0; background:var(--superficie); color:var(--tinta2);
  font-weight:600; border-bottom:1px solid var(--borda); cursor:pointer; user-select:none; }}
thead th:hover {{ color:var(--acento); }}
tbody tr:nth-child(even) {{ background:var(--zebra); }}
td.nome {{ max-width:320px; overflow:hidden; text-overflow:ellipsis; }}
td.nome small {{ display:block; color:var(--tinta2); }}
.scorebar {{ display:inline-flex; align-items:center; gap:8px; justify-content:flex-end; }}
.scorebar i {{ display:inline-block; height:8px; border-radius:4px;
  background:var(--barra); min-width:2px; }}
.aviso-pequeno {{ color:var(--tinta2); font-style:italic; }}
iframe {{ width:100%; height:calc(100vh - 190px); min-height:480px; border:1px solid var(--borda);
  border-radius:10px; background:var(--superficie); }}
.prosa {{ background:var(--superficie); border:1px solid var(--borda); border-radius:10px;
  padding:26px 30px; max-width:900px; }}
.prosa h2 {{ font-size:1.25rem; margin:18px 0 8px; }}
.prosa h3 {{ font-size:1.05rem; margin:20px 0 8px; color:var(--acento); }}
.prosa p, .prosa ul {{ margin:8px 0; color:var(--tinta); }}
.prosa ul {{ padding-left:22px; }}
.prosa hr {{ border:none; border-top:1px solid var(--borda); margin:18px 0; }}
.prosa pre {{ background:var(--zebra); border:1px solid var(--borda); border-radius:8px;
  padding:12px; overflow-x:auto; font-size:.8rem; }}
.prosa code {{ font-family:ui-monospace,Menlo,monospace; font-size:.85em; }}
.tabela-md {{ overflow-x:auto; margin:10px 0; }}
.tabela-md th, .tabela-md td {{ text-align:left; border-bottom:1px solid var(--borda);
  font-size:.82rem; }}
footer {{ color:var(--tinta2); font-size:.78rem; text-align:center; padding:26px 16px; }}
a {{ color:var(--acento); }}
.baixar {{ display:inline-block; margin:0 0 12px; font-size:.85rem; }}
@media (max-width:640px) {{ main {{ padding:14px; }} .prosa {{ padding:18px; }} }}
</style>
</head>
<body>
<header>
  <h1>Panfletagem Florianópolis 2026</h1>
  <p class="sub">Desempenho da direita (NOVO+PL) e prioridade por local de votação · dados TSE 2022/2024 · mandato Matheus Cadorin</p>
  <nav>
    <button data-aba="visao" class="ativo">Visão geral</button>
    <button data-aba="mapa">Mapa</button>
    <button data-aba="roteiro">Roteiro top 20</button>
    <button data-aba="relatorio">Relatório</button>
  </nav>
</header>
<main>

<section id="visao" class="ativa">
  <div class="tiles">
    <div class="tile"><div class="num">152</div><div class="rot">locais de votação analisados</div></div>
    <div class="tile"><div class="num">{total_aptos:,}</div><div class="rot">eleitores aptos</div></div>
    <div class="tile"><div class="num">{total_dir:,} <span style="font-size:.95rem;color:var(--tinta2)">({pct_dir:.1f}%)</span></div><div class="rot">votos NOVO+PL, dep. estadual 2022</div></div>
    <div class="tile"><div class="num">{votos_mat}</div><div class="rot">votos do Matheus na capital em 2022</div></div>
  </div>
  <div class="controles">
    <input id="busca" type="search" placeholder="Buscar local ou bairro…">
    <select id="filtro-regiao"><option value="">Todas as regiões</option>
    {"".join(f'<option>{r}</option>' for r in regioes)}</select>
  </div>
  <a class="baixar" href="ranking_panfletagem.csv" download>⬇ Baixar ranking completo (CSV)</a>
  <div class="tabela-wrap">
    <table id="ranking">
      <thead><tr>
        <th data-k="pos">#</th><th data-k="nome">Local</th><th data-k="bairro">Bairro</th>
        <th data-k="regiao">Região</th><th data-k="aptos">Eleitores</th>
        <th data-k="direita22">Direita 2022</th><th data-k="pctDireita">% direita</th>
        <th data-k="matheus">Matheus</th><th data-k="abstencao">Abstenção</th>
        <th data-k="score">Score</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <p style="color:var(--tinta2);font-size:.8rem;margin-top:10px">
    Score = índice de prioridade (potencial 0,40 · liberal 0,25 · densidade 0,20 ·
    consistência 0,15). A votação do Matheus em 2022 não entra no cálculo — a
    coluna fica só como diagnóstico. Locais com menos de {config.MIN_ELEITORES_LOCAL}
    eleitores aparecem com score 0. Clique nos cabeçalhos para ordenar.</p>
</section>

<section id="mapa">
  <p style="margin-bottom:10px"><a href="mapa_floripa.html" target="_blank" rel="noopener">Abrir o mapa em tela cheia ↗</a></p>
  <iframe src="mapa_floripa.html" title="Mapa interativo" loading="lazy"></iframe>
</section>

<section id="roteiro"><div class="prosa">{roteiro_html}</div></section>
<section id="relatorio"><div class="prosa">{relatorio_html}</div></section>

</main>
<footer>Fontes: TSE Dados Abertos (votação por seção 2022/2024, locais de votação,
perfil do eleitorado) · IBGE (malha de bairros Censo 2022) · gerado em {date.today().strftime("%d/%m/%Y")}.
Votação por local ≠ residência do eleitor.</footer>

<script>
const DADOS = {json.dumps(dados, ensure_ascii=False)};
const fmt = n => n === null ? "—" : n.toLocaleString("pt-BR");
const fmtP = n => n === null ? "—" : n.toLocaleString("pt-BR", {{minimumFractionDigits:1, maximumFractionDigits:1}}) + "%";
let ordem = {{k: "score", asc: false}};

function linhas() {{
  const q = document.getElementById("busca").value.trim().toLowerCase();
  const reg = document.getElementById("filtro-regiao").value;
  let ds = DADOS.filter(d =>
    (!reg || d.regiao === reg) &&
    (!q || d.nome.toLowerCase().includes(q) || d.bairro.toLowerCase().includes(q)));
  ds.sort((a,b) => {{
    const va = a[ordem.k], vb = b[ordem.k];
    if (va === null) return 1; if (vb === null) return -1;
    const c = typeof va === "string" ? va.localeCompare(vb, "pt-BR") : va - vb;
    return ordem.asc ? c : -c;
  }});
  return ds;
}}

function render() {{
  const tb = document.querySelector("#ranking tbody");
  tb.innerHTML = linhas().map(d => `<tr${{d.pequeno ? ' class="aviso-pequeno"' : ''}}>
    <td>${{d.pos}}</td>
    <td class="nome">${{d.nome}}<small>${{d.endereco}}</small></td>
    <td>${{d.bairro}}</td><td>${{d.regiao}}</td>
    <td>${{fmt(d.aptos)}}</td><td>${{fmt(d.direita22)}}</td><td>${{fmtP(d.pctDireita)}}</td>
    <td>${{fmt(d.matheus)}}</td><td>${{fmtP(d.abstencao)}}</td>
    <td><span class="scorebar"><i style="width:${{Math.round(d.score*0.6)}}px"></i>
    ${{d.score.toLocaleString("pt-BR", {{minimumFractionDigits:1}})}}</span></td>
  </tr>`).join("");
}}

document.querySelectorAll("#ranking th").forEach(th => th.addEventListener("click", () => {{
  const k = th.dataset.k;
  ordem = {{k, asc: ordem.k === k ? !ordem.asc : (k === "nome" || k === "bairro" || k === "regiao" || k === "pos")}};
  render();
}}));
document.getElementById("busca").addEventListener("input", render);
document.getElementById("filtro-regiao").addEventListener("change", render);

document.querySelectorAll("nav button").forEach(b => b.addEventListener("click", () => {{
  document.querySelectorAll("nav button").forEach(x => x.classList.remove("ativo"));
  document.querySelectorAll("main section").forEach(x => x.classList.remove("ativa"));
  b.classList.add("ativo");
  document.getElementById(b.dataset.aba).classList.add("ativa");
}}));

render();
</script>
</body>
</html>"""
    # números pt-BR nos tiles (o :, do Python usa vírgula de milhar americana)
    pagina = pagina.replace(f"{total_aptos:,}", f"{total_aptos:,}".replace(",", "."))
    pagina = pagina.replace(f"{total_dir:,}", f"{total_dir:,}".replace(",", "."))
    pagina = pagina.replace(f"{pct_dir:.1f}%", f"{pct_dir:.1f}%".replace(".", ","))
    caminho.write_text(pagina, encoding="utf-8")
    print(f"  dashboard salvo em {caminho}")
