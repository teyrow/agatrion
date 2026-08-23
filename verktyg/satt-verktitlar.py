#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skriv om spårlistorna på lyssna.html och arkiv.html så att verk, sats och
tonsättare står utsatta.

Uppgifterna kommer ur verktyg/verk.py. Skriptet läser vilka ljudfiler varje
spår pekar på och byter ut rubrikerna — allt annat på sidorna lämnas ifred.

    python3 verktyg/satt-verktitlar.py            # skriv om
    python3 verktyg/satt-verktitlar.py --test     # visa bara vad som skulle ändras

Lyssnasidan grupperar per verk, med tonsättare och verk i mellanrubriken och
satserna som spårrader. Arkivsidan är en rak lista, så där står verket på varje
rad. Spår vars verk ännu inte är bekräftat får en kommentar med FYLL I intill.

Skriptet sätter också id på de inspelningar som är utvalda i verk.VAL, så att
repertoarsidan kan länka till dem, och bygger avsnittet "Enstaka stycken" på
lyssnasidan för de utvalda som annars bara finns i arkivet.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verk                                                    # noqa: E402

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sajten ligger i docs/ — allt utanför den mappen publiceras aldrig
SAJT = os.path.join(ROT, "docs")
# kommentaren mellan <li> och <p> är vår egen FYLL I-markering från förra körningen
# <li> kan bära ett id från förra körningen, och kommentaren mellan <li> och <p>
# är vår egen FYLL I-markering — båda måste mönstret släppa igenom, annars läser
# vi färre spår än blocket innehåller och spärren i skriv_om() slår till
SPAR_RE = re.compile(r'<li(?:\s[^>]*)?>\s*(?:<!--.*?-->\s*)*<p class="track-title">(.*?)</p>\s*'
                     r'(<audio[^>]*src="([^"]*)"[^>]*></audio>)\s*</li>', re.S)
TID_RE = re.compile(r'<span class="duration">([^<]*)</span>')


def nyckel(src):
    """media-sökväg -> "konsert/fil.mp3", oavsett om länken går till bucketen."""
    m = re.search(r"/ljud/([^/]+/[^/\"]+\.mp3)", src)
    return m.group(1) if m else None


def spar_i(block):
    ut = []
    for m in SPAR_RE.finditer(block):
        titel, audio, src = m.group(1), m.group(2), m.group(3)
        tid = TID_RE.search(titel)
        ut.append({"hela": m.group(0), "audio": audio, "fil": nyckel(src),
                   "tid": tid.group(1) if tid else None})
    return ut


OKAND = "FYLL I"


def rad(spar, visa_verk, indrag):
    u = verk.uppgift(spar["fil"])
    if not u:
        return None
    tonsattare, titel, sats, saker = u
    delar = []
    if visa_verk and titel != OKAND:
        delar.append(html.escape(titel))
        if sats:
            delar.append('<span class="movement">%s</span>' % html.escape(sats))
    elif not visa_verk and sats:
        # verket står redan i mellanrubriken; raden behöver bara satsen
        delar.append(html.escape(sats))
    if spar["tid"]:
        delar.append('<span class="duration">%s</span>' % spar["tid"])
    if visa_verk:
        delar.append('<span class="composer">%s</span>' % html.escape(tonsattare))
    i = " " * indrag
    ank = verk.ankare_for(spar["fil"])
    rader = ['%s<li%s>' % (i, ' id="%s"' % ank if ank else "")]
    if saker == "gissning":
        rader.append("%s  <!-- FYLL I: vilket verk är det h\u00e4r? Bekr\u00e4fta genom att "
                     "lyssna, se verktyg/bygg-urval.py -->" % i)
    rader.append('%s  <p class="track-title">%s</p>' % (i, " ".join(delar)))
    rader.append("%s  %s" % (i, spar["audio"]))
    rader.append("%s</li>" % i)
    return "\n".join(rader)


def rubrik(fil, indrag):
    """Tonsättaren, och verket när vi vet vilket det är."""
    tonsattare, titel, _, _ = verk.uppgift(fil)
    if titel == OKAND:
        return "%s<h3>%s</h3>" % (" " * indrag, html.escape(tonsattare))
    return ('%s<h3>%s <span class="years">%s</span></h3>'
            % (" " * indrag, html.escape(tonsattare), html.escape(titel)))


def bygg_grupperat(spar, indrag):
    """Lyssnasidan: en mellanrubrik per verk, satserna som rader under."""
    ut, i = [], 0
    while i < len(spar):
        vid = verk.SPAR.get(spar[i]["fil"], (None,))[0]
        j = i
        while j < len(spar) and verk.SPAR.get(spar[j]["fil"], (None,))[0] == vid:
            j += 1
        ut.append(rubrik(spar[i]["fil"], indrag))
        ut.append('%s<ol class="tracks">' % (" " * indrag))
        ut += [rad(s, False, indrag + 2) for s in spar[i:j]]
        ut.append("%s</ol>" % (" " * indrag))
        i = j
    return "\n".join(ut)


def bygg_platt(spar, indrag):
    """Arkivsidan: rak lista där varje rad bär verk, sats och tonsättare."""
    ut = ['%s<ol class="tracks">' % (" " * indrag)]
    ut += [rad(s, True, indrag + 2) for s in spar]
    ut.append("%s</ol>" % (" " * indrag))
    return "\n".join(ut)


ENSTAKA_START = "  <!-- enstaka:start -->"
ENSTAKA_SLUT = "  <!-- enstaka:slut -->"


