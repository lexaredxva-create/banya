from __future__ import annotations

import math
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(r"C:\Users\lexa\Documents\Codex\2026-07-04\200-100-5400-450")
OUT = ROOT / "drawings"
PDF = OUT / "sauna_attic_3d_overall_v01.pdf"


def register_fonts() -> tuple[str, str]:
    regular = r"C:\Windows\Fonts\arial.ttf"
    bold = r"C:\Windows\Fonts\arialbd.ttf"
    if os.path.exists(regular) and os.path.exists(bold):
        pdfmetrics.registerFont(TTFont("Plan", regular))
        pdfmetrics.registerFont(TTFont("Plan-Bold", bold))
        return "Plan", "Plan-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


def m(v: float) -> float:
    return v * mm


class Draw:
    def __init__(self, c: canvas.Canvas):
        self.c = c

    def text(self, x, y, s, size=3.0, bold=False, color=colors.black, align="left"):
        self.c.saveState()
        self.c.setFont(FONT_BOLD if bold else FONT, size * mm)
        self.c.setFillColor(color)
        if align == "center":
            self.c.drawCentredString(m(x), m(y), s)
        elif align == "right":
            self.c.drawRightString(m(x), m(y), s)
        else:
            self.c.drawString(m(x), m(y), s)
        self.c.restoreState()

    def multiline(self, x, y, lines, size=2.45, leading=5.0, bold=False, color=colors.black):
        for i, line in enumerate(lines):
            self.text(x, y - i * leading, line, size=size, bold=bold, color=color)

    def line(self, x1, y1, x2, y2, lw=0.25, color=colors.black, dash=None):
        self.c.saveState()
        self.c.setStrokeColor(color)
        self.c.setLineWidth(m(lw))
        if dash:
            self.c.setDash([m(v) for v in dash], 0)
        self.c.line(m(x1), m(y1), m(x2), m(y2))
        self.c.restoreState()

    def poly(self, pts, lw=0.3, stroke=colors.black, fill=None, dash=None):
        p = self.c.beginPath()
        p.moveTo(m(pts[0][0]), m(pts[0][1]))
        for x, y in pts[1:]:
            p.lineTo(m(x), m(y))
        p.close()
        self.c.saveState()
        self.c.setStrokeColor(stroke)
        self.c.setLineWidth(m(lw))
        if dash:
            self.c.setDash([m(v) for v in dash], 0)
        if fill:
            self.c.setFillColor(fill)
        self.c.drawPath(p, stroke=1, fill=1 if fill else 0)
        self.c.restoreState()

    def rect(self, x, y, w, h, lw=0.25, stroke=colors.black, fill=None, dash=None):
        self.c.saveState()
        self.c.setStrokeColor(stroke)
        self.c.setLineWidth(m(lw))
        if dash:
            self.c.setDash([m(v) for v in dash], 0)
        if fill:
            self.c.setFillColor(fill)
        self.c.rect(m(x), m(y), m(w), m(h), stroke=1, fill=1 if fill else 0)
        self.c.restoreState()


class Axon:
    def __init__(self, origin_x=132.0, origin_y=104.0, scale=55.0):
        self.ox = origin_x
        self.oy = origin_y
        self.scale = scale

    def p(self, x: float, y: float, z: float) -> tuple[float, float]:
        # x: width across attic, y: length from sauna gable to entrance, z: height.
        xx = self.ox + (x - 3000.0) / self.scale + y / self.scale * 0.42
        yy = self.oy + z / self.scale - y / self.scale * 0.24
        return xx, yy


