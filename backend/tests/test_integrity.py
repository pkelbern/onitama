"""Partidas aleatórias completas: invariantes, serialização e replay."""
import random

import pytest

from game_engine import IllegalMoveError, Move, Pos, apply_move, build_replay, legal_moves, new_game
from game_engine.rules import board_moves
from game_engine.serialization import move_from_dict, move_to_dict, state_from_dict, state_to_dict

ALL_SQUARES = [Pos(x, y) for x in range(5) for y in range(5)]


def random_game(base_cards, seed, max_turns=300):
    rng = random.Random(seed)
    state = new_game(base_cards, seed=seed)
    initial, moves = state, []
    while not state.is_over and len(moves) < max_turns:
        move = rng.choice(legal_moves(state))
        state, _ = apply_move(state, move)
        moves.append(move)
    return initial, moves, state


@pytest.mark.parametrize("seed", range(200))
def test_random_games_keep_invariants(base_cards, seed):
    rng = random.Random(seed)
    state = new_game(base_cards, seed=seed)
    card_ids = {c.id for c in state.all_cards()}
    count = 10
    while not state.is_over and state.turn < 300:
        legal = legal_moves(state)
        assert legal, "jogo em andamento deve ter ação legal"
        # Rejeição: qualquer jogada fora da lista legal deve ser recusada.
        hand_ids = [c.id for c in state.hand(state.current)]
        for _ in range(5):
            bogus = Move(rng.choice(hand_ids), rng.choice(ALL_SQUARES), rng.choice(ALL_SQUARES))
            if bogus not in legal:
                with pytest.raises(IllegalMoveError):
                    apply_move(state, bogus)
        state, rec = apply_move(state, rng.choice(legal))
        assert {c.id for c in state.all_cards()} == card_ids  # 5 cartas conservadas
        new_count = sum(p is not None for p in state.cells)
        assert new_count == count - (1 if rec.captured else 0)
        count = new_count
        masters = [p for p in state.cells if p is not None and p.is_master]
        assert len(masters) == (1 if state.win_reason and state.win_reason.value == "way_of_the_stone" else 2)


@pytest.mark.parametrize("seed", range(30))
def test_serialization_roundtrip(base_cards, registry, seed):
    initial, moves, final = random_game(base_cards, seed)
    for s in (initial, final):
        assert state_from_dict(state_to_dict(s), registry) == s
    for m in moves:
        assert move_from_dict(move_to_dict(m)) == m


@pytest.mark.parametrize("seed", range(30))
def test_replay_reconstructs_final_state(base_cards, seed):
    initial, moves, final = random_game(base_cards, seed)
    replay = build_replay(initial, moves)
    assert replay.final == final
    assert len(replay.states) == len(moves) + 1
    assert replay.at(0) == initial


def test_replay_rejects_tampered_history(base_cards):
    initial, moves, _ = random_game(base_cards, 3)
    tampered = [Move(moves[0].card_id, Pos(0, 0), Pos(4, 4)), *moves[1:]]
    with pytest.raises(IllegalMoveError):
        build_replay(initial, tampered)


def test_legal_moves_never_land_on_own_piece(base_cards):
    for seed in range(50):
        _, _, state = random_game(base_cards, seed, max_turns=20)
        for m in board_moves(state):
            target = state.piece_at(m.destination)
            assert target is None or target.owner is not state.current
