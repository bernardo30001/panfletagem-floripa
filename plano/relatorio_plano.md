# Plano de panfletagem — Florianópolis 2026
## Mandato Matheus Cadorin (NOVO/SC) · campanha 16/08 a 03/10/2026

*Gerado em 13/08/2026 pelo pipeline `panfletagem-floripa/` — dados TSE (4 ciclos: 2018/2020/2022/2024, seções agregadas por LOCAL de votação, zonas 12/13/100 confirmadas nos dados), malha de bairros IBGE Censo 2022, e camada de fluxo físico com estimativas declaradas.*

---
## 1. Metodologia (fato × estimativa)

**Fatos (fonte oficial):** votos por seção/local (TSE Dados Abertos, acessado 13/08/2026); locais de votação com coordenadas (TSE); perfil do eleitorado por seção (TSE); bairros (IBGE CD2022); feiras livres e dias (lista oficial PMF, via ND+ 25/05/2023); VMD da SC-401 (SSP-SC, jan/2025); volume do sistema de ônibus (~140 mil usuários/dia, Consórcio Fênix).

**Estimativas (marcadas, método declarado):** ciclos semafóricos e tempos de vermelho (a PMF não publica planilha semafórica — valores de campo típicos, ±20%); pedestres/hora por ponto (distribuição do volume do sistema pelos terminais + observação de praxe); taxas de aceite (veículo 45%, pedestre 18%, feira 40%); panfletos/h/pessoa = f(ciclo, vermelho, aceite) com teto físico de 280/h (1 entrega ≈ 6 s).

**Fórmula do índice por ponto** (pesos em `pipeline/plano_config.py`):
```
índice = 100 × minmax( 0.35·AFINIDADE + 0.20·LIBERAL + 0.25·FLUXO + 0.20·PERFIL )
AFINIDADE = (2×%dir. vereador 2024 + 1×%dir. dep.est. 2022)/3 + 0,5×(Δ 2020→2024)
LIBERAL   = 0,50×%NOVO ver.2024 + 0,25×%Bruno 2018 + 0,25×%Bruno fed.2022
FLUXO     = panfletos/hora/pessoa estimados
PERFIL    = 0,7×escolaridade superior + 0,3×jovens 16–24 (raio de 1 km)
```
Seções associadas a cada ponto num raio de **1 km**, ponderadas por eleitorado.

**A votação do Cadorin em 2022 NÃO entra no índice** (decisão do coordenador em 13/08/2026, tecnicamente correta): 84 votos dão penetração abaixo de 1% em 149 dos 152 locais — ruído — e a normalização convertia essa faixa de 6 p.p. em 25% do índice, penalizando os poucos pontos onde havia base. O componente LIBERAL responde à mesma pergunta ('onde está o eleitor dele?') com amostras de 10 a 24 mil votos em vez de 84. Partimos do zero.

**Dados que NÃO existem publicamente** (não inventados): planilha semafórica da PMF/SMMU; contagem de passageiros POR terminal (só o total do sistema); MEI/CNPJ georreferenciado por bairro (o arquivo nacional da Receita tem >5 GB — proxy usado: % de superior completo do TSE, que correlaciona 0,82 com o voto NOVO; script para rodar localmente pode ser gerado sob demanda); renda por setor censitário do Censo 2022 (não integrada nesta versão).

---
## 2. O que os dados de 2024 revelaram

- Direita (NOVO+PL) p/ vereador 2024: **20,9% dos válidos** — mas o motor é o PL (**16,8%**, 3× o resultado de 2020); o NOVO FICOU MENOR: 5,3% (2020) → **4,1%** (2024).
- Tradução: o crescimento da direita na capital é bolsonarista, não liberal. O Cadorin não herda esse voto automaticamente — ele disputa o sub-segmento liberal e precisa do próprio nome na rua.
- Voto liberal de referência: Bruno Souza fez **13.198 votos** na capital em 2018 (dep. estadual, então PSB, nº 40030 — filiou-se ao NOVO em nov/2019) e **23.914** em 2022 (dep. federal, NOVO). É o teto realista do nicho: 3,5–8% dos válidos, concentrado no mesmo arco de bairros.
- Matheus 2022: **84 votos** (Itacorubi 15, Centro/Coqueiros/Trindade 7 cada, João Paulo 6). Gap total: há ~65 mil votos NOVO+PL e ~24 mil votos 'Bruno' provando demanda liberal — com penetração do Matheus de 0,13%.

