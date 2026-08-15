# Manual de coordenação — panfletagem Florianópolis 2026
## Mandato Matheus Cadorin (NOVO/SC)

**Operação: 19/08 (quarta) a 03/10 (sábado) — 46 dias · 265 turnos-ponto · 59.700 panfletos.**

> Documento operacional da equipe de rua. A escala detalhada está em `calendario_panfletagem.xlsx`; o porquê de cada ponto, em `relatorio_plano.md`.

---
## 0. O essencial (leia isto se não ler mais nada)

1. **A eleição é 04/10, mas a panfletagem acaba 03/10 às 22h.** No dia da eleição, entregar material é boca de urna — crime. Não existe 'último esforço no domingo'.
2. **Começamos com 3 dias de atraso** sobre o período legal (16/08). Restam 46 dias. Não dá para recuperar volume — dá para recuperar com concentração.
3. **A missão é nome, não convencimento.** Com 84 votos em 2022, ninguém sabe quem é o candidato. Panfleto de rua serve para gravar nome+número; conversa longa é para feira e evento.
4. **Sem foto de material no chão.** A multa municipal é por panfleto deixado na via. Toda equipe recolhe o que caiu antes de sair.
5. **Todo turno termina com número reportado.** Sem medição, na terceira semana ninguém sabe o que funciona.

---
## 1. A decisão que trava tudo (resolver ANTES de quarta)

O plano roda com **premissas** que você ainda não confirmou: 6 pessoas em dia útil, 10 no sábado, 4 no domingo, e 60.000 panfletos no período.

Com essa equipe, a capacidade física de distribuição é de cerca de **164.835 panfletos** — ou seja, a tiragem premissa ocupa apenas **36%** do que o time consegue entregar. Três saídas, decida qual:

| Cenário | Tiragem | O que acontece |
|---|---|---|
| **Saturar** | ~164.835 | time trabalha no limite; maior alcance possível |
| **Equilibrar** | ~98.901 | folga para reforçar os pontos top na reta final |
| **Manter** | 60.000 | sobra capacidade: cortar turnos P2 ou reduzir equipe |

Qualquer que seja, é **uma linha** em `pipeline/plano_config.py` (`EQUIPE` e `ORCAMENTO_PANFLETOS`) e rodar `python3 run_plano.py` — a escala inteira se refaz sozinha.

---
## 2. Estrutura do time

**A unidade é a DUPLA, nunca a pessoa sozinha.** Dupla se protege, se reveza e um segura o material enquanto o outro entrega.

Com 6 pessoas em dia útil: **3 duplas** (Alfa, Bravo, Charlie). No sábado, com voluntários, as duplas viram 5 e uma delas cobre a feira grande do Centro.

| Papel | Quem | Responsabilidade |
|---|---|---|
| Coordenador | você | escala do dia, resolve imprevisto, consolida números |
| Cabeça de dupla | 1 por dupla | leva o material, cronometra, reporta no fim do turno |
| Panfletista | demais | entrega e aborda |
| Curinga | 1 pessoa (se houver) | cobre falta e reforça o ponto que estiver rendendo |

**Regra de alocação por tipo de ponto** (já embutida na escala):
- Semáforo de 3 faixas: 3 pessoas (uma por faixa, nunca entre carros em movimento).
- Semáforo de 2 faixas: 2 pessoas.
- Terminal: 1 pessoa por porta de embarque — não adianta amontoar na entrada.
- Feira/calçadão: 2 a 3, espalhados ao longo do fluxo, não em bloco.

---
## 3. O ritmo da semana

A escala repete um padrão. Decorar isto vale mais que consultar a planilha todo dia:

| Dia | Manhã | Tarde |
|---|---|---|
| Segunda | pico 7h–9h (terminais) | pico 17h–19h30 (semáforos) |
| Terça | almoço 11h30–13h30 (calçadão/mercado/tech) | pico 17h–19h30 |
| Quarta | **feira 8h30–12h** | pico 17h–19h30 |
| Quinta | almoço 11h30–13h30 | pico 17h–19h30 |
| Sexta | **feira 8h30–12h** | pico 17h–19h30 |
| Sábado | **feiras 8h30–12h** (equipe ampliada) | centrinhos 16h–19h |
| Domingo | — | centrinhos/orlas 16h–19h (turno leve) |

Carga média: **1.298 panfletos/dia** (mínimo 250, máximo 1.900).

### Prioridade P1 / P2 — a coluna mais útil da planilha

Cada turno vem marcado **P1** ou **P2**. P1 é o que sai mesmo com equipe reduzida (até 4 pessoas); P2 só com time completo. Faltou gente? Corta os P2 de cima para baixo e não improvisa. São 170 turnos P1 e 95 P2.

---
## 4. A rotina do dia

