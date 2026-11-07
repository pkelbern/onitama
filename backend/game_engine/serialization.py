"""Conversão do estado e das jogadas para dicionários JSON (API, banco, WebSocket)."""
from __future__ import annotations

from typing import Any

from .cards import Card, CardRegistry, describe_move
from .core import Piece, PieceType, Player, Pos, WinReason
from .rules import GameState, GameStatus, Move, MoveRecord, legal_moves

SCHEMA_VERSION = 1


def card_to_dict(card: Card) -> dict[str, Any]:
    return {
        "id": card.id,
        "name_en": card.name_en,
        "name_pt": card.name_pt,
        "expansion": card.expansion,
        "stamp": card.stamp.value if card.stamp else None,
        "status": card.status.value,
        "moves": [
            {"x": dx, "y": dy, "description": describe_move(dx, dy)} for dx, dy in card.moves
        ],
    }


def move_to_dict(move: Move) -> dict[str, Any]:
    return {
        "card": move.card_id,
        "from": str(move.origin) if move.origin else None,
        "to": str(move.destination) if move.destination else None,
    }


def move_from_dict(data: dict[str, Any]) -> Move:
    origin, dest = data.get("from"), data.get("to")
    return Move(
        card_id=str(data["card"]),
        origin=Pos.parse(origin) if origin else None,
        destination=Pos.parse(dest) if dest else None,
    )


def _piece_to_dict(piece: Piece | None) -> dict[str, str] | None:
    return None if piece is None else {"owner": piece.owner.value, "kind": piece.kind.value}


def state_to_dict(state: GameState, include_legal_moves: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "board": [_piece_to_dict(p) for p in state.cells],
        "hands": {p.value: [c.id for c in state.hand(p)] for p in Player},
        "side_card": state.side_card.id,
        "current": state.current.value,
        "first_player": state.first_player.value,
        "turn": state.turn,
        "status": state.status.value,
        "winner": state.winner.value if state.winner else None,
        "win_reason": state.win_reason.value if state.win_reason else None,
    }
    if include_legal_moves:
        data["legal_moves"] = [move_to_dict(m) for m in legal_moves(state)]
    return data


def state_from_dict(data: dict[str, Any], registry: CardRegistry) -> GameState:
    if data.get("schema") != SCHEMA_VERSION:
        raise ValueError(f"Versão de esquema não suportada: {data.get('schema')}")
    cells = tuple(
        None if p is None else Piece(Player(p["owner"]), PieceType(p["kind"]))
        for p in data["board"]
    )
    if len(cells) != 25:
        raise ValueError("Tabuleiro deve ter 25 casas")
    hands = tuple(tuple(registry.get(cid) for cid in data["hands"][p.value]) for p in Player)
    return GameState(
        cells=cells,
        hands=hands,  # type: ignore[arg-type]
        side_card=registry.get(data["side_card"]),
        current=Player(data["current"]),
        first_player=Player(data["first_player"]),
        turn=int(data["turn"]),
        status=GameStatus(data["status"]),
        winner=Player(data["winner"]) if data["winner"] else None,
        win_reason=WinReason(data["win_reason"]) if data["win_reason"] else None,
    )


def record_to_dict(rec: MoveRecord) -> dict[str, Any]:
    return {
        "turn": rec.turn,
        "player": rec.player.value,
        **move_to_dict(rec.move),
        "piece": _piece_to_dict(rec.piece),
        "captured": _piece_to_dict(rec.captured),
        "card_received": rec.card_received,
        "winner": rec.winner.value if rec.winner else None,
        "win_reason": rec.win_reason.value if rec.win_reason else None,
    }
