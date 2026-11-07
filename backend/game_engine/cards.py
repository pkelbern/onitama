"""Cartas de movimento: modelo, carga dos dados versionados e descrição textual."""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from importlib import resources
from typing import Iterable

from .core import Player


class CardStatus(str, Enum):
    OFFICIAL = "official"
    PENDING_VALIDATION = "pending_validation"


@dataclass(frozen=True, slots=True)
class Card:
    id: str
    name_en: str
    name_pt: str
    expansion: str
    moves: tuple[tuple[int, int], ...]
    stamp: Player | None
    status: CardStatus

    def deltas_for(self, player: Player) -> tuple[tuple[int, int], ...]:
        """Deslocamentos absolutos no tabuleiro para quem está usando a carta."""
        o = player.orientation
        return tuple((dx * o, dy * o) for dx, dy in self.moves)

    @property
    def playable(self) -> bool:
        return self.status is CardStatus.OFFICIAL and self.stamp is not None


def describe_move(dx: int, dy: int) -> str:
    """Descrição em português de um deslocamento relativo (perspectiva do dono)."""
    parts: list[str] = []
    if dy:
        parts.append(f"{abs(dy)} para {'frente' if dy > 0 else 'trás'}")
    if dx:
        parts.append(f"{abs(dx)} para a {'direita' if dx > 0 else 'esquerda'}")
    return " e ".join(parts) if parts else "parado"


class CardError(ValueError):
    pass


def _parse_card(raw: dict, expansion: str, status: CardStatus) -> Card:
    moves = tuple((int(m[0]), int(m[1])) for m in raw["moves"])
    if not moves:
        raise CardError(f"Carta {raw['id']} sem movimentos")
    if len(set(moves)) != len(moves):
        raise CardError(f"Carta {raw['id']} com movimento duplicado")
    if (0, 0) in moves:
        raise CardError(f"Carta {raw['id']} com movimento nulo")
    if any(abs(dx) > 2 or abs(dy) > 2 for dx, dy in moves):
        raise CardError(f"Carta {raw['id']} excede o diagrama 5x5")
    stamp = Player(raw["stamp"]) if raw.get("stamp") else None
    return Card(
        id=raw["id"],
        name_en=raw["name_en"],
        name_pt=raw["name_pt"],
        expansion=expansion,
        moves=moves,
        stamp=stamp,
        status=status,
    )


def load_expansion(expansion: str) -> list[Card]:
    """Carrega o arquivo de dados versionado ``data/cards/<expansion>.json``."""
    path = resources.files(__package__).joinpath("data", "cards", f"{expansion}.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    status = CardStatus(data["status"])
    return [_parse_card(c, data["expansion"], status) for c in data["cards"]]


class CardRegistry:
    """Catálogo de cartas indexado por id."""

    def __init__(self, cards: Iterable[Card]):
        self._cards: dict[str, Card] = {}
        for card in cards:
            if card.id in self._cards:
                raise CardError(f"Id de carta duplicado: {card.id}")
            self._cards[card.id] = card

    @classmethod
    def default(cls) -> "CardRegistry":
        return cls([*load_expansion("base"), *load_expansion("senseis_path")])

    def get(self, card_id: str) -> Card:
        try:
            return self._cards[card_id]
        except KeyError:
            raise CardError(f"Carta desconhecida: {card_id}") from None

    def by_expansion(self, expansion: str) -> list[Card]:
        return [c for c in self._cards.values() if c.expansion == expansion]

    def all(self) -> list[Card]:
        return list(self._cards.values())
