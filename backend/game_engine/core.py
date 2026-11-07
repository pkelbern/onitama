"""Tipos fundamentais do motor: jogadores, peças, posições.

Convenção de coordenadas do tabuleiro (absolutas):
    x = coluna 0..4 (a..e), da esquerda para a direita do jogador VERMELHO
    y = linha  0..4 (1..5), y=0 é a fileira inicial do VERMELHO

Convenção das cartas (relativas ao dono): x = direita, y = frente.
O VERMELHO usa o diagrama como está; o AZUL, sentado do lado oposto,
usa o diagrama girado 180° (−x, −y).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

BOARD_SIZE = 5
FILES = "abcde"


class Player(str, Enum):
    RED = "red"
    BLUE = "blue"

    @property
    def opponent(self) -> "Player":
        return Player.BLUE if self is Player.RED else Player.RED

    @property
    def index(self) -> int:
        return 0 if self is Player.RED else 1

    @property
    def orientation(self) -> int:
        """+1 para o vermelho, −1 para o azul (rotação de 180°)."""
        return 1 if self is Player.RED else -1


class PieceType(str, Enum):
    MASTER = "master"
    STUDENT = "student"


class WinReason(str, Enum):
    WAY_OF_THE_STONE = "way_of_the_stone"    # captura do Mestre
    WAY_OF_THE_STREAM = "way_of_the_stream"  # Mestre no Arco do Templo adversário
    RESIGNATION = "resignation"              # regra de plataforma (abandono)


@dataclass(frozen=True, slots=True, order=True)
class Pos:
    x: int
    y: int

    def on_board(self) -> bool:
        return 0 <= self.x < BOARD_SIZE and 0 <= self.y < BOARD_SIZE

    def shifted(self, dx: int, dy: int) -> "Pos":
        return Pos(self.x + dx, self.y + dy)

    @property
    def index(self) -> int:
        return self.y * BOARD_SIZE + self.x

    @classmethod
    def from_index(cls, i: int) -> "Pos":
        return cls(i % BOARD_SIZE, i // BOARD_SIZE)

    def __str__(self) -> str:
        return f"{FILES[self.x]}{self.y + 1}"

    @classmethod
    def parse(cls, text: str) -> "Pos":
        text = text.strip().lower()
        if len(text) != 2 or text[0] not in FILES or not text[1].isdigit():
            raise ValueError(f"Coordenada inválida: {text!r}")
        pos = cls(FILES.index(text[0]), int(text[1]) - 1)
        if not pos.on_board():
            raise ValueError(f"Coordenada fora do tabuleiro: {text!r}")
        return pos


@dataclass(frozen=True, slots=True)
class Piece:
    owner: Player
    kind: PieceType

    @property
    def is_master(self) -> bool:
        return self.kind is PieceType.MASTER


TEMPLE_ARCH: dict[Player, Pos] = {
    Player.RED: Pos(2, 0),
    Player.BLUE: Pos(2, BOARD_SIZE - 1),
}
HOME_ROW: dict[Player, int] = {Player.RED: 0, Player.BLUE: BOARD_SIZE - 1}
