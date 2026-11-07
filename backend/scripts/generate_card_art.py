"""Gera a arte das cartas (SVG) a partir dos dados versionados em game_engine/data/cards.

Arte original do projeto: papel washi, diagrama 5x5, ideograma em pincel e selo
(hanko) com a cor de quem começa. Todo texto é convertido em contornos, então
os SVGs não dependem de fontes instaladas.

Fontes (SIL Open Font License, Google Fonts):
    Yuji Syuku (pincel)  e  Shippori Mincho (serifa)
    curl -LO https://raw.githubusercontent.com/google/fonts/main/ofl/yujisyuku/YujiSyuku-Regular.ttf
    curl -LO https://raw.githubusercontent.com/google/fonts/main/ofl/shipporimincho/ShipporiMincho-Bold.ttf
    curl -LO https://raw.githubusercontent.com/google/fonts/main/ofl/shipporimincho/ShipporiMincho-Regular.ttf

Uso:
    python scripts/generate_card_art.py --fonts DIR --out ../frontend/src/assets/cards
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

DATA = Path(__file__).resolve().parents[1] / "game_engine" / "data" / "cards"

W, H = 640, 360
INK = "#1f1b17"
PAPER = "#f3ead8"
CELL = "#e9dec6"
CELL_LINE = "#b8a684"
ACCENT = {"red": "#b3352c", "blue": "#2d4f7d", None: "#857c70"}
ACCENT_SOFT = {"red": "#e7c2b6", "blue": "#c3cfdd", None: "#d6cfc3"}
EXPANSION_LABEL = {"base": "ONITAMA · JOGO-BASE", "senseis_path": "SENSEI'S PATH"}


class Typeface:
    def __init__(self, path: Path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def advance(self, ch: str, size: float) -> float:
        return self.hmtx[self.cmap[ord(ch)]][0] * size / self.upm

    def width(self, text: str, size: float, tracking: float = 0) -> float:
        return sum(self.advance(c, size) for c in text) + tracking * max(len(text) - 1, 0)

    def path(self, text: str, size: float, x: float, baseline: float,
             anchor: str = "start", tracking: float = 0) -> str:
        """Texto horizontal convertido em <path d>."""
        w = self.width(text, size, tracking)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        s = size / self.upm
        d = []
        for ch in text:
            name = self.cmap[ord(ch)]
            pen = SVGPathPen(self.glyphs)
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x0, baseline)))
            d.append(pen.getCommands())
            x0 += self.advance(ch, size) + tracking
        return " ".join(d)

    def glyph_box(self, ch: str, size: float, cx: float, cy: float) -> str:
        """Um ideograma centralizado (pela caixa do glifo) em (cx, cy)."""
        from fontTools.pens.boundsPen import BoundsPen
        name = self.cmap[ord(ch)]
        bp = BoundsPen(self.glyphs)
        self.glyphs[name].draw(bp)
        xmin, ymin, xmax, ymax = bp.bounds
        s = size / self.upm
        tx = cx - (xmin + xmax) / 2 * s
        ty = cy + (ymin + ymax) / 2 * s
        pen = SVGPathPen(self.glyphs)
        self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, tx, ty)))
        return pen.getCommands()


def fit(face: Typeface, text: str, size: float, max_w: float, tracking: float = 0) -> float:
    w = face.width(text, size, tracking)
    return size if w <= max_w else size * max_w / w


def render_card(card: dict, expansion: str, pending: bool, fonts: dict[str, Typeface]) -> str:
    stamp = card.get("stamp")
    accent, soft = ACCENT[stamp], ACCENT_SOFT[stamp]
    brush, serif, serif_r = fonts["brush"], fonts["serif"], fonts["serif_r"]
    out: list[str] = []
    add = out.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Carta {card["name_pt"]} ({card["name_en"]})">')
    add(f'<title>{card["name_pt"]} — {card["name_en"]}</title>')
    add('<defs>'
        '<filter id="washi" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7" result="n"/>'
        '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.28  0 0 0 0.10 0"/>'
        '</filter>'
        '<filter id="fibers" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="turbulence" baseFrequency="0.012 0.18" numOctaves="2" seed="3" result="f"/>'
        '<feColorMatrix in="f" type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.47  0 0 0 0 0.35  0 0 0 0.07 0"/>'
        '</filter>'
        '</defs>')

    # Papel e moldura
    add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="{PAPER}" stroke="#cdbf9f" stroke-width="2"/>')
    add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" filter="url(#washi)"/>')
    add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" filter="url(#fibers)"/>')
    add(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" rx="12" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    add(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" rx="8" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.6"/>')
    for cx, cy, sx, sy in ((20, 20, 1, 1), (W-20, 20, -1, 1), (20, H-20, 1, -1), (W-20, H-20, -1, -1)):
        add(f'<path d="M{cx+8*sx} {cy+26*sy} V{cy+8*sy} H{cx+26*sx}" fill="none" stroke="{accent}" stroke-width="2.4"/>')

    # Diagrama 5x5
    cell, gx, gy = 46, 44, 66
    deltas = {tuple(m) for m in card["moves"]}
    add(f'<rect x="{gx-6}" y="{gy-6}" width="{cell*5+12}" height="{cell*5+12}" rx="6" fill="#efe5cf" stroke="{INK}" stroke-width="1.4"/>')
    for row in range(5):
        for col in range(5):
            dx, dy = col - 2, 2 - row
            x, y = gx + col * cell, gy + row * cell
            if (dx, dy) == (0, 0):
                fill = INK
            elif (dx, dy) in deltas:
                fill = accent
            else:
                fill = CELL
            add(f'<rect x="{x+2}" y="{y+2}" width="{cell-4}" height="{cell-4}" rx="4" fill="{fill}" '
                f'stroke="{CELL_LINE if fill == CELL else "none"}" stroke-width="0.8"/>')
            if (dx, dy) in deltas:
                add(f'<circle cx="{x+cell/2}" cy="{y+cell/2}" r="5" fill="{PAPER}" opacity="0.85"/>')
            if (dx, dy) == (0, 0):
                add(f'<path d="{brush.glyph_box("人", 26, x+cell/2, y+cell/2)}" fill="{PAPER}"/>')
    # Indicação de "frente"
    fx = gx + cell * 2.5
    add(f'<path d="M{fx-9} {gy-14} L{fx} {gy-26} L{fx+9} {gy-14} Z" fill="{INK}"/>')
    add(f'<path d="{serif_r.path("FRENTE", 10, fx + 16, gy - 15, tracking=2.4)}" fill="{INK}" opacity="0.7"/>')
    add(f'<path d="{serif_r.path("前", 13, fx - 16, gy - 14, anchor="end")}" fill="{INK}" opacity="0.7"/>')

    # Rótulo da expansão
    label = EXPANSION_LABEL.get(expansion, expansion.upper())
    add(f'<path d="{serif_r.path(label, 10.5, gx + cell*2.5, H - 30, anchor="middle", tracking=2.2)}" fill="{INK}" opacity="0.65"/>')

    # Divisória em pincel
    add(f'<path d="M318 44 C 321 120, 315 240, 319 316" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" opacity="0.8"/>')
    add(f'<path d="M323 60 C 325 150, 321 230, 324 300" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.4"/>')

    # Ensō e ideograma
    ex, ey = 400, 182
    add(f'<circle cx="{ex}" cy="{ey}" r="86" fill="none" stroke="{accent}" stroke-width="12" '
        f'stroke-linecap="round" stroke-dasharray="470 70" transform="rotate(-62 {ex} {ey})" opacity="0.16"/>')
    add(f'<circle cx="{ex}" cy="{ey}" r="86" fill="none" stroke="{accent}" stroke-width="4" '
        f'stroke-dasharray="430 110" transform="rotate(-58 {ex} {ey})" opacity="0.22"/>')
    glyph = card["glyph"]
    n = len(glyph)
    size = {1: 136, 2: 100, 3: 72, 4: 54}[n]
    step = size * 0.98
    top = ey - step * (n - 1) / 2
    for i, ch in enumerate(glyph):
        add(f'<path d="{brush.glyph_box(ch, size, ex, top + i*step)}" fill="{INK}"/>')

    # Nomes
    nx, max_w = 556, 104
    en = card["name_en"].upper()
    s_en = fit(serif, en, 24, max_w, tracking=3)
    add(f'<path d="{serif.path(en, s_en, nx, 168, anchor="middle", tracking=3)}" fill="{INK}"/>')
    add(f'<rect x="{nx-26}" y="181" width="52" height="1.6" fill="{accent}"/>')
    s_pt = fit(serif_r, card["name_pt"], 17, max_w)
    add(f'<path d="{serif_r.path(card["name_pt"], s_pt, nx, 207, anchor="middle")}" fill="{INK}" opacity="0.85"/>')

    # Selo (hanko) — cor de quem começa
    hx, hy = 552, 280
    add(f'<g transform="rotate(-5 {hx} {hy})">'
        f'<rect x="{hx-24}" y="{hy-24}" width="48" height="48" rx="7" fill="{accent}"/>'
        f'<rect x="{hx-19}" y="{hy-19}" width="38" height="38" rx="4" fill="none" stroke="{PAPER}" stroke-width="1.6"/>'
        f'<path d="{brush.glyph_box("?" if stamp is None else "先", 28, hx, hy)}" fill="{PAPER}"/></g>')

    if pending:
        add(f'<rect x="336" y="30" width="268" height="24" rx="3" fill="{INK}" opacity="0.85"/>')
        add(f'<path d="{serif.path("PRÉVIA · AGUARDA VALIDAÇÃO", 10.5, 470, 46, anchor="middle", tracking=2.6)}" fill="{PAPER}"/>')
        add(f'<rect x="{gx-6}" y="{gy-6}" width="{cell*5+12}" height="{cell*5+12}" rx="6" fill="none" '
            f'stroke="{accent}" stroke-width="2" stroke-dasharray="6 5"/>')

    add('</svg>')
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    fonts = {
        "brush": Typeface(args.fonts / "YujiSyuku-Regular.ttf"),
        "serif": Typeface(args.fonts / "ShipporiMincho-Bold.ttf"),
        "serif_r": Typeface(args.fonts / "ShipporiMincho-Regular.ttf"),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for data_file in sorted(DATA.glob("*.json")):
        data = json.loads(data_file.read_text(encoding="utf-8"))
        pending = data["status"] != "official"
        for card in data["cards"]:
            svg = render_card(card, data["expansion"], pending, fonts)
            (args.out / f'{card["id"]}.svg').write_text(svg, encoding="utf-8")
            manifest.append({"id": card["id"], "expansion": data["expansion"],
                             "image": f'assets/cards/{card["id"]}.svg', "pending": pending})
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(manifest)} cartas geradas em {args.out}")


if __name__ == "__main__":
    main()
