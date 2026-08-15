# -*- coding: utf-8 -*-
"""Funções utilitárias compartilhadas: normalização de texto e leitura dos CSVs
do TSE (separador ';', encoding latin-1) direto de dentro dos zips, em chunks,
para não carregar arquivos de 600+ MB inteiros na memória."""

import io
import unicodedata
import zipfile

import pandas as pd


def norm_txt(s) -> str:
    """Normaliza texto do TSE para comparação: remove acentos, caixa alta,
    espaços colapsados. Ex.: 'Florianópolis ' -> 'FLORIANOPOLIS'."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(s.upper().split())


def ler_zip_chunks(zip_path, csv_membro, usecols=None, chunksize=500_000):
    """Gera chunks de um CSV do TSE contido em `zip_path`.

    O TSE distribui CSVs com separador ';' e encoding latin-1 (ISO-8859-1);
    campos de texto vêm entre aspas. Ler direto do zip evita extrair 600 MB
    para o disco.
    """
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(csv_membro) as f:
            yield from pd.read_csv(
                f, sep=";", encoding="latin-1", usecols=usecols,
                chunksize=chunksize, dtype_backend="pyarrow",
            )


def chave_local(df, col_zona="NR_ZONA", col_local="NR_LOCAL_VOTACAO"):
    """Chave única de um local de votação: zona + número do local.

    O número do local (NR_LOCAL_VOTACAO) só é único dentro da zona eleitoral,
    então a chave precisa combinar os dois.
    """
    return (
        "Z" + df[col_zona].astype("int64").astype(str)
        + "-L" + df[col_local].astype("int64").astype(str)
    )
