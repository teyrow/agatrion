#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Koda arkivets inspelningar och skriv arkiv.html.

Arkivet är sidan som inte länkas från menyn: konserter som finns inspelade men
inte hör hemma på lyssnasidan. Källorna ligger utanför repot — i Apple Music,
i tempschumann och bland Audacity-projekten.

    python3 verktyg/bygg-arkiv.py            # koda det som saknas + skriv sidan
    python3 verktyg/bygg-arkiv.py --bara-sida  # skriv bara om arkiv.html

Ljudet hamnar i media/ljud/<konsert>/ och laddas upp med publicera-media.sh.

Spårrubrikerna här är bara de råa etiketterna. Verk, sats och tonsättare sätts
efteråt av verktyg/satt-verktitlar.py, som skriptet kör automatiskt på slutet —
kör aldrig det här skriptet utan att låta det steget gå igenom, annars ramlar
sidan tillbaka till namn som "Haydn II".
"""
import html
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import wave

import numpy as np

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sajten ligger i docs/ — allt utanför den mappen publiceras aldrig
SAJT = os.path.join(ROT, "docs")
OUT = os.path.join(SAJT, "media", "ljud")
TMP = "/tmp/agatrion-arkiv"
AM = os.path.expanduser("~/Music/Music/Media.localized/Music/AGA-trion")
TS = "/Users/aj/tempschumann"
TARGET_PEAK = 10 ** (-1.5 / 20)
BAS = "https://agatrion-media.objects.dc-fbg1.glesys.net"

# ---------------------------------------------------------------- konserter
# (slug, plats, datum, ingress, källa, spår)
AIFF = [
    ("lillkyrkan-2021", "Lillkyrkan, Motala", "18 juli 2021",
     "Musikgudstjänst i sommarkväll. Samma program spelades några dagar senare på "
     "Bjärka-Säby och i Västra Ryd.",
     os.path.join(AM, "Lillkyrkan Motala 2021"),
     [("01 Haydn trio C-dur.aiff", "Pianotrio i C-dur", "Joseph Haydn"),
      ("02 Sommarsång W.P.H.aiff", "Sommarsång", "Wilhelm Peterson-Berger"),
      ("03 Lawn tennis W.P.H.aiff", "Lawn tennis", "Wilhelm Peterson-Berger"),
      ("04 Fantasiestücke R. Schumann.aiff", "Fantasiestücke", "Robert Schumann"),
      ("05 Mediation, F.Bridge.aiff", "Romance", "Frank Bridge"),
      ("06 Trio i Ess, A. Meier-Röntgen.aiff", "Pianotrio i Ess-dur", "Amanda Maier-Röntgen"),
      ("07 Sång till Lotta, J. Sandström.aiff", "Sång till Lotta", "Jan Sandström")]),
    ("bjarka-saby-2021", "Nya Slottet Bjärka-Säby", "22 juli 2021",
     "Musik i Nya Slottet.",
     os.path.join(AM, "Bjärka Säby 2021"),
     [("01 Haydn C-dur.aiff", "Pianotrio i C-dur", "Joseph Haydn"),
      ("02 Sommarsång.aiff", "Sommarsång", "Wilhelm Peterson-Berger"),
      ("03 Lawn tennis.aiff", "Lawn tennis", "Wilhelm Peterson-Berger"),
      ("04 Fantasiestücke.aiff", "Fantasiestücke", "Robert Schumann"),
      ("05 Meditation, Bridge.aiff", "Romance", "Frank Bridge"),
      ("06 A.M. Röntgen.aiff", "Pianotrio i Ess-dur", "Amanda Maier-Röntgen"),
      ("07 Sång till Lotta.aiff", "Sång till Lotta", "Jan Sandström")]),
    ("vastra-ryd-2021", "Västra Ryds kyrka, Rydsnäs", "25 juli 2021",
     "Musikens kvinnor.",
     os.path.join(AM, "Västra Ryds kyrka, Ydre"),
     [("01 Pianotrio i ess. A. Maier-Röntgen.aiff", "Pianotrio i Ess-dur", "Amanda Maier-Röntgen"),
      ("02 Andante. C Schumann.aiff", "Andante", "Clara Schumann"),
      ("03 Scherzo. C Schumann.aiff", "Scherzo", "Clara Schumann"),
      ("04 Chaminade.aiff", "Ur pianotrion", "Cécile Chaminade"),
      ("05 Sång till Lotta.aiff", "Sång till Lotta", "Jan Sandström")]),
    ("vreta-2021", "Vreta klosters kyrka", "12 september 2021",
     "2⨉3 — två trior av Clara Schumann och Amanda Maier-Röntgen.",
     os.path.join(AM, "Vreta kloster 2021"),
     [("01 Clara Schumann I.aiff", "Allegro moderato", "Clara Schumann"),
      ("02 Clara Schumann II.aiff", "Scherzo och Trio", "Clara Schumann"),
      ("03 Clara Schumann III.aiff", "Andante", "Clara Schumann"),
      ("04 Clara Schumann IV.aiff", "Allegretto", "Clara Schumann"),
      ("05 Amanda Maier Röntgen I.aiff", "Allegro", "Amanda Maier-Röntgen"),
      ("06 Amanda Maier Röntgen II.aiff", "Scherzo", "Amanda Maier-Röntgen"),
      ("07 Amanda Maier Röntgen III.aiff", "Andante", "Amanda Maier-Röntgen"),
      ("08 Amanda Maier Röntgen IV.aiff", "Finale. Allegro con fuoco", "Amanda Maier-Röntgen"),
      ("09 Sång till Lotta.aiff", "Sång till Lotta", "Jan Sandström")]),
    ("motala-2022", "Motala kyrka", "26 februari 2022",
     "Musikandakt: Robert Schumanns pianotrio nr 2 i F-dur, op. 80, i sin helhet.",
     os.path.join(AM, "Motala 2022, Robert Schumann, pianotrio nr 2"),
     [("01 Sehr lebhaft.aiff", "Sehr lebhaft", "Robert Schumann"),
      ("02 Mit innigem Ausdruck - Lebhaft.aiff", "Mit innigem Ausdruck – Lebhaft", "Robert Schumann"),
      ("03 In mässiger Bewegung.aiff", "In mässiger Bewegung", "Robert Schumann"),
      ("04 Nicht zu rasch.aiff", "Nicht zu rasch", "Robert Schumann")]),
]

WAV = [
    ("landeryd-2022", "Landeryds kyrka, Linköping", "10 juli 2022", "Sommarmusik.",
     os.path.join(TS, "landeryd", "Landeryd20220710.wav"),
     os.path.join(TS, "landeryd", "Label Track.txt")),
    ("bjarka-saby-2022", "Nya Slottet Bjärka-Säby", "14 juli 2022",
     "Sommarkonsert — det utförligaste programmet vi har bevarat.",
     os.path.join(TS, "bjarka2022", "bjärka20220714-175324.wav"),
     os.path.join(TS, "landeryd", "bjärka.txt")),
    ("ekeby-2023", "Ekeby kyrka, Boxholm", "11 mars 2023", "Musik i fastan.",
     os.path.join(TS, "Ekeby2023", "aga-ekeby2023.wav"),
     os.path.join(TS, "Ekeby2023", "Labels 1.txt")),
    ("skanninge-2024", "Rådhuset, Skänninge", "4 februari 2024",
     "Hos Lindbladsällskapet: Robert Schumanns pianotrio nr 2 och Piazzolla.",
     os.path.join(TS, "Lindbladsskällskapet2024", "050614_0137.wav"),
     os.path.join(TS, "Lindbladsskällskapet2024", "Labels 1.txt")),
]

FARDIGA_MP3 = [
    ("rassnas-2023", "Råssnäskyrkan, Motala", "1 januari 2023",
     "Nyårsdagen.", os.path.join(TS, "Råssnäs2023"),
     [("01-Haydn pianotrio G-dur.mp3", "Pianotrio i G-dur", "Joseph Haydn"),
      ("02-Bridge Meditation.mp3", "Romance", "Frank Bridge"),
      ("03-Piazolla Oblivion.mp3", "Oblivion", "Astor Piazzolla"),
      ("04-Låt till Lotta - Sandström.mp3", "Sång till Lotta", "Jan Sandström"),
      ("05-Mendelsohn sats 3 Pianotrio.mp3", "Pianotrio, tredje satsen", "Felix Mendelssohn")]),
]

# Konserter som redan är kodade sedan tidigare — de låg bara på lyssnasidan, som
# numera visar ett urval per verk i stället för hela konserter. Spårtitlarna
# sätts av satt-verktitlar.py, så här behövs bara plats, datum och ingress.
REDAN_KODADE = [
    ("tranas-2026", "Tranås kyrka", "7 mars 2026",
     "Fastemusik — meditativa toner. De långsamma satserna ur tre pianotrior, "
     "därefter Glière, Juon, Chaminade och John Williams."),
    ("brannestad-2024", "Brännestad musikateljé, Huaröd", "10 november 2024",
     "En temadag med kvinnliga tonsättare hemma hos Tomas och Tove på Linderödsåsen: "
     "Clara Schumanns och Amanda Maier-Röntgens pianotrior, med Chaminade som extranummer."),
    ("tranas-2024", "Tranås kyrka", "3 november 2024",
     "Amanda Maier-Röntgen och Clara Schumanns pianotrior, med Chaminade och "
     "Sång till Lotta som avslutning."),
]

VIDEO = [
    ("ekebyborna-2021", "Ekebyborna hembygdsgård", "17 juli 2021",
     "Tre telefonklipp från sommarspelningen inomhus, i full HD.",
     [("ekebyborna-2021-1.mp4", "Klipp 1"),
      ("ekebyborna-2021-2.mp4", "Klipp 2"),
      ("ekebyborna-2021-3.mp4", "Klipp 3")]),
]


def slug(text):
    t = text.lower().replace("ä", "a").replace("å", "a").replace("ö", "o").replace("é", "e")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return "-".join(filter(None, re.sub(r"[^a-z0-9]+", "-", t).split("-")))[:60]


def parse_labels(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    rader = re.findall(r"(\d+\.\d+)\t(\d+\.\d+)\t(.*?)(?=\s*\d+\.\d+\t\d+\.\d+\t|\s*\Z)", txt, re.S)
    return [(float(a), float(b), " ".join(t.split())) for a, b, t in rader]


def lame(indata, dest, gain, titel, tonsattare, album, ar, nr, raw=False, rate=48):
    cmd = ["lame", "--scale", "%.4f" % gain, "-m", "j", "-V", "3", "--quiet",
           "--tt", titel, "--ta", "AGA-trion", "--tl", album, "--ty", ar,
           "--tn", str(nr), "--tg", "Classical"]
    if tonsattare:
        cmd += ["--tc", tonsattare]
    if raw:
        cmd = cmd[:1] + ["-r", "-s", str(rate), "--bitwidth", "16", "--signed",
                         "--little-endian"] + cmd[1:] + ["-", dest]
        return subprocess.Popen(cmd, stdin=subprocess.PIPE)
    subprocess.run(cmd + [indata, dest], check=True)


def toppen_wav16(vagar):
    topp = 1
    for v in vagar:
        with wave.open(v, "rb") as w:
            n, rate = w.getnframes(), w.getframerate()
            pos = 0
            while pos < n:
                cnt = min(20 * rate, n - pos)
                w.setpos(pos)
                a = np.frombuffer(w.readframes(cnt), dtype="<i2")
                if a.size:
                    topp = max(topp, int(np.abs(a).max()))
                pos += cnt
    return topp


def koda_aiff(slug_namn, mapp, spar, album, ar):
    d = os.path.join(OUT, slug_namn)
    os.makedirs(d, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    vagar = []
    for i, (fil, _, _) in enumerate(spar):
        w = os.path.join(TMP, "%s-%02d.wav" % (slug_namn, i))
        if not os.path.exists(w):
            subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@48000",
                            os.path.join(mapp, fil), w], check=True, capture_output=True)
        vagar.append(w)
    gain = min(TARGET_PEAK * 32767 / toppen_wav16(vagar), 8.0)
    for i, (w, (_, titel, tons)) in enumerate(zip(vagar, spar), 1):
        namn = "%02d-%s.mp3" % (i, slug(("%s %s" % (tons, titel)).strip()))
        dest = os.path.join(d, namn)
        if not os.path.exists(dest):
            lame(w, dest, gain, titel, tons, album, ar, i)
        print("   %-56s %5.1f MB" % (namn, os.path.getsize(dest) / 1e6), flush=True)
    for w in vagar:
        os.remove(w)


def koda_wav(slug_namn, wavfil, etiketter, album, ar):
    d = os.path.join(OUT, slug_namn)
    os.makedirs(d, exist_ok=True)
    labels = parse_labels(etiketter)
    with wave.open(wavfil, "rb") as w:
        rate, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        decim = rate // 48000
        topp = 1
        for a, b, _ in labels:
            pos, slut = int(a * rate), int(b * rate)
            while pos < slut:
                n = min(20 * rate, slut - pos)
                w.setpos(pos)
                raw = w.readframes(n)
                v = np.frombuffer(raw, dtype="<i4" if sw == 4 else "<i2")
                if v.size:
                    topp = max(topp, int(np.abs(v).max()))
                pos += n
        full = 2147483647 if sw == 4 else 32767
        gain = min(TARGET_PEAK * full / topp, 8.0)
        for i, (a, b, titel) in enumerate(labels, 1):
            namn = "%02d-%s.mp3" % (i, slug(titel))
            dest = os.path.join(d, namn)
            if not os.path.exists(dest):
                proc = lame(None, dest, 1.0, titel, "", album, ar, i, raw=True)
                pos, carry = int(a * rate), None
                slut = int(b * rate)
                while pos < slut:
                    n = min(20 * rate, slut - pos)
                    w.setpos(pos)
                    raw = w.readframes(n)
                    pos += n
                    if sw == 4:
                        block = np.frombuffer(raw, dtype="<i4").astype(np.float32) * gain / 65536.0
                    else:
                        block = np.frombuffer(raw, dtype="<i2").astype(np.float32) * gain
                    block = block.reshape(-1, ch)
                    if decim == 2:
                        if carry is not None:
                            block = np.concatenate([carry, block]); carry = None
                        if len(block) % 2:
                            carry = block[-1:]; block = block[:-1]
                        block = block.reshape(-1, 2, ch).mean(axis=1)
                    proc.stdin.write(np.clip(block, -32768, 32767).astype("<i2").tobytes())
                proc.stdin.close()
                if proc.wait() != 0:
                    sys.exit("lame misslyckades: %s" % dest)
            print("   %-56s %5.1f MB" % (namn, os.path.getsize(dest) / 1e6), flush=True)


def koda_allt():
    for s, plats, datum, _, mapp, spar in AIFF:
        print("== %s" % s, flush=True)
        koda_aiff(s, mapp, spar, "AGA-trion live, %s %s" % (plats, datum), datum[-4:])
    for s, plats, datum, _, wavfil, etiketter in WAV:
        print("== %s" % s, flush=True)
        koda_wav(s, wavfil, etiketter, "AGA-trion live, %s %s" % (plats, datum), datum[-4:])
    for s, plats, datum, _, mapp, spar in FARDIGA_MP3:
        print("== %s (kopieras)" % s, flush=True)
        d = os.path.join(OUT, s); os.makedirs(d, exist_ok=True)
        for i, (fil, titel, tons) in enumerate(spar, 1):
            namn = "%02d-%s.mp3" % (i, slug(("%s %s" % (tons, titel)).strip()))
            dest = os.path.join(d, namn)
            if not os.path.exists(dest):
                shutil.copy2(os.path.join(mapp, fil), dest)
            print("   %-56s %5.1f MB" % (namn, os.path.getsize(dest) / 1e6), flush=True)


# ---------------------------------------------------------------- sidan
HUVUD = '''<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arkiv — AGA-trion</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="Inspelningar ur AGA-trions arkiv.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/style.css">
</head>
<body>
<a class="skip-link" href="#main">Hoppa till innehållet</a>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">AGA-trion</a>
    <nav class="site-nav" aria-label="Huvudmeny">
      <ul>
        <li><a href="/">Start</a></li>
        <li><a href="/konserter.html">Konserter</a></li>
        <li><a href="/repertoar.html">Repertoar</a></li>
        <li><a href="/lyssna.html">Lyssna</a></li>
        <li><a href="/kontakt.html">Kontakt</a></li>
      </ul>
    </nav>
  </div>
</header>

<main id="main">

  <section class="section" style="border-top:0">
    <div class="wrap">
      <h1>Arkiv</h1>
      <p class="section-lead prose">Allt vi har, konsert för konsert och spår för spår.
      Lyssnasidan visar ett verk i taget; här ligger hela kvällarna. Sidan är inte länkad från
      menyn och inte sökbar — den finns för er egen skull, och för den ni väljer att ge adressen
      till. Ljudet kommer från Apple Music-arkivet, Audacity-projekten och de färdigklippta
      spåren; kvaliteten varierar därefter.</p>
    </div>
  </section>

'''

FOT = '''</main>

<footer class="site-footer">
  <div class="wrap">
    <p>AGA-trion — arkiv.
      <button type="button" class="dela" hidden>Dela sidan</button></p>
    <ul>
      <li><a href="/">Till sajten</a></li>
      <li><a href="https://soundcloud.com/aga-trion">SoundCloud</a></li>
      <li><a href="https://www.youtube.com/@agatrion">YouTube</a></li>
    </ul>
  </div>
</footer>
<script src="/js/player.js" defer></script>
<script src="/js/dela.js" defer></script>
</body>
</html>
'''


def skriv_sida():
    delar = [HUVUD]
    poster = []
    for s, plats, datum, ingress, _, spar in AIFF:
        poster.append((datum, s, plats, ingress, [(t, k) for _, t, k in spar]))
    for s, plats, datum, ingress, _, etiketter in WAV:
        poster.append((datum, s, plats, ingress,
                       [(t, "") for _, _, t in parse_labels(etiketter)]))
    for s, plats, datum, ingress, _, spar in FARDIGA_MP3:
        poster.append((datum, s, plats, ingress, [(t, k) for _, t, k in spar]))
    for s, plats, datum, ingress in REDAN_KODADE:
        mapp = os.path.join(OUT, s)
        antal = len([f for f in os.listdir(mapp) if f.endswith(".mp3")]) \
            if os.path.isdir(mapp) else 0
        poster.append((datum, s, plats, ingress, [("", "")] * antal))

    MANADER = ["januari", "februari", "mars", "april", "maj", "juni", "juli",
               "augusti", "september", "oktober", "november", "december"]

    def datumnyckel(d):
        """"14 juli 2022" -> (2022, 7, 14)"""
        delar = d.split()
        return (int(delar[-1]), MANADER.index(delar[1]) + 1, int(delar[0]))

    poster.sort(key=lambda p: datumnyckel(p[0]), reverse=True)

    delar.append('  <section class="section">\n    <div class="wrap">\n')
    delar.append("      <h2>Film</h2>\n")
    for s, plats, datum, ingress, klipp in VIDEO:
        delar.append('      <article class="recording" id="%s">\n' % s)
        delar.append('        <h3>%s <span class="years">%s</span></h3>\n'
                     % (html.escape(plats), html.escape(datum)))
        delar.append('        <p class="recording-meta">%s</p>\n' % html.escape(ingress))
        delar.append('        <div class="video-grid">\n')
        for fil, rubrik in klipp:
            delar.append('          <figure>\n'
                         '            <video controls preload="none" playsinline '
                         'poster="/media/bild/%s.webp">\n'
                         '              <source src="%s/video/%s" type="video/mp4">\n'
                         '            </video>\n'
                         '            <figcaption>%s</figcaption>\n'
                         '          </figure>\n'
                         % (fil[:-4], BAS, fil, html.escape(rubrik)))
        delar.append("        </div>\n      </article>\n")
    delar.append("    </div>\n  </section>\n\n")

    delar.append('  <section class="section">\n    <div class="wrap">\n      <h2>Inspelningar</h2>\n')
    for datum, s, plats, ingress, spar in poster:
        mapp = os.path.join(OUT, s)
        filer = sorted(f for f in os.listdir(mapp) if f.endswith(".mp3")) if os.path.isdir(mapp) else []
        delar.append('      <article class="recording" id="%s">\n' % s)
        delar.append('        <h3>%s <span class="years">%s</span></h3>\n'
                     % (html.escape(plats), html.escape(datum)))
        if ingress:
            delar.append('        <p class="recording-meta">%s</p>\n' % html.escape(ingress))
        delar.append('        <ol class="tracks">\n')
        for fil, (titel, tons) in zip(filer, spar):
            etikett = html.escape(titel)
            if tons:
                etikett += ' <span class="composer">%s</span>' % html.escape(tons)
            delar.append('          <li>\n            <p class="track-title">%s</p>\n'
                         '            <audio controls preload="none" src="%s/ljud/%s/%s"></audio>\n'
                         '          </li>\n' % (etikett, BAS, s, fil))
        delar.append("        </ol>\n      </article>\n")
    delar.append("    </div>\n  </section>\n\n")
    delar.append(FOT)

    with open(os.path.join(SAJT, "arkiv.html"), "w") as fh:
        fh.write("".join(delar))
    print("arkiv.html skriven — %d konserter, %d spår"
          % (len(poster), sum(len(p[4]) for p in poster)))


def satt_titlar():
    """Låt verk.py bestämma vad som står på raderna."""
    subprocess.run([sys.executable, os.path.join(ROT, "verktyg", "satt-verktitlar.py")],
                   check=True)


if __name__ == "__main__":
    if "--bara-sida" not in sys.argv:
        koda_allt()
    skriv_sida()
    satt_titlar()