def title_block(d: Draw, sheet_no: str, title: str):
    d.rect(8, 8, 404, 281, lw=0.45)
    d.rect(8, 8, 404, 18, lw=0.35)
    d.line(92, 8, 92, 26, lw=0.2)
    d.line(230, 8, 230, 26, lw=0.2)
    d.line(325, 8, 325, 26, lw=0.2)
    d.text(12, 19, "Проект: баня на чердаке мастерской", size=3.0, bold=True)
    d.text(96, 19, title, size=2.8)
    d.text(234, 19, "Общая аксонометрия, пропорции 12 x 6", size=2.7)
    d.text(329, 19, f"Лист {sheet_no}", size=3.0, bold=True)
    d.text(12, 13, "Статус: общая объемная схема для обсуждения", size=2.35, color=colors.HexColor("#9b1c1c"))
    d.text(234, 13, "Детальные узлы печи, пола, воды и вентиляции будут отдельными листами.", size=2.35)


def face(d: Draw, ax: Axon, pts3, fill, stroke=colors.black, lw=0.3, dash=None):
    d.poly([ax.p(*p) for p in pts3], lw=lw, stroke=stroke, fill=fill, dash=dash)


def polyline3(d: Draw, ax: Axon, pts3, lw=0.25, color=colors.black, dash=None):
    pts = [ax.p(*p) for p in pts3]
    for a, b in zip(pts, pts[1:]):
        d.line(a[0], a[1], b[0], b[1], lw=lw, color=color, dash=dash)