### Hipótese do corredor universitário: CONFIRMADA COM CORREÇÃO

- O voto NOVO 2024 por bairro correlaciona **r = 0.817** com % de superior completo — e **r = -0.285** (negativo!) com % de jovens 16–24.
- Ou seja: o eleitorado natural é o **profissional formado** (tech, empreendedor, servidor qualificado), não o 'estudante'. O corredor universitário funciona porque concentra diplomas, não calouros — e a portaria da UFSC tem entorno eleitoral fraco (Serrinha/Carvoeira).
- E o dado derruba a oposição 'universitário × bairro rico': **Jurerê Oeste é o 2º bairro do NOVO (8,5%) e foi o 1º do Bruno em 2018 E 2022**. Rico escolarizado também é núcleo. Top NOVO 2024: Santa Mônica 10,6%, Jurerê Oeste 8,5%, João Paulo 8,0%, Itacorubi 7,9%, Centro 7,1%, Trindade 6,3%, Córrego Grande 6,1%.

---
## 3. Territórios A / B / C (bairros com 1.500+ eleitores)

**A — núcleo liberal (converter):** Santa Mônica (10,6% NOVO), Jurere Oeste (8,5% NOVO), João Paulo (8,0% NOVO), Itacorubi (7,9% NOVO), Centro (7,1% NOVO), Trindade (6,3% NOVO), Córrego Grande (6,1% NOVO), Santo Antônio (5,3% NOVO), Coqueiros (4,8% NOVO), Balneário (4,5% NOVO), Jurere Leste (4,4% NOVO), Moenda (3,6% NOVO), Rio Tavares do Norte (2,6% NOVO), Campeche Central (2,3% NOVO)

**B — fronteira de direita (apresentar o nome):** Agronômica, Estreito, Vargem Grande, Coloninha, Pantanal, Vargem de Fora, Morro das Pedras, Ingleses Centro, Campeche Leste, Ingleses Sul, Barra da Lagoa, Santinho, Capivari, Rio Vermelho, Costeira do Pirajubaé

**C — baixa afinidade (só fluxo de passagem):** Saco Grande, Abraão, Lagoa, Canto, Canasvieiras, Daniela, Capoeiras, Sambaqui, Jardim Atlântico, Monte Verde, Carianos, Ratones, Armação, Cachoeira do Bom Jesus Leste, Saco dos Limões, Ponta das Canas, Vargem do Bom Jesus, José Mendes, Pântano do Sul, Vargem Pequena, Ribeirão da Ilha, Alto Ribeirão, Base Aérea, Tapera da Base, Monte Cristo

---
## 4. Os 15 pontos de ouro

**1. Calçadão da Felipe Schmidt** — índice 100.0 (OURO — fluxo e afinidade altos)  
R. Felipe Schmidt, Centro · Centro · ~280 panf/h/pessoa  
_Entorno de 1 km: direita 2024 24,8%, NOVO 7,1%, superior completo 51%, 36.351 eleitores, Matheus tinha 7 votos. Janelas: almoco. Equipe ideal: 3._

**2. TITRI — Terminal da Trindade** — índice 89.2 (misto)  
R. Lauro Linhares, Trindade · Centro · ~280 panf/h/pessoa  
_Entorno de 1 km: direita 2024 21,3%, NOVO 6,6%, superior completo 45%, 9.926 eleitores, Matheus tinha 3 votos. Janelas: manha,tarde. Equipe ideal: 3._

**3. Rótula do Itacorubi (Admar Gonzaga × Amaro A. Vieira)** — índice 83.5 (OURO — fluxo e afinidade altos)  
Rótula do Itacorubi, Itacorubi · Centro · ~169 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,3%, NOVO 7,7%, superior completo 55%, 20.828 eleitores, Matheus tinha 15 votos. Janelas: manha,tarde. Equipe ideal: 3._

