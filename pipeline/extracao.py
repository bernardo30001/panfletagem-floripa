# -*- coding: utf-8 -*-
"""Extração: filtra Florianópolis dos CSVs brutos do TSE e salva recortes
enxutos em parquet (data/processed/). Rodar uma vez por download; os passos
seguintes do pipeline só leem os parquets.

O filtro de município é SEMPRE por nome normalizado (norm_txt), nunca por
código fixo — o TSE grafa 'FLORIANÓPOLIS' com acento e latin-1.
"""

import sys

import pandas as pd

from . import config
from .util import ler_zip_chunks, norm_txt

COLS_VOTACAO = [
    "ANO_ELEICAO", "NR_TURNO", "SG_UF", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO",
    "CD_CARGO", "DS_CARGO", "NR_VOTAVEL", "NM_VOTAVEL", "QT_VOTOS",
    "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_LOCAL_VOTACAO_ENDERECO",
]

COLS_LOCAIS = [
    "SG_UF", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO",
    "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO", "NR_CEP",
    "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO", "NR_TURNO",
]

COLS_PERFIL = [
    "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO",
    "DS_GENERO", "DS_FAIXA_ETARIA", "DS_GRAU_ESCOLARIDADE",
    "QT_ELEITORES_PERFIL",
]

COLS_MUNZONA = [
    "NM_MUNICIPIO", "DS_CARGO", "NR_CANDIDATO", "NM_URNA_CANDIDATO",
    "SG_PARTIDO", "NR_PARTIDO", "QT_VOTOS_NOMINAIS", "DS_SIT_TOT_TURNO",
]


def _filtra_municipio(chunk: pd.DataFrame) -> pd.DataFrame:
    return chunk[chunk["NM_MUNICIPIO"].map(norm_txt) == config.MUNICIPIO_ALVO]


def _extrai(zip_nome, csv_nome, usecols, filtro_extra=None, rotulo=""):
    """Varre um CSV do TSE em chunks e devolve só as linhas de Florianópolis."""
    partes = []
    zp = config.DIR_RAW / zip_nome
    for chunk in ler_zip_chunks(zp, csv_nome, usecols=usecols):
        if filtro_extra is not None:
            chunk = filtro_extra(chunk)
        fl = _filtra_municipio(chunk)
        if len(fl):
            partes.append(fl)
    if not partes:
        print(f"  AVISO: nenhuma linha de Florianópolis em {csv_nome}!", file=sys.stderr)
        return pd.DataFrame(columns=usecols)
    df = pd.concat(partes, ignore_index=True)
    print(f"  {rotulo or csv_nome}: {len(df):,} linhas de Florianópolis")
    return df


def extrair_votacao_historica():
    """Ciclos 2018 e 2020 (para tendência e base histórica do voto liberal).
    Os arquivos regenerados pelo TSE têm o mesmo leiaute de 26 colunas,
    incluindo NR_LOCAL_VOTACAO — confirmado no cabeçalho antes de usar."""
    for ano in (2018, 2020):
        saida = config.DIR_PROC / f"votacao_{ano}.parquet"
        if saida.exists():
            continue
        df = _extrai(f"votacao_secao_{ano}_SC.zip", f"votacao_secao_{ano}_SC.csv",
                     COLS_VOTACAO, rotulo=f"votação {ano}")
        df.to_parquet(saida, index=False)


def extrair_votacao():
    """Recortes de votação por seção. Presidente só existe no arquivo _BR
    (abrangência federal), por isso 2022 = concat(_SC, _BR)."""
    saida22 = config.DIR_PROC / "votacao_2022.parquet"
    saida24 = config.DIR_PROC / "votacao_2024.parquet"

    if not saida22.exists():
        sc = _extrai("votacao_secao_2022_SC.zip", "votacao_secao_2022_SC.csv",
                     COLS_VOTACAO, rotulo="votação 2022 (cargos estaduais)")
        br = _extrai("votacao_secao_2022_BR.zip", "votacao_secao_2022_BR.csv",
                     COLS_VOTACAO,
                     filtro_extra=lambda c: c[c["SG_UF"] == "SC"],
                     rotulo="votação 2022 (Presidente, arquivo BR)")
        pd.concat([sc, br], ignore_index=True).to_parquet(saida22, index=False)

    if not saida24.exists():
        v24 = _extrai("votacao_secao_2024_SC.zip", "votacao_secao_2024_SC.csv",
                      COLS_VOTACAO, rotulo="votação 2024")
        v24.to_parquet(saida24, index=False)


def extrair_locais():
    """Locais de votação (endereço, bairro, coordenadas, eleitores por seção).
    Arquivo nacional -> pré-filtra SG_UF antes do filtro por nome."""
    for ano in (2018, 2020, config.ANO_GERAL, config.ANO_MUNICIPAL):
        saida = config.DIR_PROC / f"locais_{ano}.parquet"
        if saida.exists():
            continue
        df = _extrai(
            f"eleitorado_local_votacao_{ano}.zip",
            f"eleitorado_local_votacao_{ano}.csv",
            COLS_LOCAIS,
            filtro_extra=lambda c: c[c["SG_UF"] == "SC"],
            rotulo=f"locais de votação {ano}",
        )
        # O arquivo repete cada local por turno; para cadastro basta o 1º turno.
        df = df[df["NR_TURNO"] == 1].drop(columns=["NR_TURNO"])
        df.to_parquet(saida, index=False)


def extrair_perfil():
    """Perfil do eleitorado por seção (faixa etária, gênero, escolaridade)."""
    saida = config.DIR_PROC / "perfil_2022.parquet"
    if saida.exists():
        return
    df = _extrai("perfil_eleitor_secao_2022_SC.zip",
                 "perfil_eleitor_secao_2022_SC.csv",
                 COLS_PERFIL, rotulo="perfil do eleitorado 2022")
    df.to_parquet(saida, index=False)


def extrair_eleitos_2024():
    """Resultado por candidato (munzona 2024): de onde sai quem foi ELEITO.
    Usado na análise de 'voto órfão' (bairro forte sem vereador local)."""
    saida = config.DIR_PROC / "resultado_vereador_2024.parquet"
    if saida.exists():
        return
    df = _extrai("votacao_candidato_munzona_2024.zip",
                 "votacao_candidato_munzona_2024_SC.csv",
                 COLS_MUNZONA, rotulo="resultado vereadores 2024")
    df = df[df["DS_CARGO"].map(norm_txt) == "VEREADOR"]
    # soma zonas -> total por candidato
    df = (df.groupby(["NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO",
                      "NR_PARTIDO", "DS_SIT_TOT_TURNO"], as_index=False)
            ["QT_VOTOS_NOMINAIS"].sum())
    df.to_parquet(saida, index=False)


def extrair_tudo():
    config.DIR_PROC.mkdir(parents=True, exist_ok=True)
    extrair_votacao()
    extrair_locais()
    extrair_perfil()
    extrair_eleitos_2024()
