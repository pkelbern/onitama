# Arquitetura — Plataforma Onitama

## 1. Princípio central

O **motor de regras (`game_engine`) é Python puro**, sem Django, rede ou banco. Ele é a única fonte de verdade sobre legalidade. Tudo o mais — API, WebSocket, IA, replay, admin — é cliente dele.

```
 Angular (board, cards, lobby, rules, history)
        │  REST (comandos/consultas)   WebSocket (eventos)
        ▼
 Django: api/ ── rooms/ ── games/ ── history/ ── accounts/
        │              │
        │        Channels + Redis (presença, broadcast, locks)
        ▼
 game_engine/  ◄── ai/ (usa o mesmo motor)
   core · cards · rules · serialization · replay · (rulesets de expansão)
        ▲
 data/cards/*.json  (dados versionados → comando `import_cards` → PostgreSQL)
```

## 2. Motor (implementado na Etapa 1)

| Módulo | Responsabilidade |
|---|---|
| `core.py` | `Player`, `PieceType`, `Pos`, `Piece`, Arcos do Templo, convenção de coordenadas |
| `cards.py` | `Card`, carga dos JSON versionados, validação dos diagramas, `CardRegistry`, descrição textual dos movimentos |
| `rules.py` | `GameState` imutável, `setup_game`/`new_game` (seed reprodutível), `legal_moves`, `validate`, `apply_move` → `(novo_estado, MoveRecord)`, zugzwang/passe, vitória, `resign`, detecção de ameaça |
| `serialization.py` | Estado/jogada ↔ JSON com versão de esquema |
| `replay.py` | Reconstrói todos os estados revalidando cada jogada |
| `cli.py` | Partida local em terminal, para validar o núcleo |

Decisões:

- **Imutabilidade**: `apply_move` nunca altera o estado recebido. Facilita IA (busca em árvore), replay e transações.
- **Códigos de erro estáveis** (`not_your_turn`, `must_move`, `illegal_destination`…) para o frontend traduzir.
- **Cartas não validadas não jogam**: `Card.playable` exige status `official` e selo conhecido. Sensei's Path já está cadastrado, mas bloqueado.
- **Abandono** é `WinReason.RESIGNATION`, separado das vitórias do manual.

## 3. Expansões (Etapa 3) — como entram

Cada expansão vira um *ruleset* que estende o núcleo sem condicionais espalhadas:

- **Sensei's Path**: só dados (pool de cartas). Nenhum código novo.
- **Way of the Wind**: peça neutra no `GameState`; tipo de carta `wind` com dois diagramas; ação de turno passa a ser uma lista (`[mover peça, mover Espírito]`).
- **Light & Shadow**: estado oculto por jogador; o serializer passa a gerar **visão por jogador** (`state_to_dict(state, viewer=...)`), nunca enviando posição de Ninja ao adversário.

Por isso o `GameMove` do banco deve guardar o turno inteiro em `actions` (JSON), e não só origem/destino (ver matriz, seção 7).

## 4. Backend Django (Etapa 4)

- `cards`: modelos `Expansion`, `MovementCard`; comando `import_cards` lê `game_engine/data/cards/*.json` (dados versionados; admin só consulta).
- `games`: `Game` guarda `initial_state` + `state` (JSON do motor) + `version` (inteiro). Jogada = transação `select_for_update` no `Game`, checa `version` enviada pelo cliente (protege contra duplicidade), chama `apply_move`, grava `GameMove` e incrementa `version`.
- `rooms`: `GameRoom` com código de convite; `GamePlayer` liga usuário ↔ cor.
- `api`: DRF; o cliente nunca envia estado, só a intenção (`{card, from, to, expected_version}`).
- WebSocket (Channels/Redis): grupo por partida; eventos `state`, `move`, `game_over`, `presence`. Reconexão = reenvio do estado completo.

## 5. IA (Etapa 5)

Minimax com poda Alfa-Beta sobre `legal_moves`/`apply_move`. Níveis = profundidade + ruído. Para Light & Shadow, Minimax puro não se aplica (informação oculta) — pendência P-12.

## 6. Frontend Angular (Etapa 2)

Módulos `core` (serviços REST/WS), `shared` (componente `card-diagram` em SVG, reutilizado em mão/biblioteca/regras/histórico), `board`, `cards`, `lobby`, `history`, `rules`. No modo local o frontend pode rodar o mesmo motor via API do servidor; não haverá motor duplicado em TypeScript para validar jogadas.
