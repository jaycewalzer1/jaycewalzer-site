"""Wash photos into the site's look: faded, low-contrast, cool shadows, fog highlights.

    uv run --with pillow --with numpy tools/wash.py assets/raw assets/washed

Each step is a plain tone operation, applied in order:
  1. desaturate most of the colour away
  2. compress contrast and lift the blacks (the faded, matte look)
  3. split-tone: shadows toward Pacific blue, highlights toward fog
  4. soft bloom so highlights bleed slightly, like old film
  5. fine monochrome grain
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

FOG = np.array([0xEE, 0xEB, 0xE4]) / 255     # highlight tint
SEA = np.array([0x3F, 0x58, 0x66]) / 255     # shadow tint
DRIFT = np.array([0x85, 0x74, 0x62]) / 255   # midtone warmth

SATURATION = 0.28   # keep this much of the original colour
BLACK_LIFT = 0.20   # darkest pixel ends up this bright
WHITE_CAP = 0.95    # brightest pixel
TONE = 0.55         # split-tone strength
BLOOM = 0.18
GRAIN = 0.022
MAX_WIDTH = 1800


def wash(img: Image.Image, seed: int) -> Image.Image:
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255

    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    a = lum[..., None] + SATURATION * (a - lum[..., None])

    a = BLACK_LIFT + (WHITE_CAP - BLACK_LIFT) * a
    lum = a @ np.array([0.2126, 0.7152, 0.0722])

    # weights for shadow / mid / highlight, smooth in luminance
    t = np.clip((lum - BLACK_LIFT) / (WHITE_CAP - BLACK_LIFT), 0, 1)[..., None]
    shadow, high = (1 - t) ** 2, t ** 2
    mid = 1 - shadow - high
    tint = shadow * SEA + mid * DRIFT + high * FOG
    # tint by colour, keep the original brightness
    tinted = tint * (lum[..., None] / np.maximum(tint @ np.array([0.2126, 0.7152, 0.0722]), 1e-3)[..., None])
    a = (1 - TONE) * a + TONE * tinted

    blur = np.asarray(
        Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12)),
        dtype=np.float32) / 255
    a = 1 - (1 - a) * (1 - BLOOM * blur)  # screen blend

    rng = np.random.default_rng(seed)
    a = a + rng.normal(0, GRAIN, a.shape[:2])[..., None]

    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def main(src: str, dst: str) -> None:
    out = Path(dst)
    out.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(sorted(Path(src).glob("*.jp*g"))):
        wash(Image.open(p), seed=i).save(out / f"{p.stem}.jpg", quality=84, optimize=True, progressive=True)
        print(p.name)


if __name__ == "__main__":
    main(*sys.argv[1:3])
