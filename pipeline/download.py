# -*- coding: utf-8 -*-
"""Download dos dados brutos com cache em data/raw/.

IMPORTANTE: nesta máquina o Python (requests/urllib) falha o handshake SSL com
cdn.tse.jus.br — há um proxy de rede com certificado self-signed no caminho.
O curl do sistema resolve, então TODOS os downloads usam curl via subprocess.
Não trocar por requests sem testar.
"""

import subprocess
import sys

from . import config


def _curl(url: str, destino) -> bool:
    """Baixa `url` para `destino` com curl. Retorna True se ok."""
    r = subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", "1800", "-o", str(destino), url],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ERRO ao baixar {url}\n  {r.stderr.strip()}", file=sys.stderr)
        if destino.exists():
            destino.unlink()  # não deixar arquivo pela metade no cache
        return False
    return True


def baixar_tudo() -> list[str]:
    """Garante que todos os arquivos-fonte existem em data/raw/.

    Retorna a lista de arquivos que FALTARAM (vazia = tudo ok). Arquivos já
    presentes não são rebaixados (cache).
    """
    config.DIR_RAW.mkdir(parents=True, exist_ok=True)
    faltando = []

    for nome, url in config.URLS_TSE.items():
        destino = config.DIR_RAW / nome
        if destino.exists() and destino.stat().st_size > 10_000:
            print(f"  [cache] {nome}")
            continue
        print(f"  [baixando] {nome} ...")
        if not _curl(url, destino):
            faltando.append(nome)

    # Limite municipal (IBGE, API de malhas)
    limite = config.DIR_RAW / "limite_florianopolis.geojson"
    if not limite.exists():
        print("  [baixando] limite municipal IBGE ...")
        if not _curl(config.URL_LIMITE_IBGE, limite):
            faltando.append("limite_florianopolis.geojson")

    # Malha de bairros do Censo 2022 (shapefile por UF)
    bairros = config.DIR_RAW / "SC_bairros_CD2022.zip"
    if not bairros.exists():
        print("  [baixando] malha de bairros IBGE (Censo 2022) ...")
        if not _curl(config.URL_BAIRROS_IBGE, bairros):
            faltando.append("SC_bairros_CD2022.zip")

    if faltando:
        print(
            "\nATENÇÃO: fontes indisponíveis: " + ", ".join(faltando)
            + "\nVerifique se o TSE renomeou o arquivo em "
            "https://dadosabertos.tse.jus.br/ e ajuste config.URLS_TSE.",
            file=sys.stderr,
        )
    return faltando
