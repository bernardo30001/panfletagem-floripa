# -*- coding: utf-8 -*-
"""Bloco 4 — Índice de Prioridade de Panfletagem.

Fórmula (documentada também no relatório):

    score = 100 * minmax( w_pot*POT + w_lib*LIB + w_den*DEN + w_con*CON )

onde cada componente é normalizado (min-max por padrão, z-score opcional em
config.NORMALIZACAO) antes da soma ponderada:

    POT (potencial)    = votos absolutos NOVO+PL p/ dep. estadual 2022 no local
    LIB (liberal)      = média do %NOVO p/ vereador 2024 e dep. estadual 2022
    DEN (densidade)    = eleitores aptos do local (2022; 2024 se local novo)
    CON (consistência) = 1 - |%direita dep.est. 2022 - %direita vereador 2024|

A votação do Matheus NÃO entra no score (ver a justificativa em
config.PESOS_INDICE) — ela segue no CSV e nos popups apenas como diagnóstico.
LIB substituiu o antigo GAP: em vez de perguntar "onde ele não teve voto"
(ruído, com 84 votos), pergunta "onde vive o eleitor liberal" — que é o
mesmo eleitor, medido com uma amostra 700x maior.

Pesos em config.PESOS_INDICE. Locais com menos de config.MIN_ELEITORES_LOCAL
eleitores recebem score 0 e ficam sinalizados (flag_pequeno) — sem equipe.
"""

import numpy as np
import pandas as pd

from . import config


def _normaliza(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if config.NORMALIZACAO == "zscore":
        z = (s - s.mean()) / (s.std() or 1.0)
        # traz o z-score para [0,1] para os pesos manterem a interpretação
        return (z - z.min()) / ((z.max() - z.min()) or 1.0)
    lo, hi = s.min(), s.max()
    return (s - lo) / ((hi - lo) or 1.0)


def calcular_indice(tab: pd.DataFrame) -> pd.DataFrame:
    w = config.PESOS_INDICE

    pot = tab["votos_direita_dep_est_22"].fillna(0)
    den = tab["aptos"].fillna(0)
    # consistência: sem dado de 2024 (local desativado) -> neutro (mediana)
    delta = tab["delta_direita_22_24"].abs()
    con = (1 - delta).fillna((1 - delta).median())
    # liberal: % do NOVO especificamente (não o agregado NOVO+PL, que em 2024
    # é dominado pelo PL). Média das duas eleições disponíveis; onde só existe
    # uma delas (local novo ou desativado), usa a que existir.
    lib = pd.concat([
        _normaliza(tab["pct_novo_ver_24"]),
        _normaliza(tab["pct_novo_dep_est_22"]),
    ], axis=1).mean(axis=1, skipna=True)
    lib = lib.fillna(lib.median())

    tab["comp_potencial"] = _normaliza(pot)
    tab["comp_liberal"] = lib
    tab["comp_densidade"] = _normaliza(den)
    tab["comp_consistencia"] = _normaliza(con)

    bruto = (w["potencial"] * tab["comp_potencial"]
             + w["liberal"] * tab["comp_liberal"]
             + w["densidade"] * tab["comp_densidade"]
             + w["consistencia"] * tab["comp_consistencia"])

    tab["flag_pequeno"] = tab["aptos"].fillna(0) < config.MIN_ELEITORES_LOCAL
    bruto = bruto.where(~tab["flag_pequeno"], 0.0)

    tab["score"] = (100 * _normaliza(bruto)).round(1)
    return tab.sort_values("score", ascending=False)
