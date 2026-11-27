"""Ставит логотип ciraGram во все иконки клиента.
Запуск: python cira-cloud/logo.py <корень репозитория>  (нужен Pillow).
Исходники знака: cira-cloud/icons/*.svg, готовые PNG 1024x1024 рядом (make_icons.py их пересоздаёт).
"""
import glob
import os
import sys

from PIL import Image

root = os.path.abspath(sys.argv[1])
here = os.path.join(root, 'cira-cloud', 'icons')
os.chdir(root)

MAIN = Image.open(os.path.join(here, 'main.png')).convert('RGBA')
ROUND = Image.open(os.path.join(here, 'classic.png')).convert('RGBA')


def fit(master, size):
    return master.resize((size, size), Image.LANCZOS)


def content_box(img):
    """Где в старой иконке был сам значок: новые иконки ставим в то же место с теми же полями."""
    alpha = img.getchannel('A')
    box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    if not box:
        return (0, 0, img.width, img.height)
    x0, y0, x1, y1 = box
    side = max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0 = max(0, round(cx - side / 2))
    y0 = max(0, round(cy - side / 2))
    side = min(side, img.width - x0, img.height - y0)
    return (x0, y0, x0 + side, y0 + side)


def place(path, master, margin=None):
    old = Image.open(path).convert('RGBA')
    if old.width != old.height:
        print('skip non-square', path, old.size)
        return
    out = Image.new('RGBA', old.size, (0, 0, 0, 0))
    if margin is not None:
        m = round(old.width * margin)
        box = (m, m, old.width - m, old.height - m)
    else:
        box = content_box(old)
    side = box[2] - box[0]
    out.alpha_composite(fit(master, side), (box[0], box[1]))
    out.save(path)


targets = sorted(set(
    glob.glob('Telegram/Resources/art/icon[0-9]*.png')
    + glob.glob('Telegram/Resources/art/logo_256*.png')
    + ['docs/readme/logo.png']))
for t in targets:
    if os.path.exists(t):
        place(t, MAIN)
if os.path.exists('Telegram/Resources/art/icon_round512@2x.png'):
    place('Telegram/Resources/art/icon_round512@2x.png', ROUND)

for t in sorted(glob.glob('Telegram/Resources/uwp/AppX/Assets/*/*.png')):
    place(t, MAIN, margin=0.02 if 'unplated' in t else 0.10)

ico = 'Telegram/Resources/art/icon256.ico'
if os.path.exists(ico):
    MAIN.save(ico, sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)])

print('logo done:', len(targets) + 1, 'png,', len(glob.glob('Telegram/Resources/uwp/AppX/Assets/*/*.png')), 'uwp, ico')