**Briefing (15 min, antes de sair)**
- Ponto de cada dupla, com endereço aberto no celular.
- Quantidade de material entregue a cada dupla (anotar!).
- A mensagem do dia (uma frase — ver seção 6).
- Confirmação do plano B de chuva daquele dia (está na planilha).

**Execução**
- Chegar 10 min antes do horário: no pico, os primeiros 20 minutos são os melhores e quase sempre se perdem no deslocamento.
- Colete/camiseta identificando a candidatura, sempre.
- Semáforo: só aborda com o vermelho fechado, do canteiro ou da calçada. Fechou o sinal, sai da pista. Sem exceção.
- Recolher material caído nos últimos 10 minutos do turno.

**Check-out (5 min, no fim do turno) — obrigatório**
Cada cabeça de dupla manda no grupo, em UMA mensagem:
```
PONTO / HORÁRIO / PESSOAS / LEVOU / VOLTOU / CLIMA / OBS
Ex.: TITRI 17h-19h30 · 3 pessoas · levou 700 · voltou 120 · seco ·
     muita gente perguntando de saúde
```
`LEVOU − VOLTOU = entregues`. É a única métrica que interessa.

---
## 5. Medição: o que fazer com os números

As estimativas de fluxo deste plano (45% de aceite em carro, 18% em pedestre, 40% em feira) são **de praxe, não medidas** — não existe dado público disso. Nas duas primeiras semanas você substitui a estimativa pela realidade:

1. Some `entregues ÷ (pessoas × horas)` de cada turno = **panfletos por hora por pessoa** reais.
2. Compare com a coluna de estimativa da planilha.
3. Ponto que render **menos de 60% do previsto por duas visitas** sai da rotação; ponto que render **acima de 130%** ganha turno extra.
4. No fim da 2ª semana, me passe a planilha preenchida que eu recalibro o modelo e regenero a escala das fases 2 e 3 com as taxas reais — o ranking pode mudar bastante.

**Meta simples para o time:** cada pessoa entrega o que levou. Se voltou com mais de 20% do material, ou o ponto está fraco ou a abordagem está tímida — as duas coisas se resolvem, mas só se forem medidas.

---
## 6. Como abordar (o roteiro muda com o ponto)

O erro clássico é usar o mesmo discurso em semáforo e em feira. O tempo disponível é completamente diferente.

**Semáforo — 8 segundos.** Só cabe nome + número + uma âncora.
> "Matheus Cadorin, deputado estadual. Menos imposto e menos burocracia pra quem trabalha. Tá tudo aqui, ó."

**Terminal — 15 segundos.** Entrega em movimento, sem travar o fluxo.
> "Bom dia! Matheus Cadorin pra deputado estadual. Fim do alvará pra quase 900 atividades — se você tem um negócio, dá uma olhada."

**Feira / calçadão — 1 a 2 minutos.** Aqui se conversa e se coleta contato de apoiador. É o ponto de conversão de verdade.
> Abrir com pergunta: "O senhor tem negócio próprio aqui na região?" e deixar a pessoa falar. O panfleto entra no fim, não no começo.

**Universidade / polo tech — 30 segundos.** Público formado, cético a slogan; funciona dado concreto e QR code.
> "Liberdade econômica e contas públicas. Tem o histórico de votação dele no QR aqui."

**Regra de ouro:** ninguém discute política na rua. Recebeu crítica, agradece, entrega e segue. Discussão em semáforo custa 10 abordagens e vira vídeo.

---
## 7. Kit de campo (por dupla)

- Material do dia + 15% de reserva, em sacola impermeável.
- Colete/camiseta da campanha, boné, protetor solar, água.
- Saco plástico para **recolher material caído** (não é opcional).
- Powerbank — o celular é o instrumento de reporte.
- Cartão de conformidade (seção 9) plastificado.
- Guarda-chuva/capa: em setembro chove em Floripa.

---
## 8. Contingências

| Situação | O que fazer |
|---|---|
| **Chuva** | cada linha da planilha tem alternativa coberta (terminal, Mercado Público, marquises da Fúlvio Aducci). Terminal em dia de chuva rende MAIS que o normal |
| **Faltou gente** | corta os turnos P2, mantém todos os P1. Nunca mandar pessoa sozinha para semáforo |
| **Outra campanha no ponto** | não disputa espaço. Vai para o lado oposto do cruzamento ou aciona o ponto reserva da região |
| **Fiscal / guarda municipal** | equipe é cordial, mostra que está em calçada/canteiro e que recolhe material. Distribuição em mão é legal e não exige licença (art. 37 §8º) |
| **Material acabou no meio do turno** | dupla vira 'abordagem sem papel': anota contatos de interessados. Não vale ficar parado |
| **Calor extremo / evento na via** | remaneja para o turno da tarde do mesmo ponto |

