# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO CENTRAL DO PIPELINE DE PANFLETAGEM — FLORIANÓPOLIS 2026
====================================================================
Tudo que é parametrizável fica aqui: anos, cargos, partidos, candidato-alvo,
pesos do Índice de Prioridade de Panfletagem e caminhos de arquivos.

Para rodar de novo com outros parâmetros, edite este arquivo e execute:
    python3 run_pipeline.py
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# CAMINHOS
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
DIR_RAW = RAIZ / "data" / "raw"          # downloads brutos (cache — não rebaixa)
DIR_PROC = RAIZ / "data" / "processed"   # recortes de Florianópolis (parquet)
DIR_SAIDA = RAIZ / "saida"               # entregáveis finais

# ---------------------------------------------------------------------------
# MUNICÍPIO-ALVO
# ---------------------------------------------------------------------------
# O filtro é SEMPRE pelo nome normalizado (sem acento, maiúsculas), nunca por
# código fixo — conforme requisito. "FLORIANÓPOLIS" no TSE vira "FLORIANOPOLIS".
MUNICIPIO_ALVO = "FLORIANOPOLIS"
CODIGO_IBGE_MUNICIPIO = "4205407"        # usado só para a malha do IBGE

# Centro do mapa (Leaflet) e zoom inicial
MAPA_CENTRO = [-27.5945, -48.5477]
MAPA_ZOOM = 11

# ---------------------------------------------------------------------------
# PARTIDOS E CANDIDATO-ALVO
# ---------------------------------------------------------------------------
# Números de legenda no TSE. Nominal de proporcionais = número do candidato
# começa com o número do partido (5 dígitos p/ dep. estadual e vereador,
# 4 dígitos p/ dep. federal). Voto de legenda = NR_VOTAVEL igual ao número
# do partido.
PARTIDOS_DIREITA = {30: "NOVO", 22: "PL"}

# Candidato cuja penetração queremos medir (Bloco 2)
CANDIDATO_ALVO = {
    "nr_votavel": 30001,                  # Matheus Cadorin, dep. estadual 2022
    "nome": "MATHEUS ANDREIS CADORIN",
    "rotulo": "Matheus Cadorin",
}

# Candidato de referência do teto da direita em 2022 (Presidente, 1º turno)
PRESIDENTE_DIREITA_NR = 22               # Bolsonaro (PL)

# ---------------------------------------------------------------------------
# ELEIÇÕES / CARGOS ANALISADOS
# ---------------------------------------------------------------------------
ANO_GERAL = 2022                          # eleição geral de referência
ANO_MUNICIPAL = 2024                      # eleição municipal de referência
TURNO_ANALISE = 1                         # sempre 1º turno nos proporcionais

# DS_CARGO exatamente como vem no TSE (title case)
CARGOS_2022 = ["Deputado Estadual", "Deputado Federal", "Governador", "Presidente"]
CARGOS_2024 = ["Vereador", "Prefeito"]

# NR_VOTAVEL especiais (não são votos válidos)
NR_NAO_VALIDOS = {95, 96, 97, 98}         # 95=branco, 96=nulo, 97/98=especiais

# ---------------------------------------------------------------------------
# ÍNDICE DE PRIORIDADE DE PANFLETAGEM (Bloco 4)
# ---------------------------------------------------------------------------
# score = POTENCIAL*w1 + LIBERAL*w2 + DENSIDADE*w3 + CONSISTENCIA*w4 (0 a 100)
# Cada componente é normalizado (min-max por padrão) antes da soma.
#
# DECISÃO (13/08/2026): o componente GAP — que media 1 - penetração do Matheus
# — foi REMOVIDO a pedido do coordenador. Motivo técnico que confirma a
# decisão: os 84 votos de 2022 dão penetração < 1% em 149 dos 152 locais, ou
# seja, o sinal é ruído; mas o min-max esticava essa faixa de 6 p.p. para 0..1
# e transformava ruído em 35% do score — chegando a PENALIZAR justamente os
# poucos locais onde havia base (média do componente 0,92 onde ele tinha voto
# contra 1,00 onde estava zerado). A premissa agora é começar do zero: todo
# local é território de conquista, e o que ordena é onde está o eleitor
# receptivo (com destaque para o liberal), em volume e alcançável.
PESOS_INDICE = {
    "potencial": 0.40,     # votos absolutos NOVO+PL (dep. estadual 2022) no local
    "liberal": 0.25,       # peso do voto NOVO especificamente (2024 e 2022)
    "densidade": 0.20,     # eleitorado apto do local
    "consistencia": 0.15,  # estabilidade do % de direita entre 2022 e 2024
}
NORMALIZACAO = "minmax"    # "minmax" ou "zscore"

