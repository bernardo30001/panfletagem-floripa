#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plano de panfletagem 2026 — orquestrador.

Pré-requisito: `python3 run_pipeline.py` já rodado (gera a tabela de locais).
Uso: python3 run_plano.py
Parâmetros (equipe, orçamento, pesos, catálogo de pontos): pipeline/plano_config.py
"""

import pandas as pd

from pipeline import (config, plano_analise, plano_calendario, plano_estrategia,
                      plano_mapa, plano_pontos, plano_relatorio, plano_xlsx)


def main():
    config.DIR_SAIDA.mkdir(parents=True, exist_ok=True)

    print("== 1/4 Análise dos 4 ciclos por local ==")
    tab = plano_analise.montar_plano_locais()
    plano_analise.testar_hipotese(tab)

    print("== 2/4 Índice por ponto físico ==")
    pts = plano_pontos.montar_pontos()
    csv = config.DIR_SAIDA / "ranking_pontos.csv"
    pts.to_csv(csv, encoding="utf-8-sig", sep=";", decimal=",", float_format="%.4f")
    print(f"  ranking de pontos salvo em {csv}")

    print("== 3/4 Calendário operacional ==")
    cal = plano_calendario.gerar_calendario(pts)
    plano_xlsx.escrever_xlsx(cal, config.DIR_SAIDA / "calendario_panfletagem.xlsx")

    print("== 4/4 Mapa e relatório ==")
    plano_mapa.gerar_mapa_plano(config.DIR_SAIDA / "mapa_plano.html")
    plano_relatorio.gerar_relatorio_plano(config.DIR_SAIDA / "relatorio_plano.md")
    plano_estrategia.gerar_estrategia(
        config.DIR_SAIDA / "estrategia_coordenacao.md")

    print("\n============= 15 PONTOS DE OURO =============")
    for i, (pid, r) in enumerate(pts[~pts["inviavel"]].nlargest(15, "indice").iterrows(), 1):
        print(f"{i:2d}. [{r['indice']:5.1f}] {r['nome']}")
    print("=============================================")
    print(f"\nEntregáveis do plano em {config.DIR_SAIDA}/")


if __name__ == "__main__":
    main()