---
## 9. Cartão de conformidade (plastificar e pôr em cada kit)

```
PODE                                  NÃO PODE
- entregar em mão, na calçada         - colar em poste, semáforo, abrigo
- feira, terminal, calçadão           - entrar em shopping/prédio privado
- até 22h do dia 03/10                - QUALQUER material no dia 04/10
- caminhada, carreata, bandeira       - deixar panfleto no chão (multa!)
                                      - discutir com eleitor ou adversário

Todo material impresso traz CNPJ/CPF do responsável + tiragem.
Dúvida na rua? Liga para o coordenador. Não improvisa.
```

---
## 10. Os marcos do período

**Fase 1 — Nome na rua (alto fluxo)** — 20 dias, 109 turnos, 26.350 panfletos.

**Fase 2 — Conversão (território liberal)** — 19 dias, 115 turnos, 24.150 panfletos.

**Fase 3 — Saturação (top + locais de votação)** — 7 dias, 41 turnos, 9.200 panfletos.

### 7 de setembro (segunda) — o dia mais importante da Fase 1

Desfile cívico: maior concentração de rua do período, público majoritariamente de direita e clima favorável à pauta de liberdade/orgulho catarinense. **A escala automática não sabe onde passa o desfile — este dia é override manual seu.** Recomendação: toda a equipe disponível no entorno do evento (Beira-Mar Norte / Centro), posicionada na dispersão do público (fim do desfile), fora do perímetro oficial. Vale levar o candidato.

### Últimas 72 horas (01 a 03/10)

- Saturar os pontos do topo do ranking, sem inventar ponto novo.
- Reforçar o **entorno dos locais de votação** do top-20 eleitoral (estão em `ranking_panfletagem.csv`) — memória fresca vale mais perto de onde a pessoa vai votar.
- **03/10 encerra às 22h.** Contagem final do material e recolhimento.
- **Proibido derrame de santinhos.** Além de multa, é o tipo de imagem que vira matéria contra a campanha.

---
## 11. Os cinco erros que matam a operação

1. **Chegar no horário em vez de antes dele.** O pico não espera; 20 minutos perdidos são 30% do turno.
2. **Não medir.** Sem `levou/voltou`, na semana 3 a escala vira achismo — exatamente o que este plano existe para evitar.
3. **Espalhar demais.** Concentração gera memória: os 10 pontos do topo recebem visita repetida de propósito. Resistir à tentação de 'cobrir a cidade toda'.
4. **Discutir política na rua.** Custa tempo, moral da equipe e eventualmente um vídeo viral.
5. **Deixar material no chão.** Multa por panfleto e desgaste de imagem — o eleitor de perfil ambientalista da Ilha pune isso.

---
## 12. Sua rotina como coordenador

- **Domingo à noite (15 min):** conferir a escala da semana, confirmar presença das duplas, checar previsão do tempo e já decidir os dias que provavelmente vão para o plano B.
- **Todo dia, 5 min após cada turno:** consolidar os check-outs numa planilha. Só isso.
- **Sexta (30 min):** calcular panfletos/hora/pessoa por ponto, cortar os fracos, reforçar os fortes.
- **Fim da semana 2 (04–05/09):** recalibração geral com dados reais de campo (ver seção 5) e regeneração da escala das fases 2 e 3.

### Os 10 pontos que não podem falhar

| # | Ponto | Região | Índice |
|---|---|---|---|
| 1 | Calçadão da Felipe Schmidt | Centro | 100 |
| 2 | TITRI — Terminal da Trindade | Centro | 89 |
| 3 | Rótula do Itacorubi (Admar Gonzaga × Amaro A. Vieira) | Centro | 84 |
| 4 | Semáforo Madre Benvenuta × Lauro Linhares | Centro | 84 |
| 5 | TICEN — Terminal do Centro | Centro | 83 |
| 6 | IFSC — Centro (Mauro Ramos) | Centro | 82 |
| 7 | Mercado Público de Florianópolis | Centro | 80 |
| 8 | Feira do Largo da Alfândega (Centro) | Centro | 77 |
| 9 | Semáforo do Iguatemi (Av. Madre Benvenuta) | Centro | 76 |
| 10 | UDESC/ESAG — Itacorubi | Centro | 76 |

*Observação de cobertura: o Centro concentra 58% dos turnos — é deliberado (é onde fluxo e voto liberal coincidem), mas é uma escolha sua, não uma imposição dos dados. Se quiser mais presença no Continente ou Norte, é ajuste de peso no índice.*

---

*Gerado em 15/08/2026 a partir da escala real do pipeline. Para refazer com outra equipe/tiragem: editar `pipeline/plano_config.py` e rodar `python3 run_plano.py`.*