**4. Semáforo Madre Benvenuta × Lauro Linhares** — índice 83.5 (OURO — fluxo e afinidade altos)  
Av. Madre Benvenuta, Santa Mônica · Centro · ~162 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,5%, NOVO 8,2%, superior completo 54%, 24.125 eleitores, Matheus tinha 13 votos. Janelas: manha,tarde. Equipe ideal: 2._

**5. TICEN — Terminal do Centro** — índice 83.3 (misto)  
Av. Paulo Fontes, Centro · Centro · ~280 panf/h/pessoa  
_Entorno de 1 km: direita 2024 21,2%, NOVO 5,6%, superior completo 45%, 16.948 eleitores, Matheus tinha 2 votos. Janelas: manha,tarde. Equipe ideal: 4._

**6. IFSC — Centro (Mauro Ramos)** — índice 82.4 (misto)  
Av. Mauro Ramos, 950 — Centro · Centro · ~135 panf/h/pessoa  
_Entorno de 1 km: direita 2024 25,1%, NOVO 7,3%, superior completo 52%, 41.927 eleitores, Matheus tinha 7 votos. Janelas: manha,tarde. Equipe ideal: 2._

**7. Mercado Público de Florianópolis** — índice 79.8 (OURO — fluxo e afinidade altos)  
R. Jerônimo Coelho, Centro · Centro · ~180 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,5%, NOVO 6,5%, superior completo 49%, 29.768 eleitores, Matheus tinha 5 votos. Janelas: almoco. Equipe ideal: 2._

**8. Feira do Largo da Alfândega (Centro)** — índice 77.0 (OURO — fluxo e afinidade altos)  
Largo da Alfândega, Centro · Centro · ~160 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,5%, NOVO 6,5%, superior completo 49%, 29.768 eleitores, Matheus tinha 5 votos. Janelas: feira,almoco. Equipe ideal: 3._

**9. Semáforo do Iguatemi (Av. Madre Benvenuta)** — índice 76.3 (misto)  
Av. Madre Benvenuta, 687 — Santa Mônica · Centro · ~148 panf/h/pessoa  
_Entorno de 1 km: direita 2024 22,5%, NOVO 7,9%, superior completo 55%, 23.775 eleitores, Matheus tinha 11 votos. Janelas: almoco,tarde. Equipe ideal: 2._

**10. UDESC/ESAG — Itacorubi** — índice 75.7 (misto)  
Av. Madre Benvenuta, 2007 — Itacorubi · Centro · ~108 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,5%, NOVO 8,2%, superior completo 53%, 23.062 eleitores, Matheus tinha 12 votos. Janelas: manha,tarde. Equipe ideal: 2._

**11. TIRIO — Terminal do Rio Tavares** — índice 74.0 (misto)  
SC-405, Rio Tavares · Sul da Ilha · ~225 panf/h/pessoa  
_Entorno de 1 km: direita 2024 21,1%, NOVO 2,6%, superior completo 38%, 6.940 eleitores, Matheus tinha 3 votos. Janelas: manha,tarde. Equipe ideal: 2._

**12. Rótula do CIC/Beiramar (Irineu Bornhausen × H. S. Fontes)** — índice 73.6 (misto)  
Av. Gov. Irineu Bornhausen, Agronômica · Centro · ~166 panf/h/pessoa  
_Entorno de 1 km: direita 2024 21,3%, NOVO 6,6%, superior completo 45%, 9.876 eleitores, Matheus tinha 3 votos. Janelas: manha,tarde. Equipe ideal: 3._

**13. Corporate Park / escritórios Itacorubi** — índice 70.1 (alta afinidade / baixo fluxo — porta a porta e eventos)  
Av. Madre Benvenuta / R. Pastor W. R. Schürmann · Centro · ~54 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,7%, NOVO 8,4%, superior completo 57%, 18.586 eleitores, Matheus tinha 11 votos. Janelas: almoco. Equipe ideal: 2._

