#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Klipp ut de tre porträtten ur gruppfotot från Tranås.

    python3 verktyg/klipp-portratt.py            # skriv bilderna
    python3 verktyg/klipp-portratt.py --prov      # bara en kontaktkarta att titta på

Originalet ligger utanför repot, i music-convert, och är 4151×4566. Alla tre
sitter fritt i bilden, så porträtten går att beskära utan att någon skärs av.
Måtten nedan är i originalets pixlar: (vänster, övre, höger, undre), alltid i
förhållandet 3:4 så att raderna blir lika höga på sajten.

Resultatet hamnar i docs/media/bild/ som webp och jpg, 700 px breda — dubbelt
mot hur stora de visas, för skärmar med hög upplösning.
"""
import argparse
import os
import sys

from PIL import Image

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")
KALLA = "/Users/aj/code/music-convert/sources/tranås2026.jpeg"
BREDD = 700

PORTRATT = [
    # namn,                fil,                    beskärning
    ("Anna Ighe Ramqvist", "portratt-anna", (2972, 1420, 3822, 2553)),
    ("Gösta Nylund", "portratt-gosta", (2122, 830, 2872, 1830)),
    ("Andreas Josephson", "portratt-andreas", (250, 1180, 1250, 2513)),
]


def klipp(bild, ruta):
    v, o, h, u = ruta
    del_ = bild.crop(ruta)
    return del_.resize((BREDD, round(BREDD * (u - o) / (h - v))), Image.LANCZOS)


def main():
    a = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--prov", action="store_true",
                   help="lägg de tre bredvid varandra i en provbild i stället")
    args = a.parse_args()

    if not os.path.exists(KALLA):
        sys.exit("hittar inte originalet: %s" % KALLA)
    bild = Image.open(KALLA)

    if args.prov:
        delar = [klipp(bild, r) for _, _, r in PORTRATT]
        h = max(d.height for d in delar)
        karta = Image.new("RGB", (sum(d.width for d in delar) + 40, h), "white")
        x = 0
        for d in delar:
            karta.paste(d, (x, 0))
            x += d.width + 20
        ut = "/tmp/portratt-prov.jpg"
        karta.save(ut, quality=88)
        print("Skrev %s" % ut)
        return

    mapp = os.path.join(SAJT, "media", "bild")
    for namn, fil, ruta in PORTRATT:
        d = klipp(bild, ruta)
        d.save(os.path.join(mapp, fil + ".webp"), quality=82, method=6)
        d.save(os.path.join(mapp, fil + ".jpg"), quality=82, optimize=True,
               progressive=True)
        w = os.path.getsize(os.path.join(mapp, fil + ".webp"))
        j = os.path.getsize(os.path.join(mapp, fil + ".jpg"))
        print("%-20s %d×%d   webp %d kB, jpg %d kB"
              % (namn, d.width, d.height, w // 1024, j // 1024))


if __name__ == "__main__":
    main()
