#!/usr/bin/env python3
"""Generate the app icon as a PNG, no third-party libraries.

Draws a dumbbell on a dark gradient, antialiased by 3x3 supersampling.
"""
import struct, zlib, sys, math

BG_TOP    = (0xfa, 0xf9, 0xf6)
BG_BOTTOM = (0xec, 0xeb, 0xe6)
MARK      = (0x23, 0x26, 0x2b)

def rrect(px, py, x0, y0, x1, y1, r):
    """Signed distance to a rounded rect; negative inside."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    dx, dy = abs(px - cx) - hx, abs(py - cy) - hy
    return math.hypot(max(dx, 0), max(dy, 0)) + min(max(dx, dy), 0) - r

def shape(x, y):
    """Dumbbell in 0..1 space. Returns True inside the mark."""
    parts = (
        (0.300, 0.468, 0.700, 0.532, 0.012),   # handle
        (0.236, 0.372, 0.300, 0.628, 0.022),   # inner plate L
        (0.700, 0.372, 0.764, 0.628, 0.022),   # inner plate R
        (0.178, 0.420, 0.236, 0.580, 0.020),   # outer plate L
        (0.764, 0.420, 0.822, 0.580, 0.020),   # outer plate R
    )
    return any(rrect(x, y, *p) < 0 for p in parts)

def render(size):
    ss = 3
    rows = []
    for py in range(size):
        row = bytearray()
        for px in range(size):
            hits = 0
            for sy in range(ss):
                for sx in range(ss):
                    u = (px + (sx + 0.5) / ss) / size
                    v = (py + (sy + 0.5) / ss) / size
                    if shape(u, v):
                        hits += 1
            a = hits / (ss * ss)
            t = py / (size - 1)
            for c in range(3):
                bg = BG_TOP[c] + (BG_BOTTOM[c] - BG_TOP[c]) * t
                row.append(int(round(bg + (MARK[c] - bg) * a)))
        rows.append(bytes(row))
    return rows

def png(rows, size):
    raw = b''.join(b'\x00' + r for r in rows)
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        path, _, s = arg.rpartition(':')
        size = int(s)
        open(path, 'wb').write(png(render(size), size))
        print('wrote %s (%dx%d)' % (path, size, size))
