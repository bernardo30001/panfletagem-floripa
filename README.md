# Panfletagem Florianópolis 2026 — inteligência eleitoral

Dashboard com o desempenho da direita (NOVO+PL) por local de votação em
Florianópolis (TSE 2022/2024) e o índice de prioridade de panfletagem do
mandato do deputado estadual Matheus Cadorin (NOVO/SC).

**Acesse: https://bernardo30001.github.io/panfletagem-floripa/**

- `index.html` — dashboard (visão geral, mapa, roteiro top 20, relatório)
- `mapa_floripa.html` — mapa interativo standalone
- `ranking_panfletagem.csv` — ranking completo dos 152 locais de votação

Fontes: [TSE Dados Abertos](https://dadosabertos.tse.jus.br/) (votação por
seção 2022/2024, locais de votação, perfil do eleitorado) e IBGE (malha de
bairros do Censo 2022). Gerado por pipeline Python reproduzível (repositório
local do mandato). Votação por local de votação ≠ residência do eleitor.