# Locais com menos eleitores que isso não valem equipe de rua (entram no CSV,
# mas com score penalizado a zero e sinalizados).
MIN_ELEITORES_LOCAL = 500

# ---------------------------------------------------------------------------
# FONTES DE DADOS (URLs oficiais — TSE Dados Abertos e IBGE)
# ---------------------------------------------------------------------------
# ATENÇÃO: o Python desta máquina falha o handshake SSL com cdn.tse.jus.br
# (proxy com certificado self-signed). Todos os downloads são feitos com
# curl via subprocess — não trocar por requests.
URLS_TSE = {
    "votacao_secao_2022_SC.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2022_SC.zip",
    "votacao_secao_2022_BR.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2022_BR.zip",  # Presidente (abrangência federal só existe no _BR)
    "votacao_secao_2024_SC.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2024_SC.zip",
    "eleitorado_local_votacao_2022.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2022.zip",
    "eleitorado_local_votacao_2024.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2024.zip",
    "perfil_eleitor_secao_2022_SC.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitor_secao/perfil_eleitor_secao_2022_SC.zip",
    # 2024 não tem recorte por UF deste arquivo — só o nacional (~46 MB)
    "votacao_candidato_munzona_2024.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2024.zip",
}
URL_LIMITE_IBGE = (
    "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/"
    f"{CODIGO_IBGE_MUNICIPIO}?formato=application/vnd.geo+json"
)
# Malha de bairros oficial do Censo 2022 (dispensou o Voronoi do plano B)
URL_BAIRROS_IBGE = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
    "malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/"
    "bairros/shp/UF/SC_bairros_CD2022.zip"
)

# Correções manuais de coordenada (chave do local -> lat, lon), para locais
# cujo endereço no TSE tem erro de grafia e nem o Nominatim resolve.
COORDS_MANUAIS = {
    # Anexo II da Escola Intendente José Fernandes (Ingleses): endereço vem
    # como "RUA INTENDENTE JUÃO NUNES VIEIRA" (typo). Aproximado pela escola
    # principal, que fica na mesma rua.
    "Z100-L1830": (-27.4442, -48.4010),
}

# Geocodificação de locais sem coordenada (TSE usa -1 para "sem coordenada")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_PAUSA_S = 1.2                  # rate limit de cortesia
GEOCODE_CACHE = DIR_RAW / "geocode_cache.json"

