# -*- coding: utf-8 -*-
"""Métricas por local de votação (Blocos 1 a 3 do escopo).

Tudo gira em torno da chave de local `Z{zona}-L{local}` (o número do local só
é único dentro da zona). A tabela final tem uma linha por local com:
  - cadastro (nome, endereço, bairro TSE, bairro IBGE, coordenadas)
  - desempenho da direita por cargo/ano (Bloco 1)
  - votos e penetração do candidato-alvo (Bloco 2)
  - eleitorado, comparecimento e abstenção (Bloco 3)
  - perfil demográfico (gênero, jovens, 60+, superior completo)
"""

import json
import subprocess
import time
import urllib.parse

import geopandas as gpd
import numpy as np
import pandas as pd

from . import config
from .util import chave_local, norm_txt

AVISOS: list[str] = []  # avisos de qualidade de dados exibidos no relatório


def _aviso(msg: str):
    print(f"  AVISO: {msg}")
    AVISOS.append(msg)


# ---------------------------------------------------------------------------
# Cadastro de locais (endereço, bairro, coordenadas, eleitores aptos)
# ---------------------------------------------------------------------------

def _cadastro_ano(ano: int) -> pd.DataFrame:
    df = pd.read_parquet(config.DIR_PROC / f"locais_{ano}.parquet")
    df["chave"] = chave_local(df)
    # coordenada ausente vem como -1 no TSE
    for c in ("NR_LATITUDE", "NR_LONGITUDE"):
        df[c] = pd.to_numeric(df[c], errors="coerce").replace(-1.0, np.nan)
    agg = df.groupby("chave").agg(
        nome=("NM_LOCAL_VOTACAO", "first"),
        endereco=("DS_ENDERECO", "first"),
        bairro_tse=("NM_BAIRRO", "first"),
        cep=("NR_CEP", "first"),
        lat=("NR_LATITUDE", "max"),
        lon=("NR_LONGITUDE", "max"),
        aptos=("QT_ELEITOR_SECAO", "sum"),
        n_secoes=("NR_SECAO", "nunique"),
    )
    return agg.add_suffix(f"_{ano}")


def montar_cadastro() -> pd.DataFrame:
    """União dos locais de 2022 e 2024; dados de 2022 têm prioridade (a
    referência da análise é a eleição geral), 2024 preenche lacunas."""
    c22 = _cadastro_ano(config.ANO_GERAL)
    c24 = _cadastro_ano(config.ANO_MUNICIPAL)
    cad = c22.join(c24, how="outer")
    for col in ("nome", "endereco", "bairro_tse", "cep", "lat", "lon"):
        cad[col] = cad[f"{col}_2022"].fillna(cad[f"{col}_2024"])
    cad["aptos"] = cad["aptos_2022"].fillna(cad["aptos_2024"])
    cad["so_2022"] = cad["aptos_2024"].isna()   # local desativado em 2024
    cad["so_2024"] = cad["aptos_2022"].isna()   # local novo em 2024
    cols = ["nome", "endereco", "bairro_tse", "cep", "lat", "lon",
            "aptos", "aptos_2022", "aptos_2024", "n_secoes_2022",
            "so_2022", "so_2024"]
    return cad[cols]


# ---------------------------------------------------------------------------
# Geocodificação de locais sem coordenada (Nominatim, com cache e rate limit)
# ---------------------------------------------------------------------------

