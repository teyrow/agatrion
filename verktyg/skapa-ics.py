#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skapa en kalenderfil för en kommande konsert.

    python3 verktyg/skapa-ics.py \\
        --datum 2026-11-14 --tid 18:00 --langd 60 \\
        --plats "Tranås kyrka" --ort "Tranås" \\
        --titel "AGA-trion i Tranås kyrka" \\
        --text "Meditativa toner. Fri entré."

Filen hamnar i kalender/ och skriptet skriver ut den rad du klistrar in i
konserter.html. Tiderna räknas om till UTC, så filen fungerar oavsett vilken
tidszon besökarens kalender står i.
"""
import argparse
import datetime
import os
import re
import unicodedata
from zoneinfo import ZoneInfo

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sajten ligger i docs/ — allt utanför den mappen publiceras aldrig
SAJT = os.path.join(ROT, "docs")
TZ = ZoneInfo("Europe/Stockholm")


def slug(text):
    t = text.lower().replace("ä", "a").replace("å", "a").replace("ö", "o").replace("é", "e")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return "-".join(filter(None, re.sub(r"[^a-z0-9]+", "-", t).split("-")))


def fold(rad):
    """iCalendar tillåter högst 75 oktetter per rad; fortsättning börjar med mellanslag."""
    ut, b = [], rad.encode("utf-8")
    medan = 75
    while len(b) > medan:
        brytpunkt = medan
        while brytpunkt > 0 and (b[brytpunkt] & 0xC0) == 0x80:   # klyv inte en tecken-sekvens
            brytpunkt -= 1
        ut.append(b[:brytpunkt].decode("utf-8"))
        b = b[brytpunkt:]
        medan = 74
    ut.append(b.decode("utf-8"))
    return "\r\n ".join(ut)


def esc(text):
    return (text.replace("\\", "\\\\").replace(";", r"\;")
                .replace(",", r"\,").replace("\n", r"\n"))


def main():
    a = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--datum", required=True, help="ÅÅÅÅ-MM-DD")
    a.add_argument("--tid", required=True, help="HH:MM")
    a.add_argument("--langd", type=int, default=60, help="minuter, standard 60")
    a.add_argument("--plats", required=True, help='t.ex. "Tranås kyrka"')
    a.add_argument("--ort", default="", help="ort, hamnar i LOCATION")
    a.add_argument("--titel", default="", help="standard: AGA-trion i <plats>")
    a.add_argument("--text", default="", help="kort programbeskrivning")
    args = a.parse_args()

    start = datetime.datetime.strptime("%s %s" % (args.datum, args.tid),
                                       "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    slut = start + datetime.timedelta(minutes=args.langd)
    stamp = datetime.datetime.now(datetime.timezone.utc)
    titel = args.titel or "AGA-trion i %s" % args.plats
    plats = ", ".join(x for x in (args.plats, args.ort) if x)
    namn = "%s-%s" % (args.datum, slug(args.plats))
    u = lambda d: d.astimezone(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    rader = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AGA-trion//agatrion.se//SV",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        "UID:%s@agatrion.se" % namn,
        "DTSTAMP:%s" % u(stamp),
        "DTSTART:%s" % u(start),
        "DTEND:%s" % u(slut),
        "SUMMARY:%s" % esc(titel),
        "LOCATION:%s" % esc(plats),
        "URL:https://agatrion.se/konserter.html",
    ]
    if args.text:
        rader.append("DESCRIPTION:%s" % esc(args.text))
    rader += ["END:VEVENT", "END:VCALENDAR"]

    katalog = os.path.join(SAJT, "kalender")
    os.makedirs(katalog, exist_ok=True)
    sokvag = os.path.join(katalog, namn + ".ics")
    with open(sokvag, "w", newline="") as fh:
        fh.write("\r\n".join(fold(r) for r in rader) + "\r\n")

    print("Skrev %s" % os.path.relpath(sokvag, SAJT))
    print()
    print("Klistra in i konserter.html, i konsertens <p class=\"programme\">:")
    print()
    print('  <a class="kalender" href="/kalender/%s.ics">Lägg till i kalendern</a>' % namn)


if __name__ == "__main__":
    main()
