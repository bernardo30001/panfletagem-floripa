# Relatório — Inteligência eleitoral para panfletagem
## Florianópolis, ciclo 2026 · Mandato Matheus Cadorin (NOVO/SC)

*Gerado pelo pipeline em `panfletagem-floripa/` com dados abertos do TSE (votação por seção 2022/2024, locais de votação, perfil do eleitorado) e malha de bairros do Censo 2022 (IBGE).*

---
## 1. Números de partida

- **152** locais de votação analisados; **415.033** eleitores aptos.
- Direita (NOVO+PL) p/ **dep. estadual 2022**: **65.168** votos = **21,9%** dos válidos (NOVO 3,8%, PL 18,1%).
- Teto da direita (Bolsonaro 1º turno 2022): **45,7%** — a distância entre o voto proporcional da direita e esse teto é eleitor alcançável.
- Direita p/ **vereador 2024**: 20,9% dos válidos.
- **Matheus em 2022**: **84 votos** na capital, presentes em 44 dos 152 locais — penetração média de 0,13% sobre o voto de direita. Na prática, a capital é campo aberto: quase todo o voto de direita está disponível.

---
## 2. Como o Índice de Prioridade é calculado

```
score = 100 × minmax( 0.40·POTENCIAL + 0.25·LIBERAL + 0.20·DENSIDADE + 0.15·CONSISTÊNCIA )

POTENCIAL    = votos absolutos NOVO+PL, dep. estadual 2022 (min-max)
LIBERAL      = média do %NOVO p/ vereador 2024 e dep. estadual 2022 (min-max)
DENSIDADE    = eleitores aptos do local (min-max)
CONSISTÊNCIA = 1 − |%direita 2022 − %direita 2024| (min-max)
```

Pesos e método de normalização em `pipeline/config.py` (`PESOS_INDICE`, `NORMALIZACAO='minmax'`). Locais com menos de 500 eleitores recebem score 0 (`flag_pequeno`) — não valem hora de equipe.

**A votação do Matheus em 2022 NÃO entra no score.** O componente anterior (GAP = 1 − penetração dele) foi removido: com 84 votos, a penetração fica abaixo de 1% em 149 dos 152 locais — é ruído — e a normalização esticava essa faixa de 6 p.p. para 0..1, transformando ruído em 35% do score e penalizando justamente os poucos locais onde havia base. No lugar entrou LIBERAL, que mede onde vive o eleitor-alvo com uma amostra ~700× maior. Os votos dele seguem no CSV e nos popups como diagnóstico, sem efeito no ranking. Premissa: começamos do zero.

---
## 3. Núcleo duro da direita (quartil superior de % NOVO+PL, bairros com 1.000+ eleitores)

| Bairro | Região | Aptos | Votos direita 22 | % direita | % NOVO | % PL | Matheus | Score |
|---|---|---|---|---|---|---|---|---|
| Jurere Oeste | Norte da Ilha | 3.188 | 902 | 36,7% | 9,4% | 27,4% | 2 | 63.1 |
| Jurere Leste | Norte da Ilha | 3.050 | 675 | 28,7% | 4,8% | 23,9% | 0 | 35.1 |
| Daniela | Norte da Ilha | 1.608 | 172 | 28,7% | 2,8% | 25,8% | 0 | 25.8 |
| Santa Mônica | Centro | 2.777 | 618 | 27,7% | 8,5% | 19,2% | 0 | 59.2 |
| Balneário | Continente | 8.577 | 1.804 | 26,8% | 4,2% | 22,6% | 2 | 58.2 |
| Ingleses Centro | Norte da Ilha | 16.545 | 3.014 | 26,7% | 3,5% | 23,2% | 4 | 61.8 |
| Carianos | Sul da Ilha | 6.966 | 1.260 | 26,0% | 2,4% | 23,6% | 4 | 58.2 |
| Canto | Continente | 7.581 | 1.512 | 25,5% | 3,2% | 22,3% | 3 | 42.6 |
| Centro | Centro | 43.582 | 8.529 | 25,4% | 5,7% | 19,7% | 7 | 65.0 |
| Canasvieiras | Norte da Ilha | 10.401 | 1.825 | 24,5% | 3,1% | 21,4% | 0 | 56.4 |
| Estreito | Continente | 6.354 | 1.191 | 24,4% | 3,6% | 20,8% | 0 | 46.3 |
| Coloninha | Continente | 8.957 | 1.660 | 24,3% | 3,8% | 20,4% | 1 | 61.5 |

