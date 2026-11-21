#!/usr/bin/env python3
"""news-image-20261120: draw one image summing up Friday 20 November 2026.

Pure Python 3.13 standard library. No network, no randomness, no clock:
both runs write byte-identical PNGs to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png).

Design: a newspaper front page. Masthead with the date, one lead story,
then a grid of the day's other big stories, each with a small drawn icon,
a headline and one line of summary, plus a bottom ticker of further news.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024


# ---------------------------------------------------------------- PNG output
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, width, height, rgb):
    """rgb: bytes of width*height*3. Deterministic: fixed zlib level."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(
        b"\x00" + rgb[y * width * 3:(y + 1) * width * 3]
        for y in range(height)
    )
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows, each a 5-bit int, bit 4 = leftmost pixel.
# Uppercase, digits and the punctuation the headlines need.
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "+": (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    "=": (0, 0, 0b11111, 0, 0b11111, 0, 0),
}

CHAR_ADVANCE = 6  # 5 px glyph + 1 px gap, times the scale


def text_width(text, scale):
    return len(text) * CHAR_ADVANCE * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(yy * self.w + x1) * 3] = color * (x1 - x0)

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(-(t // 2), t // 2 + 1):
                for b in range(-(t // 2), t // 2 + 1):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, color)

    def circle(self, cx, cy, r, color, t=2):
        for rr in range(r - t + 1, r + 1):
            for ang in range(360):
                import math
                x = cx + int(rr * math.cos(ang * math.pi / 180))
                y = cy + int(rr * math.sin(ang * math.pi / 180))
                self.set(x, y, color)

    def fill_triangle(self, p1, p2, p3, color):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        x1, y1, x2, y2, x3, y3 = (int(v) for v in (x1, y1, x2, y2, x3, y3))
        ymin, ymax = min(y1, y2, y3), max(y1, y2, y3)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (xa, ya), (xb, yb) in ((p1, p2), (p2, p3), (p3, p1)):
                if ya == yb:
                    continue
                if min(ya, yb) <= yy <= max(ya, yb):
                    xs.append(xa + (xb - xa) * (yy - ya) / (yb - ya))
            if len(xs) >= 2:
                self.fill_rect(int(min(xs)), yy, int(max(xs)) - int(min(xs)) + 1, 1, color)

    def text(self, x, y, s, color, scale=2, align="left"):
        s = s.upper()
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.fill_rect(
                            x + col * scale, y + row * scale,
                            scale, scale, color,
                        )
            x += CHAR_ADVANCE * scale
        return x

    def text_block(self, x, y, s, color, scale, max_width, leading=None):
        """Wrapped, left-aligned text; returns the y below the block."""
        leading = leading if leading is not None else 9 * scale
        for line in wrap_text(s, max_width, scale):
            self.text(x, y, line, color, scale)
            y += leading
        return y

    def save(self, path):
        write_png(path, self.w, self.h, bytes(self.px))


# ------------------------------------------------------------------ palette
PAPER = bytes((245, 239, 224))
WHITE = bytes((252, 250, 244))
INK = bytes((18, 18, 20))
GRAY = bytes((105, 105, 100))
RED = bytes((178, 34, 34))
NAVY = bytes((18, 38, 66))
GOLD = bytes((198, 142, 30))
TEAL = bytes((14, 110, 110))
GREEN = bytes((34, 120, 60))
BLUE = bytes((40, 90, 160))
LIGHT = bytes((232, 226, 210))
CREAM = bytes((245, 239, 224))


# -------------------------------------------------------------------- icons
# Each draws inside a square of side s with its top-left corner at (x, y).
def icon_courthouse(cv, x, y, s, ink=INK, accent=NAVY):
    u = s / 10.0
    # pediment
    cv.fill_triangle((x, y + 3 * u), (x + 10 * u, y + 3 * u), (x + 5 * u, y), accent)
    cv.fill_rect(x, int(y + 3 * u), int(10 * u), int(0.7 * u), ink)
    # columns
    for cx in (1.2, 4.2, 7.2):
        cv.fill_rect(int(x + cx * u), int(y + 4 * u), int(1.4 * u), int(4.4 * u), ink)
    # base + steps
    cv.fill_rect(x, int(y + 8.6 * u), int(10 * u), int(0.8 * u), ink)
    cv.fill_rect(int(x - 0.6 * u), int(y + 9.4 * u), int(11.2 * u), int(0.6 * u), accent)


def icon_flags(cv, x, y, s, ink=INK, accent=RED):
    u = s / 10.0
    fw, fh = 3.1 * u, 2.4 * u
    pole_h = 6.6 * u
    # pole + US flag: stripes with blue canton
    px = x
    cv.fill_rect(int(px + 1.4 * u), int(y + 0.4 * u), int(0.3 * u), int(pole_h), ink)
    for i in range(5):
        cv.fill_rect(int(px), int(y + 0.8 * u + i * fh / 5),
                     int(fw), max(1, int(fh / 5)), RED if i % 2 == 0 else WHITE)
    cv.fill_rect(int(px), int(y + 0.8 * u), int(1.3 * u), int(fh * 0.42), NAVY)
    # pole + China flag: red field, yellow stars as dots
    px = x + 3.4 * u
    cv.fill_rect(int(px + 1.4 * u), int(y + 0.4 * u), int(0.3 * u), int(pole_h), ink)
    cv.fill_rect(int(px), int(y + 0.8 * u), int(fw), int(fh), RED)
    cv.fill_circle(int(px + 0.75 * u), int(y + 1.4 * u), max(2, int(0.4 * u)), GOLD)
    cv.fill_circle(int(px + 2.2 * u), int(y + 1.1 * u), max(1, int(0.2 * u)), GOLD)
    cv.fill_circle(int(px + 2.4 * u), int(y + 1.9 * u), max(1, int(0.2 * u)), GOLD)
    # pole + Russia flag: white / blue / red bands
    px = x + 6.8 * u
    cv.fill_rect(int(px + 1.4 * u), int(y + 0.4 * u), int(0.3 * u), int(pole_h), ink)
    cv.fill_rect(int(px), int(y + 0.8 * u), int(fw), int(fh / 3), WHITE)
    cv.fill_rect(int(px), int(y + 0.8 * u + fh / 3), int(fw), int(fh / 3), BLUE)
    cv.fill_rect(int(px), int(y + 0.8 * u + 2 * fh / 3), int(fw), int(fh / 3), RED)
    cv.rect(int(px), int(y + 0.8 * u), int(fw), int(fh), ink, 1)


def icon_skyline_burst(cv, x, y, s, ink=INK, accent=RED):
    u = s / 10.0
    # buildings
    cv.fill_rect(int(x + 0.5 * u), int(y + 5 * u), int(2.4 * u), int(5 * u), ink)
    cv.fill_rect(int(x + 3.4 * u), int(y + 3.4 * u), int(2.6 * u), int(6.6 * u), NAVY)
    cv.fill_rect(int(x + 6.5 * u), int(y + 5.6 * u), int(2.4 * u), int(4.4 * u), ink)
    # windows
    for wx in (1.0, 1.9, 3.9, 4.8, 7.0, 7.9):
        for wy in (5.8, 6.9, 8.0):
            cv.fill_rect(int(x + wx * u), int(y + wy * u),
                         max(1, int(0.35 * u)), max(1, int(0.35 * u)), GOLD)
    # explosion burst top-right
    bx, by = int(x + 8.2 * u), int(y + 2.2 * u)
    cv.fill_circle(bx, by, int(1.1 * u), accent)
    for (dx, dy) in ((-2.2, -1.2), (2.2, -1.4), (-2.6, 0.8), (2.6, 0.6),
                     (-1.0, -2.4), (1.2, -2.2), (0, 2.6)):
        cv.line(bx, by, int(bx + dx * u), int(by + dy * u), accent, 2)


def icon_tower(cv, x, y, s, ink=INK, accent=RED):
    u = s / 10.0
    # skyscraper with setbacks
    cv.fill_rect(int(x + 3.4 * u), int(y + 1.2 * u), int(3.2 * u), int(8.8 * u), NAVY)
    cv.fill_rect(int(x + 2.6 * u), int(y + 4 * u), int(4.8 * u), int(6 * u), NAVY)
    cv.fill_rect(int(x + 1.8 * u), int(y + 7 * u), int(6.4 * u), int(3 * u), ink)
    for wy in range(6):
        for wx in (3.8, 5.0, 6.2):
            cv.fill_rect(int(x + wx * u), int(y + (2.0 + wy * 1.1) * u),
                         max(1, int(0.4 * u)), max(1, int(0.4 * u)), GOLD)
    # impact burst at the top
    bx, by = int(x + 5 * u), int(y + 1.0 * u)
    cv.fill_circle(bx, by, int(0.9 * u), accent)
    for (dx, dy) in ((-2.4, -1.0), (2.4, -1.2), (-2.0, 1.4), (2.2, 1.2), (0, -2.4)):
        cv.line(bx, by, int(bx + dx * u), int(by + dy * u), accent, 2)


def icon_chart_down(cv, x, y, s, ink=INK, accent=RED):
    u = s / 10.0
    # axes
    cv.fill_rect(int(x + 1 * u), int(y + 1 * u), int(0.5 * u), int(8 * u), ink)
    cv.fill_rect(int(x + 1 * u), int(y + 8.5 * u), int(8 * u), int(0.5 * u), ink)
    # falling line with arrowhead
    pts = [(1.5, 2.0), (3.2, 3.2), (4.6, 2.8), (6.2, 5.2), (7.8, 6.8), (9.0, 8.2)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(int(x + ax * u), int(y + ay * u), int(x + bx * u), int(y + by * u), accent, 3)
    ex, ey = int(x + 9.0 * u), int(y + 8.2 * u)
    cv.fill_triangle((ex, ey), (ex - int(1.2 * u), ey - int(0.2 * u)),
                     (ex - int(0.2 * u), ey - int(1.2 * u)), accent)


def icon_globe_leaf(cv, x, y, s, ink=INK, accent=GREEN):
    u = s / 10.0
    cx, cy, r = int(x + 4.6 * u), int(y + 4.8 * u), int(3.6 * u)
    cv.circle(cx, cy, r, ink, 2)
    cv.line(cx - r, cy, cx + r, cy, ink, 1)
    cv.line(cx, cy - r, cx, cy + r, ink, 1)
    # leaf at lower right
    lx, ly = int(x + 7.2 * u), int(y + 7.6 * u)
    cv.fill_triangle((lx, ly - int(1.6 * u)), (lx + int(1.8 * u), ly),
                     (lx, ly + int(1.4 * u)), accent)
    cv.fill_triangle((lx, ly - int(1.6 * u)), (lx - int(1.4 * u), ly + int(0.4 * u)),
                     (lx, ly + int(1.4 * u)), accent)
    cv.line(lx, ly + int(1.4 * u), lx - int(1.2 * u), ly + int(2.4 * u), accent, 2)


def story_panel(cv, x, y, w, h, tag, tag_color, headline, summary,
                icon=None, icon_size=72, head_scale=2, sum_scale=2):
    """One white news panel: coloured tag bar, icon, headline, summary."""
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 26, tag_color)
    cv.text(x + 10, y + 6, tag, WHITE, 2)
    inner = x + 12
    content_w = w - 24
    cy = y + 36
    if icon is not None:
        icon(cv, x + (w - icon_size) // 2, cy, icon_size)
        cy += icon_size + 8
    cy = cv.text_block(inner, cy, headline, INK, head_scale, content_w, 9 * head_scale + 4)
    cv.text_block(inner, cy + 4, summary, GRAY, sum_scale, content_w, 9 * sum_scale + 2)
    return cy


# ------------------------------------------------------------------ stories
# All six stories verified against real reporting of 20 November 2026
# (ICJ ruling, Shenzhen declaration, Kyiv strikes, Riyadh strike, market
# slide, COP31 draft) plus the day's further news in the ticker.
LEAD = {
    "tag": "JUSTICE - THE HAGUE",
    "headline": "WORLD COURT: MYANMAR GUILTY OF GENOCIDE",
    "summary": ("ICJ RULES 9-6 THAT MYANMAR COMMITTED GENOCIDE AGAINST THE "
                "ROHINGYA IN THE 2017 CRACKDOWN - THE FIRST TIME ANY STATE "
                "HAS BEEN FOUND GUILTY. THE COURT ORDERED REPARATIONS; MORE "
                "THAN 730,000 ROHINGYA FLED TO BANGLADESH."),
}

ROW2 = [
    {
        "tag": "DIPLOMACY - SHENZHEN",
        "color": RED,
        "headline": "TRUMP, XI AND PUTIN SIGN PEACE DECLARATION",
        "summary": ("FOUR-POINT DECLARATION ON UN REFORM, FUEL, COURTS AND "
                    "NUCLEAR RISK - BUT NO WORD ON UKRAINE OR IRAN."),
        "icon": icon_flags,
    },
    {
        "tag": "WAR - KYIV",
        "color": NAVY,
        "headline": "KYIV HIT IN OVERNIGHT MISSILE STRIKES",
        "summary": ("RUSSIA STRIKES THREE BRIDGES OVER THE DNIPRO; DEBRIS "
                    "SETS BUILDING ABLAZE."),
        "icon": icon_skyline_burst,
    },
]

ROW3 = [
    {
        "tag": "CONFLICT - RIYADH",
        "color": RED,
        "headline": "HOUTHI MISSILE HITS RIYADH TOWER",
        "summary": "SAUDI FINANCIAL DISTRICT STRUCK; PIF TOWER DAMAGED.",
        "icon": icon_tower,
    },
    {
        "tag": "ECONOMY - MARKETS",
        "color": TEAL,
        "headline": "MARKETS SLIDE WORLDWIDE",
        "summary": "S&P 500 DOWN 2% FOR A FIFTH DAY; NIKKEI SINKS 4.8%.",
        "icon": icon_chart_down,
    },
    {
        "tag": "CLIMATE - ANTALYA",
        "color": GREEN,
        "headline": "COP31 DROPS FOSSIL-FUEL PHASE-OUT",
        "summary": "DRAFT DEAL OMITS ANY CALL TO END FOSSIL FUEL USE.",
        "icon": icon_globe_leaf,
    },
]

TICKER = [
    "ALSO TODAY: KENYA BEGINS EBOLA-FREE COUNTDOWN - CYCLONE AKVAN HITS ODISHA",
    "ISRAELI TROOPS CROSS GAZA YELLOW LINE - US SENATE PASSES ENERGY BILL 62-33",
]


# ------------------------------------------------------------------ compose
def compose():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    mx = 28
    cw = WIDTH - 2 * mx

    # Masthead
    cv.text(WIDTH // 2, 34, "THE WORLD IN ONE DAY", INK, 5, align="center")
    cv.fill_rect(mx, 82, cw, 3, INK)
    cv.fill_rect(mx, 92, cw, 38, RED)
    cv.text(WIDTH // 2, 100, "FRIDAY, 20 NOVEMBER 2026 - WORLD NEWS",
            WHITE, 3, align="center")
    cv.fill_rect(mx, 140, cw, 3, INK)

    # Lead story: icon left, headline + summary right
    lx, ly, lw, lh = mx, 156, cw, 210
    cv.fill_rect(lx, ly, lw, lh, WHITE)
    cv.rect(lx, ly, lw, lh, INK, 2)
    cv.fill_rect(lx, ly, lw, 26, NAVY)
    cv.text(lx + 10, ly + 6, LEAD["tag"], WHITE, 2)
    icon_courthouse(cv, lx + 24, ly + 52, 120)
    tx = lx + 180
    tw = lw - 180 - 24
    hy = cv.text_block(tx, ly + 48, LEAD["headline"], INK, 3, tw, 34)
    cv.text_block(tx, hy + 10, LEAD["summary"], GRAY, 2, tw, 20)

    # Row 2: two half-width panels
    y2, h2 = 382, 228
    w2 = (cw - 16) // 2
    for i, s in enumerate(ROW2):
        story_panel(cv, mx + i * (w2 + 16), y2, w2, h2,
                    s["tag"], s["color"], s["headline"], s["summary"],
                    icon=s["icon"], icon_size=72, head_scale=2, sum_scale=2)

    # Row 3: three third-width panels
    y3, h3 = 626, 228
    w3 = (cw - 32) // 3
    for i, s in enumerate(ROW3):
        story_panel(cv, mx + i * (w3 + 16), y3, w3, h3,
                    s["tag"], s["color"], s["headline"], s["summary"],
                    icon=s["icon"], icon_size=64, head_scale=2, sum_scale=2)

    # Ticker: the day's further news
    ty, th = 870, 84
    cv.fill_rect(mx, ty, cw, th, INK)
    cv.text(WIDTH // 2, ty + 12, TICKER[0], WHITE, 2, align="center")
    cv.text(WIDTH // 2, ty + 44, TICKER[1], WHITE, 2, align="center")

    # Footer
    cv.text(WIDTH // 2, 972, "DRAWN FROM 20 NOVEMBER 2026 REPORTS",
            GRAY, 2, align="center")
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    compose().save(os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()