def geocodificar_faltantes(cad: pd.DataFrame) -> pd.DataFrame:
    # correções manuais primeiro (endereços com typo que o Nominatim não acha)
    for chave, (lat, lon) in config.COORDS_MANUAIS.items():
        if chave in cad.index and pd.isna(cad.loc[chave, "lat"]):
            cad.loc[chave, ["lat", "lon"]] = (lat, lon)
    falt = cad[cad["lat"].isna() | cad["lon"].isna()]
    if falt.empty:
        return cad
    cache = {}
    if config.GEOCODE_CACHE.exists():
        cache = json.loads(config.GEOCODE_CACHE.read_text())
    for chave, row in falt.iterrows():
        consulta = f"{row['endereco']}, Florianópolis, SC, Brasil"
        if consulta not in cache:
            url = (config.NOMINATIM_URL + "?format=json&limit=1&q="
                   + urllib.parse.quote(consulta))
            # curl pelo mesmo motivo do download.py (SSL do proxy local)
            r = subprocess.run(
                ["curl", "-sS", "--max-time", "30",
                 "-H", "User-Agent: pipeline-panfletagem-fln/1.0", url],
                capture_output=True, text=True)
            try:
                hits = json.loads(r.stdout)
                cache[consulta] = ([hits[0]["lat"], hits[0]["lon"]]
                                   if hits else None)
            except (json.JSONDecodeError, KeyError, IndexError):
                cache[consulta] = None
            config.GEOCODE_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
            time.sleep(config.NOMINATIM_PAUSA_S)
        if cache.get(consulta):
            cad.loc[chave, "lat"] = float(cache[consulta][0])
            cad.loc[chave, "lon"] = float(cache[consulta][1])
    restantes = int(cad["lat"].isna().sum())
    if restantes:
        _aviso(f"{restantes} locais sem coordenada mesmo após geocodificação "
               "(ficam fora do mapa, mas seguem no ranking).")
    return cad


# ---------------------------------------------------------------------------
# Helpers de apuração
# ---------------------------------------------------------------------------

def _carrega_votacao(ano: int) -> pd.DataFrame:
    df = pd.read_parquet(config.DIR_PROC / f"votacao_{ano}.parquet")
    df["chave"] = chave_local(df)
    df["NR_VOTAVEL"] = pd.to_numeric(df["NR_VOTAVEL"], errors="coerce")
    return df


def _cargo(df, nome_cargo, turno=None):
    turno = turno or config.TURNO_ANALISE
    return df[(df["DS_CARGO"].map(norm_txt) == norm_txt(nome_cargo))
              & (df["NR_TURNO"] == turno)]


def _soma_por_local(df, filtro, nome):
    """Soma QT_VOTOS por local para as linhas que passam no filtro booleano."""
    s = df[filtro].groupby("chave")["QT_VOTOS"].sum()
    s.name = nome
    return s


def _mascara_partido_proporcional(df, nr_partido):
    """Voto de um partido em cargo proporcional = nominal (número do candidato
    começa com o nº do partido; 5 dígitos p/ estadual+vereador, 4 p/ federal)
    + voto de legenda (NR_VOTAVEL == nº do partido)."""
    nv = df["NR_VOTAVEL"]
    nominal = ((nv >= 1000) & (nv <= 99999)
               & (nv.astype("Int64").astype(str).str[:2] == str(nr_partido)))
    legenda = nv == nr_partido
    return nominal | legenda


