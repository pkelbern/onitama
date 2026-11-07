import pytest

from game_engine import CardStatus, Player, describe_move, load_expansion

# Gabarito independente do JSON: diagramas do manual (perspectiva do dono).
EXPECTED_BASE = {
    "tiger": {(0, 2), (0, -1)},
    "crab": {(-2, 0), (2, 0), (0, 1)},
    "monkey": {(-1, 1), (1, 1), (-1, -1), (1, -1)},
    "crane": {(0, 1), (-1, -1), (1, -1)},
    "dragon": {(-2, 1), (2, 1), (-1, -1), (1, -1)},
    "elephant": {(-1, 1), (1, 1), (-1, 0), (1, 0)},
    "mantis": {(-1, 1), (1, 1), (0, -1)},
    "boar": {(-1, 0), (1, 0), (0, 1)},
    "frog": {(-2, 0), (-1, 1), (1, -1)},
    "goose": {(-1, 0), (-1, 1), (1, 0), (1, -1)},
    "horse": {(-1, 0), (0, 1), (0, -1)},
    "eel": {(-1, 1), (-1, -1), (1, 0)},
    "rabbit": {(2, 0), (1, 1), (-1, -1)},
    "rooster": {(1, 0), (1, 1), (-1, 0), (-1, -1)},
    "ox": {(1, 0), (0, 1), (0, -1)},
    "cobra": {(-1, 0), (1, 1), (1, -1)},
}
MIRROR_PAIRS = [("frog", "rabbit"), ("goose", "rooster"), ("horse", "ox"), ("eel", "cobra")]


def test_base_has_exactly_16_official_cards(base_cards):
    assert len(base_cards) == 16
    assert {c.id for c in base_cards} == set(EXPECTED_BASE)
    assert all(c.status is CardStatus.OFFICIAL and c.playable for c in base_cards)


def test_stamps_are_balanced(base_cards):
    reds = [c for c in base_cards if c.stamp is Player.RED]
    assert len(reds) == 8


@pytest.mark.parametrize("card_id", sorted(EXPECTED_BASE))
def test_card_moves_match_manual(card, card_id):
    assert set(card(card_id).moves) == EXPECTED_BASE[card_id]


@pytest.mark.parametrize("left,right", MIRROR_PAIRS)
def test_mirror_pairs(card, left, right):
    assert {(-dx, dy) for dx, dy in card(left).moves} == set(card(right).moves)


@pytest.mark.parametrize("card_id", sorted(EXPECTED_BASE))
def test_blue_orientation_is_rotated_180(card, card_id):
    c = card(card_id)
    assert c.deltas_for(Player.RED) == c.moves
    assert c.deltas_for(Player.BLUE) == tuple((-dx, -dy) for dx, dy in c.moves)


def test_senseis_path_is_blocked_until_validated():
    cards = load_expansion("senseis_path")
    assert len(cards) == 16
    assert all(not c.playable for c in cards)


def test_describe_move():
    assert describe_move(0, 2) == "2 para frente"
    assert describe_move(-1, -1) == "1 para trás e 1 para a esquerda"
