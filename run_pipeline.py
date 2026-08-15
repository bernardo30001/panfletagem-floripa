#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pipeline de inteligência eleitoral para panfletagem — Florianópolis 2026.

Uso:
    python3 run_pipeline.py            # roda tudo (downloads ficam em cache)

Etapas: download -> extração (recorte Floripa) -> métricas por local ->
índice de prioridade -> mapa + ranking + roteiro + relatório.
Parâmetros (anos, partidos, pesos do índice…): pipeline/config.py.
"""

from pipeline import (config, dashboard, download, extracao, indice, mapa,
                      metricas, relatorios)


def main():
    print("== 1/5 Download (cache em data/raw/) ==")
    faltando = download.baixar_tudo()
    if faltando:
        raise SystemExit("Abortado: fontes essenciais indisponíveis (ver acima).")

    print("== 2/5 Extração do recorte de Florianópolis ==")
    extracao.extrair_tudo()

    print("== 3/5 Métricas por local de votação ==")
    tab = metricas.montar_tabela_locais()

    print("== 4/5 Índice de prioridade ==")
    tab = indice.calcular_indice(tab)
    agg = metricas.agregar_bairros(tab)

    print("== 5/5 Entregáveis ==")
    config.DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    mapa.gerar_mapa(tab, agg, config.DIR_SAIDA / "mapa_floripa.html")
    relatorios.gerar_ranking_csv(tab, config.DIR_SAIDA / "ranking_panfletagem.csv")
    relatorios.gerar_top20(tab, config.DIR_SAIDA / "top20_roteiro.md")
    relatorios.gerar_relatorio(tab, agg, config.DIR_SAIDA / "relatorio.md")
    dashboard.gerar_dashboard(tab, config.DIR_SAIDA / "index.html")

    # tabela consolidada também em parquet, para análises ad hoc
    tab.to_parquet(config.DIR_PROC / "tabela_locais_final.parquet")

    print("\n================ TOP 10 LOCAIS PRIORITÁRIOS ================")
    top = tab[~tab["flag_pequeno"]].nlargest(10, "score")
    for i, (chave, r) in enumerate(top.iterrows(), 1):
        print(f"{i:2d}. [{r['score']:5.1f}] {r['nome']}"
              f"  ({r['bairro_ibge']} — {r['regiao']})")
        print(f"      direita 2022: {int(r['votos_direita_dep_est_22'])} votos"
              f" ({r['pct_direita_dep_est_22']*100:.1f}%)"
              f" | Matheus: {int(r['votos_matheus_22'])}"
              f" | aptos: {int(r['aptos'])}")
    print("============================================================")
    print(f"\nEntregáveis em {config.DIR_SAIDA}/")


if __name__ == "__main__":
    main()