**14. Semáforo Mauro Ramos (IEE/CEFET)** — índice 70.1 (misto)  
Av. Mauro Ramos, Centro · Centro · ~150 panf/h/pessoa  
_Entorno de 1 km: direita 2024 22,0%, NOVO 6,1%, superior completo 46%, 27.404 eleitores, Matheus tinha 2 votos. Janelas: manha,almoco,tarde. Equipe ideal: 2._

**15. Semáforo centrinho dos Ingleses (Dom João Becker)** — índice 69.8 (misto)  
Rod. Dom João Becker, Ingleses · Norte da Ilha · ~150 panf/h/pessoa  
_Entorno de 1 km: direita 2024 23,2%, NOVO 2,1%, superior completo 21%, 15.580 eleitores, Matheus tinha 1 votos. Janelas: manha,tarde. Equipe ideal: 2._

---
## 5. Rankings parciais (para discordar dos pesos)

### Por AFINIDADE (entorno mais alinhado)

| Ponto | Direita 24 (1 km) | Tendência 20→24 | Índice |
|---|---|---|---|
| Semáforo centrinho dos Ingleses (Dom João Becker) | 23,2% | 17,3% | 70 |
| Centrinho dos Ingleses (Dom João Becker) | 22,2% | 16,1% | 60 |
| Feira do Campeche (Av. Pequeno Príncipe) | 24,0% | 17,0% | 59 |
| Centrinho do Campeche | 24,0% | 17,0% | 58 |
| IFSC — Centro (Mauro Ramos) | 25,1% | 7,0% | 82 |
| Calçadão da Felipe Schmidt | 24,8% | 6,1% | 100 |
| UDESC/ESAG — Itacorubi | 23,5% | 7,7% | 76 |
| Semáforo Madre Benvenuta × Lauro Linhares | 23,5% | 7,7% | 84 |

### Por FLUXO (mais panfletos/hora)

| Ponto | Panf/h/pessoa (est.) | Direita 24 | Índice |
|---|---|---|---|
| Calçadão da Felipe Schmidt | 280 | 24,8% | 100 |
| TITRI — Terminal da Trindade | 280 | 21,3% | 89 |
| TICEN — Terminal do Centro | 280 | 21,2% | 83 |
| TIRIO — Terminal do Rio Tavares | 225 | 21,1% | 74 |
| UFSC — portaria Trindade (Delfino Conti) | 225 | 17,4% | 68 |
| TICAN — Terminal de Canasvieiras | 198 | 15,2% | 57 |
| Mercado Público de Florianópolis | 180 | 23,5% | 80 |
| Rótula do Itacorubi (Admar Gonzaga × Amaro A. Vieira) | 169 | 23,3% | 84 |

### Por PERFIL (entorno mais 'público-alvo')

| Ponto | Superior (1 km) | 16–24 (1 km) | Índice |
|---|---|---|---|
| Corporate Park / escritórios Itacorubi | 57% | 10% | 70 |
| Feira do Córrego Grande (Jardim Anchieta) | 57% | 10% | 70 |
| UFSC — CTC/Biblioteca (entrada Pantanal) | 47% | 17% | 53 |
| Feira do Itacorubi (Amaro Antônio Vieira) | 56% | 10% | 70 |
| Rótula do Itacorubi (Admar Gonzaga × Amaro A. Vieira) | 55% | 10% | 84 |
| Semáforo Madre Benvenuta × Lauro Linhares | 54% | 10% | 84 |
| UFSC — portaria Trindade (Delfino Conti) | 46% | 16% | 68 |
| UDESC/ESAG — Itacorubi | 53% | 10% | 76 |

