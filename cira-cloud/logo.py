"""Рисует логотип ciraGram и заменяет иконки. Запуск: python cira-cloud/logo.py <корень репозитория> (нужен Pillow)."""
import os, sys, math, glob
from PIL import Image, ImageDraw, ImageChops
os.chdir(os.path.abspath(sys.argv[1]))

def make(size, bbox, circle):
    S = 4
    W = size * S
    img = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    x0, y0, x1, y1 = [v * S for v in bbox]
    w, h = x1 - x0, y1 - y0
    # gradient teal -> indigo, diagonal
    g = Image.new('RGBA', (int(w), int(h)))
    px = g.load()
    c1, c2 = (24, 214, 190), (92, 72, 235)
    for yy in range(int(h)):
        for xx in range(int(w)):
            t = (xx / w * 0.45 + yy / h * 0.55)
            px[xx, yy] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)
    mask = Image.new('L', (int(w), int(h)), 0)
    md = ImageDraw.Draw(mask)
    if circle:
        md.ellipse((0, 0, w - 1, h - 1), fill=255)
    else:
        md.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(min(w, h) * 0.225), fill=255)
    # glyph: open ring "c" + dot
    gl = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(gl)
    cx, cy = w / 2, h / 2
    R = min(w, h) * 0.27
    th = min(w, h) * 0.11
    rc = R - th / 2
    steps = 720
    for i in range(steps + 1):
        a = math.radians(40 + 280 * i / steps)
        ex, ey = cx + rc * math.cos(a), cy + rc * math.sin(a)
        d.ellipse((ex - th / 2, ey - th / 2, ex + th / 2, ey + th / 2), fill=(255, 255, 255, 255))
    dr = th * 0.62
    d.ellipse((cx + R * 0.12 - dr, cy - dr, cx + R * 0.12 + dr, cy + dr), fill=(255, 255, 255, 255))
    g.alpha_composite(gl)
    g.putalpha(mask)
    img.alpha_composite(g, (int(x0), int(y0)))
    return img.resize((size, size), Image.LANCZOS)

def bbox_circle(path):
    im = Image.open(path).convert('RGBA'); a = im.split()[3]
    bb = a.point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, im.width, im.height)
    area = sum(1 for v in a.getdata() if v > 128)
    fill = area / max(1, (bb[2] - bb[0]) * (bb[3] - bb[1]))
    return im.size[0], bb, fill < 0.88

targets = (glob.glob('Telegram/Resources/art/icon[0-9]*.png') + glob.glob('Telegram/Resources/art/logo_256*.png')
           + ['Telegram/Resources/art/icon_round512@2x.png', 'docs/readme/logo.png']
           + glob.glob('Telegram/Resources/uwp/AppX/Assets/*/*.png'))
targets = [t for t in targets if 'logo_telegram_userpic' not in t]
for t in sorted(set(targets)):
    size, bb, circle = bbox_circle(t)
    if '/uwp/' in t:
        m = size * (0.02 if 'unplated' in t else 0.08)
        bb, circle = (m, m, size - m, size - m), False
    im = Image.open(t)
    if im.size[0] != im.size[1]:
        print('skip non-square', t, im.size); continue
    make(size, bb, circle).save(t)
    print('ok', t, size, bb, 'circle' if circle else 'rounded')
# ico
ico = 'Telegram/Resources/art/icon256.ico'
base = make(256, bbox_circle('Telegram/Resources/art/icon256.png')[1], False)
base.save(ico, sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('ico done')
