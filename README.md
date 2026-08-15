# Panfletagem Florianópolis 2026 — inteligência eleitoral

Análise de dados eleitorais e plano operacional de panfletagem de rua em
Florianópolis para a campanha do deputado estadual **Matheus Cadorin
(NOVO/SC)**, com dados abertos do TSE (4 ciclos: 2018, 2020, 2022 e 2024) e
malha de bairros do Censo 2022 do IBGE.

**Dashboard: https://bernardo30001.github.io/panfletagem-floripa/**

## Conteúdo

### Análise por local de votação (raiz)

| Arquivo | O que é |
|---|---|
| [`index.html`](index.html) | Dashboard: visão geral, mapa, roteiro top 20 e relatório |
| [`mapa_floripa.html`](mapa_floripa.html) | Mapa interativo: heatmap de votos, coropléticos por bairro, 152 locais de votação |
| [`ranking_panfletagem.csv`](ranking_panfletagem.csv) | Ranking dos 152 locais com todas as métricas |
| [`relatorio.md`](relatorio.md) | Leitura analítica: núcleo duro, fronteira, perfil demográfico, voto órfão |
| [`top20_roteiro.md`](top20_roteiro.md) | 20 locais prioritários agrupados por região |

### Plano operacional ([`plano/`](plano/))

| Arquivo | O que é |
|---|---|
| [`estrategia_coordenacao.md`](plano/estrategia_coordenacao.md) | Manual de coordenação do time: estrutura, rotina, medição, abordagem, contingências |
| [`calendario_panfletagem.xlsx`](plano/calendario_panfletagem.xlsx) | Escala dia a dia de 19/08 a 03/10/2026 — 46 dias, 265 turnos-ponto |
| [`ranking_pontos.csv`](plano/ranking_pontos.csv) | ~40 pontos físicos (semáforos, terminais, feiras) com índice composto |
| [`mapa_plano.html`](plano/mapa_plano.html) | Mapa com heatmaps por ciclo eleitoral e pontos ranqueados |
| [`relatorio_plano.md`](plano/relatorio_plano.md) | Metodologia, achados de 2024, territórios A/B/C, 15 pontos de ouro, conformidade legal |

### Pipeline

Código Python que gera tudo acima, de forma reproduzível:

```bash
python3 run_pipeline.py   # base eleitoral por local de votação
python3 run_plano.py      # pontos, índice, calendário, mapa e relatórios
```

Parâmetros (partidos, pesos dos índices, equipe, tiragem, catálogo de pontos)
ficam em [`pipeline/config.py`](pipeline/config.py) e
[`pipeline/plano_config.py`](pipeline/plano_config.py). Os dados brutos do TSE
(~700 MB) são baixados automaticamente para `data/` (fora do versionamento).

Requer `pandas`, `geopandas`, `folium`, `openpyxl`, `pyarrow`.

## Metodologia em uma linha

O índice por local de votação combina **potencial** (votos absolutos NOVO+PL),
**liberal** (voto NOVO especificamente), **densidade** (eleitorado) e
**consistência** (estabilidade 2022→2024). O índice por ponto físico combina
**afinidade**, **liberal**, **fluxo estimado** e **perfil socioeconômico** do
entorno de 1 km. Pesos explícitos e ajustáveis nos arquivos de configuração.

## Fontes

- [TSE Dados Abertos](https://dadosabertos.tse.jus.br/) — votação por seção
  (2018/2020/2022/2024), locais de votação, perfil do eleitorado
- IBGE — malha de bairros do Censo 2022, limite municipal
- Feiras livres: lista oficial da Prefeitura de Florianópolis
- Fluxo viário: SSP-SC / DEINFRA; transporte coletivo: Consórcio Fênix

## Ressalvas

- Votação por **local de votação ≠ residência** do eleitor (há defasagem de
  transferência de título).
- As métricas de fluxo de pedestres e ciclos semafóricos são **estimativas
  declaradas** — não existe dado público desses números. O método de cálculo
  está explicado no relatório do plano.
- Percentuais calculados sobre votos válidos (excluem brancos e nulos).
