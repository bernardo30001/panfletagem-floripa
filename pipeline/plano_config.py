# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO DO PLANO DE PANFLETAGEM 2026 (Blocos 2, 3 e 4)
============================================================
Catálogo de pontos físicos, modelo de fluxo, pesos do índice e parâmetros
operacionais do calendário. TODAS as estimativas estão marcadas; os fatos
citam fonte no relatório.

PREMISSAS OPERACIONAIS EDITÁVEIS (o usuário não informou equipe/orçamento):
ajuste EQUIPE e ORCAMENTO_PANFLETOS e rode `python3 run_plano.py` de novo.
"""

from datetime import date

# ---------------------------------------------------------------------------
# PERÍODO E FASES
# ---------------------------------------------------------------------------
# Início REAL da operação (o coordenador informou em 15/08/2026 que a equipe
# começa na quarta 19/08) — 3 dias a menos que o período legal, que abriu em
# 16/08. Fim em 03/10: no dia 04/10 (eleição) distribuir material é crime de
# boca de urna, art. 39 §5º da Lei 9.504/97.
INICIO_CAMPANHA = date(2026, 8, 19)   # quarta-feira
FIM_PANFLETAGEM = date(2026, 10, 3)   # véspera; panfletagem até 22h (TSE 2026)

# Fases reproporcionadas para a janela de 46 dias (era 21/20/8 em 49 dias)
FASES = [
    {"nome": "Fase 1 — Nome na rua (alto fluxo)", "inicio": date(2026, 8, 19),
     "fim": date(2026, 9, 7),
     "logica": "construção de reconhecimento: semáforos e terminais de maior "
               "fluxo bruto, mesmo fora do território de maior afinidade"},
    {"nome": "Fase 2 — Conversão (território liberal)", "inicio": date(2026, 9, 8),
     "fim": date(2026, 9, 26),
     "logica": "concentração nos pontos de maior AFINIDADE×PERFIL: corredor "
               "universitário/tech, feiras e centrinhos de bairro alinhado"},
    {"nome": "Fase 3 — Saturação (top + locais de votação)", "inicio": date(2026, 9, 27),
     "fim": date(2026, 10, 3),
     "logica": "repetição dos 10 pontos de maior índice + entorno dos locais "
               "de votação do top-20 do ranking eleitoral"},
]

# Datas com dinâmica própria (entram como observação na escala)
DATAS_ESPECIAIS = {
    date(2026, 9, 7): ("7 de Setembro — desfile cívico (segunda-feira). Maior "
                       "concentração de rua do período e público majoritariamente "
                       "de direita. Alocar TODA a equipe disponível no entorno do "
                       "desfile (Beira-Mar Norte / Centro), fora do perímetro "
                       "oficial do evento."),
    date(2026, 10, 3): ("Véspera da eleição: panfletagem permitida até 22h. "
                        "PROIBIDO 'derrame' de santinhos — multa eleitoral e do "
                        "Código de Posturas. Última carga nos pontos top."),
}

# ---------------------------------------------------------------------------
# EQUIPE E MATERIAL — PREMISSAS (o coordenador deve ajustar)
# ---------------------------------------------------------------------------
EQUIPE = {
    "fixos_dia_util": 6,        # pessoas disponíveis seg–sex (PREMISSA)
    "sabado": 10,               # fixos + voluntários no sábado (PREMISSA)
    "domingo": 4,               # ação leve opcional de domingo (PREMISSA)
    "carro_apoio": True,        # há veículo para deslocar equipe (PREMISSA)
    # Se no dia aparecer menos gente que o previsto, os turnos marcados P1 na
    # escala são os que NÃO podem cair. Este número define o corte P1/P2.
    "minimo_viavel": 4,
}
ORCAMENTO_PANFLETOS = 60_000    # tiragem total para os 49 dias (PREMISSA)

# turnos padrão (hora local)
TURNOS = {
    "manha":  ("07:00", "09:00"),    # pico casa->trabalho
    "almoco": ("11:30", "13:30"),    # centro/calçadões
    "tarde":  ("17:00", "19:30"),    # pico trabalho->casa
    "feira":  ("08:30", "12:00"),    # feiras livres
    "fds_tarde": ("16:00", "19:00"), # praças/centrinhos no fim de semana
}

# ---------------------------------------------------------------------------
# PESOS DO ÍNDICE DE PRIORIZAÇÃO POR PONTO (Bloco 3)
# ---------------------------------------------------------------------------
# DECISÃO (13/08/2026): o componente GAP (1 - penetração do Cadorin) foi
# REMOVIDO a pedido do coordenador — 84 votos não sustentam um sinal, e a
# normalização transformava esse ruído em 25% do índice. No lugar entrou
# LIBERAL, que mede onde vive o eleitor-alvo usando amostras grandes: o voto
# NOVO de 2024 e a referência Bruno Souza (2018 estadual + 2022 federal).
# Premissa: partimos do zero, todo ponto é território de conquista.
PESOS_PONTO = {
    "afinidade": 0.35,   # direita ampla no entorno; 2024 vale 2x 2022; 2020 só tendência
    "liberal": 0.20,     # voto NOVO 2024 + referência Bruno Souza no entorno
    "fluxo": 0.25,       # panfletos/hora estimados (modelo abaixo)
    "perfil": 0.20,      # escolaridade superior + jovens no entorno (proxy do público-alvo)
}
RAIO_ENTORNO_KM = 1.0    # seções associadas ao ponto num raio de 1 km

# ---------------------------------------------------------------------------
# MODELO DE FLUXO (todas ESTIMATIVAS — método declarado no relatório)
# ---------------------------------------------------------------------------
# Semáforo: entregas/h/pessoa = (3600/ciclo_s) * (vermelho_s/6s por entrega)
#            * taxa de aceite veicular (0.45), teto físico de 280/h.
# Pedestre: entregas/h/pessoa = min(280, ped_hora_pico * 0.18 / 2 pessoas de ref.)
# Taxas de aceite: veículo parado 45%, pedestre em deslocamento 18%, feira 40%
# — estimativas de praxe de campanha, não há medição pública.
TAXA_ACEITE = {"veiculo": 0.45, "pedestre": 0.18, "feira": 0.40}
SEGUNDOS_POR_ENTREGA = 6
TETO_ENTREGAS_HORA = 280

# ---------------------------------------------------------------------------
# CATÁLOGO DE PONTOS FÍSICOS
# ---------------------------------------------------------------------------
# Campos: tipo: semaforo|terminal|universidade|tech|feira|calcadao|mercado|praca
#   ciclo_s/vermelho_s/faixas: só semáforos (ESTIMATIVAS de campo — a PMF não
#   publica planilha semafórica; declarado no relatório)
#   ped_hora: pedestres/hora no pico (ESTIMATIVA salvo fonte citada)
#   dias: restrição de dia da semana (feiras); None = qualquer dia
#   coordenadas: aproximadas (precisão de esquina, não de metro)
PONTOS = [
    # ---------------- SEMÁFOROS / CRUZAMENTOS ----------------
    {"id": "SEM-ITACORUBI", "nome": "Rótula do Itacorubi (Admar Gonzaga × Amaro A. Vieira)",
     "tipo": "semaforo", "lat": -27.5796, "lon": -48.4936, "regiao": "Centro",
     "endereco": "Rótula do Itacorubi, Itacorubi",
     "ciclo_s": 120, "vermelho_s": 75, "faixas": 3, "pessoas_ideal": 3,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-EDU-VIEIRA", "nome": "Semáforo UFSC Sul (Dep. Antônio Edu Vieira × Cap. Romualdo)",
     "tipo": "semaforo", "lat": -27.6063, "lon": -48.5227, "regiao": "Centro",
     "endereco": "R. Dep. Antônio Edu Vieira, Pantanal",
     "ciclo_s": 110, "vermelho_s": 65, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-MADRE-LAURO", "nome": "Semáforo Madre Benvenuta × Lauro Linhares",
     "tipo": "semaforo", "lat": -27.5901, "lon": -48.5094, "regiao": "Centro",
     "endereco": "Av. Madre Benvenuta, Santa Mônica",
     "ciclo_s": 100, "vermelho_s": 60, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-IGUATEMI", "nome": "Semáforo do Iguatemi (Av. Madre Benvenuta)",
     "tipo": "semaforo", "lat": -27.5931, "lon": -48.5023, "regiao": "Centro",
     "endereco": "Av. Madre Benvenuta, 687 — Santa Mônica",
     "ciclo_s": 100, "vermelho_s": 55, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["almoco", "tarde"]},
    {"id": "SEM-CIC", "nome": "Rótula do CIC/Beiramar (Irineu Bornhausen × H. S. Fontes)",
     "tipo": "semaforo", "lat": -27.5860, "lon": -48.5236, "regiao": "Centro",
     "endereco": "Av. Gov. Irineu Bornhausen, Agronômica",
     "ciclo_s": 130, "vermelho_s": 80, "faixas": 3, "pessoas_ideal": 3,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-MAURO-RAMOS", "nome": "Semáforo Mauro Ramos (IEE/CEFET)",
     "tipo": "semaforo", "lat": -27.5940, "lon": -48.5440, "regiao": "Centro",
     "endereco": "Av. Mauro Ramos, Centro",
     "ciclo_s": 90, "vermelho_s": 50, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "almoco", "tarde"]},
    {"id": "SEM-IVO-SILVEIRA", "nome": "Semáforo Via Expressa/Ivo Silveira (fim da BR-282)",
     "tipo": "semaforo", "lat": -27.5936, "lon": -48.5910, "regiao": "Continente",
     "endereco": "Av. Ivo Silveira, Estreito",
     "ciclo_s": 120, "vermelho_s": 70, "faixas": 3, "pessoas_ideal": 3,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-FULVIO", "nome": "Semáforo Fúlvio Aducci × Santos Saraiva (Estreito)",
     "tipo": "semaforo", "lat": -27.5924, "lon": -48.5806, "regiao": "Continente",
     "endereco": "R. Fúlvio Aducci, Estreito",
     "ciclo_s": 90, "vermelho_s": 50, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "almoco", "tarde"]},
    {"id": "SEM-MAX-SCHRAMM", "nome": "Semáforo Max Schramm (Jardim Atlântico)",
     "tipo": "semaforo", "lat": -27.5893, "lon": -48.5989, "regiao": "Continente",
     "endereco": "Av. Marinheiro Max Schramm, Jardim Atlântico",
     "ciclo_s": 110, "vermelho_s": 65, "faixas": 3, "pessoas_ideal": 3,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-CAMPECHE", "nome": "Semáforo entrada do Campeche (Pequeno Príncipe × SC-405)",
     "tipo": "semaforo", "lat": -27.6520, "lon": -48.4838, "regiao": "Sul da Ilha",
     "endereco": "Av. Pequeno Príncipe × SC-405, Rio Tavares",
     "ciclo_s": 110, "vermelho_s": 65, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-RIO-TAVARES", "nome": "Rótula do Rio Tavares (SC-405 × Moura Gonzaga)",
     "tipo": "semaforo", "lat": -27.6425, "lon": -48.4869, "regiao": "Sul da Ilha",
     "endereco": "SC-405, Rio Tavares",
     "ciclo_s": 120, "vermelho_s": 70, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-CANASVIEIRAS", "nome": "Semáforo entrada de Canasvieiras (Tertuliano B. Xavier)",
     "tipo": "semaforo", "lat": -27.4335, "lon": -48.4623, "regiao": "Norte da Ilha",
     "endereco": "Rod. Tertuliano Brito Xavier, Canasvieiras",
     "ciclo_s": 100, "vermelho_s": 55, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-INGLESES", "nome": "Semáforo centrinho dos Ingleses (Dom João Becker)",
     "tipo": "semaforo", "lat": -27.4358, "lon": -48.3972, "regiao": "Norte da Ilha",
     "endereco": "Rod. Dom João Becker, Ingleses",
     "ciclo_s": 90, "vermelho_s": 50, "faixas": 2, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "SEM-RENDEIRAS", "nome": "Av. das Rendeiras (Lagoa da Conceição)",
     "tipo": "semaforo", "lat": -27.6068, "lon": -48.4485, "regiao": "Leste/Lagoa",
     "endereco": "Av. das Rendeiras, Lagoa da Conceição",
     "ciclo_s": 90, "vermelho_s": 45, "faixas": 1, "pessoas_ideal": 1,
     "janelas": ["tarde", "fds_tarde"]},
    # SC-401 em pista: fluxo altíssimo mas SEM parada segura — mantida no
    # catálogo apenas para o mapa, marcada como inviável (ver relatório).
    {"id": "SC401-TREVO", "nome": "SC-401 (trevos) — INVIÁVEL para abordagem",
     "tipo": "semaforo", "lat": -27.5385, "lon": -48.5008, "regiao": "Norte da Ilha",
     "endereco": "SC-401, João Paulo", "inviavel": True,
     "ciclo_s": 0, "vermelho_s": 0, "faixas": 0, "pessoas_ideal": 0, "janelas": []},

    # ---------------- TERMINAIS DE INTEGRAÇÃO ----------------
    # ped_hora: estimado a partir dos ~140 mil usuários/dia do sistema
    # (Consórcio Fênix) distribuídos por terminal e concentrados nos picos.
    {"id": "TICEN", "nome": "TICEN — Terminal do Centro", "tipo": "terminal",
     "lat": -27.5992, "lon": -48.5525, "regiao": "Centro",
     "endereco": "Av. Paulo Fontes, Centro", "ped_hora": 9000, "pessoas_ideal": 4,
     "portas": 4, "janelas": ["manha", "tarde"], "coberto": True},
    {"id": "TITRI", "nome": "TITRI — Terminal da Trindade", "tipo": "terminal",
     "lat": -27.5891, "lon": -48.5219, "regiao": "Centro",
     "endereco": "R. Lauro Linhares, Trindade", "ped_hora": 3500, "pessoas_ideal": 3,
     "portas": 2, "janelas": ["manha", "tarde"], "coberto": True},
    {"id": "TIRIO", "nome": "TIRIO — Terminal do Rio Tavares", "tipo": "terminal",
     "lat": -27.6482, "lon": -48.4818, "regiao": "Sul da Ilha",
     "endereco": "SC-405, Rio Tavares", "ped_hora": 2500, "pessoas_ideal": 2,
     "portas": 2, "janelas": ["manha", "tarde"], "coberto": True},
    {"id": "TILAG", "nome": "TILAG — Terminal da Lagoa", "tipo": "terminal",
     "lat": -27.6066, "lon": -48.4691, "regiao": "Leste/Lagoa",
     "endereco": "Av. Afonso Delambert Neto, Lagoa", "ped_hora": 1800, "pessoas_ideal": 2,
     "portas": 2, "janelas": ["manha", "tarde"], "coberto": True},
    {"id": "TISAN", "nome": "TISAN — Terminal de Santo Antônio", "tipo": "terminal",
     "lat": -27.5077, "lon": -48.5145, "regiao": "Centro",
     "endereco": "SC-401, Santo Antônio de Lisboa", "ped_hora": 1500, "pessoas_ideal": 2,
     "portas": 2, "janelas": ["manha", "tarde"], "coberto": True},
    {"id": "TICAN", "nome": "TICAN — Terminal de Canasvieiras", "tipo": "terminal",
     "lat": -27.4293, "lon": -48.4645, "regiao": "Norte da Ilha",
     "endereco": "Rod. Tertuliano Brito Xavier, Canasvieiras", "ped_hora": 2200,
     "pessoas_ideal": 2, "portas": 2, "janelas": ["manha", "tarde"], "coberto": True},

    # ---------------- UNIVERSIDADES / TECH ----------------
    {"id": "UFSC-TRINDADE", "nome": "UFSC — portaria Trindade (Delfino Conti)",
     "tipo": "universidade", "lat": -27.5999, "lon": -48.5192, "regiao": "Centro",
     "endereco": "R. Delfino Conti, Trindade", "ped_hora": 2500, "pessoas_ideal": 2,
     "janelas": ["manha", "almoco", "tarde"]},
    {"id": "UFSC-CTC", "nome": "UFSC — CTC/Biblioteca (entrada Pantanal)",
     "tipo": "universidade", "lat": -27.6015, "lon": -48.5187, "regiao": "Centro",
     "endereco": "Campus UFSC, acesso Pantanal", "ped_hora": 1800, "pessoas_ideal": 2,
     "janelas": ["manha", "almoco", "tarde"]},
    {"id": "UDESC-ITACORUBI", "nome": "UDESC/ESAG — Itacorubi",
     "tipo": "universidade", "lat": -27.5920, "lon": -48.5085, "regiao": "Centro",
     "endereco": "Av. Madre Benvenuta, 2007 — Itacorubi", "ped_hora": 1200,
     "pessoas_ideal": 2, "janelas": ["manha", "tarde"]},
    {"id": "IFSC-CENTRO", "nome": "IFSC — Centro (Mauro Ramos)",
     "tipo": "universidade", "lat": -27.5928, "lon": -48.5464, "regiao": "Centro",
     "endereco": "Av. Mauro Ramos, 950 — Centro", "ped_hora": 1500, "pessoas_ideal": 2,
     "janelas": ["manha", "tarde"]},
    {"id": "PARQTEC-ALFA", "nome": "ParqTec Alfa / ACATE (SC-401 João Paulo)",
     "tipo": "tech", "lat": -27.5385, "lon": -48.5020, "regiao": "Centro",
     "endereco": "SC-401 km 4, João Paulo", "ped_hora": 500, "pessoas_ideal": 2,
     "janelas": ["almoco"]},
    {"id": "SAPIENS", "nome": "Sapiens Parque (Canasvieiras)",
     "tipo": "tech", "lat": -27.4404, "lon": -48.4521, "regiao": "Norte da Ilha",
     "endereco": "Av. Luiz Boiteux Piazza, Canasvieiras", "ped_hora": 400,
     "pessoas_ideal": 2, "janelas": ["almoco"]},
    {"id": "CORPORATE-ITACORUBI", "nome": "Corporate Park / escritórios Itacorubi",
     "tipo": "tech", "lat": -27.5910, "lon": -48.5060, "regiao": "Centro",
     "endereco": "Av. Madre Benvenuta / R. Pastor W. R. Schürmann", "ped_hora": 600,
     "pessoas_ideal": 2, "janelas": ["almoco"]},

    # ---------------- FEIRAS (dias fixos — lista oficial PMF) ----------------
    {"id": "FEIRA-TRINDADE", "nome": "Feira da Trindade (Praça Santos Dumont)",
     "tipo": "feira", "lat": -27.5876, "lon": -48.5230, "regiao": "Centro",
     "endereco": "Praça Santos Dumont, Trindade", "ped_hora": 400, "pessoas_ideal": 2,
     "dias": ["qua", "sex"], "janelas": ["feira"]},
    {"id": "FEIRA-LAGOA", "nome": "Feira da Lagoa (Praça Bento Silvério)",
     "tipo": "feira", "lat": -27.6046, "lon": -48.4682, "regiao": "Leste/Lagoa",
     "endereco": "Praça Bento Silvério, Lagoa da Conceição", "ped_hora": 350,
     "pessoas_ideal": 2, "dias": ["qua", "sab"], "janelas": ["feira"]},
    {"id": "FEIRA-CAMPECHE", "nome": "Feira do Campeche (Av. Pequeno Príncipe)",
     "tipo": "feira", "lat": -27.6777, "lon": -48.4880, "regiao": "Sul da Ilha",
     "endereco": "Av. Pequeno Príncipe (posto de saúde), Campeche", "ped_hora": 350,
     "pessoas_ideal": 2, "dias": ["qua", "sex", "sab"], "janelas": ["feira"]},
    {"id": "FEIRA-ITACORUBI", "nome": "Feira do Itacorubi (Amaro Antônio Vieira)",
     "tipo": "feira", "lat": -27.5836, "lon": -48.4966, "regiao": "Centro",
     "endereco": "Rod. Amaro Antônio Vieira (praça), Itacorubi", "ped_hora": 300,
     "pessoas_ideal": 2, "dias": ["sex"], "janelas": ["feira"]},
    {"id": "FEIRA-AGRONOMICA", "nome": "Feira da Agronômica (Praça Celso Ramos)",
     "tipo": "feira", "lat": -27.5810, "lon": -48.5390, "regiao": "Centro",
     "endereco": "Praça Celso Ramos, Agronômica", "ped_hora": 300, "pessoas_ideal": 2,
     "dias": ["sex"], "janelas": ["feira"]},
    {"id": "FEIRA-CORREGO", "nome": "Feira do Córrego Grande (Jardim Anchieta)",
     "tipo": "feira", "lat": -27.5872, "lon": -48.5062, "regiao": "Centro",
     "endereco": "Av. Gov. José Boabaid, Córrego Grande", "ped_hora": 250,
     "pessoas_ideal": 2, "dias": ["ter", "sex"], "janelas": ["feira"]},
    {"id": "FEIRA-ALFANDEGA", "nome": "Feira do Largo da Alfândega (Centro)",
     "tipo": "feira", "lat": -27.5975, "lon": -48.5514, "regiao": "Centro",
     "endereco": "Largo da Alfândega, Centro", "ped_hora": 800, "pessoas_ideal": 3,
     "dias": ["ter", "qua", "sex", "sab"], "janelas": ["feira", "almoco"]},
    {"id": "FEIRA-SACO-LIMOES", "nome": "Feira do Saco dos Limões (Praça Abdon Batista)",
     "tipo": "feira", "lat": -27.6070, "lon": -48.5350, "regiao": "Centro",
     "endereco": "Praça Abdon Batista, Saco dos Limões", "ped_hora": 250,
     "pessoas_ideal": 2, "dias": ["sab"], "janelas": ["feira"]},

    # ---------------- CALÇADÕES / COMÉRCIO / MERCADOS ----------------
    {"id": "CALCADAO-FELIPE", "nome": "Calçadão da Felipe Schmidt", "tipo": "calcadao",
     "lat": -27.5963, "lon": -48.5503, "regiao": "Centro",
     "endereco": "R. Felipe Schmidt, Centro", "ped_hora": 4000, "pessoas_ideal": 3,
     "janelas": ["almoco"]},
    {"id": "MERCADO-PUBLICO", "nome": "Mercado Público de Florianópolis", "tipo": "mercado",
     "lat": -27.5977, "lon": -48.5525, "regiao": "Centro",
     "endereco": "R. Jerônimo Coelho, Centro", "ped_hora": 2000, "pessoas_ideal": 2,
     "janelas": ["almoco"], "coberto": True},
    {"id": "COMERCIO-ESTREITO", "nome": "Comércio da Fúlvio Aducci (Estreito)",
     "tipo": "calcadao", "lat": -27.5924, "lon": -48.5804, "regiao": "Continente",
     "endereco": "R. Fúlvio Aducci, Estreito", "ped_hora": 1200, "pessoas_ideal": 2,
     "janelas": ["almoco", "tarde"]},
    {"id": "CENTRINHO-LAGOA", "nome": "Centrinho da Lagoa da Conceição", "tipo": "calcadao",
     "lat": -27.6046, "lon": -48.4674, "regiao": "Leste/Lagoa",
     "endereco": "Av. Afonso Delambert Neto, Lagoa", "ped_hora": 900, "pessoas_ideal": 2,
     "janelas": ["tarde", "fds_tarde"]},
    {"id": "CENTRINHO-CAMPECHE", "nome": "Centrinho do Campeche", "tipo": "calcadao",
     "lat": -27.6777, "lon": -48.4880, "regiao": "Sul da Ilha",
     "endereco": "Av. Pequeno Príncipe, Campeche", "ped_hora": 700, "pessoas_ideal": 2,
     "janelas": ["tarde", "fds_tarde"]},
    {"id": "CENTRINHO-INGLESES", "nome": "Centrinho dos Ingleses (Dom João Becker)",
     "tipo": "calcadao", "lat": -27.4359, "lon": -48.3958, "regiao": "Norte da Ilha",
     "endereco": "R. Dom João Becker, Ingleses", "ped_hora": 800, "pessoas_ideal": 2,
     "janelas": ["tarde", "fds_tarde"]},
    {"id": "BEIRAMAR-COQUEIROS", "nome": "Beira-mar de Coqueiros (calçadão)",
     "tipo": "calcadao", "lat": -27.6001, "lon": -48.5766, "regiao": "Continente",
     "endereco": "R. Des. Pedro Silva, Coqueiros", "ped_hora": 600, "pessoas_ideal": 2,
     "janelas": ["tarde", "fds_tarde"]},
    {"id": "IGUATEMI-ENTORNO", "nome": "Entorno do Iguatemi (calçada pública)",
     "tipo": "calcadao", "lat": -27.5928, "lon": -48.5020, "regiao": "Centro",
     "endereco": "Av. Madre Benvenuta, 687 (calçada)", "ped_hora": 900, "pessoas_ideal": 2,
     "janelas": ["almoco", "tarde", "fds_tarde"]},
    {"id": "BEIRAMAR-ENTORNO", "nome": "Entorno do Beiramar Shopping (calçada pública)",
     "tipo": "calcadao", "lat": -27.5850, "lon": -48.5330, "regiao": "Centro",
     "endereco": "R. Bocaiúva, 2468 (calçada)", "ped_hora": 1000, "pessoas_ideal": 2,
     "janelas": ["almoco", "tarde"], "coberto": False},
]

# alternativa coberta padrão por região (contingência de chuva)
PLANO_CHUVA = {
    "Centro": "TICEN (área coberta) ou Mercado Público",
    "Continente": "comércio coberto da Fúlvio Aducci (marquises) ou adiar p/ TICEN",
    "Norte da Ilha": "TICAN (área coberta)",
    "Sul da Ilha": "TIRIO (área coberta)",
    "Leste/Lagoa": "TILAG (área coberta)",
}
