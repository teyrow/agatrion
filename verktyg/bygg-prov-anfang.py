#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bygg provsidan för anfangstorlekar, docs/prov/anfang.html.

    python3 verktyg/bygg-prov-anfang.py

Sidan visar musikerporträtten i sex storlekar på anfangen, först i sidans egen
spaltbredd och sedan i en smal spalt som liknar en mobil. Den läser texterna
direkt ur index.html, så den är alltid i fas med det som står på sajten.

Storleken på riktigt sätts av `--anfang` i style.css. Vill du byta: titta här
först, sedan ändra variabeln. Sidan är noindex och länkas inte från menyn — den
är ett arbetsredskap, inte en del av sajten.
"""
import os
import re

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")
UT = os.path.join(SAJT, "prov")

STORLEKAR = ["3.1rem", "3.9rem", "4.4rem", "5.2rem", "5.8rem", "7.0rem"]


def musikerblock():
    """Musikerraderna ur index.html, utan FYLL I-kommentarerna."""
    s = open(os.path.join(SAJT, "index.html"), encoding="utf-8").read()
    m = re.search(r'<div class="musikerna">.*?\n      </div>', s, re.S)
    if not m:
        raise SystemExit("hittade inte musikerblocket i index.html")
    return re.sub(r"\n *<!--.*?-->", "", m.group(0), flags=re.S)


def etikett(storlek):
    return storlek.replace("rem", " rem").replace(".", ",")


def sida():
    block = musikerblock()

    def med(storlek):
        return block.replace('<div class="musikerna">',
                             '<div class="musikerna" style="--anfang:%s">' % storlek)

    d = ["<!DOCTYPE html>", '<html lang="sv">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<meta name="robots" content="noindex, nofollow">',
         "<title>Anfangstorlekar — AGA-trion</title>",
         '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
         '<link rel="stylesheet" href="/css/style.css">',
         "<style>%s</style>" % STIL, "</head>", "<body>", '<main class="wrap">',
         "<h1>Hur stor ska anfangen vara?</h1>",
         '<p class="ingress">Samma tre porträtt i sex storlekar. Först i sidans egen '
         "spaltbredd, sedan allihop i en smal spalt som liknar en mobil. Storleken som "
         "gäller på riktigt sätts av <code>--anfang</code> i style.css.</p>"]

    for storlek in STORLEKAR:
        d += ['<section class="prov">',
              "<h2>%s — bred spalt</h2>" % etikett(storlek),
              med(storlek), "</section>"]

    d.append('<section class="prov smal"><h2>samtliga i smal spalt</h2>')
    for storlek in STORLEKAR:
        d += ['<p class="markering">%s</p>' % etikett(storlek), med(storlek)]
    d += ["</section>", "</main>", "</body>", "</html>"]
    return "\n".join(d)


STIL = """
body { padding: 2rem 0 6rem }
.ingress { color: var(--muted); max-width: 40rem }
.prov { border-top: 2px solid var(--accent); margin-top: 3rem; padding-top: .6rem }
.prov > h2 { font-family: var(--sans); font-size: .8rem; text-transform: uppercase;
  letter-spacing: .08em; color: var(--accent); margin: 0 0 1rem }
.markering { font-family: var(--sans); font-size: .78rem; color: var(--muted);
  margin: 2rem 0 .5rem }
.smal .musikerna section { max-width: 22rem }
"""


if __name__ == "__main__":
    os.makedirs(UT, exist_ok=True)
    with open(os.path.join(UT, "anfang.html"), "w", encoding="utf-8") as fh:
        fh.write(sida())
    print("Skrev docs/prov/anfang.html — %d storlekar" % len(STORLEKAR))
