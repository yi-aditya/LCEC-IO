#!/usr/bin/env python3
"""3D renders of a placement board (top view and two angled views) with KiCad's own renderer.

    python3 -I scripts/render_3d.py v1      # docs/review/L1-3d-v1-top.png, -iso.png, -front.png

The parts that found no room on the board and are parked outside the outline are left out of the render.
"""
import os
import subprocess
import sys
import tempfile

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(v):
    src = os.path.join(ROOT, "hardware", f"lcec-io-{v}.kicad_pcb")
    b = pcbnew.LoadBoard(src)
    bb = b.GetBoardEdgesBoundingBox()
    for fp in list(b.GetFootprints()):
        c = fp.GetPosition()
        if c.x > bb.GetRight() or c.y > bb.GetBottom():
            b.Remove(fp)
    tmp = os.path.join(os.path.dirname(src), f".render-{v}.kicad_pcb")      # next to the project so ${KIPRJMOD} resolves
    pcbnew.SaveBoard(tmp, b)
    out = os.path.join(ROOT, "docs", "review")
    views = {"top": ["--side", "top", "--perspective", "--zoom", "1.15"],
             "iso": ["--rotate", "-52,0,28", "--perspective", "--zoom", "1.0"],
             "front": ["--rotate", "-72,0,0", "--perspective", "--zoom", "1.1", "--pan", "0,-2,0"]}
    try:
        for name, args in views.items():
            subprocess.run(["kicad-cli", "pcb", "render", "-o", os.path.join(out, f"L1-3d-{v}-{name}.png"), "--width", "2000", "--height", "1300",
                            "--quality", "high", "--background", "opaque", "--light-top", "0.9", "--light-camera", "0.5", "--light-side", "0.6"] + args + [tmp],
                           check=True, capture_output=True)
    finally:
        os.remove(tmp)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