# ---------------------------------------------------------------------------
# REGIÕES DE FLORIANÓPOLIS (para o roteiro top-20)
# ---------------------------------------------------------------------------
# Mapeamento bairro (nome TSE/IBGE normalizado) -> macrorregião.
# Preenchido a partir dos bairros que realmente aparecem nos dados; bairros
# não mapeados caem em "Outros" e são listados no relatório para ajuste.
REGIOES = {
    # Centro e entorno (ilha central)
    "CENTRO": "Centro", "AGRONOMICA": "Centro", "TRINDADE": "Centro",
    "PANTANAL": "Centro", "CORREGO GRANDE": "Centro", "SANTA MONICA": "Centro",
    "ITACORUBI": "Centro", "JOAO PAULO": "Centro", "MONTE VERDE": "Centro",
    "SACO GRANDE": "Centro", "CACUPE": "Centro", "SANTO ANTONIO DE LISBOA": "Centro",
    "SAMBAQUI": "Centro", "BARRA DO SAMBAQUI": "Centro", "JOSE MENDES": "Centro",
    "SACO DOS LIMOES": "Centro", "COSTEIRA DO PIRAJUBAE": "Centro",
    # Norte da Ilha
    "CANASVIEIRAS": "Norte da Ilha", "INGLESES DO RIO VERMELHO": "Norte da Ilha",
    "INGLESES": "Norte da Ilha", "SAO JOAO DO RIO VERMELHO": "Norte da Ilha",
    "RIO VERMELHO": "Norte da Ilha", "CACHOEIRA DO BOM JESUS": "Norte da Ilha",
    "PONTA DAS CANAS": "Norte da Ilha", "LAGOINHA": "Norte da Ilha",
    "PRAIA BRAVA": "Norte da Ilha", "JURERE": "Norte da Ilha",
    "JURERE INTERNACIONAL": "Norte da Ilha", "DANIELA": "Norte da Ilha",
    "VARGEM PEQUENA": "Norte da Ilha", "VARGEM GRANDE": "Norte da Ilha",
    "VARGEM DO BOM JESUS": "Norte da Ilha", "RATONES": "Norte da Ilha",
    "SANTINHO": "Norte da Ilha",
    "CAPIVARI": "Norte da Ilha",          # Sítio Capivari (Ingleses/Rio Vermelho)
    "JURERE LESTE": "Norte da Ilha",
    # Leste / Lagoa
    "LAGOA DA CONCEICAO": "Leste/Lagoa", "BARRA DA LAGOA": "Leste/Lagoa",
    "CANTO DA LAGOA": "Leste/Lagoa", "COSTA DA LAGOA": "Leste/Lagoa",
    "PORTO DA LAGOA": "Leste/Lagoa", "JOAQUINA": "Leste/Lagoa",
    "CAMPECHE": "Sul da Ilha",  # Campeche fica entre Leste e Sul; convenção: Sul
    # Sul da Ilha
    "RIO TAVARES": "Sul da Ilha", "CARIANOS": "Sul da Ilha",
    "TAPERA": "Sul da Ilha", "TAPERA DA BASE": "Sul da Ilha",
    "RIBEIRAO DA ILHA": "Sul da Ilha", "ALTO RIBEIRAO": "Sul da Ilha",
    "FREGUESIA DO RIBEIRAO": "Sul da Ilha", "BARRO VERMELHO": "Sul da Ilha",
    "CAIEIRA DA BARRA DO SUL": "Sul da Ilha", "MORRO DAS PEDRAS": "Sul da Ilha",
    "ARMACAO": "Sul da Ilha", "ARMACAO DO PANTANO DO SUL": "Sul da Ilha",
    "PANTANO DO SUL": "Sul da Ilha", "COSTA DE DENTRO": "Sul da Ilha",
    "LAGOA DO PERI": "Sul da Ilha", "COSTEIRA DO RIBEIRAO": "Sul da Ilha",
    "MORRO DO PERALTA": "Sul da Ilha",    # polígono IBGE na região da Tapera
    "RETIRO": "Leste/Lagoa",              # Retiro da Lagoa
    # Continente
    "ESTREITO": "Continente", "BALNEARIO": "Continente", "CANTO": "Continente",
    "COQUEIROS": "Continente", "ITAGUACU": "Continente", "BOM ABRIGO": "Continente",
    "ABRAAO": "Continente", "CAPOEIRAS": "Continente", "MONTE CRISTO": "Continente",
    "COLONINHA": "Continente", "JARDIM ATLANTICO": "Continente",
    "VILA APARECIDA": "Continente", "SAPE": "Continente",
    "BALNEARIO DO ESTREITO": "Continente",
}

