import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_engine import CardRegistry, Piece, PieceType, Player, Pos, load_expansion  # noqa: E402


@pytest.fixture(scope="session")
def base_cards():
    return load_expansion("base")


@pytest.fixture(scope="session")
def registry():
    return CardRegistry.default()


@pytest.fixture
def card(registry):
    return registry.get


def empty_cells():
    return [None] * 25


def layout(**placements):
    """layout(c1="R", c5="B", a2="r") -> tupla de 25 casas. R/B = mestre, r/b = aluno."""
    cells = empty_cells()
    for square, sym in placements.items():
        owner = Player.RED if sym.lower() == "r" else Player.BLUE
        kind = PieceType.MASTER if sym.isupper() else PieceType.STUDENT
        cells[Pos.parse(square).index] = Piece(owner, kind)
    return tuple(cells)