É onde a mensagem já tem audiência: material de reforço e recrutamento de voluntários rendem mais que persuasão.

## 4. Fronteira competitiva (acima da média municipal, abaixo do núcleo)

| Bairro | Região | Aptos | Votos direita 22 | % direita | Abstenção 22 | Score |
|---|---|---|---|---|---|---|
| Itacorubi | Centro | 20.828 | 3.186 | 23,2% | 14,9% | 65.9 |
| Capoeiras | Continente | 12.815 | 1.835 | 22,3% | 17,1% | 41.3 |
| Capivari | Norte da Ilha | 11.095 | 1.782 | 23,8% | 22,9% | 51.3 |
| Jardim Atlântico | Continente | 8.346 | 1.327 | 22,6% | 18,8% | 47.2 |
| Córrego Grande | Centro | 6.679 | 1.101 | 22,2% | 15,6% | 45.4 |
| Santinho | Norte da Ilha | 3.550 | 559 | 22,8% | 22,4% | 43.2 |
| Ingleses Sul | Norte da Ilha | 3.561 | 557 | 22,7% | 23,2% | 43.3 |
| Ratones | Norte da Ilha | 2.472 | 431 | 23,6% | 17,8% | 33.4 |

Volume alto e % intermediário = melhor custo-benefício de persuasão. É o coração do roteiro de panfletagem.

## 5. Onde o Matheus já tem base (e onde está zerado)

Os 84 votos de 2022 caíram assim:

| Local | Bairro | Votos Matheus | Direita no local | Penetração |
|---|---|---|---|---|
| UDESC - CENTRO DE ARTES - CEART | Itacorubi | 9 | 1.429 | 0,63% |
| ESCOLA BASICA JOSÉ DO VALLE PEREIRA | João Paulo | 6 | 828 | 0,72% |
| ESCOLA DE EDUCACAO BASICA IDELFONSO LINHARES | Carianos | 4 | 1.260 | 0,32% |
| ESCOLA DE ENSINO BASICO LEONOR DE BARROS | Itacorubi | 4 | 848 | 0,47% |
| ESCOLA BÁSICA MUNICIPAL JOÃO GONÇALVES PINHEIRO | Rio Tavares do Norte | 3 | 944 | 0,32% |
| COLEGIO CATARINENSE | Centro | 3 | 1.930 | 0,16% |
| N.E.I. - NÚCLEO DE EDUCAÇÃO INFANTIL MARIA SALOMÉ DOS SANTOS | Sambaqui | 3 | 197 | 1,52% |
| ESCOLA BÁSICA MUNICIPAL PROFESSORA HERONDINA MEDEIROS ZEFERINO | Ingleses Centro | 3 | 1.348 | 0,22% |
| O. ASSIST. SOCIAL DOM ORIONE (PARÓQUIA SÃO JOÃO BATISTA E SANTA LUZIA) | Capoeiras | 2 | 201 | 1,00% |
| ESCOLA BÁSICA MUNICIPAL ALMIRANTE CARVALHAL | Coqueiros | 2 | 848 | 0,24% |

**88 locais (57,9%) estão zerados** (outros 20 são locais criados em 2024, sem dado de 2022). O voto existente concentra-se no eixo Centro–UFSC–Itacorubi (perfil universitário/liberal, aderente ao NOVO). A leitura estratégica: não há reduto a defender — TODO local de score alto é terreno de conquista.

## 6. Perfil demográfico dos clusters (para calibrar linguagem do panfleto)

