---
title: "Onitama — Matriz de regras, cartas, peças e compatibilidade"
subtitle: "Levantamento pré-implementação (Etapa 0) — versão 0.1, 06/11/2026"
---

# 1. Fontes consultadas e grau de confiança

| Código | Fonte | Tipo | Confiança |
|---|---|---|---|
| F1 | Manual oficial Onitama (Arcane Wonders, PDF `Onitama-Rulebook.pdf`) — conteúdo obtido via transcrição em rulespal.com e guias de terceiros | Oficial (indireto) | Alta |
| F2 | Página oficial Way of the Wind (arcanewonders.com) + transcrição do manual (rulespal.com) | Oficial + indireto | Média-alta |
| F3 | Página oficial Light and Shadow (arcanewonders.com) + transcrição do manual (rulespal.com) | Oficial + indireto | Média |
| F4 | Manual Onitama Big Box (Pegasus Spiele, transcrição rulespal.com) | Oficial (licenciado) | Média |
| F5 | chessvariants.org — descrição textual dos movimentos (base + Sensei's Path) | Terceiro | Média |
| F6 | Lojas/BGG — listas de componentes e nomes de cartas | Terceiro | Alta para nomes, nula para regras |

**Limitação importante:** o acesso direto aos PDFs oficiais foi bloqueado no ambiente de pesquisa. As regras abaixo vieram de transcrições/resumos dos manuais. **Antes da Etapa 3 (expansões) é obrigatório conferir contra os PDFs oficiais ou as cartas físicas** (ver pendências P-01 a P-14).

# 2. Jogo-base (F1) — CONFIRMADO, implementado na Etapa 1

| Item | Regra |
|---|---|
| Tabuleiro | 5 × 5; Arco do Templo no centro da fileira inicial de cada jogador |
| Peças | Por cor: 1 Mestre (no Arco do Templo) + 4 Alunos (nas outras casas da fileira inicial) |
| Cartas | 16 cartas; por partida usam-se 5: 2 por jogador (abertas) + 1 lateral |
| Primeiro jogador | Cor do selo (canto inferior direito) da 5ª carta; ela fica à direita do primeiro jogador |
| Movimento | Escolhe 1 das 2 cartas, move 1 peça própria (Mestre ou Aluno) conforme o diagrama, relativo à posição da peça |
| Bloqueio | Peças e arcos **não** bloqueiam (salto livre); proibido sair do tabuleiro ou terminar em casa com peça própria |
| Captura | Terminar em casa com peça adversária remove-a; passar por cima **não** captura |
| Troca | Carta usada vai para a lateral (girada 180°, voltada ao adversário); o jogador pega a carta lateral, usável a partir do seu próximo turno |
| Zugzwang | Se existe movimento legal com qualquer carta, é obrigatório mover. Só se passa quando nenhuma carta permite movimento — e ainda assim se troca uma das duas cartas |
| Vitória | Caminho da Pedra: capturar o Mestre adversário. Caminho do Fluxo: levar o **próprio Mestre** ao Arco do Templo adversário |
| Empate | **Não existe regra de empate** no manual |
| Xeque | **Não existe** regra de xeque: é permitido mover para casa atacada (inclusive com o Mestre) |

## 2.1 Cartas do jogo-base (16)

Convenção: `x` = direita do dono da carta, `y` = para frente. Para o adversário, inverte-se (−x, −y).

| Carta (EN) | Nome PT (provisório) | Movimentos (x,y) | Selo (1º jogador) |
|---|---|---|---|
| Tiger | Tigre | (0,2) (0,−1) | Azul |
| Crab | Caranguejo | (−2,0) (2,0) (0,1) | Azul |
| Monkey | Macaco | (−1,1) (1,1) (−1,−1) (1,−1) | Azul |
| Crane | Grou | (0,1) (−1,−1) (1,−1) | Azul |
| Dragon | Dragão | (−2,1) (2,1) (−1,−1) (1,−1) | Vermelho |
| Elephant | Elefante | (−1,1) (1,1) (−1,0) (1,0) | Vermelho |
| Mantis | Louva-a-deus | (−1,1) (1,1) (0,−1) | Vermelho |
| Boar | Javali | (−1,0) (1,0) (0,1) | Vermelho |
| Frog | Sapo | (−2,0) (−1,1) (1,−1) | Vermelho |
| Goose | Ganso | (−1,0) (−1,1) (1,0) (1,−1) | Azul |
| Horse | Cavalo | (−1,0) (0,1) (0,−1) | Vermelho |
| Eel | Enguia | (−1,1) (−1,−1) (1,0) | Azul |
| Rabbit | Coelho | (2,0) (1,1) (−1,−1) | Azul |
| Rooster | Galo | (1,0) (1,1) (−1,0) (−1,−1) | Vermelho |
| Ox | Boi | (1,0) (0,1) (0,−1) | Azul |
| Cobra | Cobra | (−1,0) (1,1) (1,−1) | Vermelho |

Movimentos conferidos com a descrição textual F5. Cores dos selos: ver P-01.

# 3. Sensei's Path (F5, F6) — DADOS PRÉ-CADASTRADOS, BLOQUEADOS ATÉ VALIDAÇÃO

Regras: **nenhuma regra nova**. 16 cartas que podem substituir as do jogo-base ou ser embaralhadas com elas (pool de 32).

| Carta (EN) | Movimentos (x,y) segundo F5 | Selo |
|---|---|---|
| Giraffe | (−2,1) (2,1) (0,−1) | ? |
| Kirin | (−1,2) (1,2) (0,−2) | ? |
| Phoenix | (−1,1) (1,1) (−2,0) (2,0) | ? |
| Turtle | (−2,0) (2,0) (−1,−1) (1,−1) | ? |
| Dog / Fox | (−1,1) (−1,0) (−1,−1) / espelho | ? |
| Bear / Panda | (0,1) (−1,1) (1,−1) / espelho | ? |
| Viper / Sea Snake | (0,1) (−2,0) (1,−1) / espelho | ? |
| Rat / Mouse | (0,1) (−1,0) (1,−1) / espelho | ? |
| Iguana / Tanuki | (0,1) (−2,1) (1,−1) / espelho | ? |
| Otter / Sable | (−1,1) (1,−1) (2,0) / espelho | ? |

Pendências: P-02 (diagramas), P-03 (selos). Leitura de "pulo em L" e "esquerda/direita" feita por analogia com o jogo-base — **precisa de conferência visual**.

# 4. Way of the Wind (F2, F4) — REGRAS LEVANTADAS, CARTAS SEM DADOS

**Componentes:** 1 Espírito do Vento; 2 cartas de movimento (Goat, Sheep); 8 cartas de Espírito do Vento (Bat, Eagle, Hawk, Lion, Octopus, Rhinoceros, Scorpion, Spider).

| Item | Regra |
|---|---|
| Preparação | Espírito na casa central. 5 cartas = 2 de Vento + 3 de movimento (do base e/ou expansões). Cada jogador recebe 1 de Vento + 1 de movimento; a 3ª de movimento vai para o centro e seu selo define o 1º jogador |
| Carta de movimento | Move 1 peça própria **ou** o Espírito (só se este tiver movimento legal com a carta) |
| Carta de Vento | Diagrama superior move peça própria; depois, **obrigatoriamente se possível**, diagrama inferior move o Espírito. Se uma das partes não tiver opção legal, é pulada e a outra é feita |
| Espírito × Aluno | Ao terminar sobre um Aluno (qualquer cor), **troca de lugar** com ele (não captura) |
| Espírito × Mestre | Não pode terminar em casa com Mestre (qualquer cor) |
| Bloqueio | Mestre e Alunos nunca podem terminar na casa do Espírito |
| Captura | O Espírito não captura e não pode ser capturado |
| Arco do Templo | Espírito no Arco adversário **não** dá vitória |
| Vitória | Inalteradas (Pedra e Fluxo) |
| Zugzwang | Mantido (F4) |
| Variantes | Grande Espírito: 3V+2M, 4V+1M, 5V+0M. Pequeno Espírito: 1V+4M, 0V+5M (Espírito presente, só cartas de movimento) |

Pendências: P-04 (diagramas das 10 cartas), P-05 (selos das cartas de Vento — necessário nas variantes 4V+1M? não; 5V+0M sim, pois a carta central é de Vento), P-06 (orientação/inversão do diagrama do Espírito para cada jogador), P-07 (o Aluno trocado pode cair no Arco? efeitos).

# 5. Light & Shadow (F3, F4) — REGRAS LEVANTADAS, LACUNAS RELEVANTES

**Componentes:** 2 Ninjas, 4 Lanternas, 2 tabuleiros de Ninja, 2 biombos.

## 5.1 Caminho da Sombra (simétrico)

| Item | Regra |
|---|---|
| Peças | Mestre no Arco + **apenas 2 Alunos** nos cantos da fileira inicial + 1 Ninja oculto numa das 2 casas vizinhas ao Mestre |
| Ninja | Está "no tabuleiro principal" na casa correspondente; apenas sua posição é secreta |
| Turno — passo 1 | Movimento obrigatório de peça visível; **depois, opcionalmente**, o Ninja com a **mesma carta** (movimento pode ser diferente) |
| Zugzwang | Obrigatório mover peça visível se possível; se nenhuma pode mas o Ninja pode, pode mover o Ninja ou passar |
| Restrições do Ninja | Não termina sobre peça visível própria; os dois Ninjas podem ocupar a mesma casa |
| Ninja captura | Ninja termina sobre peça adversária → revela, remove a peça, fica visível até o início do próximo turno do dono |
| Captura de Ninja | Peça adversária termina na casa do Ninja oculto → dono anuncia, Ninja sai do jogo |
| Ninja × Ninja | Após mover o Ninja para casa vazia, pode declarar tentativa; se o Ninja inimigo estiver lá, é removido |
| Passo 2 | Troca normal de cartas |
| Passo 3 (opcional) | Lanterna: 2 por partida, 1 por turno, uma linha ou coluna; resposta só "sim/não". 1º jogador não usa no 1º turno |
| Vitória | Pedra e Fluxo |

## 5.2 Caminho da Luz (assimétrico)

| Item | Regra |
|---|---|
| Luz | Mestre + 4 Alunos, 2 Lanternas, **sempre começa** (ignora selo) |
| Sombra | Só 2 Ninjas ocultos, em qualquer casa da sua fileira inicial |
| Turno | Cada jogador move **uma** peça; Sombra deve mover um Ninja se possível |
| Lanterna | Só a Luz usa; resposta "sim" pode significar 1 ou 2 Ninjas |
| Vitória Sombra | Somente capturar o Mestre da Luz |
| Vitória Luz | Capturar os 2 Ninjas **ou** Mestre no Arco do Templo da Sombra |

Pendências: P-08 a P-12.

# 6. Matriz de compatibilidade

| Combinação | Situação oficial | Decisão proposta |
|---|---|---|
| Base | Oficial | Permitir |
| Base + Sensei's Path (pool 32) | Oficial | Permitir |
| Só Sensei's Path (16) | Oficial (substitui as do base) | Permitir |
| Way of the Wind + base e/ou Sensei's Path | Oficial — o manual manda tirar as cartas de movimento "do jogo original e/ou de uma expansão" | Permitir |
| Light & Shadow + base / Sensei's Path | L&S usa as cartas normais | Permitir |
| Light & Shadow + Way of the Wind | **"Não recomendado"**, mas "tecnicamente compatível" (manual L&S). Big Box diz que expansões combinam livremente | **P-13 — decisão do cliente** (proposta: bloquear por padrão, liberar como "modo avançado não oficial") |
| Promos (14 cartas, Big Box) | Fora do escopo do prompt | P-14 |

# 7. Impactos na arquitetura detectados

1. **Turno com mais de um movimento** (carta de Vento: peça + Espírito; Sombra: peça + Ninja opcional + Lanterna). O modelo `GameMove` do prompt (1 origem/1 destino) **não comporta**; proposta: `GameMove` = turno, com lista `actions` em JSON.
2. **Informação oculta** (Light & Shadow): o backend não pode enviar a posição dos Ninjas ao adversário — exige "visão por jogador" no serializer e no WebSocket. Replay público só após o fim da partida.
3. **Partida local com Ninja**: num só dispositivo, o biombo precisa ser simulado (tela de passagem obrigatória). P-11.
4. **IA**: Minimax/Alpha-Beta pressupõe informação perfeita. Para Light & Shadow é necessária outra abordagem (ex.: amostragem de posições possíveis do Ninja). P-12.
5. **Empate**: não há regra oficial. Partidas IA × IA ou bloqueio cíclico podem não terminar. Proposta: nenhuma regra de empate no motor; só limite técnico configurável de "abandono por inatividade" na plataforma. P-15.
6. **Abandono** é regra da plataforma, não do jogo — registrar como `win_reason = resignation`.

# 8. Pendências que exigem validação

| ID | Pendência | Bloqueia |
|---|---|---|
| P-01 | Conferir cor do selo das 16 cartas base nas cartas físicas | Etapa 1 (baixo risco; dado isolado em JSON) |
| P-02 | Conferir diagramas das 16 cartas Sensei's Path | Etapa 3 |
| P-03 | Cor do selo das 16 cartas Sensei's Path | Etapa 3 |
| P-04 | Diagramas das cartas Goat, Sheep e das 8 de Vento (superior e inferior) — sem fonte textual pública | Etapa 3 |
| P-05 | Selo das cartas de Vento (variante 5V+0M) | Etapa 3 |
| P-06 | Diagrama inferior (Espírito) é orientado ao jogador que usa a carta? | Etapa 3 |
| P-07 | Troca Espírito ↔ Aluno: Aluno pode cair no Arco ou em casa "ilegal"? | Etapa 3 |
| P-08 | Caminho da Sombra: a peça visível pode ficar parada e só o Ninja mover? (texto indica que não, salvo zugzwang) | Etapa 3 |
| P-09 | Caminho da Luz: Ninja captura peças da Luz como na Sombra? (resumo do manual é omisso) | Etapa 3 |
| P-10 | Ninja pode ir ao Arco do Templo / vencer pelo Fluxo? | Etapa 3 |
| P-11 | Como tratar informação oculta no modo local (mesmo aparelho) | Etapa 3/2 |
| P-12 | Estratégia de IA para informação oculta | Etapa 5 |
| P-13 | Permitir Light & Shadow + Way of the Wind? | Etapa 3 |
| P-14 | Incluir cartas promocionais? | Etapa 3 |
| P-15 | Política para partidas que não terminam | Etapa 4 |
| P-16 | Nomes oficiais em português (houve edição brasileira?) | Catálogo |
| P-17 | Direitos sobre o nome/logo "Onitama" (marca registrada da Arcane Wonders) para uso público | Lançamento |

**Pedido:** enviar os PDFs oficiais dos manuais das três expansões (ou fotos das cartas) para fechar P-02 a P-10.