def _metricas_proporcional(df_cargo, prefixo):
    """Válidos, votos e % de cada partido-alvo num cargo proporcional."""
    validos = _soma_por_local(
        df_cargo, ~df_cargo["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS),
        f"validos_{prefixo}")
    out = validos.to_frame()
    total_direita = None
    for nr, sigla in config.PARTIDOS_DIREITA.items():
        v = _soma_por_local(df_cargo, _mascara_partido_proporcional(df_cargo, nr),
                            f"votos_{sigla.lower()}_{prefixo}")
        out = out.join(v, how="left")
        out[v.name] = out[v.name].fillna(0)
        out[f"pct_{sigla.lower()}_{prefixo}"] = out[v.name] / out[f"validos_{prefixo}"]
        total_direita = out[v.name] if total_direita is None else total_direita + out[v.name]
    out[f"votos_direita_{prefixo}"] = total_direita
    out[f"pct_direita_{prefixo}"] = total_direita / out[f"validos_{prefixo}"]
    return out


# ---------------------------------------------------------------------------
# Blocos 1 e 2 — desempenho eleitoral por local
# ---------------------------------------------------------------------------

def metricas_2022() -> pd.DataFrame:
    v = _carrega_votacao(config.ANO_GERAL)

    dep_est = _cargo(v, "Deputado Estadual")
    dep_fed = _cargo(v, "Deputado Federal")
    pres = _cargo(v, "Presidente")
    gov = _cargo(v, "Governador")

    out = _metricas_proporcional(dep_est, "dep_est_22")
    out = out.join(_metricas_proporcional(dep_fed, "dep_fed_22"), how="outer")

    # Presidente: referência de teto da direita (candidato nº 22 em 2022)
    out = out.join(_soma_por_local(
        pres, ~pres["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS), "validos_pres_22"),
        how="outer")
    out = out.join(_soma_por_local(
        pres, pres["NR_VOTAVEL"] == config.PRESIDENTE_DIREITA_NR,
        "votos_bolsonaro_22"), how="outer")
    out["pct_bolsonaro_22"] = out["votos_bolsonaro_22"] / out["validos_pres_22"]

    # Governador: NOVO/PL só entram se de fato tiverem candidato
    nrs_gov = set(gov["NR_VOTAVEL"].dropna().astype(int).unique())
    for nr, sigla in config.PARTIDOS_DIREITA.items():
        col = f"votos_gov_{sigla.lower()}_22"
        if nr in nrs_gov:
            out = out.join(_soma_por_local(gov, gov["NR_VOTAVEL"] == nr, col),
                           how="outer")
            out[f"pct_gov_{sigla.lower()}_22"] = out[col] / out.join(
                _soma_por_local(gov, ~gov["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS),
                                "val_gov"), how="left")["val_gov"]
        else:
            _aviso(f"O {sigla} não teve candidato a Governador de SC em 2022 "
                   "(nenhum voto com esse número na capital) — colunas de "
                   "governador desse partido ficam zeradas.")
            out[col] = 0
            out[f"pct_gov_{sigla.lower()}_22"] = 0.0

    # Bloco 2 — candidato-alvo (Matheus Cadorin, dep. estadual)
    out = out.join(_soma_por_local(
        dep_est, dep_est["NR_VOTAVEL"] == config.CANDIDATO_ALVO["nr_votavel"],
        "votos_matheus_22"), how="outer")
    out["votos_matheus_22"] = out["votos_matheus_22"].fillna(0)
    out["penetracao_matheus"] = np.where(
        out["votos_direita_dep_est_22"] > 0,
        out["votos_matheus_22"] / out["votos_direita_dep_est_22"], 0.0)

    # Bloco 3 — comparecimento estimado: todos os votos do cargo de referência
    # (válidos + brancos + nulos) — o TSE registra branco/nulo por seção.
    out = out.join(_soma_por_local(
        dep_est, pd.Series(True, index=dep_est.index), "comparecimento_22"),
        how="outer")
    return out


def metricas_2024() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (métricas por local, tabela de candidatos a prefeito)."""
    v = _carrega_votacao(config.ANO_MUNICIPAL)
    ver = _cargo(v, "Vereador")
    pref = _cargo(v, "Prefeito")

    out = _metricas_proporcional(ver, "ver_24")

    # Top 3 vereadores NOVO/PL mais votados em cada local (nominal, 5 dígitos)
    nom = ver[(ver["NR_VOTAVEL"] >= 10000) & (ver["NR_VOTAVEL"] <= 99999)].copy()
    nom["partido"] = nom["NR_VOTAVEL"].astype(int).astype(str).str[:2].astype(int)
    nom = nom[nom["partido"].isin(config.PARTIDOS_DIREITA)]
    top = (nom.groupby(["chave", "NM_VOTAVEL", "partido"], as_index=False)
              ["QT_VOTOS"].sum()
              .sort_values(["chave", "QT_VOTOS"], ascending=[True, False]))
    top["rotulo"] = (top["NM_VOTAVEL"].str.title() + " ("
                     + top["partido"].map(config.PARTIDOS_DIREITA) + ", "
                     + top["QT_VOTOS"].astype(str) + " votos)")
    top3 = (top.groupby("chave")["rotulo"]
               .apply(lambda s: " | ".join(s.head(3))).rename("top3_vereadores_direita"))
    out = out.join(top3, how="left")

    # Prefeito: % por candidato (leitura de alinhamento local)
    validos_pref = _soma_por_local(
        pref, ~pref["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS), "validos_pref_24")
    cand = (pref[~pref["NR_VOTAVEL"].isin(config.NR_NAO_VALIDOS)]
            .groupby(["chave", "NM_VOTAVEL"])["QT_VOTOS"].sum().reset_index())
    cand = cand.merge(validos_pref, on="chave")
    cand["pct"] = cand["QT_VOTOS"] / cand["validos_pref_24"]
    # dict {candidato: %} por local, serializado em JSON para o CSV/popup
    pref_json = (cand.groupby("chave")
                 .apply(lambda g: json.dumps(
                     {r["NM_VOTAVEL"].title(): round(r["pct"] * 100, 1)
                      for _, r in g.sort_values("QT_VOTOS", ascending=False).iterrows()},
                     ensure_ascii=False), include_groups=False)
                 .rename("prefeito_2024_pct"))
    lider = (cand.sort_values("QT_VOTOS", ascending=False)
             .drop_duplicates("chave").set_index("chave"))
    out = out.join(pref_json, how="left")
    out["prefeito_lider_24"] = (
        lider["NM_VOTAVEL"].str.title() + " ("
        + (lider["pct"] * 100).map(lambda x: f"{x:.1f}".replace(".", ","))
        + "%)")
    return out, cand


# ---------------------------------------------------------------------------
# Perfil demográfico por local (Bloco 3 / caracterização p/ linguagem)
# ---------------------------------------------------------------------------

FAIXAS_JOVEM = {"16 ANOS", "17 ANOS", "18 ANOS", "18 A 20 ANOS", "19 ANOS",
                "20 ANOS", "21 A 24 ANOS"}
FAIXAS_60MAIS = {"60 A 64 ANOS", "65 A 69 ANOS", "70 A 74 ANOS",
                 "75 A 79 ANOS", "80 A 84 ANOS", "85 A 89 ANOS",
                 "90 A 94 ANOS", "95 A 99 ANOS", "100 ANOS OU MAIS"}


def perfil_por_local() -> pd.DataFrame:
    p = pd.read_parquet(config.DIR_PROC / "perfil_2022.parquet")
    p["chave"] = chave_local(p)
    p["QT"] = p["QT_ELEITORES_PERFIL"]
    total = p.groupby("chave")["QT"].sum().rename("perfil_total")

    def share(mask, nome):
        s = p[mask].groupby("chave")["QT"].sum()
        return (s / total).rename(nome)

    fx = p["DS_FAIXA_ETARIA"].map(norm_txt)
    esc = p["DS_GRAU_ESCOLARIDADE"].map(norm_txt)
    gen = p["DS_GENERO"].map(norm_txt)
    out = pd.concat([
        total,
        share(fx.isin(FAIXAS_JOVEM), "pct_16a24"),
        share(fx.isin(FAIXAS_60MAIS), "pct_60mais"),
        share(esc == "SUPERIOR COMPLETO", "pct_superior"),
        share(gen == "FEMININO", "pct_feminino"),
    ], axis=1)
    return out


# ---------------------------------------------------------------------------
# Bairro oficial (IBGE Censo 2022) via point-in-polygon
# ---------------------------------------------------------------------------

def bairros_ibge() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(config.DIR_RAW / "bairros_sc" / "SC_bairros_CD2022.shp")
    fln = gdf[gdf["CD_MUN"].astype(str) == config.CODIGO_IBGE_MUNICIPIO]
    return fln[["CD_BAIRRO", "NM_BAIRRO", "geometry"]].to_crs("EPSG:4326")


def atribuir_bairro_ibge(tab: pd.DataFrame) -> pd.DataFrame:
    """Casa cada local com o polígono de bairro do IBGE pela COORDENADA
    (não pelo nome — grafias do TSE divergem). Sem coordenada ou fora da
    malha -> usa o bairro do TSE como fallback."""
    poligonos = bairros_ibge()
    com_coord = tab.dropna(subset=["lat", "lon"])
    pts = gpd.GeoDataFrame(
        com_coord[[]],
        geometry=gpd.points_from_xy(com_coord["lon"], com_coord["lat"]),
        crs="EPSG:4326")
    join = gpd.sjoin(pts, poligonos, how="left", predicate="within")
    join = join[~join.index.duplicated(keep="first")]  # pontos em fronteira
    tab["bairro_ibge"] = join["NM_BAIRRO"]
    fora = tab["bairro_ibge"].isna() & tab["lat"].notna()
    if fora.any():
        # ponto fora de qualquer polígono (coordenada imprecisa do TSE):
        # casa com o polígono mais próximo em vez de descartar
        pts_fora = gpd.GeoDataFrame(
            tab[fora][[]],
            geometry=gpd.points_from_xy(tab.loc[fora, "lon"], tab.loc[fora, "lat"]),
            crs="EPSG:4326")
        # nearest exige CRS projetado; SIRGAS 2000 / UTM 22S cobre Floripa
        near = gpd.sjoin_nearest(pts_fora.to_crs("EPSG:31982"),
                                 poligonos.to_crs("EPSG:31982"), how="left")
        near = near[~near.index.duplicated(keep="first")]
        tab.loc[fora, "bairro_ibge"] = near["NM_BAIRRO"]
    tab["bairro_ibge"] = tab["bairro_ibge"].fillna(tab["bairro_tse"].str.title())
    return tab


# ---------------------------------------------------------------------------
# Montagem final
# ---------------------------------------------------------------------------

def montar_tabela_locais() -> pd.DataFrame:
    print("  cadastro de locais…")
    cad = montar_cadastro()
    cad = geocodificar_faltantes(cad)

    print("  métricas 2022…")
    m22 = metricas_2022()
    print("  métricas 2024…")
    m24, _ = metricas_2024()
    print("  perfil demográfico…")
    perf = perfil_por_local()

    tab = cad.join(m22, how="left").join(m24, how="left").join(perf, how="left")

    # abstenção 2022 (cargo de referência: dep. estadual, inclui brancos/nulos);
    # locais com 0 aptos em 2022 (seções remanejadas) ficam sem o dado.
    # (floats explícitos: dtypes pyarrow propagam pd.NA, que quebra np.where)
    aptos22 = pd.to_numeric(tab["aptos_2022"], errors="coerce").astype("float64")
    comp22 = pd.to_numeric(tab["comparecimento_22"], errors="coerce").astype("float64")
    tab["abstencao_22"] = np.where(aptos22 > 0, 1 - comp22 / aptos22, np.nan)

    # consistência da direita 2022 -> 2024 (usada no índice)
    tab["delta_direita_22_24"] = (tab["pct_direita_ver_24"]
                                  - tab["pct_direita_dep_est_22"])

    print("  bairros IBGE (point-in-polygon)…")
    tab = atribuir_bairro_ibge(tab)

    # macrorregião para o roteiro
    tab["regiao"] = (tab["bairro_ibge"].map(norm_txt).map(config.REGIOES)
                     .fillna(tab["bairro_tse"].map(norm_txt).map(config.REGIOES)))
    sem_regiao = tab["regiao"].isna()
    if sem_regiao.any():
        nomes = sorted(set(tab.loc[sem_regiao, "bairro_ibge"].dropna()))
        _aviso("bairros sem macrorregião mapeada (caíram em 'Outros'): "
               + ", ".join(nomes))
        tab["regiao"] = tab["regiao"].fillna("Outros")

    n_novos = int(tab["so_2024"].sum())
    if n_novos:
        maior = tab[tab["so_2024"]].nlargest(1, "aptos")
        _aviso(f"{n_novos} locais criados em 2024 não têm histórico de 2022 "
               f"(o maior: {maior['nome'].iat[0]}, {int(maior['aptos'].iat[0])} "
               "eleitores) — o componente POTENCIAL deles fica subestimado; "
               "em geral são desmembramentos de locais vizinhos do ranking.")

    tab.index.name = "chave"

    # Converte tudo que é numérico para float64/NaN puro: os dtypes pyarrow
    # herdados da leitura propagam pd.NA, que estoura em np.where / contexto
    # booleano nas etapas seguintes (mapa, índice).
    TEXTO = {"nome", "endereco", "bairro_tse", "bairro_ibge", "cep", "regiao",
             "top3_vereadores_direita", "prefeito_lider_24", "prefeito_2024_pct"}
    BOOL = {"so_2022", "so_2024"}
    for c in tab.columns:
        if c in TEXTO:
            tab[c] = tab[c].astype(object).where(tab[c].notna(), None)
        elif c in BOOL:
            tab[c] = tab[c].fillna(False).astype(bool)
        else:
            tab[c] = pd.to_numeric(tab[c], errors="coerce").astype("float64")
    return tab


# ---------------------------------------------------------------------------
# Agregação por bairro (IBGE) — alimenta os coropléticos e o relatório
# ---------------------------------------------------------------------------

def agregar_bairros(tab: pd.DataFrame) -> pd.DataFrame:
    """Soma/pondera as métricas dos locais dentro de cada bairro IBGE.
    Percentuais são recalculados das somas (não é média de percentuais)."""
    g = tab.groupby("bairro_ibge")
    agg = pd.DataFrame({
        "regiao": g["regiao"].agg(lambda s: s.mode().iat[0]),
        "n_locais": g.size(),
        "aptos": g["aptos"].sum(),
        "votos_direita_22": g["votos_direita_dep_est_22"].sum(),
        "validos_22": g["validos_dep_est_22"].sum(),
        "votos_novo_22": g["votos_novo_dep_est_22"].sum(),
        "votos_pl_22": g["votos_pl_dep_est_22"].sum(),
        "votos_direita_24": g["votos_direita_ver_24"].sum(),
        "validos_24": g["validos_ver_24"].sum(),
        "votos_bolsonaro_22": g["votos_bolsonaro_22"].sum(),
        "validos_pres_22": g["validos_pres_22"].sum(),
        "votos_matheus_22": g["votos_matheus_22"].sum(),
        "comparecimento_22": g["comparecimento_22"].sum(),
        "aptos_2022": g["aptos_2022"].sum(),
    })
    agg["pct_direita_22"] = agg["votos_direita_22"] / agg["validos_22"]
    agg["pct_novo_22"] = agg["votos_novo_22"] / agg["validos_22"]
    agg["pct_pl_22"] = agg["votos_pl_22"] / agg["validos_22"]
    agg["pct_direita_24"] = agg["votos_direita_24"] / agg["validos_24"]
    agg["pct_bolsonaro_22"] = agg["votos_bolsonaro_22"] / agg["validos_pres_22"]
    agg["penetracao_matheus"] = np.where(
        agg["votos_direita_22"] > 0,
        agg["votos_matheus_22"] / agg["votos_direita_22"], 0.0)
    agg["abstencao_22"] = np.where(
        agg["aptos_2022"] > 0,
        1 - agg["comparecimento_22"] / agg["aptos_2022"], np.nan)
    # score do bairro = média dos locais ponderada pelo eleitorado
    peso = tab["aptos"].fillna(0)
    agg["score"] = (tab["score"] * peso).groupby(tab["bairro_ibge"]).sum() / \
        peso.groupby(tab["bairro_ibge"]).sum()
    # perfil ponderado pelo nº de eleitores com perfil conhecido
    pp = tab["perfil_total"].fillna(0)
    for col in ("pct_16a24", "pct_60mais", "pct_superior", "pct_feminino"):
        agg[col] = (tab[col] * pp).groupby(tab["bairro_ibge"]).sum() / \
            pp.groupby(tab["bairro_ibge"]).sum()
    return agg.sort_values("score", ascending=False)
