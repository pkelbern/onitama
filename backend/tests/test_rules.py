import pytest

from game_engine import (
    TEMPLE_ARCH,
    GameStatus,
    IllegalMoveError,
    Move,
    PieceType,
    Player,
    Pos,
    WinReason,
    apply_move,
    destinations,
    is_master_threatened,
    legal_moves,
    new_game,
    resign,
    setup_game,
)
from game_engine.rules import GameState

from .conftest import layout
from .test_cards import EXPECTED_BASE

P = Pos.parse


def game(card, red=("tiger", "crab"), blue=("monkey", "crane"), side="ox", cells=None):
    return setup_game(
        (card(red[0]), card(red[1])), (card(blue[0]), card(blue[1])), card(side), cells
    )


# ---- preparação ---------------------------------------------------------------

def test_initial_position(card):
    s = game(card)
    for player, row in ((Player.RED, 0), (Player.BLUE, 4)):
        pieces = dict(s.pieces(player))
        assert set(pieces) == {Pos(x, row) for x in range(5)}
        assert pieces[TEMPLE_ARCH[player]].kind is PieceType.MASTER
        assert sum(p.kind is PieceType.STUDENT for p in pieces.values()) == 4
    assert sum(p is not None for p in s.cells) == 10


@pytest.mark.parametrize("side,first", [("ox", Player.BLUE), ("dragon", Player.RED)])
def test_first_player_is_side_card_stamp(card, side, first):
    s = game(card, red=("tiger", "crab"), blue=("monkey", "crane"), side=side)
    assert s.current is first and s.first_player is first


def test_new_game_deals_five_distinct_cards(base_cards):
    for seed in range(50):
        s = new_game(base_cards, seed=seed)
        ids = [c.id for c in s.all_cards()]
        assert len(set(ids)) == 5
        assert s.current is s.side_card.stamp


def test_new_game_is_deterministic_with_seed(base_cards):
    assert new_game(base_cards, seed=7) == new_game(base_cards, seed=7)


def test_setup_rejects_unvalidated_cards(card):
    with pytest.raises(ValueError):
        game(card, side="kirin")


# ---- movimentos de todas as cartas -------------------------------------------

@pytest.mark.parametrize("card_id", sorted(EXPECTED_BASE))
@pytest.mark.parametrize("player", list(Player))
def test_every_card_from_center(card, card_id, player):
    """Peça sozinha no centro: destinos = diagrama (girado para o azul)."""
    other = [cid for cid in EXPECTED_BASE if cid != card_id][:4]
    cells = layout(c3="R" if player is Player.RED else "B",
                   a1="b" if player is Player.RED else "r")
    s = setup_game((card(other[0]), card(other[1])), (card(other[2]), card(other[3])),
                   card(card_id), cells)
    o = player.orientation
    expected = {Pos(2 + dx * o, 2 + dy * o) for dx, dy in EXPECTED_BASE[card_id]}
    assert set(destinations(s, card(card_id), P("c3"))) == expected


def test_cannot_leave_board(card):
    s = game(card, red=("crab", "tiger"), cells=layout(a1="R", e5="B"))
    assert set(destinations(s, card("crab"), P("a1"))) == {P("c1"), P("a2")}


def test_cannot_land_on_own_piece_but_can_jump(card):
    cells = layout(c1="R", c2="r", c3="r", e5="B")
    s = game(card, cells=cells)
    assert destinations(s, card("tiger"), P("c1")) == []
    cells = layout(c1="R", c2="r", e5="B")
    s = game(card, cells=cells)
    assert destinations(s, card("tiger"), P("c1")) == [P("c3")]  # salta sobre c2


# ---- capturas e vitória -------------------------------------------------------

def test_capture_student(card):
    s = game(card, side="dragon", cells=layout(c1="R", c3="b", e5="B"))
    s2, rec = apply_move(s, Move("tiger", P("c1"), P("c3")))
    assert rec.captured.kind is PieceType.STUDENT
    assert s2.piece_at(P("c3")).owner is Player.RED
    assert len(s2.pieces(Player.BLUE)) == 1
    assert not s2.is_over


def test_capture_master_way_of_the_stone(card):
    s = game(card, side="dragon", cells=layout(a1="r", c1="R", c3="B"))
    s2, rec = apply_move(s, Move("tiger", P("c1"), P("c3")))
    assert s2.status is GameStatus.FINISHED
    assert s2.winner is Player.RED and s2.win_reason is WinReason.WAY_OF_THE_STONE
    assert rec.win_reason is WinReason.WAY_OF_THE_STONE


def test_student_capturing_master_also_wins(card):
    s = game(card, side="dragon", cells=layout(a1="R", c1="r", c3="B"))
    s2, _ = apply_move(s, Move("tiger", P("c1"), P("c3")))
    assert s2.winner is Player.RED and s2.win_reason is WinReason.WAY_OF_THE_STONE


def test_way_of_the_stream(card):
    s = game(card, side="dragon", cells=layout(c3="R", a5="B"))
    s2, _ = apply_move(s, Move("tiger", P("c3"), P("c5")))
    assert s2.winner is Player.RED and s2.win_reason is WinReason.WAY_OF_THE_STREAM