# ---------------------------------------------------------------------------
# PONTOS DE FLUXO DE PEDESTRES (para o cruzamento sugerido no relatório)
# ---------------------------------------------------------------------------
# Curadoria manual: terminais de integração, mercados, feiras e calçadões.
# Coordenadas aproximadas (WGS84). dias_horarios = sugestão operacional.
PONTOS_FLUXO = [
    {"nome": "TICEN — Terminal de Integração do Centro", "lat": -27.5992, "lon": -48.5525,
     "tipo": "terminal", "regiao": "Centro",
     "dias_horarios": "Seg–sex 7h–9h e 17h30–19h30 (pico de baldeação)"},
    {"nome": "TITRI — Terminal de Integração da Trindade", "lat": -27.5891, "lon": -48.5219,
     "tipo": "terminal", "regiao": "Centro",
     "dias_horarios": "Seg–sex 7h–9h e 17h30–19h (fluxo UFSC + bairros do leste)"},
    {"nome": "TIRIO — Terminal de Integração do Rio Tavares", "lat": -27.6482, "lon": -48.4818,
     "tipo": "terminal", "regiao": "Sul da Ilha",
     "dias_horarios": "Seg–sex 7h–9h e 18h–19h30 (funil do Sul da Ilha)"},
    {"nome": "TILAG — Terminal de Integração da Lagoa", "lat": -27.6066, "lon": -48.4691,
     "tipo": "terminal", "regiao": "Leste/Lagoa",
     "dias_horarios": "Seg–sex 17h–19h; sáb 10h–13h (turismo + moradores)"},
    {"nome": "TISAN — Terminal de Integração de Santo Antônio", "lat": -27.5077, "lon": -48.5145,
     "tipo": "terminal", "regiao": "Norte da Ilha",
     "dias_horarios": "Seg–sex 7h–9h (funil do Norte via SC-401)"},
    {"nome": "TICAN — Terminal de Integração de Canasvieiras", "lat": -27.4293, "lon": -48.4645,
     "tipo": "terminal", "regiao": "Norte da Ilha",
     "dias_horarios": "Seg–sex 7h30–9h; alta temporada: fim de tarde"},
    {"nome": "Mercado Público de Florianópolis", "lat": -27.5977, "lon": -48.5525,
     "tipo": "mercado", "regiao": "Centro",
     "dias_horarios": "Sáb 10h–13h (pico de circulação); seg–sex 11h30–14h"},
    {"nome": "Calçadão da Felipe Schmidt", "lat": -27.5963, "lon": -48.5503,
     "tipo": "calcadao", "regiao": "Centro",
     "dias_horarios": "Seg–sex 11h30–14h e 17h–18h30; sáb 10h–13h"},
    {"nome": "Largo da Alfândega", "lat": -27.5975, "lon": -48.5514,
     "tipo": "praca", "regiao": "Centro",
     "dias_horarios": "Seg–sex 11h30–14h (feiras e eventos frequentes)"},
    {"nome": "Feira do Largo da Lagoa (Lagoa da Conceição)", "lat": -27.6046, "lon": -48.4682,
     "tipo": "feira", "regiao": "Leste/Lagoa",
     "dias_horarios": "Qua e sáb de manhã (feira); dom fim de tarde (passeio)"},
    {"nome": "Beira-mar de Coqueiros (Praça Nossa Senhora de Fátima)", "lat": -27.6001, "lon": -48.5766,
     "tipo": "praca", "regiao": "Continente",
     "dias_horarios": "Fim de tarde 17h–19h30 (caminhada); dom de manhã"},
    {"nome": "Calçadão/comércio do Estreito (Rua Fúlvio Aducci)", "lat": -27.5924, "lon": -48.5804,
     "tipo": "calcadao", "regiao": "Continente",
     "dias_horarios": "Seg–sex 10h–12h e 16h–18h30; sáb de manhã"},
    {"nome": "Praça Renato Silveira (Canasvieiras)", "lat": -27.4290, "lon": -48.4630,
     "tipo": "praca", "regiao": "Norte da Ilha",
     "dias_horarios": "Sáb/dom fim de tarde; verão: todo dia 17h–20h"},
    {"nome": "Centrinho dos Ingleses (Rua Dom João Becker)", "lat": -27.4359, "lon": -48.3958,
     "tipo": "calcadao", "regiao": "Norte da Ilha",
     "dias_horarios": "Sáb 10h–13h; seg–sex 17h–19h"},
    {"nome": "Centrinho do Campeche (Av. Pequeno Príncipe)", "lat": -27.6777, "lon": -48.4880,
     "tipo": "calcadao", "regiao": "Sul da Ilha",
     "dias_horarios": "Sáb de manhã (feira orgânica); fim de tarde em semana"},
]