### Casos especiais
- **Alto fluxo / baixa afinidade** (só reconhecimento de nome): UFSC — portaria Trindade (Delfino Conti); TICAN — Terminal de Canasvieiras; UFSC — CTC/Biblioteca (entrada Pantanal); Semáforo UFSC Sul (Dep. Antônio Edu Vieira × Cap. Romualdo); TILAG — Terminal da Lagoa; Semáforo Max Schramm (Jardim Atlântico)
- **Alta afinidade / baixo fluxo** (porta a porta e eventos, não panfleto): Corporate Park / escritórios Itacorubi; Feira do Córrego Grande (Jardim Anchieta); Feira do Itacorubi (Amaro Antônio Vieira); Centrinho dos Ingleses (Dom João Becker); Feira do Campeche (Av. Pequeno Príncipe); Centrinho do Campeche
- **SC-401 em pista**: maior fluxo da cidade (VMD ~60,6 mil veículos/dia no trecho norte fora de temporada — SSP-SC, jan/2025), mas SEM parada segura para abordagem: rodovia de fluxo contínuo. Usar os terminais e semáforos das entradas de bairro que a alimentam.

---
## 6. Calendário (resumo — detalhe no calendario_panfletagem.xlsx)

- **Fase 1 — Nome na rua (alto fluxo)**: 109 turnos-ponto, 26.350 panfletos.
- **Fase 2 — Conversão (território liberal)**: 115 turnos-ponto, 24.150 panfletos.
- **Fase 3 — Saturação (top + locais de votação)**: 41 turnos-ponto, 9.200 panfletos.

- Premissas NÃO informadas pelo coordenador (edite `plano_config.py` e regenere): equipe 6 pessoas em dia útil, 10 no sábado, 4 no domingo; tiragem 60.000.
- **A capacidade física da equipe é ~2.7× a tiragem premissa** (o plano escala a distribuição por 0,35 para caber nos 60 mil). Ou aumenta a tiragem (~170 mil) ou reduz turnos — decidir.
- Rotação: nenhum ponto repete em dias consecutivos (exceto fim de semana, quando a oferta de pontos abertos é menor); os 10 primeiros do índice recebem 7+ visitas cada (mínimo pedido: 4).
- Chuva: toda linha do XLSX tem alternativa coberta da região (terminais, Mercado Público, marquises da Fúlvio Aducci). Setembro é chuvoso em SC (Epagri/CIRAM); planejar ~1/3 dos dias com plano B acionado (estimativa).

---
## 7. Conformidade legal (verificada em 13/08/2026)

- **Período**: propaganda a partir de **16/08/2026** (Lei 9.504/97, art. 36). Distribuição de material impresso **independe de licença municipal** (art. 37, §8º) e pode ir **até 22h de 03/10** (véspera).
- **Dia 04/10 (eleição): distribuir material é CRIME** (boca de urna — art. 39, §5º). O plano termina dia 03/10. No dia, só manifestação individual e silenciosa.
- **Material**: todo impresso deve trazer CNPJ/CPF do responsável pela confecção, de quem contratou e a TIRAGEM (art. 38, §1º; Res. TSE 23.610/2019, atualizada pela Res. 23.755/2026).
- **Bens públicos**: proibido colar/pendurar em postes, semáforos, abrigos de ônibus e viadutos (art. 37). Entrega em mão é livre.
- **Código de Posturas de Floripa (LC 442/2012, alt. LC 634/2018)**: multa de **R$ 100 POR PANFLETO deixado** em logradouro público (reincidência). Operacionalmente: equipe recolhe material caído no fim de cada turno e registra em foto — 'derrame de santinhos' na véspera também gera multa eleitoral.
- **Semáforos**: NÃO encontrei lei municipal de Florianópolis que proíba expressamente a abordagem em cruzamento (diferente de outras capitais). Regra operacional para reduzir risco CTB/segurança: equipe no canteiro/passeio, nunca entre faixas em movimento; colete; abordar apenas com o vermelho fechado; nada de material no para-brisa.
- **Shoppings (Iguatemi/Beiramar)**: área INTERNA é privada — só com autorização. O plano usa as calçadas públicas do entorno.
- **Cabos eleitorais**: contratação sem vínculo CLT (art. 100); limite quantitativo do art. 100-A — p/ deputado estadual, 50% do limite de federal na circunscrição (em Floripa o teto passa de 300 pessoas; nossa equipe premissa de 6–10 está muito abaixo). Registrar todos na prestação de contas.

