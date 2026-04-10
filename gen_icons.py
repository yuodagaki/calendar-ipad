#!/usr/bin/env python3
"""Generate PWA icons using only Python stdlib (no Pillow needed)."""
import struct, zlib, os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── PNG writer ──────────────────────────────────────────────────────────────
def make_png(w, h, pixels):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    raw = []
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw.extend(pixels[y * w + x])
    data = zlib.compress(bytes(raw), 9)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', data) + chunk(b'IEND', b'')

# ── 5×7 pixel font ──────────────────────────────────────────────────────────
FONT = {
    'C': ['01110','10001','10000','10000','10000','10001','01110'],
    'A': ['00100','01010','10001','11111','10001','10001','10001'],
    'L': ['10000','10000','10000','10000','10000','10000','11111'],
    'I': ['11111','00100','00100','00100','00100','00100','11111'],
    'P': ['11110','10001','10001','11110','10000','10000','10000'],
    'D': ['11110','10001','10001','10001','10001','10001','11110'],
}

# ── Colors ──────────────────────────────────────────────────────────────────
BG    = (10,  10,  8)
ON    = (0,  255, 65)   # CASIO green
GLOW  = (0,  100, 25)   # glow halo
GHOST = (0,   30, 10)   # unlit segment
FRAME = (0,   60, 15)   # border

# ── Icon renderer ────────────────────────────────────────────────────────────
def draw_icon(size):
    pixels = [list(BG)] * (size * size)
    pixels = [list(BG) for _ in range(size * size)]

    def put(x, y, rgb):
        if 0 <= x < size and 0 <= y < size:
            pixels[y * size + x] = list(rgb)

    def blend(x, y, rgb, alpha):
        if 0 <= x < size and 0 <= y < size:
            p = pixels[y * size + x]
            pixels[y * size + x] = [
                int(p[i] * (1 - alpha) + rgb[i] * alpha) for i in range(3)
            ]

    ps = max(2, size // 40)  # pixel size per font-dot

    def draw_char(ch, cx, cy, lit):
        rows = FONT.get(ch, [])
        for ri, row in enumerate(rows):
            for ci, bit in enumerate(row):
                x0, y0 = cx + ci * ps, cy + ri * ps
                color = ON if (bit == '1' and lit) else GHOST
                if bit == '1' and lit:
                    # glow halo (1-dot border)
                    for dy in range(-1, ps + 1):
                        for dx in range(-1, ps + 1):
                            blend(x0 + dx, y0 + dy, GLOW, 0.6)
                for py in range(ps):
                    for px in range(ps):
                        put(x0 + px, y0 + py, color)

    char_w = 5 * ps
    gap    = max(1, ps * 2)
    char_h = 7 * ps
    line_gap = max(1, ps * 3)

    line1, line2 = "CAL", "IPAD"
    w1 = len(line1) * char_w + (len(line1) - 1) * gap
    w2 = len(line2) * char_w + (len(line2) - 1) * gap
    total_h = char_h * 2 + line_gap

    x1 = (size - w1) // 2
    x2 = (size - w2) // 2
    y0 = (size - total_h) // 2

    for i, ch in enumerate(line1):
        draw_char(ch, x1 + i * (char_w + gap), y0, lit=True)
    for i, ch in enumerate(line2):
        draw_char(ch, x2 + i * (char_w + gap), y0 + char_h + line_gap, lit=True)

    # Thin frame
    border = max(2, size // 64)
    for i in range(border):
        for x in range(size):
            put(x, i, FRAME); put(x, size - 1 - i, FRAME)
        for y in range(size):
            put(i, y, FRAME); put(size - 1 - i, y, FRAME)

    return make_png(size, size, pixels)

# ── Generate ─────────────────────────────────────────────────────────────────
for sz, name in [(192, 'icon-192.png'), (512, 'icon-512.png')]:
    with open(os.path.join(BASE, name), 'wb') as f:
        f.write(draw_icon(sz))
    print(f'{name} generated ({sz}x{sz})')
