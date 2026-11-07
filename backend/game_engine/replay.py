"""Replay: reconstrói todos os estados a partir do estado inicial + jogadas registradas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .rules import GameState, Move, MoveRecord, apply_move


@dataclass(frozen=True, slots=True)
class Replay:
    states: tuple[GameState, ...]     # states[0] = inicial; states[i] = após o turno i
    records: tuple[MoveRecord, ...]

    def at(self, turn: int) -> GameState:
        if not 0 <= turn < len(self.states):
            raise IndexError(f"Turno fora do intervalo: {turn}")
        return self.states[turn]

    @property
    def final(self) -> GameState:
        return self.states[-1]


def build_replay(initial: GameState, moves: Sequence[Move]) -> Replay:
    """Revalida cada jogada pelo motor: um histórico adulterado lança ``IllegalMoveError``."""
    states = [initial]
    records = []
    state = initial
    for move in moves:
        state, rec = apply_move(state, move)
        states.append(state)
        records.append(rec)
    return Replay(tuple(states), tuple(records))
