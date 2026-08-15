# -*- coding: utf-8 -*-
"""Bloco 4: calendário operacional dia a dia (16/08 a 03/10/2026).

Lógica:
  - Dias úteis: 2 turnos (manhã e tarde) com a equipe fixa; às qua/sex a
    manhã prioriza feiras livres do território de afinidade.
  - Sábado: feiras de manhã (equipe ampliada) + centrinhos à tarde.
  - Domingo: ação leve opcional (orlas/praças), 1 turno.
  - Fases (plano_config.FASES): 1 nome-na-rua (fluxo), 2 conversão
    (afinidade×perfil), 3 saturação (top índice).
  - Rotação: cooldown de 1 dia por ponto; pontos top ganham reforço até
    atingirem ao menos 4 visitas na campanha.
  - Chuva: cada linha tem alternativa coberta da região.
  - 04/10 (dia da eleição) fica FORA: distribuir material no dia é crime
    (boca de urna). Último dia: 03/10, até 22h.
"""

from datetime import timedelta

import numpy as np
import pandas as pd

from . import config, plano_config

DIAS_PT = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def _fase_do_dia(d):
    for f in plano_config.FASES:
        if f["inicio"] <= d <= f["fim"]:
            return f["nome"]
    return "?"


def _pool_da_fase(pts, fase_nome):
    v = pts[~pts["inviavel"]]
    if fase_nome.startswith("Fase 1"):
        return v.sort_values("comp_fluxo", ascending=False)
    if fase_nome.startswith("Fase 2"):
        chave = 0.6 * v["comp_afinidade"] + 0.4 * v["comp_perfil"]
        return v.loc[chave.sort_values(ascending=False).index]
    return v.sort_values("indice", ascending=False)


def gerar_calendario(pts: pd.DataFrame) -> pd.DataFrame:
    pts = pts.copy()
    visitas = {i: 0 for i in pts.index}
    ultimo_dia = {i: None for i in pts.index}
    linhas = []

    d = plano_config.INICIO_CAMPANHA
    while d <= plano_config.FIM_PANFLETAGEM:
        dow = DIAS_PT[d.weekday()]
        fase = _fase_do_dia(d)
        pool = _pool_da_fase(pts, fase)

        if dow in ("seg", "ter", "qua", "qui", "sex"):
            equipe_dia = plano_config.EQUIPE["fixos_dia_util"]
            turnos_dia = [("manha", equipe_dia), ("tarde", equipe_dia)]
            # qua/sex de manhã: janela de feira substitui a manhã comum;
            # ter/qui: turno de almoço (calçadão, mercado, polos tech) no
            # lugar da manhã — sem isso os pontos de janela "almoco" nunca
            # entrariam na escala
            if dow in ("qua", "sex"):
                turnos_dia[0] = ("feira", equipe_dia)
            elif dow in ("ter", "qui"):
                turnos_dia[0] = ("almoco", equipe_dia)
        elif dow == "sab":
            equipe_dia = plano_config.EQUIPE["sabado"]
            turnos_dia = [("feira", equipe_dia), ("fds_tarde", equipe_dia)]
        else:
            equipe_dia = plano_config.EQUIPE["domingo"]
            turnos_dia = [("fds_tarde", equipe_dia)] if equipe_dia else []

        usados_hoje = set()
        for turno, equipe in turnos_dia:
            h_ini, h_fim = plano_config.TURNOS[turno]
            horas = ((int(h_fim[:2]) * 60 + int(h_fim[3:5]))
                     - (int(h_ini[:2]) * 60 + int(h_ini[3:5]))) / 60

            # elegíveis: janela compatível, dia de feira respeitado, não usado
            # hoje; cooldown de 1 dia (relaxado se faltar candidato)
            def elegivel(pid, r, com_cooldown=True):
                if turno not in r["janelas"].split(","):
                    return False
                # dias_fixos vira NaN (float) no parquet quando é None
                if isinstance(r["dias_fixos"], str) and dow not in r["dias_fixos"].split(","):
                    return False
                if pid in usados_hoje:
                    return False
                if com_cooldown and ultimo_dia[pid] == d - timedelta(days=1):
                    return False
                return True

            cand = [(pid, r) for pid, r in pool.iterrows() if elegivel(pid, r)]
            if len(cand) < 2:  # fim de semana aperta a rotação: ignora cooldown
                cand = [(pid, r) for pid, r in pool.iterrows()
                        if elegivel(pid, r, com_cooldown=False)]
            # reforço para os top-10 que ainda não bateram 4 visitas
            top10 = set(pts.nlargest(10, "indice").index)
            cand.sort(key=lambda x: (
                -(2.0 if x[0] in top10 and visitas[x[0]] < 4 else 1.0)
                * (x[1]["indice"] + 1) / (1 + visitas[x[0]])))

            restante = equipe
            alocados = 0
            for pid, r in cand:
                if restante <= 0:
                    break
                pessoas = int(min(r["pessoas_ideal"], restante))
                if pessoas < max(1, r["pessoas_ideal"] - 1):
                    continue  # não vale mandar equipe pela metade
                restante -= pessoas
                # P1 = cabe dentro da equipe mínima viável; é o que não cai
                # se faltar gente no dia. P2 = só com equipe completa.
                prioridade = ("P1" if alocados < plano_config.EQUIPE["minimo_viavel"]
                              else "P2")
                alocados += pessoas
                visitas[pid] += 1
                ultimo_dia[pid] = d
                usados_hoje.add(pid)
                panfletos = r["fluxo_panfletos_hora"] * pessoas * horas * 0.85
                linhas.append({
                    "data": d.strftime("%d/%m/%Y"), "dia": dow, "fase": fase,
                    "turno": turno, "inicio": h_ini, "fim": h_fim,
                    "ponto_id": pid, "ponto": r["nome"], "endereco": r["endereco"],
                    "regiao": r["regiao"], "tipo": r["tipo"], "pessoas": pessoas,
                    "panfletos": panfletos, "prioridade": prioridade,
                    "observacao": plano_config.DATAS_ESPECIAIS.get(d, ""),
                    "indice_ponto": r["indice"],
                    "justificativa": (
                        f"índice {r['indice']:.0f}; direita 2024 no entorno "
                        f"{100*r['pct_direita_ver24_1km']:.0f}%; "
                        f"~{r['fluxo_panfletos_hora']:.0f} panfletos/h/pessoa"),
                    "alternativa_chuva": ("ponto já coberto" if r["coberto"]
                                          else plano_config.PLANO_CHUVA[r["regiao"]]),
                })
        d += timedelta(days=1)

    cal = pd.DataFrame(linhas)
    # escala a tiragem para caber no orçamento e arredonda em múltiplos de 50
    fator = plano_config.ORCAMENTO_PANFLETOS / cal["panfletos"].sum()
    cal["panfletos"] = (cal["panfletos"] * min(fator, 1.0) / 50).round() * 50
    cal.attrs["fator_orcamento"] = round(float(fator), 3)
    cal.to_parquet(config.DIR_PROC / "plano_calendario.parquet")
    return cal
