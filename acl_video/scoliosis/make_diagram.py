import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
ROOT = os.path.dirname(os.path.abspath(__file__))
TEAL = (13, 59, 66)
BONE = (214, 224, 228)
ACCENT = (240, 122, 50)


def font(size, bold=False):
    name = "FreeSansBold.ttf" if bold else "FreeSans.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/freefont/" + name, size)


def spine(draw, cx, top, bottom, offsets):
    steps = len(offsets)
    for i, off in enumerate(offsets):
        y = top + (bottom - top) * i / (steps - 1)
        x = cx + off
        draw.rounded_rectangle([x - 27, y, x + 27, y + 30], radius=10)
        if i:
            py = top + (bottom - top) * (i - 1) / (steps - 1) + 30
            px = cx + offsets[i - 1]
            draw.line([(px, py), (x, y)], width=8)


def diag_panel(d, x0, offsets, label, color):
    d.rounded_rectangle([x0, 140, x0 + 400, 830], radius=24, fill=(9, 44, 50))
    d.rounded_rectangle([x0 + 40, 180, x0 + 360, 660], radius=120,
                        outline=(30, 90, 98), width=4)
    spine(d, x0 + 200, 220, 620, offsets)
    f = font(36, bold=True)
    for i, ln in enumerate(label):
        tw = d.textlength(ln, font=f)
        d.text((x0 + 200 - tw / 2, 690 + i * 44), ln, font=f, fill=color)


def make(path):
    img = Image.new("RGB", (W, H), TEAL)
    d = ImageDraw.Draw(img)
    normal = [0, 3, 6, 3, -3, -6, -3, 0]
    scol = [0, -10, -22, -34, -25, -9, 8, 18]
    diag_panel(d, 1060, normal, ["Tulang belakang normal"], BONE)
    diag_panel(d, 1490, scol, ["Skoliosis", "(melengkung ke samping)"], ACCENT)
    f = font(32)
    note = "Kelengkungan ke samping lebih dari 10 derajat"
    note2 = "pada pemeriksaan rontgen disebut skoliosis."
    d.text((1060, 880), note, font=f, fill=(200, 220, 224))
    d.text((1060, 928), note2, font=f, fill=(200, 220, 224))
    img.save(path, quality=92)
    print("diagram", path)


if __name__ == "__main__":
    make(os.path.join(ROOT, "img", "spine-diagram.png"))
