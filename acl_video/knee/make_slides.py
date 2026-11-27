import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "img")
OUT = os.path.join(ROOT, "slides")
ANIM = os.path.join(ROOT, "anim")
os.makedirs(OUT, exist_ok=True)
os.makedirs(ANIM, exist_ok=True)

W, H = 2160, 3840  # 4K vertical

# Panduan Tenang design tokens
BG = (250, 247, 242)       # #FAF7F2
TEXT = (46, 50, 48)        # #2E3230
MUTED = (95, 102, 98)
ACCENT = (47, 111, 94)     # #2F6F5E
HEADING = (34, 48, 43)     # #22302B
CREAM = (250, 247, 242)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def scrim(img, top=0.45, bot=0.98, strength=210):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    y0 = int(img.size[1] * top)
    y1 = int(img.size[1] * bot)
    for y in range(y0, y1):
        a = int(strength * ((y - y0) / max(1, y1 - y0)) ** 1.5)
        d.line([(0, y), (img.size[0], y)], fill=(20, 26, 24, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def darken(img, factor=0.45):
    return Image.eval(img, lambda p: int(p * factor))


def base_canvas(image_path, zoom=1.0, focus=(0.5, 0.4)):
    src = Image.open(image_path).convert("RGB")
    cover_w, cover_h = W, W * src.height // src.width
    if cover_h < H:
        cover_h = H
        cover_w = H * src.width // src.height
    src = src.resize((cover_w, cover_h), Image.LANCZOS)
    cw, ch = int(cover_w / zoom), int(cover_h / zoom)
    fx, fy = focus
    x = int((cover_w - cw) * fx)
    y = int((cover_h - ch) * fy)
    return src.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)


def draw_footer(d):
    font = f(SANS_B, 46)
    txt = "PRAKTEK FISIOTERAPI KAJHU  -  @ftr.sayed"
    tw = d.textlength(txt, font=font)
    y = H - 150
    d.rounded_rectangle([(W - tw) / 2 - 60, y - 38, (W + tw) / 2 + 60, y + 66],
                        radius=28, fill=(15, 30, 25, 200))
    d.text(((W - tw) / 2, y), txt, font=font, fill=CREAM)


def eyebrow(d, x, y, text):
    font = f(SANS_B, 56)
    tw = d.textlength(text, font=font)
    d.rounded_rectangle([x, y, x + tw + 90, y + 118], radius=59, fill=ACCENT)
    d.text((x + 45, y + 26), text, font=font, fill=CREAM)


def make_overlay(scene):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    on_photo = bool(scene.get("image"))
    main_txt = CREAM if on_photo else TEXT
    sub_txt = (235, 240, 237) if on_photo else MUTED
    badge_txt = (240, 200, 90) if on_photo else ACCENT
    x = 120
    y = int(H * 0.60)
    eyebrow(d, x, y, scene["eyebrow"])
    y += 230
    hf = f(SERIF_B, 170)
    for line in wrap(d, scene["title"], hf, W - 240):
        d.text((x, y), line, font=hf, fill=main_txt)
        y += 210
    y += 70
    if scene.get("subtitle"):
        sf = f(SERIF_R, 84)
        for line in wrap(d, scene["subtitle"], sf, W - 240):
            d.text((x, y), line, font=sf, fill=sub_txt)
            y += 110
        y += 30
    if scene.get("bullets"):
        bf = f(SANS, 68)
        for b in scene["bullets"]:
            d.ellipse([x + 6, y + 34, x + 42, y + 70], fill=(240, 200, 90) if on_photo else ACCENT)
            for i, line in enumerate(wrap(d, b, bf, W - 340)):
                d.text((x + 80, y + (0 if i == 0 else 86)), line, font=bf, fill=sub_txt)
                y += 86 if i == 0 else 86
            y += 50
    if scene.get("cta"):
        cf = f(SERIF_R, 76)
        y += 10
        for line in wrap(d, scene["cta"], cf, W - 240):
            d.text((x, y), line, font=cf, fill=sub_txt)
            y += 104
    if scene.get("instagram"):
        sf = f(SANS_B, 62)
        y += 30
        d.text((x, y), f"Instagram {scene['instagram']}     TikTok {scene['tiktok']}",
               font=sf, fill=badge_txt)
    draw_footer(d)
    img.save(os.path.join(OUT, f"{scene['id']}_overlay.png"))


def make_background(scene, focus):
    if scene.get("image"):
        img = base_canvas(os.path.join(IMG, scene["image"]), focus=focus)
        img = scrim(img)
    else:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for i in range(H):
            t = i / H
            d.line([(0, i), (W, i)],
                   fill=(int(BG[0] - 14 * t), int(BG[1] - 12 * t), int(BG[2] - 10 * t)))
    img.convert("RGB").save(os.path.join(OUT, f"{scene['id']}_bg.png"))


def make_anatomy_frames(n_frames=200):
    # Animated knee joint: femur/tibia flexing, cartilage highlight, slow zoom
    R = 1080, 1920
    cx, cy = R[0] // 2, int(R[1] * 0.44)
    for i in range(n_frames):
        t = i / n_frames
        zoom = 1.04 + 0.05 * t
        ang = math.radians(18 + 26 * math.sin(2 * math.pi * t))  # flexion oscillation
        img = Image.new("RGB", R, BG)
        d = ImageDraw.Draw(img)
        # background vignette
        d.ellipse([cx - 620, cy - 620, cx + 620, cy + 620], fill=(242, 240, 232))
        d.ellipse([cx - 480, cy - 480, cx + 480, cy + 480], fill=(233, 236, 230))
        BONE = (238, 228, 210)
        BONE_EDGE = (196, 178, 150)
        # femur (upper bone), fixed vertical
        d.rounded_rectangle([cx - 95, cy - 560, cx + 95, cy + 20], radius=90,
                            fill=BONE, outline=BONE_EDGE, width=6)
        # femoral condyles
        d.ellipse([cx - 150, cy - 60, cx + 40, cy + 130], fill=BONE, outline=BONE_EDGE, width=6)
        d.ellipse([cx - 40, cy - 60, cx + 150, cy + 130], fill=BONE, outline=BONE_EDGE, width=6)
        # tibia rotates around joint centre (cx, cy+95)
        jx, jy = cx, cy + 95
        tl = 430
        ex = jx + tl * math.sin(ang)
        ey = jy + tl * math.cos(ang)
        # cartilage meniscus wedge (accent, pulses)
        pulse = 26 + 8 * math.sin(2 * math.pi * t * 2)
        d.ellipse([jx - 150, jy - pulse, jx + 150, jy + pulse], fill=(111, 178, 158))
        # tibia: rotated capsule from joint to (ex, ey)
        d.line([(jx, jy + 40), (ex, ey)], fill=BONE_EDGE, width=200)
        d.line([(jx, jy + 40), (ex, ey)], fill=BONE, width=180)
        d.ellipse([jx - 100, jy - 60, jx + 100, jy + 140], fill=BONE, outline=BONE_EDGE, width=6)
        d.ellipse([ex - 100, ey - 100, ex + 100, ey + 100], fill=BONE, outline=BONE_EDGE, width=6)
        # patella
        d.ellipse([cx - 70, cy - 240, cx + 70, cy - 110], fill=(246, 238, 224),
                  outline=BONE_EDGE, width=6)
        # flexion angle text near joint
        af = f(SANS_B, 54)
        d.text((jx + 190, jy + 60), f"{int(math.degrees(ang))} derajat", font=af, fill=ACCENT)
        # labels inside the canvas
        lf = f(SANS, 44)
        d.text((cx + 130, cy - 230), "Patella", font=lf, fill=TEXT)
        d.text((cx - 430, cy - 520), "Femur", font=lf, fill=TEXT)
        d.text((ex + 130, ey + 20), "Tibia", font=lf, fill=TEXT)
        d.text((jx - 430, jy + 230), "Meniskus / kartilago", font=lf, fill=ACCENT)
        if zoom > 1.0:
            img = img.resize((int(R[0] / zoom), int(R[1] / zoom)), Image.LANCZOS)
            img = img.crop(((img.width - R[0]) // 2, (img.height - R[1]) // 2,
                            (img.width - R[0]) // 2 + R[0], (img.height - R[1]) // 2 + R[1]))
        img.save(os.path.join(ANIM, f"f{i:04d}.png"))


if __name__ == "__main__":
    import importlib.util
    spec = importlib.util.spec_from_file_location("sc", os.path.join(ROOT, "script.py"))
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    for s in sc.SCENES:
        make_background(s, (0.5, 0.4))
        make_overlay(s)
        print("ok", s["id"])
    make_anatomy_frames()
    print("anatomy frames ok")
