# Plataforma Onitama

Estado: **Etapa 1 concluída** — motor de regras do jogo-base + testes.

## Estrutura atual

```
docs/
  01-matriz-regras.md   matriz de regras, cartas, compatibilidade e pendências
  02-arquitetura.md     arquitetura e plano de integração Django/Angular
backend/
  game_engine/          motor puro (sem dependências)
    data/cards/         cartas versionadas (base oficial; Sensei's Path bloqueado)
  tests/                363 testes (pytest)
```

## Protótipo jogável

`prototype/index.html` é a mesa de jogo no navegador: jogo-base contra a IA (4 níveis) ou 2 jogadores no mesmo aparelho.
Abra com um servidor local (as cartas são carregadas de `prototype/cards/`):

```bash
cd prototype && python -m http.server 8000   # http://localhost:8000
```

É provisório: as regras rodam em JavaScript no próprio navegador. Na versão final o servidor Django é quem valida as jogadas.

## Executar

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install pytest
pytest                          # suíte completa
python -m game_engine.cli --seed 42   # partida local no terminal
```

Requer Python 3.12+. No terminal: `tiger c1 c3` (carta origem destino) ou `crab pass` (só quando não há movimento legal).

## Uso do motor

```python
from game_engine import load_expansion, new_game, legal_moves, apply_move

state = new_game(load_expansion("base"), seed=1)
move = legal_moves(state)[0]
state, record = apply_move(state, move)
```

## Próximos passos

1. Validar pendências da matriz (principalmente P-01 e as cartas das expansões).
2. Etapa 2: Django + DRF por cima do motor e interface Angular do tabuleiro.
