"""Cada carta dos dados versionados precisa ter sua arte gerada."""
import json
from pathlib import Path

from game_engine import CardRegistry

ART = Path(__file__).resolve().parents[2] / "frontend" / "src" / "assets" / "cards"


def test_every_card_has_art():
    manifest = {m["id"] for m in json.loads((ART / "manifest.json").read_text())}
    ids = {c.id for c in CardRegistry.default().all()}
    assert ids == manifest
    for cid in ids:
        assert (ART / f"{cid}.svg").read_text().startswith("<svg")