def label_zone(d: Draw, ax: Axon, x, y, z, text, color=colors.black, size=2.5):
    px, py = ax.p(x, y, z)
    d.text(px, py, text, size=size, bold=True, color=color, align="center")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    width = 6000.0
    length = 12000.0
    height = 3000.0
    steam_len = 2400.0
    wash_len = 2000.0
    rest_len = length - steam_len - wash_len
    steam_w = 2400.0
    wash_w = 2800.0
    ceiling = 2400.0

    # Layer assumptions until rafter is measured.
    vent = 50.0
    rafter = 200.0
    insulation = 200.0
    finish = 45.0
    slope = height / (width / 2.0)
    inward_insulation = max(0.0, insulation - max(0.0, rafter - vent))
    loss_normal = inward_insulation + finish
    vertical_loss = loss_normal * math.sqrt(1 + slope * slope) / slope

    def clean_roof_y(x: float) -> float:
        return min(slope * x, slope * (width - x)) - vertical_loss

    steam_left = width / 2 - steam_w / 2
    steam_right = width / 2 + steam_w / 2
    edge_h = clean_roof_y(steam_left)
    left_break = (ceiling + vertical_loss) / slope
    right_break = width - left_break
    standing_w = width - 2 * ((2100 + vertical_loss) / slope)
    for name, x, z in [
        ("left edge", steam_left, edge_h),
        ("left break", left_break, ceiling),
        ("right break", right_break, ceiling),
        ("right edge", steam_right, edge_h),
    ]:
        if z > clean_roof_y(x) + 0.1:
            raise ValueError(f"{name} outside clean roof envelope")

    c = canvas.Canvas(str(PDF), pagesize=landscape(A3))
    c.setTitle("Sauna attic 3D overall")
    d = Draw(c)
    ax = Axon()
    title_block(d, "A-3D-102", "Общая объемная схема")

    d.text(18, 276, "A-3D-102. Общая схема: чердак 12 x 6 м, зоны бани, слои и наружный сэндвич-дымоход", size=4.3, bold=True)
    d.text(18, 269, "Цель: увидеть все вместе в пропорциях. Это обзорный лист; узлы и размеры будут отдельными проверяемыми листами.", size=2.65)

    # Floor zones, drawn back-to-front so long proportions read correctly.
    zones = [
        (steam_len + wash_len, length, colors.Color(0.87, 0.90, 0.78, alpha=0.72), colors.HexColor("#69703d"), "отдых / вход", rest_len),
        (steam_len, steam_len + wash_len, colors.Color(0.78, 0.91, 0.96, alpha=0.75), colors.HexColor("#2f6b82"), "помывочная", wash_len),
        (0, steam_len, colors.Color(0.96, 0.84, 0.73, alpha=0.78), colors.HexColor("#8b4f22"), "парная", steam_len),
    ]
    for y0, y1, fill, stroke, _, _ in zones:
        face(d, ax, [(0, y0, 0), (width, y0, 0), (width, y1, 0), (0, y1, 0)], fill, stroke=stroke, lw=0.28)

    # Roof envelope over full 12 m.
    left_roof = [(0, 0, 0), (width / 2, 0, height), (width / 2, length, height), (0, length, 0)]
    right_roof = [(width, 0, 0), (width / 2, 0, height), (width / 2, length, height), (width, length, 0)]
    face(d, ax, left_roof, colors.Color(0.78, 0.84, 0.88, alpha=0.12), stroke=colors.HexColor("#222222"), lw=0.45)
    face(d, ax, right_roof, colors.Color(0.78, 0.84, 0.88, alpha=0.12), stroke=colors.HexColor("#222222"), lw=0.45)
    polyline3(d, ax, [(0, 0, 0), (width / 2, 0, height), (width, 0, 0), (0, 0, 0)], lw=0.55)
    polyline3(d, ax, [(0, length, 0), (width / 2, length, height), (width, length, 0), (0, length, 0)], lw=0.28, dash=[3, 2])
    polyline3(d, ax, [(width / 2, 0, height), (width / 2, length, height)], lw=0.35, color=colors.HexColor("#333333"))

    # Zone separators.
    for yy in [steam_len, steam_len + wash_len]:
        polyline3(d, ax, [(0, yy, 0), (width, yy, 0)], lw=0.35, color=colors.HexColor("#444444"))
        polyline3(d, ax, [(width / 2, yy, 0), (width / 2, yy, 300)], lw=0.2, color=colors.HexColor("#444444"), dash=[2, 2])

    # Clean sauna capsule volume, at the gable.
    y0, y1 = 120.0, steam_len
    sec = [
        (steam_left, 0, 0),
        (steam_left, 0, edge_h),
        (left_break, 0, ceiling),
        (right_break, 0, ceiling),
        (steam_right, 0, edge_h),
        (steam_right, 0, 0),
    ]
    sec0 = [(x, y0, z) for x, _, z in sec]
    sec1 = [(x, y1, z) for x, _, z in sec]
    face(d, ax, sec1, colors.Color(0.96, 0.84, 0.73, alpha=0.26), stroke=colors.HexColor("#8b4f22"), lw=0.25)
    for i in range(len(sec0)):
        j = (i + 1) % len(sec0)
        face(d, ax, [sec0[i], sec0[j], sec1[j], sec1[i]], colors.Color(0.96, 0.84, 0.73, alpha=0.16), stroke=colors.HexColor("#8b4f22"), lw=0.2)
    face(d, ax, sec0, colors.Color(0.96, 0.84, 0.73, alpha=0.36), stroke=colors.HexColor("#8b4f22"), lw=0.45)

    # Washing lightweight zone outline.
    wash_left = width / 2 - wash_w / 2
    wash_right = width / 2 + wash_w / 2
    face(
        d,
        ax,
        [(wash_left, steam_len, 0), (wash_right, steam_len, 0), (wash_right, steam_len + wash_len, 0), (wash_left, steam_len + wash_len, 0)],
        colors.Color(0.78, 0.91, 0.96, alpha=0.22),
        stroke=colors.HexColor("#2f6b82"),
        lw=0.35,
        dash=[3, 2],
    )

    # Stove and outside sandwich chimney at gable.
    stove_base = [
        (steam_left + 380, 420, 0),
        (steam_left + 760, 420, 0),
        (steam_left + 760, 780, 0),
        (steam_left + 380, 780, 0),
    ]
    stove_top = [(x, y, 720) for x, y, _ in stove_base]
    face(d, ax, stove_base, colors.Color(0.25, 0.25, 0.25, alpha=0.75), lw=0.22)
    face(d, ax, stove_top, colors.Color(0.16, 0.16, 0.16, alpha=0.9), lw=0.22)
    pipe_x = steam_left + 570
    pipe_y = 520
    polyline3(d, ax, [(pipe_x, pipe_y, 720), (pipe_x, pipe_y, 1500), (pipe_x - 650, -180, 1500)], lw=0.38, color=colors.HexColor("#555555"))
    polyline3(d, ax, [(pipe_x - 650, -180, 850), (pipe_x - 650, -180, 4200)], lw=0.7, color=colors.HexColor("#777f84"))
    # Sandwich thickness indicator.
    polyline3(d, ax, [(pipe_x - 700, -180, 850), (pipe_x - 700, -180, 4200)], lw=0.28, color=colors.HexColor("#222222"))
    polyline3(d, ax, [(pipe_x - 600, -180, 850), (pipe_x - 600, -180, 4200)], lw=0.28, color=colors.HexColor("#222222"))

    # Drain and water hint in washing zone.
    drain = ax.p(width / 2 + 720, steam_len + 1150, 20)
    d.rect(drain[0] - 2.5, drain[1] - 2.0, 5, 4, lw=0.2, fill=colors.HexColor("#2f6b82"))

    # Labels on the floor zones.
    label_zone(d, ax, width / 2, 1100, 60, "Парная 2.4 м", colors.HexColor("#8b4f22"), size=2.55)
    label_zone(d, ax, width / 2, steam_len + 1050, 60, "Помывочная 2.0 м", colors.HexColor("#2f6b82"), size=2.55)
    label_zone(d, ax, width / 2, steam_len + wash_len + 3800, 60, "Отдых / вход 7.6 м", colors.HexColor("#69703d"), size=2.55)

    # Overall proportions callouts.
    d.text(45, 224, "Пропорции учтены: чердак 12 000 x 6 000, высота 3 000", size=2.7, bold=True)
    d.text(45, 216, "Зоны по длине: 2400 парная + 2000 помывочная + 7600 отдых/вход", size=2.55)
    d.text(51, 81, "наружный утепленный сэндвич-дымоход через торцевую стену", size=2.4, color=colors.HexColor("#555555"))

    # Right panel: layers and assumptions.
    px, py = 292, 204
    d.rect(px - 8, py - 12, 110, 76, lw=0.32, stroke=colors.HexColor("#333333"))
    d.text(px, py + 52, "Пирог ската: снаружи внутрь", size=3.0, bold=True)
    layers = [
        ("металл / кровля", "#9aa4aa"),
        ("вентзазор V 50-100", "#bfe3ff"),
        ("утепление T 150-200+", "#f1d29b"),
        ("фольга, швы проклеить", "#ffd45a"),
        ("контррейка 20-30", "#d6f0d2"),
        ("вагонка 14-16", "#d4a36a"),
    ]
    for i, (label, hex_color) in enumerate(layers):
        yy = py + 39 - i * 9
        d.rect(px + 4, yy, 43, 3.6, lw=0.18, stroke=colors.HexColor("#444444"), fill=colors.HexColor(hex_color))
        d.text(px + 51, yy + 0.1, label, size=2.25)

    bx, by = 292, 78
    d.rect(bx - 8, by - 10, 110, 94, lw=0.32, fill=colors.HexColor("#fff8dd"), stroke=colors.HexColor("#bd8c00"))
    d.text(bx, by + 70, "Что уже заложено в общий лист", size=2.95, bold=True)
    d.multiline(
        bx,
        by + 60,
        [
            f"Чистая парная: {steam_w:.0f} x {steam_len:.0f}.",
            f"Край парной по высоте: ~{edge_h:.0f}.",
            f"Зона 2100+ внутри: ~{standing_w:.0f}.",
            f"Потеря внутрь по нормали: {loss_normal:.0f}.",
            "Бойлер не на чердаке.",
            "Помывочная легкая, слив 50 вниз.",
            "Пар не выпускать в подкровелье.",
            "Печь/дымоход/пол - отдельные узлы.",
        ],
        size=2.3,
        leading=5.1,
    )

    c.showPage()
    c.save()
    print(PDF)
    print(f"edge_h={edge_h:.1f}; standing_w={standing_w:.1f}; loss_normal={loss_normal:.1f}")


if __name__ == "__main__":
    main()
