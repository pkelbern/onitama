"""Motor de regras do Onitama (jogo-base).

Puro, determinístico e imutável: toda função recebe um ``GameState`` e
devolve um novo, sem efeitos colaterais. É a única autoridade sobre o que é
legal — API, WebSocket, IA e replay chamam estas mesmas funções.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Sequence

from .cards import Card
from .core import (
    BOARD_SIZE,
    HOME_ROW,
    TEMPLE_ARCH,
    Piece,
    PieceType,
    Player,
    Pos,
    WinReason,
)

CARDS_PER_GAME = 5


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class IllegalMoveError(ValueError):
    """Jogada rejeitada. ``code`` é estável para a API/cliente."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class Move:
    """Ação de um turno. ``origin``/``destination`` nulos = passar (só sem movimento legal)."""

    card_id: str
    origin: Pos | None = None
    destination: Pos | None = None

    @property
    def is_pass(self) -> bool:
        return self.origin is None

    def __str__(self) -> str:
        if self.is_pass:
            return f"{self.card_id}: passa"
        return f"{self.card_id}: {self.origin}-{self.destination}"


@dataclass(frozen=True, slots=True)
class GameState:
    cells: tuple[Piece | None, ...]                 # 25 casas, índice y*5+x
    hands: tuple[tuple[Card, Card], tuple[Card, Card]]  # [vermelho, azul]
    side_card: Card
    current: Player
    first_player: Player
    turn: int = 0                                   # turnos já jogados
    status: GameStatus = GameStatus.IN_PROGRESS
    winner: Player | None = None
    win_reason: WinReason | None = None

    # ---- consultas -------------------------------------------------------
    def piece_at(self, pos: Pos) -> Piece | None:
        return self.cells[pos.index]

    def hand(self, player: Player) -> tuple[Card, Card]:
        return self.hands[player.index]

    def pieces(self, player: Player) -> list[tuple[Pos, Piece]]:
        return [
            (Pos.from_index(i), p)
            for i, p in enumerate(self.cells)
            if p is not None and p.owner is player
        ]

    def master_pos(self, player: Player) -> Pos | None:
        for pos, piece in self.pieces(player):
            if piece.is_master:
                return pos
        return None

    @property
    def is_over(self) -> bool:
        return self.status is GameStatus.FINISHED

    def all_cards(self) -> tuple[Card, ...]:
        return (*self.hands[0], *self.hands[1], self.side_card)


@dataclass(frozen=True, slots=True)
class MoveRecord:
    """O que aconteceu num turno — base do histórico e das notificações."""

    turn: int
    player: Player
    move: Move
    piece: Piece | None
    captured: Piece | None
    card_received: str          # carta que estava na lateral e entrou na mão
    winner: Player | None
    win_reason: WinReason | None


# ---- preparação ------------------------------------------------------------

def initial_cells() -> tuple[Piece | None, ...]:
    cells: list[Piece | None] = [None] * (BOARD_SIZE * BOARD_SIZE)
    for player in Player:
        row = HOME_ROW[player]
        for x in range(BOARD_SIZE):
            kind = PieceType.MASTER if x == TEMPLE_ARCH[player].x else PieceType.STUDENT
            cells[Pos(x, row).index] = Piece(player, kind)
    return tuple(cells)


def setup_game(
    red_hand: tuple[Card, Card],
    blue_hand: tuple[Card, Card],
    side_card: Card,
    cells: tuple[Piece | None, ...] | None = None,
) -> GameState:
    """Monta uma partida com cartas definidas. O selo da carta lateral define quem começa."""
    cards = (*red_hand, *blue_hand, side_card)
    if len({c.id for c in cards}) != CARDS_PER_GAME:
        raise ValueError("As 5 cartas da partida devem ser distintas")
    if side_card.stamp is None:
        raise ValueError(f"Carta {side_card.id} não tem selo validado; não pode definir o 1º jogador")
    for card in cards:
        if not card.playable:
            raise ValueError(f"Carta {card.id} ainda não foi validada para partidas")
    first = side_card.stamp
    return GameState(
        cells=cells if cells is not None else initial_cells(),
        hands=(tuple(red_hand), tuple(blue_hand)),  # type: ignore[arg-type]
        side_card=side_card,
        current=first,
        first_player=first,
    )


def new_game(pool: Sequence[Card], seed: int | None = None) -> GameState:
    """Embaralha o conjunto de cartas e distribui como no manual (2 + 2 + 1).

    Com ``seed`` a distribuição é reprodutível (necessário para replay/testes).
    """
    playable = [c for c in pool if c.playable]
    if len(playable) < CARDS_PER_GAME:
        raise ValueError("São necessárias ao menos 5 cartas validadas")
    rng = random.Random(seed)
    deck = sorted(playable, key=lambda c: c.id)
    rng.shuffle(deck)
    return setup_game((deck[0], deck[1]), (deck[2], deck[3]), deck[4])


# ---- geração de jogadas -----------------------------------------------------

def _card_from_hand(state: GameState, card_id: str) -> Card | None:
    for card in state.hand(state.current):
        if card.id == card_id:
            return card
    return None


