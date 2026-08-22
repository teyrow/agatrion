#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Peka om sajtens ljud- och videolänkar mellan lokala filer och objektlagringen.

    python3 verktyg/satt-mediabas.py https://media.agatrion.se
    python3 verktyg/satt-mediabas.py --lokalt

Bilder rörs inte — de ligger kvar i repot eftersom de är små och används av
Open Graph-taggarna, som måste ligga på samma domän som sidan.

Kör alltid --test först om du är osäker; då skrivs inget, bara en sammanfattning.
"""
import glob
import os
import re
import sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPAR = ("ljud", "video")


def filer():
    return sorted(glob.glob(os.path.join(ROT, "*.html")))


def byt(bas, test=False):
    """bas = "" ger lokala sökvägar (/media/ljud/...), annars https://.../ljud/..."""
    total = 0
    for path in filer():
        s = original = open(path, encoding="utf-8").read()
        for mapp in MAPPAR:
            if bas:
                # /media/ljud/x  ->  https://bas/ljud/x
                s = re.sub(r'(["\'])/media/%s/' % mapp, r'\1%s/%s/' % (bas, mapp), s)
                # redan omskriven mot en annan bas -> flytta till den nya
                s = re.sub(r'(["\'])https?://[^"\']*?/%s/' % mapp, r'\1%s/%s/' % (bas, mapp), s)
            else:
                s = re.sub(r'(["\'])https?://[^"\']*?/%s/' % mapp, r'\1/media/%s/' % mapp, s)
        if s != original:
            antal = sum(1 for _ in re.finditer(r'(src|href)="[^"]*/(ljud|video)/', s))
            total += antal
            print("  %-18s %d länkar" % (os.path.basename(path), antal))
            if not test:
                open(path, "w", encoding="utf-8").write(s)
    return total


def main():
    args = [a for a in sys.argv[1:] if a != "--test"]
    test = "--test" in sys.argv
    if not args:
        sys.exit(__doc__)
    if args[0] == "--lokalt":
        bas = ""
        print("Pekar om till lokala filer i media/")
    else:
        bas = args[0].rstrip("/")
        if not bas.startswith("http"):
            sys.exit("Basen måste börja med https:// — fick %r" % bas)
        print("Pekar om till %s" % bas)
    n = byt(bas, test)
    print("%s%d länkar" % ("Skulle ändra " if test else "Ändrade ", n))
    if bas and not test:
        print("\nKom ihåg: filerna måste ligga uppe innan du pushar, annars "
              "tystnar sajten.\n  ./verktyg/publicera-media.sh")


if __name__ == "__main__":
    main()