- **Núcleo duro** (15 bairros): 10,4% jovens (16–24), 24,8% com 60+, 40,8% com superior completo, 54,2% mulheres.
- **Fronteira** (8 bairros): 10,9% jovens (16–24), 19,5% com 60+, 33,4% com superior completo, 54,0% mulheres.
- **Abaixo da média** (34 bairros): 12,9% jovens (16–24), 17,5% com 60+, 26,8% com superior completo, 53,4% mulheres.

Recomendações práticas:
- Onde **superior completo** é alto (Centro, Itacorubi, Coqueiros): panfleto de dados — emendas, economia gerada, fiscalização; QR code para o portal do mandato.
- Onde **60+** pesa (Estreito, Balneário, Canto): fonte maior, foco em saúde, segurança e previsibilidade; linguagem direta sem jargão liberal.
- Onde **jovens** pesam (Trindade, Pantanal, Ingleses): estética de rede social, pauta de oportunidade/empreendedorismo, link para Instagram do mandato.

---
## 7. Abstenção alta + potencial alto (abordagem diferenciada)

Locais no quartil superior de abstenção 2022 (>19,3%) e score acima da mediana — aqui o panfleto precisa primeiro convencer a VOTAR:

| Local | Bairro | Abstenção 22 | Votos direita 22 | Score |
|---|---|---|---|---|
| ESCOLA BÁSICA MUNICIPAL PROFESSORA HERONDINA MEDEIROS ZEFERINO | Ingleses Centro | 23,3% | 1.348 | 73.0 |
| ESCOLA BASICA MUNICIPAL OSMAR CUNHA | Canasvieiras | 21,8% | 1.168 | 62.9 |
| ESCOLA DE ENSINO BÁSICO INTENDENTE JOSE FERNANDES | Capivari | 23,8% | 1.018 | 59.7 |
| ESCOLA DE EDUCAÇÃO BÁSICA PADRE ANCHIETA | Agronômica | 21,6% | 784 | 57.2 |
| COLÉGIO SANTA TEREZINHA | Ingleses Centro | 23,5% | 1.002 | 56.3 |
| INSTITUTO ESTADUAL DE EDUCAÇÃO - IEE | Centro | 22,5% | 728 | 54.5 |
| ESCOLA TÉCNICA - CENTRO FEDERAL DE EDUC. TECNOLÓGICA DE SC - CEFET/SC | Centro | 19,6% | 712 | 54.3 |
| COLÉGIO DA LAGOA | Lagoa | 21,2% | 659 | 53.6 |

---
## 8. Voto órfão (bairro forte em NOVO/PL sem vereador local eleito em 2024)

Bairros acima da mediana de % direita p/ vereador em 2024 onde os vereadores ELEITOS de NOVO/PL captaram menos de 35% do voto de direita local — eleitor habituado a votar na sigla, sem 'dono' político no território:

| Bairro | Região | Votos direita ver. 24 | % direita 24 | % capturado por eleitos |
|---|---|---|---|---|
| Centro | Centro | 7.438 | 24,7% | 31,2% |
| Itacorubi | Centro | 2.899 | 23,5% | 35,0% |
| Coqueiros | Continente | 2.496 | 18,8% | 32,5% |
| Balneário | Continente | 1.293 | 20,9% | 31,4% |
| Coloninha | Continente | 1.253 | 20,8% | 34,9% |
| Canto | Continente | 978 | 18,8% | 33,1% |
| João Paulo | Centro | 758 | 24,0% | 33,9% |
| Jurere Oeste | Norte da Ilha | 622 | 31,2% | 29,6% |
| Santinho | Norte da Ilha | 555 | 23,2% | 20,2% |
| Santa Mônica | Centro | 501 | 26,8% | 32,5% |

---
## 9. Pontos de fluxo × locais prioritários (rendimento por hora de equipe)

Panfletagem em ponto de fluxo rende mais contatos/hora que porta a porta. Sugestão de alocação, cruzando os pontos com o score da região:

