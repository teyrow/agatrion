#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skriv docs/sitemap.xml med datum hämtade ur git.

    python3 verktyg/bygg-sitemap.py            # skriv om filen
    python3 verktyg/bygg-sitemap.py --visa      # skriv ut den utan att spara

För en sajt med fem sidor som alla står i menyn gör en sajtkarta nästan ingen
nytta — en robot som hittar startsidan har hittat allt. Den finns kvar av ett
enda skäl: `lastmod` talar om när en sida faktiskt ändrades, vilket spelar roll
för konserter.html som uppdateras löpande.

`priority` och `changefreq` är medvetet borta. Google slutade läsa dem 2023, och
en fil som påstår saker ingen lyssnar på är sämre än en kort fil som stämmer.

Datumen kommer ur den senaste commit som rörde varje fil. Därför måste den här
köras *före* commit, och sajtkartan commitas i samma svep — annars ligger den
alltid ett steg efter. kolla-sajten.py säger till om den glidit isär.
"""
import argparse
import os
import subprocess
import sys
import datetime

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")

# Sidorna som får synas i sökresultaten, i den ordning de står i menyn.
# Arkivet, granskningssidan och profilen är noindex och hör inte hemma här.
SIDOR = ["index.html", "konserter.html", "repertoar.html", "lyssna.html", "kontakt.html"]


def andrad(sida):
    """Datumet för den senaste commit som rörde filen, annars filens egen tid."""
    rel = os.path.join("docs", sida)
    try:
        ut = subprocess.run(["git", "-C", ROT, "log", "-1", "--format=%cs", "--", rel],
                            capture_output=True, text=True, check=True).stdout.strip()
        if ut:
            return ut
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    stamp = os.path.getmtime(os.path.join(SAJT, sida))
    return datetime.date.fromtimestamp(stamp).isoformat()


def xml():
    rader = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for sida in SIDOR:
        url = "https://agatrion.se/" + ("" if sida == "index.html" else sida)
        rader.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (url, andrad(sida)))
    rader += ["</urlset>", ""]
    return "\n".join(rader)


def main():
    a = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--visa", action="store_true", help="skriv ut i stället för att spara")
    args = a.parse_args()

    ny = xml()
    if args.visa:
        sys.stdout.write(ny)
        return 0
    bana = os.path.join(SAJT, "sitemap.xml")
    gammal = open(bana, encoding="utf-8").read() if os.path.exists(bana) else ""
    if ny == gammal:
        print("sitemap.xml är redan aktuell")
        return 0
    with open(bana, "w", encoding="utf-8") as fh:
        fh.write(ny)
    print("Skrev docs/sitemap.xml — %d sidor" % len(SIDOR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
