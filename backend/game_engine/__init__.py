"""Motor de regras do Onitama — independente de Django, frontend e rede."""
from .cards import Card, CardRegistry, CardStatus, describe_move, load_expansion
from .core import TEMPLE_ARCH, Piece, PieceType, Player, Pos, WinReason
from .replay import Replay, build_replay
from .rules import (
    GameState,
    GameStatus,
    IllegalMoveError,
    Move,
    MoveRecord,
    apply_move,
    attacked_squares,
    destinations,
    is_master_threatened,
    legal_moves,
    new_game,
    resign,
    setup_game,
)

__all__ = [
    "Card", "CardRegistry", "CardStatus", "describe_move", "load_expansion",
    "TEMPLE_ARCH", "Piece", "PieceType", "Player", "Pos", "WinReason",
    "Replay", "build_replay",
    "GameState", "GameStatus", "IllegalMoveError", "Move", "MoveRecord",
    "apply_move", "attacked_squares", "destinations", "is_master_threatened",
    "legal_moves", "new_game", "resign", "setup_game",
]