def bygg_enstaka(bas):
    """Lyssnasidans enda innehållsavsnitt: en rak lista över det som går att höra.

    Urvalet står i verk.VAL. Ingen gruppering — varje rad bär allt den behöver:
    verk, sats, tonsättare, och var och när inspelningen gjordes. Hela konserter
    hör hemma i arkivet; den här sidan svarar på "hur låter det verket".
    """
    if not verk.VAL:
        return ""

    def sortnyckel(fil):
        vid, sats, _ = verk.SPAR[fil]
        v = verk.VERK[vid]
        return (v["tonsattare"].split()[-1], v["titel"], sats)

    ut = [ENSTAKA_START,
          '  <section class="section" id="inspelningar">',
          '    <div class="wrap">',
          "      <h2>Inspelningar</h2>",
          '      <p class="section-lead prose">Ett litet urval — fem verk i de inspelningar '
          "vi tycker bäst om. Under varje rad står var och när den gjordes.</p>",
          '      <ol class="tracks">']
    for fil in sorted(verk.VAL, key=sortnyckel):
        tonsattare, titel, sats, saker = verk.uppgift(fil)
        plats, datum, _ = verk.KONSERTER[fil.split("/")[0]]
        namn = html.escape(titel)
        if sats:
            namn += ' <span class="movement">%s</span>' % html.escape(sats)
        ank = verk.ankare_for(fil)
        ut += ['        <li%s>' % (' id="%s"' % ank if ank else ""),
               '          <p class="track-title">%s <span class="composer">%s</span></p>'
               % (namn, html.escape(tonsattare)),
               '          <p class="recording-meta">%s, %s</p>'
               % (html.escape(plats), html.escape(datum)),
               '          <audio controls preload="none" src="%s/ljud/%s"></audio>'
               % (bas, html.escape(fil)),
               "        </li>"]
    ut += ["      </ol>", "    </div>", "  </section>", ENSTAKA_SLUT]
    return "\n".join(ut)


def mediabas(s):
    """Var ljudet ligger. Lyssnasidan kan sakna ljudlänkar just när avsnittet är
    urlyft, så arkivet får svara i andra hand."""
    for text in (s, open(os.path.join(SAJT, "arkiv.html"), encoding="utf-8").read()):
        m = re.search(r'src="(https?://[^"]*?)/ljud/', text)
        if m:
            return m.group(1)
    raise SystemExit("hittade ingen mediabas — kör verktyg/satt-mediabas.py först")


def satt_enstaka(s):
    """Byt ut avsnittet, eller lägg in det efter liveinspelningarna första gången."""
    nytt = bygg_enstaka(mediabas(s))
    if ENSTAKA_START in s:
        i = s.index(ENSTAKA_START)
        j = s.index(ENSTAKA_SLUT) + len(ENSTAKA_SLUT)
        return s[:i] + nytt + s[j:]
    # direkt före SoundCloud-notisen, som avslutar inspelningsdelen
    märke = '  <section class="section">\n    <div class="wrap">\n      <p class="recording-meta">Äldre'
    if märke not in s:
        raise SystemExit("hittade inte var avsnittet Enstaka stycken ska in")
    return s.replace(märke, nytt + "\n\n" + märke, 1)


def skriv_om(sidnamn, grupperat, test):
    bana = os.path.join(SAJT, sidnamn)
    s = original = open(bana, encoding="utf-8").read()
    # avsnittet byggs om från grunden längre ner, så lyft undan det medan
    # artikelloopen går — annars skulle den försöka skriva om det också
    if ENSTAKA_START in s:
        i, j = s.index(ENSTAKA_START), s.index(ENSTAKA_SLUT) + len(ENSTAKA_SLUT)
        s = s[:i] + ENSTAKA_START + ENSTAKA_SLUT + s[j:]
    ändrade = 0
    for artikel in re.findall(r'<article class="recording".*?</article>', s, re.S):
        spar = spar_i(artikel)
        if not spar or any(x["fil"] is None or verk.uppgift(x["fil"]) is None for x in spar):
            continue
        # skriv aldrig om ett block vi inte lyckats läsa i sin helhet — då skulle
        # spåren vi missade försvinna ur sidan
        if len(spar) != artikel.count("<audio"):
            raise SystemExit("%s: hittade %d spår men %d ljudelement i %s — avbryter"
                             % (sidnamn, len(spar), artikel.count("<audio"),
                                re.search(r'id="([^"]*)"', artikel).group(1)))
        # allt från första mellanrubriken eller spårlistan fram till </article>
        start = artikel.find("<h3>") if grupperat else artikel.find('<ol class="tracks">')
        if start < 0:
            start = artikel.find('<ol class="tracks">')
        radslut = artikel.rfind("\n", 0, start)
        indrag = start - radslut - 1
        avslut = re.search(r"\n(\s*)</article>", artikel)
        ny = (artikel[:start]
              + (bygg_grupperat(spar, indrag) if grupperat
                 else bygg_platt(spar, indrag)).lstrip()
              + "\n%s</article>" % avslut.group(1))
        if ny != artikel:
            s = s.replace(artikel, ny)
            ändrade += 1
    if grupperat:
        s = satt_enstaka(s)
    if test:
        print("%s: %d block skulle skrivas om" % (sidnamn, ändrade))
    elif s != original:
        open(bana, "w", encoding="utf-8").write(s)
        print("%s: skrev om %d block" % (sidnamn, ändrade))
    else:
        print("%s: oförändrad" % sidnamn)


if __name__ == "__main__":
    test = "--test" in sys.argv
    skriv_om("lyssna.html", grupperat=True, test=test)
    skriv_om("arkiv.html", grupperat=False, test=test)
