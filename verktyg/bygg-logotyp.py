#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rita AGA-trions logotyp och märke som SVG.

    python3 verktyg/bygg-logotyp.py

Skriver docs/media/bild/logotyp.svg (liggande) och docs/favicon.svg (kvadratiskt
märke). Båda byter färg med systemets mörka läge via en mediefråga inuti filen.

Formen är anfangen från sajten, förstorad: ett rundat block med AGA i omvända
färger, och fem tunna strängar tvärs över — tre stämmor räckte inte, fem läser
som ett notsystem. Efter blocket står -trion i vanlig textfärg.

Bokstäverna är **banor**, inte text. Det är hela poängen med en logotyp: den ska
se likadan ut oavsett vilka typsnitt som finns på datorn som visar den.
Konturerna ligger i verktyg/logotyp/glyfer.json och är utdragna ur TeX Gyre
Pagella Bold — en fri Palatino, samma formvärld som sajtens brödtext. Se
docs/profil/ för licensen.

Måttsystemet: versalhöjden är 100 enheter, y växer nedåt.
"""
import json
import os
import re

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")
G = json.load(open(os.path.join(ROT, "verktyg", "logotyp", "glyfer.json"),
                   encoding="utf-8"))["bold"]

# samma värden som sajtens :root
LJUS = dict(ruta="#2d4a72", inuti="#fbf9f5", ord="#1c1a17")
MORK = dict(ruta="#9dbbe6", inuti="#16171a", ord="#ece7dd")

LUFT = 38          # över och under versalerna
SIDLUFT = 32       # blockets vänstra och högra marginal
SPARR = 30         # mellan bokstäverna i blocket
GLORIA = 15        # bokstävernas kantlinje, som bryter strängarna
LINJER = 5
TJOCKLEK = 4
TON = .5           # strängarnas genomskinlighet
RADIE = 14
MELLANRUM = 34     # mellan blocket och ordet


def kapa(bana, decimaler=2):
    """Konturerna kommer med sjutton decimaler ur typsnittet. Två räcker gott —
    versalhöjden är 100 enheter, så det är hundradels procent av bokstaven, och
    filen krymper till hälften."""
    return re.sub(r"-?\d+\.\d+",
                  lambda m: ("%.*f" % (decimaler, float(m.group()))).rstrip("0").rstrip(".")
                  or "0", bana)


def bokstav(tecken, x, baslinje, fyll, gloria=None):
    g = G[tecken]
    kant = ""
    if gloria:
        kant = (' stroke="%s" stroke-width="%s" stroke-linejoin="round" '
                'style="paint-order:stroke"' % (gloria, GLORIA))
    return ('  <path transform="translate(%s %s)" d="%s" fill="%s"%s/>'
            % (round(x, 2), round(baslinje, 2), kapa(g["bana"]), fyll, kant)), g["bredd"]


def strangar(bredd, hojd, fyll):
    steg = hojd / (LINJER + 1)
    ut = ['  <g stroke="%s" stroke-opacity="%s" stroke-width="%s" stroke-linecap="round">'
          % (fyll, TON, TJOCKLEK)]
    for i in range(1, LINJER + 1):
        y = round(steg * i, 1)
        ut.append('    <line x1="0" y1="%s" x2="%s" y2="%s"/>' % (y, round(bredd, 2), y))
    ut.append("  </g>")
    return ut


def logotyp(med_ord=True):
    """Returnerar (rader, bredd, höjd) i logotypens eget måttsystem."""
    aga = "AGA"
    bredder = [G[t]["bredd"] for t in aga]
    bw = sum(bredder) + SPARR * (len(aga) - 1) + 2 * SIDLUFT
    bh = LUFT + 100 + LUFT
    baslinje = LUFT + 100

    d = ['  <rect class="ruta" x="0" y="0" width="%s" height="%s" rx="%s"/>'
         % (round(bw, 2), bh, RADIE)]
    d += strangar(bw, bh, "var(--inuti)")
    x = SIDLUFT
    for t, b in zip(aga, bredder):
        rad, _ = bokstav(t, x, baslinje, "var(--inuti)", "var(--ruta)")
        d.append(rad)
        x += b + SPARR
    total = bw
    if med_ord:
        x = bw + MELLANRUM
        for t in "-trion":
            rad, b = bokstav(t, x, baslinje, "var(--ord)")
            d.append(rad)
            x += b
        total = x
    return d, total, bh


def marke():
    """Kvadratiskt märke: ett A, samma strängar."""
    sida = 176
    d = ['  <rect class="ruta" x="0" y="0" width="%s" height="%s" rx="%s"/>'
         % (sida, sida, RADIE)]
    d += strangar(sida, sida, "var(--inuti)")
    b = G["A"]["bredd"]
    rad, _ = bokstav("A", (sida - b) / 2, (sida + 100) / 2, "var(--inuti)", "var(--ruta)")
    d.append(rad)
    return d, sida


STIL = """    :root { --ruta: %(ruta)s; --inuti: %(inuti)s; --ord: %(ord)s }
    @media (prefers-color-scheme: dark) {
      :root { --ruta: %(mruta)s; --inuti: %(minuti)s; --ord: %(mord)s }
    }
    .ruta { fill: var(--ruta) }"""


def fil(rader, bredd, hojd, titel):
    stil = STIL % dict(ruta=LJUS["ruta"], inuti=LJUS["inuti"], ord=LJUS["ord"],
                       mruta=MORK["ruta"], minuti=MORK["inuti"], mord=MORK["ord"])
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" role="img" '
        'aria-label="%s">' % (round(bredd, 2), round(hojd, 2), titel),
        "  <title>%s</title>" % titel,
        "  <style>", stil, "  </style>",
        *rader,
        "</svg>", ""])


def skriv():
    bild = os.path.join(SAJT, "media", "bild")
    os.makedirs(bild, exist_ok=True)

    rader, bredd, hojd = logotyp()
    with open(os.path.join(bild, "logotyp.svg"), "w", encoding="utf-8") as fh:
        fh.write(fil(rader, bredd, hojd, "AGA-trion"))

    rader, bredd, hojd = logotyp(med_ord=False)
    with open(os.path.join(bild, "logotyp-block.svg"), "w", encoding="utf-8") as fh:
        fh.write(fil(rader, bredd, hojd, "AGA"))

    rader, sida = marke()
    with open(os.path.join(SAJT, "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(fil(rader, sida, sida, "AGA-trion"))

    for namn in ("media/bild/logotyp.svg", "media/bild/logotyp-block.svg", "favicon.svg"):
        p = os.path.join(SAJT, namn)
        print("%-32s %5d B" % (namn, os.path.getsize(p)))


if __name__ == "__main__":
    skriv()