def test_blue_way_of_the_stream(card):
    s = game(card, red=("crab", "boar"), blue=("tiger", "eel"), side="ox",
             cells=layout(c3="B", e1="R"))
    s2, _ = apply_move(s, Move("tiger", P("c3"), P("c1")))  # azul: "frente" = y−
    assert s2.winner is Player.BLUE and s2.win_reason is WinReason.WAY_OF_THE_STREAM


def test_student_on_temple_arch_does_not_win(card):
    s = game(card, side="dragon", cells=layout(c3="r", a1="R", a5="B"))
    s2, _ = apply_move(s, Move("tiger", P("c3"), P("c5")))
    assert not s2.is_over


def test_master_on_own_arch_does_not_win(card):
    s = game(card, side="dragon", cells=layout(c2="R", a5="B"))
    s2, _ = apply_move(s, Move("tiger", P("c2"), P("c1")))
    assert not s2.is_over


def test_no_moves_after_game_over(card):
    s = game(card, side="dragon", cells=layout(c3="R", a5="B"))
    s2, _ = apply_move(s, Move("tiger", P("c3"), P("c5")))
    assert legal_moves(s2) == []
    with pytest.raises(IllegalMoveError) as e:
        apply_move(s2, Move("monkey", P("a5"), P("b4")))
    assert e.value.code == "game_over"


# ---- troca de cartas ----------------------------------------------------------

def test_card_exchange(card):
    s = game(card, side="dragon")  # vermelho começa com tiger, crab; lateral dragon
    s2, rec = apply_move(s, Move("tiger", P("c1"), P("c3")))
    assert [c.id for c in s2.hand(Player.RED)] == ["dragon", "crab"]
    assert s2.side_card.id == "tiger"
    assert [c.id for c in s2.hand(Player.BLUE)] == ["monkey", "crane"]
    assert rec.card_received == "dragon"
    assert s2.current is Player.BLUE and s2.turn == 1
    # Azul joga; a carta que o vermelho usou (tiger) entra na mão do azul.
    s3, _ = apply_move(s2, Move("monkey", P("b5"), P("a4")))
    assert {c.id for c in s3.hand(Player.BLUE)} == {"tiger", "crane"}
    assert s3.side_card.id == "monkey"


# ---- jogadas inválidas --------------------------------------------------------

@pytest.mark.parametrize(
    "move,code",
    [
        (Move("monkey", P("a1"), P("b2")), "card_not_in_hand"),
        (Move("tiger", P("c3"), P("c5")), "no_piece"),
        (Move("tiger", P("c5"), P("c3")), "not_your_piece"),
        (Move("tiger", P("c1"), P("c2")), "illegal_destination"),
        (Move("crab", P("a1"), P("b1")), "illegal_destination"),
        (Move("tiger"), "must_move"),
    ],
)
def test_invalid_moves_rejected(card, move, code):
    s = game(card, side="dragon")
    with pytest.raises(IllegalMoveError) as e:
        apply_move(s, move)
    assert e.value.code == code


def test_not_your_turn(card):
    s = game(card, side="dragon")
    with pytest.raises(IllegalMoveError) as e:
        apply_move(s, Move("tiger", P("c1"), P("c3")), player=Player.BLUE)
    assert e.value.code == "not_your_turn"


def test_state_is_immutable(card):
    s = game(card, side="dragon")
    before = s.cells
    apply_move(s, Move("tiger", P("c1"), P("c3")))
    assert s.cells == before


# ---- sem movimentos possíveis -------------------------------------------------

def _stuck_state(card) -> GameState:
    # Vermelho preenche a fileira 5 (topo); Elefante e Caranguejo não têm movimento
    # para trás: todo destino sai do tabuleiro ou cai sobre peça própria.
    cells = layout(a5="R", b5="r", c5="r", d5="r", e5="r", c1="B")
    return game(card, red=("elephant", "crab"), blue=("monkey", "crane"),
                side="dragon", cells=cells)


def test_pass_only_when_no_legal_move(card):
    s = _stuck_state(card)
    moves = legal_moves(s)
    assert all(m.is_pass for m in moves)
    assert {m.card_id for m in moves} == {"elephant", "crab"}


def test_pass_still_exchanges_card(card):
    s = _stuck_state(card)
    s2, rec = apply_move(s, Move("crab"))
    assert rec.piece is None and rec.captured is None
    assert s2.cells == s.cells
    assert [c.id for c in s2.hand(Player.RED)] == ["elephant", "dragon"]
    assert s2.side_card.id == "crab"
    assert s2.current is Player.BLUE


# ---- ameaça e abandono --------------------------------------------------------

def test_master_threat_detection(card):
    # Azul tem Tiger: do c5, ataca c3 (2 casas à frente dele = y−2).
    s = game(card, red=("crab", "boar"), blue=("tiger", "eel"), side="dragon",
             cells=layout(c3="R", c5="B"))
    assert is_master_threatened(s, Player.RED)
    assert not is_master_threatened(s, Player.BLUE)


def test_resign(card):
    s = game(card, side="dragon")
    s2 = resign(s, Player.RED)
    assert s2.winner is Player.BLUE and s2.win_reason is WinReason.RESIGNATION
