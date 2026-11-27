import subprocess, os
import importlib.util
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "img")
SLIDES = os.path.join(ROOT, "slides")
AUDIO = os.path.join(ROOT, "audio")
os.makedirs(SLIDES, exist_ok=True)

spec = importlib.util.spec_from_file_location("neckscript", os.path.join(ROOT, "script.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SCENES, FOOTER = mod.SCENES, mod.FOOTER

TEAL = (13, 59, 66)
ACCENT = (240, 122, 50)
WHITE = (255, 255, 255)
INK = (28, 40, 45)

def font(size, bold=False):
    if bold:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", size)
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf", size)

def cover(img):
    sw, sh = img.size
    scale = max(W / sw, H / sh)
    img = img.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    x = (img.width - W) // 2
    y = (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))

def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def bullets_block(draw, items, x, y, maxw):
    f = font(40)
    lh = 64
    for it in items:
        lines = wrap(draw, it, f, maxw - 70)
        draw.ellipse([x, y + 20, x + 18, y + 38], fill=ACCENT)
        for i, ln in enumerate(lines):
            draw.text((x + 40, y + 4), ln, font=f, fill=WHITE)
            y += lh
        y += 18
    return y

def base_canvas(photo_path, dark=0.55):
    img = Image.open(photo_path).convert("RGB")
    img = cover(img)
    grad = Image.new("L", (W, 1))
    for x in range(W):
        t = x / W
        alpha = int(255 * dark * max(0.0, 1.0 - t * 1.35))
        grad.putpixel((x, 0), alpha)
    grad = grad.resize((W, H))
    overlay = Image.new("RGB", (W, H), (8, 24, 30))
    img = Image.composite(overlay, img, grad)
    veil = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.blend(img, veil, 0.15)
    return img

def slide_title(s, path):
    img = base_canvas(os.path.join(IMG, s["image"]), dark=0.7)
    d = ImageDraw.Draw(img)
    f1 = font(120, bold=True)
    lines = wrap(d, s["title"], f1, 1000)
    y = 360
    for ln in lines:
        d.text((120, y), ln, font=f1, fill=WHITE)
        y += 140
    d.rectangle([120, y + 10, 420, y + 26], fill=ACCENT)
    f2 = font(54)
    y += 70
    for ln in wrap(d, s["subtitle"], f2, 1000):
        d.text((120, y), ln, font=f2, fill=(220, 235, 238))
        y += 66
    img.save(path, quality=92)

def slide_content(s, path):
    img = base_canvas(os.path.join(IMG, s["image"]))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 12], fill=ACCENT)
    f1 = font(76, bold=True)
    d.text((120, 90), s["title"], font=f1, fill=WHITE)
    d.rectangle([120, 190, 320, 202], fill=ACCENT)
    y = 300
    bullets_block(d, s["bullets"], 120, y, 1180)
    f3 = font(28)
    d.text((120, H - 70), FOOTER, font=f3, fill=(200, 215, 220))
    img.save(path, quality=92)

for s in SCENES:
    p = os.path.join(SLIDES, s["id"] + ".png")
    if "subtitle" in s:
        slide_title(s, p)
    else:
        slide_content(s, p)
    print("slide", p)