| Ponto | Tipo | Região | Quando |
|---|---|---|---|
| TICEN — Terminal de Integração do Centro | Terminal | Centro | Seg–sex 7h–9h e 17h30–19h30 (pico de baldeação) |
| TITRI — Terminal de Integração da Trindade | Terminal | Centro | Seg–sex 7h–9h e 17h30–19h (fluxo UFSC + bairros do leste) |
| TIRIO — Terminal de Integração do Rio Tavares | Terminal | Sul da Ilha | Seg–sex 7h–9h e 18h–19h30 (funil do Sul da Ilha) |
| TILAG — Terminal de Integração da Lagoa | Terminal | Leste/Lagoa | Seg–sex 17h–19h; sáb 10h–13h (turismo + moradores) |
| TISAN — Terminal de Integração de Santo Antônio | Terminal | Norte da Ilha | Seg–sex 7h–9h (funil do Norte via SC-401) |
| TICAN — Terminal de Integração de Canasvieiras | Terminal | Norte da Ilha | Seg–sex 7h30–9h; alta temporada: fim de tarde |
| Mercado Público de Florianópolis | Mercado | Centro | Sáb 10h–13h (pico de circulação); seg–sex 11h30–14h |
| Calçadão da Felipe Schmidt | Calcadao | Centro | Seg–sex 11h30–14h e 17h–18h30; sáb 10h–13h |
| Largo da Alfândega | Praca | Centro | Seg–sex 11h30–14h (feiras e eventos frequentes) |
| Feira do Largo da Lagoa (Lagoa da Conceição) | Feira | Leste/Lagoa | Qua e sáb de manhã (feira); dom fim de tarde (passeio) |
| Beira-mar de Coqueiros (Praça Nossa Senhora de Fátima) | Praca | Continente | Fim de tarde 17h–19h30 (caminhada); dom de manhã |
| Calçadão/comércio do Estreito (Rua Fúlvio Aducci) | Calcadao | Continente | Seg–sex 10h–12h e 16h–18h30; sáb de manhã |
| Praça Renato Silveira (Canasvieiras) | Praca | Norte da Ilha | Sáb/dom fim de tarde; verão: todo dia 17h–20h |
| Centrinho dos Ingleses (Rua Dom João Becker) | Calcadao | Norte da Ilha | Sáb 10h–13h; seg–sex 17h–19h |
| Centrinho do Campeche (Av. Pequeno Príncipe) | Calcadao | Sul da Ilha | Sáb de manhã (feira orgânica); fim de tarde em semana |

Regras de bolso:
- **Terminais no pico da manhã (7h–9h)**: maior volume bruto de contatos/hora; material curto, entrega rápida. TICEN e TITRI primeiro — concentram baldeações das regiões de maior score.
- **Feiras e mercados no sábado de manhã**: menos volume, muito mais tempo de conversa; ideal para material denso e presença do deputado.
- **Calçadões no almoço (11h30–14h)**: público economicamente ativo do Centro; bom para pauta de economia/impostos.
- **Praças de bairro no fim de tarde**: famílias e 60+; pauta local (saúde, segurança).

---
## 10. Avisos de qualidade de dados

- 20 locais criados em 2024 não têm histórico de 2022 (o maior: UDESC - CENTRO DE CIÊNCIAS HUMANAS - FAED, 3628 eleitores) — o componente POTENCIAL deles fica subestimado; em geral são desmembramentos de locais vizinhos do ranking.
- Votação por local ≠ residência do eleitor: o eleitor vota onde tem título, que costuma acompanhar a residência, mas há defasagem (mudanças sem transferência).
- % calculados sobre votos válidos (exclui brancos 95 e nulos 96).
- Comparecimento estimado pela soma de todos os votos do cargo de dep. estadual (inclui brancos/nulos) — o TSE não publica comparecimento por local diretamente.

## 11. Para recalcular com outros parâmetros

Edite `pipeline/config.py` (pesos, partidos, candidato, mínimo de eleitores, normalização) e rode `python3 run_pipeline.py`. Os downloads ficam em cache em `data/raw/`; para forçar rebaixamento, apague o arquivo correspondente.