---
## 8. As três decisões estratégicas

**1) Assumir o eleitor formado, não o 'jovem universitário'.** A correlação voto NOVO × superior completo é 0,82; com jovens é negativa. Panfleto com densidade (dado, entrega, QR p/ portal) no arco Santa Mônica–Itacorubi–Córrego Grande–João Paulo–Centro **e em Jurerê Oeste** — o dado mandou incluir o bairro rico que a hipótese descartava.

**2) Não disputar o voto PL na rua — capturar o órfão liberal.** O PL fez 16,8% p/ vereador com máquina bolsonarista; brigar por esse eleitor em ponto de rua é caro. O alvo é o eleitor 'Bruno 2018/2022' (13–24 mil pessoas mapeadas por local no ranking) hoje sem candidato liberal na capital — daí o peso de 20% do componente LIBERAL, que localiza esse eleitor por onde ele já votou (NOVO 2024 e Bruno 2018/2022).

**3) Resolver a matemática tiragem × capacidade ANTES do dia 16/08.** Com 60 mil panfletos, a equipe premissa opera a 35% da capacidade física; com 170 mil, satura o plano inteiro. Decidir tiragem + equipe agora muda TODO o calendário — o XLSX regenera em 1 comando.

---
### Fontes externas (acesso 13/08/2026)
- TSE Dados Abertos — votação por seção 2018/2020/2022/2024, eleitorado/locais, perfil (dadosabertos.tse.jus.br)
- [Res. TSE 23.755/2026](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-755-de-2-de-marco-de-2026) e [regras de propaganda 2026 (TSE, jul/2026)](https://www.tse.jus.br/comunicacao/noticias/2026/Julho/saiba-quando-comeca-a-propaganda-eleitoral-e-conheca-as-novas-regras-para-as-eleicoes-2026); [O Tempo, 06/08/2026](https://www.otempo.com.br/politica/2026/8/6/eleicoes-2026-veja-quando-comeca-a-propaganda-nas-ruas-o-que-e-permitido-e-o-que-e-proibido)
- [SSP-SC — fluxo SC-401 (jan/2025)](https://ssp.sc.gov.br/trecho-norte-da-sc-401-registra-aumento-significativo-no-fluxo-diario-de-veiculos-em-janeiro-de-2025/); [ND+ — tráfego SC-401](https://ndmais.com.br/transito/trafego-na-sc-401-dispara-38-chega-a-quase-100-mil-veiculos-dia-e-supera-janeiro-de-2024/)
- [Consórcio Fênix — sistema de transporte](https://www.consorciofenix.com.br/noticias/novidades-no-pagamento-da-tarifa-do-sistema-de-transporte-coletivo-de-florianopolis,817) (~140 mil usuários/dia)
- [Feiras livres — lista oficial PMF via ND+ (25/05/2023)](https://ndmais.com.br/economia/e-dia-de-feira-e-elas-estao-por-toda-florianopolis-saiba-onde-encontra-las/)
- [Código de Posturas de Florianópolis / LC 442/2012](https://leismunicipais.com.br/a/sc/f/florianopolis/lei-complementar/2012/44/442/lei-complementar-n-442-2012-altera-o-art-28-da-lei-n-1224-de-1974-codigo-de-posturas-municipal)
- [TSE — limites de contratação de cabos eleitorais (art. 100-A)](https://www.tse.jus.br/comunicacao/noticias/2013/Dezembro/especial-minirreforma-lei-impoe-limites-para-a-contratacao-de-cabos-eleitorais)
- [Epagri/CIRAM — chuva de setembro em SC](https://ciram.epagri.sc.gov.br/index.php/2025/09/10/a-chuva-de-setembro-em-sc-e-a-previsao-de-dias-mais-secos/)
- Bruno Souza 2018: [Memória Política ALESC](https://memoriapolitica.alesc.sc.gov.br/biografia/1019-Bruno_Souza); [NSC Total — filiação ao NOVO](https://www.nsctotal.com.br/colunistas/moacir-pereira/deputado-bruno-souza-filia-se-ao-partido-novo-em-sc)