def destinations(state: GameState, card: Card, origin: Pos) -> list[Pos]:
    """Casas de destino legais para a peça em ``origin`` usando ``card``."""
    piece = state.piece_at(origin)
    if piece is None:
        return []
    result = []
    for dx, dy in card.deltas_for(piece.owner):
        dest = origin.shifted(dx, dy)
        if not dest.on_board():
            continue
        target = state.piece_at(dest)
        if target is not None and target.owner is piece.owner:
            continue
        result.append(dest)
    return result


def board_moves(state: GameState, player: Player | None = None) -> list[Move]:
    """Todos os movimentos de peça (sem passes) para o jogador."""
    player = player or state.current
    moves: list[Move] = []
    for card in state.hand(player):
        for origin, _ in state.pieces(player):
            for dest in destinations(state, card, origin):
                moves.append(Move(card.id, origin, dest))
    return moves


def legal_moves(state: GameState) -> list[Move]:
    """Ações legais do jogador da vez.

    Zugzwang: havendo movimento, ele é obrigatório. Só sem nenhum movimento
    o jogador passa — escolhendo qual das duas cartas troca.
    """
    if state.is_over:
        return []
    moves = board_moves(state)
    if moves:
        return moves
    return [Move(card.id) for card in state.hand(state.current)]


def attacked_squares(state: GameState, by: Player) -> set[Pos]:
    """Casas que ``by`` pode atingir com a mão atual (para destacar ameaças)."""
    return {m.destination for m in board_moves(state, by) if m.destination is not None}


def is_master_threatened(state: GameState, player: Player) -> bool:
    master = state.master_pos(player)
    return master is not None and master in attacked_squares(state, player.opponent)


# ---- aplicação --------------------------------------------------------------

def validate(state: GameState, move: Move, player: Player | None = None) -> Card:
    """Valida a jogada e devolve a carta usada; lança ``IllegalMoveError``."""
    if state.is_over:
        raise IllegalMoveError("game_over", "A partida já terminou")
    if player is not None and player is not state.current:
        raise IllegalMoveError("not_your_turn", "Não é o seu turno")
    card = _card_from_hand(state, move.card_id)
    if card is None:
        raise IllegalMoveError("card_not_in_hand", f"A carta {move.card_id} não está na sua mão")
    if move.is_pass:
        if move.destination is not None:
            raise IllegalMoveError("malformed", "Passe não tem destino")
        if board_moves(state):
            raise IllegalMoveError("must_move", "Há movimento legal: passar não é permitido")
        return card
    if move.destination is None:
        raise IllegalMoveError("malformed", "Movimento sem destino")
    if not move.origin.on_board() or not move.destination.on_board():
        raise IllegalMoveError("off_board", "Coordenada fora do tabuleiro")
    piece = state.piece_at(move.origin)
    if piece is None:
        raise IllegalMoveError("no_piece", f"Não há peça em {move.origin}")
    if piece.owner is not state.current:
        raise IllegalMoveError("not_your_piece", f"A peça em {move.origin} não é sua")
    if move.destination not in destinations(state, card, move.origin):
        raise IllegalMoveError(
            "illegal_destination",
            f"{card.name_en} não leva {move.origin} a {move.destination}",
        )
    return card


def apply_move(state: GameState, move: Move, player: Player | None = None) -> tuple[GameState, MoveRecord]:
    """Executa a jogada (após validar) e devolve o novo estado e o registro do turno."""
    card = validate(state, move, player)
    mover = state.current
    cells = list(state.cells)
    piece: Piece | None = None
    captured: Piece | None = None
    winner: Player | None = None
    reason: WinReason | None = None

    if not move.is_pass:
        piece = cells[move.origin.index]
        captured = cells[move.destination.index]
        cells[move.origin.index] = None
        cells[move.destination.index] = piece
        if captured is not None and captured.is_master:
            winner, reason = mover, WinReason.WAY_OF_THE_STONE
        elif piece.is_master and move.destination == TEMPLE_ARCH[mover.opponent]:
            winner, reason = mover, WinReason.WAY_OF_THE_STREAM

    # Troca: a carta usada vai para a lateral; a lateral entra no lugar dela.
    hand = state.hand(mover)
    new_hand = tuple(state.side_card if c.id == card.id else c for c in hand)
    hands = list(state.hands)
    hands[mover.index] = new_hand  # type: ignore[assignment]

    new_state = replace(
        state,
        cells=tuple(cells),
        hands=tuple(hands),  # type: ignore[arg-type]
        side_card=card,
        current=mover.opponent,
        turn=state.turn + 1,
        status=GameStatus.FINISHED if winner else GameStatus.IN_PROGRESS,
        winner=winner,
        win_reason=reason,
    )
    record = MoveRecord(
        turn=state.turn + 1,
        player=mover,
        move=move,
        piece=piece,
        captured=captured,
        card_received=state.side_card.id,
        winner=winner,
        win_reason=reason,
    )
    return new_state, record


def resign(state: GameState, player: Player) -> GameState:
    """Abandono (regra da plataforma, não do manual): o adversário vence."""
    if state.is_over:
        raise IllegalMoveError("game_over", "A partida já terminou")
    return replace(
        state,
        status=GameStatus.FINISHED,
        winner=player.opponent,
        win_reason=WinReason.RESIGNATION,
    )


def play_all(state: GameState, moves: Iterable[Move]) -> tuple[GameState, list[MoveRecord]]:
    records = []
    for move in moves:
        state, rec = apply_move(state, move)
        records.append(rec)
    return state, records
