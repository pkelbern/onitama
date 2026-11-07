"""Partida local no terminal, para validar o motor antes da interface.

Uso:  python -m game_engine.cli [--seed N]
Jogada:  <carta> <origem> <destino>   ex.: tiger c1 c3
Passe (só sem movimento legal):  <carta> pass
"""
from __future__ import annotations

import argparse

from .cards import load_expansion
from .core import Player, Pos
from .rules import GameState, IllegalMoveError, Move, apply_move, legal_moves, new_game

SYMBOL = {("red", "master"): "R", ("red", "student"): "r",
          ("blue", "master"): "B", ("blue", "student"): "b"}


def render(state: GameState) -> str:
    lines = []
    for y in range(4, -1, -1):
        row = []
        for x in range(5):
            p = state.piece_at(Pos(x, y))
            row.append(SYMBOL[(p.owner.value, p.kind.value)] if p else ".")
        lines.append(f"{y + 1}  " + " ".join(row))
    lines.append("   a b c d e")
    for player in (Player.BLUE, Player.RED):
        cards = ", ".join(f"{c.id}{list(c.moves)}" for c in state.hand(player))
        lines.append(f"{player.value:>4}: {cards}")
    lines.append(f"lateral: {state.side_card.id}  |  vez: {state.current.value}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    state = new_game(load_expansion("base"), seed=args.seed)
    while not state.is_over:
        print("\n" + render(state))
        try:
            raw = input("> ").split()
        except EOFError:
            return
        try:
            if len(raw) == 2 and raw[1] == "pass":
                move = Move(raw[0])
            elif len(raw) == 3:
                move = Move(raw[0], Pos.parse(raw[1]), Pos.parse(raw[2]))
            else:
                print("Formato: carta origem destino | carta pass")
                continue
            state, rec = apply_move(state, move)
            if rec.captured:
                print(f"Captura: {rec.captured.kind.value} {rec.captured.owner.value}")
        except (IllegalMoveError, ValueError) as exc:
            print(f"Inválido: {exc}")
            print("Legais:", ", ".join(str(m) for m in legal_moves(state)))
    print("\n" + render(state))
    print(f"Vitória de {state.winner.value} — {state.win_reason.value}")


if __name__ == "__main__":
    main()
