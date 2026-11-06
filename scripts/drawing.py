"""Small drawing helpers shared by the sheet builders (build_schematics.py, sheets_io.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schgen as G  # noqa: E402
from schgen import g  # noqa: E402

TP_FP = "TestPoint:TestPoint_Pad_D2.0mm"
GND = "power:GND"


def note(s, text, x, y, size=1.27, bold=False):
    s.text(text, x, y, size=size, bold=bold)


def vpart(s, libid, ref, x, y_top, value, lcsc, **kw):
    """Vertical two-pin part (pins 3.81 mm above and below its centre) with its TOP pin at (x, y_top).
    Returns the part; its bottom pin is at y_top + 7.62."""
    return s.place(libid, ref, x, y_top + g(3), value=value, lcsc=lcsc, **kw)


def hpart(s, libid, ref, x_left, y, value, lcsc, **kw):
    """Horizontal two-pin part with its LEFT pin at (x_left, y); the right pin is 7.62 mm further right."""
    return s.place(libid, ref, x_left + g(3), y, value=value, lcsc=lcsc, **kw)


def testpoint(s, ref, net, x, y, **kw):
    """Test point with its pin at (x, y) and the pad drawn above it; the value (net name) is not repeated."""
    return s.place("Connector:TestPoint", ref, x, y, value=net, footprint=TP_FP, in_bom=False,
                   props={"LCSC": "n/a (bare pad)"}, show_value=False, ref_at=(x + g(2), y - g(3)), justify="left", **kw)


def tp_at_net(s, ref, net, x, y):
    """Test point whose pin is wired down 2.54 mm to a net label (row of test points at the bottom of a sheet)."""
    testpoint(s, ref, net, x, y)
    s.wire((x, y), (x, y + g(2)))
    s.label(net, x, y + g(2), 0)




def decap(s, x, y, plus_glyph, plus_net, gnd_glyph, gnd_net, ref, value="100nF", code="C1591"):
    """Decoupling capacitor next to an IC: top pin at (x, y) on the supply glyph, bottom pin on the ground glyph."""
    C = vpart(s, "Device:C", ref, x, y, value, code)
    s.power(plus_glyph, plus_net, *C.pin("1"))
    s.power(gnd_glyph, gnd_net, *C.pin("2"))
    return C


def tie(s, pt, direction, glyph, net, length=4):
    """Stub from a pin to a power glyph (supply or ground)."""
    e = s.stub(pt, direction, g(length))
    s.power(glyph, net, *e)
    return e


def tie_bar(s, pts, direction, glyph, net, length=4):
    """Several pins on adjacent rows joined by a vertical bar to ONE power glyph (at the lowest pin for grounds, the highest
    for supplies)."""
    xs = [pt[0] + direction[0] * g(length) for pt in pts]
    for pt, x in zip(pts, xs):
        s.wire(pt, (x, pt[1]))
    ys = [pt[1] for pt in pts]
    s.wire((xs[0], min(ys)), (xs[0], max(ys)))
    down = glyph_down(s, glyph)
    s.power(glyph, net, xs[0], max(ys) if down else min(ys))


def glyph_down(s, glyph):
    return s.libs.get(glyph).pins["1"][2] == 270
