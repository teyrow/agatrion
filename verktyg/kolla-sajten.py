#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gå igenom sajten och leta efter fel som är lätta att missa.

    python3 verktyg/kolla-sajten.py            # allt utom nätanrop
    python3 verktyg/kolla-sajten.py --natet     # kolla även externa länkar och media

Kontrollerna är sådana som Lighthouse inte tar: att navigationen ser likadan ut
på alla sidor, att aria-current sitter rätt, att inga interna länkar pekar i
tomma luften, att ljudet har preload="none", att inget laddas från en främmande
domän, och att kontrasterna räcker i både ljust och mörkt läge.

Utskriften är rader som börjar med FEL eller VARNING. Inga rader = allt är bra.
"""
import argparse
import glob
import html.parser
import os
import re
import sys
import urllib.error
import urllib.request

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")
PUBLIKA = ["index.html", "konserter.html", "repertoar.html", "lyssna.html", "kontakt.html"]
OLANKADE = ["arkiv.html", "404.html", "profil/index.html", "granska/index.html",
            "prov/anfang.html"]
EGEN_DOMAN = ("agatrion.se", "agatrion-media.objects.dc-fbg1.glesys.net")

fel = []
varning = []


def anmal(lista, sida, text):
    lista.append("%-22s %s" % (sida, text))


# ------------------------------------------------------------------ läsning
class Sidan(html.parser.HTMLParser):
    """Plockar ut det vi behöver: taggar, attribut, rubriker, text."""
    TOMMA = {"meta", "link", "br", "img", "source", "input", "hr", "col", "area"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.obalans = []
        self.taggar = []
        self.rubriker = []
        self._rubrik = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.taggar.append((tag, d))
        if tag not in self.TOMMA:
            self.stack.append(tag)
        if re.fullmatch(r"h[1-6]", tag):
            self._rubrik = (int(tag[1]), [])

    def handle_endtag(self, tag):
        if tag in self.TOMMA:
            return
        if not self.stack or self.stack[-1] != tag:
            self.obalans.append((tag, list(self.stack[-3:])))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()
        if re.fullmatch(r"h[1-6]", tag) and self._rubrik:
            self.rubriker.append((self._rubrik[0], " ".join("".join(self._rubrik[1]).split())))
            self._rubrik = None

    def handle_data(self, data):
        self.text.append(data)
        if self._rubrik:
            self._rubrik[1].append(data)


def las(sida):
    p = os.path.join(SAJT, sida)
    d = open(p, encoding="utf-8").read()
    s = Sidan()
    s.feed(d)
    return d, s


# ------------------------------------------------------------------ kontroller
def kolla_struktur(sida, d, s):
    if s.obalans:
        for tagg, stack in s.obalans:
            anmal(fel, sida, "obalanserad </%s>, öppna taggar %s" % (tagg, stack))
    if s.stack:
        anmal(fel, sida, "taggar som aldrig stängs: %s" % s.stack)

    if not d.lstrip().lower().startswith("<!doctype html>"):
        anmal(fel, sida, "saknar <!DOCTYPE html>")
    if 'lang="sv"' not in d:
        anmal(fel, sida, "saknar lang=\"sv\"")
    if 'charset="utf-8"' not in d:
        anmal(fel, sida, "saknar charset")
    if "viewport" not in d:
        anmal(fel, sida, "saknar viewport")

    ettor = [r for n, r in s.rubriker if n == 1]
    if len(ettor) != 1:
        anmal(fel, sida, "har %d h1 (ska vara exakt en): %s" % (len(ettor), ettor))
    niva = 0
    for n, text in s.rubriker:
        if niva and n > niva + 1:
            anmal(varning, sida, "hoppar från h%d till h%d vid %r" % (niva, n, text[:40]))
        niva = n


def kolla_meta(sida, d, s):
    titel = re.search(r"<title>(.*?)</title>", d, re.S)
    if not titel:
        anmal(fel, sida, "saknar <title>")
    elif not 15 <= len(titel.group(1)) <= 65:
        anmal(varning, sida, "titeln är %d tecken (15–65 är lagom)" % len(titel.group(1)))

    besk = re.search(r'<meta name="description" content="(.*?)"', d, re.S)
    noindex = 'name="robots"' in d and "noindex" in d
    # description spelar bara roll för sidor som får hamna i sökresultaten
    if sida in PUBLIKA:
        if not besk:
            anmal(fel, sida, "saknar description")
        elif not 50 <= len(besk.group(1)) <= 165:
            anmal(varning, sida, "description är %d tecken (50–165 är lagom)"
                  % len(besk.group(1)))

    if sida in PUBLIKA:
        if 'rel="canonical"' not in d:
            anmal(fel, sida, "saknar canonical")
        for prop in ("og:title", "og:description", "og:image", "og:url"):
            if prop not in d:
                anmal(varning, sida, "saknar %s" % prop)
        if noindex:
            anmal(fel, sida, "är noindex fast den ska synas")
    elif sida != "404.html" and not noindex:
        anmal(fel, sida, "är olänkad men saknar noindex")


def kolla_navigation(sidor):
    """Sidhuvudet är kopierat till varje fil — det måste vara identiskt överallt.

    Hela huvudet jämförs, inte bara menyn: när arkivsidans mall inte hängde med
    logotypen behöll den textvarumärket, och en kontroll som bara läste <nav>
    märkte ingenting."""
    referens = huvudreferens = None
    for sida, d, _ in sidor:
        huvud = re.search(r'<header class="site-header">.*?</header>', d, re.S)
        if not huvud:
            anmal(fel, sida, "saknar sidhuvudet")
        else:
            utan = re.sub(r'\s*aria-current="page"', "", huvud.group(0))
            if huvudreferens is None:
                huvudreferens = (sida, utan)
            elif utan != huvudreferens[1]:
                anmal(fel, sida, "sidhuvudet skiljer sig från det i %s" % huvudreferens[0])

        m = re.search(r'<nav class="site-nav".*?</nav>', d, re.S)
        if not m:
            anmal(fel, sida, "saknar huvudmenyn")
            continue
        utan_current = re.sub(r'\s*aria-current="page"', "", m.group(0))
        if referens is None:
            referens = (sida, utan_current)
        elif utan_current != referens[1]:
            anmal(fel, sida, "menyn skiljer sig från den i %s" % referens[0])

        aktuella = re.findall(r'<a href="([^"]+)"[^>]*aria-current="page"', m.group(0))
        vantad = "/" if sida == "index.html" else "/" + sida
        if sida in PUBLIKA:
            if aktuella != [vantad]:
                anmal(fel, sida, "aria-current står på %s, borde vara %s"
                      % (aktuella or "ingen", vantad))
        elif aktuella:
            anmal(varning, sida, "har aria-current fast den inte är en menysida")


def kolla_lankar(sidor, natet):
    """Interna länkar ska peka på något som finns."""
    externa = set()
    for sida, d, s in sidor:
        for tagg, attr in s.taggar:
            for namn in ("href", "src"):
                url = attr.get(namn)
                if not url or url.startswith(("mailto:", "tel:", "data:", "#")):
                    continue
                if url.startswith(("http://", "https://")):
                    externa.add((sida, url))
                    continue
                bana, _, ankare = url.partition("#")
                if not bana:
                    continue
                mal = os.path.join(SAJT, bana.lstrip("/"))
                if os.path.isdir(mal):
                    mal = os.path.join(mal, "index.html")
                if not os.path.exists(mal):
                    anmal(fel, sida, "%s pekar på %s som inte finns" % (namn, url))
                elif ankare and mal.endswith(".html"):
                    text = open(mal, encoding="utf-8").read()
                    if 'id="%s"' % ankare not in text:
                        anmal(fel, sida, "%s saknar ankaret #%s" % (url, ankare))
    # tredjepartsanrop vid sidladdning är sajtens enda hårda regel
    for sida, url in sorted(externa):
        doman = url.split("/")[2]
        laddas = any(url in re.search(r"<(?:img|script|link|source|audio|video|iframe)[^>]*%s[^>]*>"
                                      % re.escape(url), d, re.S).group(0)
                     for s2, d, _ in sidor if s2 == sida
                     and re.search(r"<(?:img|script|link|source|audio|video|iframe)[^>]*%s"
                                   % re.escape(url), d, re.S))
        if laddas and not doman.endswith(EGEN_DOMAN):
            anmal(fel, sida, "laddar %s från främmande domän vid sidladdning" % url)
    if natet:
        for sida, url in sorted(externa):
            kod = hamta(url)
            if kod >= 400 or kod == 0:
                anmal(varning, sida, "%s svarar %s" % (url, kod or "inte alls"))


def hamta(url):
    begaran = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "agatrion-lankkoll"})
    try:
        with urllib.request.urlopen(begaran, timeout=15) as svar:
            return svar.status
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):                 # vissa svarar inte på HEAD
            try:
                with urllib.request.urlopen(
                        urllib.request.Request(url, headers={"User-Agent": "agatrion"}),
                        timeout=15) as svar:
                    return svar.status
            except Exception:
                return e.code
        return e.code
    except Exception:
        return 0


def kolla_media(sidor):
    for sida, d, s in sidor:
        for tagg, attr in s.taggar:
            if tagg == "audio" and attr.get("preload") != "none":
                anmal(fel, sida, "ljudspelare utan preload=\"none\" — laddar ner allt")
            if tagg == "video" and attr.get("preload") != "none":
                anmal(varning, sida, "video utan preload=\"none\"")
            if tagg == "img":
                if not attr.get("alt") and attr.get("alt") != "":
                    anmal(fel, sida, "bild utan alt: %s" % attr.get("src"))
                if not (attr.get("width") and attr.get("height")):
                    anmal(varning, sida, "bild utan mått, sidan hoppar: %s" % attr.get("src"))
        for m in re.finditer(r'<a class="lyssna"[^>]*>', d):
            pass


def kolla_bildfiler():
    for p in sorted(glob.glob(os.path.join(SAJT, "media", "bild", "*"))):
        storlek = os.path.getsize(p)
        if storlek > 400_000:
            anmal(varning, "media/bild", "%s är %d kB — skala ner eller byt till webp"
                  % (os.path.basename(p), storlek // 1024))


# ------------------------------------------------------------------ kontrast
def lum(hexf):
    r, g, b = (int(hexf[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def kontrast(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + .05) / (l2 + .05)


def kolla_kontraster():
    css = open(os.path.join(SAJT, "css", "style.css"), encoding="utf-8").read()
    varde = r"(--[a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;"
    ljus = dict(re.findall(varde, css.split("@media")[0]))
    m = re.search(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*{\s*:root\s*{([^}]*)}", css)
    mork = dict(re.findall(varde, m.group(1))) if m else {}
    par = [("--fg", "--bg", 4.5, "brödtext mot botten"),
           ("--muted", "--bg", 4.5, "dämpad text mot botten"),
           ("--muted", "--bg-soft", 4.5, "dämpad text mot tonad botten"),
           ("--accent", "--bg", 4.5, "länkar mot botten"),
           ("--bg", "--accent", 4.5, "anfangens text mot dess ruta")]
    for läge, p in (("ljust", ljus), ("mörkt", mork)):
        for a, b, krav, vad in par:
            if a not in p or b not in p:
                continue
            k = kontrast(p[a], p[b])
            if k < krav:
                anmal(fel, "kontrast/" + läge, "%s: %.2f:1, kravet är %.1f (%s mot %s)"
                      % (vad, k, krav, p[a], p[b]))
            elif k < krav + 1:
                anmal(varning, "kontrast/" + läge, "%s: %.2f:1, knappt över kravet"
                      % (vad, k))


def main():
    a = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--natet", action="store_true", help="kolla även externa länkar")
    args = a.parse_args()

    sidor = []
    for sida in PUBLIKA + OLANKADE:
        if not os.path.exists(os.path.join(SAJT, sida)):
            anmal(fel, sida, "filen saknas")
            continue
        d, s = las(sida)
        sidor.append((sida, d, s))
        kolla_struktur(sida, d, s)
        kolla_meta(sida, d, s)

    kolla_navigation([x for x in sidor if x[0] in PUBLIKA + ["arkiv.html", "404.html"]])
    kolla_lankar(sidor, args.natet)
    kolla_media(sidor)
    kolla_bildfiler()
    kolla_kontraster()

    for rad in fel:
        print("FEL      %s" % rad)
    for rad in varning:
        print("VARNING  %s" % rad)
    print("\n%d sidor granskade — %d fel, %d varningar" % (len(sidor), len(fel), len(varning)))
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
