#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skriv den grafiska profilen, docs/profil/index.html.

    python3 verktyg/bygg-profil.py

Sidan publiceras med sajten men är märkt noindex och länkas inte från menyn —
den är till för oss tre och för den som ska göra ett program eller en affisch.

Färgerna läses ur docs/css/style.css i stället för att skrivas av. Står de på
två ställen hinner de bli osams; här finns bara ett original.
"""
import os
import re

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")
UT = os.path.join(SAJT, "profil")

ROLLER = [
    ("--accent", "Accent", "Anfangernas ruta, logotypens block, länkar och knappar."),
    ("--bg", "Botten", "Sidans bakgrund, och färgen inuti anfangen."),
    ("--fg", "Text", "Brödtext och rubriker."),
    ("--muted", "Dämpad", "Speltider, tonsättarnamn, bildtexter."),
    ("--bg-soft", "Botten, tonad", "Ljudspelare och andra ytor som ska skiljas ut."),
    ("--accent-soft", "Accent, tonad", "Markering av det spår man hoppat till."),
    ("--rule", "Linje", "Avdelare mellan avsnitt."),
]


def palett():
    """{variabel: (ljus, mörk)} ur style.css."""
    css = open(os.path.join(SAJT, "css", "style.css"), encoding="utf-8").read()
    varde = r"(--[a-z-]+):\s*(#[0-9a-fA-F]{3,8})\s*;"
    ljus = dict(re.findall(varde, css.split("@media")[0]))
    m = re.search(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*{\s*:root\s*{([^}]*)}", css)
    if not m:
        raise SystemExit("hittade inget :root för mörkt läge i style.css")
    mork = dict(re.findall(varde, m.group(1)))
    saknas = [v for v, _, _ in ROLLER if v not in ljus or v not in mork]
    if saknas:
        raise SystemExit("saknar värden för %s" % ", ".join(saknas))
    return ljus, mork


def rutor(ljus, mork):
    d = ['<table class="palett">',
         "<thead><tr><th>Roll</th><th>Ljust</th><th>Mörkt</th><th>Används till</th></tr>"
         "</thead><tbody>"]
    for var, namn, bruk in ROLLER:
        l, m = ljus.get(var, "—"), mork.get(var, "—")
        d.append("<tr><td><b>%s</b><br><code>%s</code></td>"
                 '<td><span class="prov" style="background:%s"></span><code>%s</code></td>'
                 '<td><span class="prov mork" style="background:%s"></span><code>%s</code></td>'
                 "<td>%s</td></tr>" % (namn, var, l, l, m, m, bruk))
    d.append("</tbody></table>")
    return "\n".join(d)


def sida():
    ljus, mork = palett()
    d = ["<!DOCTYPE html>", '<html lang="sv">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<meta name="robots" content="noindex, nofollow">',
         "<title>Grafisk profil — AGA-trion</title>",
         '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
         '<link rel="stylesheet" href="/css/style.css">',
         "<style>%s</style>" % STIL, "</head>", "<body>",
         '<main class="wrap prose">',
         "<h1>Grafisk profil</h1>",
         '<p class="lead">Så här ser AGA-trion ut. Sidan är till för oss själva och för '
         "den som ska sätta ett program, en affisch eller en annons. Den är inte länkad "
         "från menyn.</p>",

         "<h2>Logotypen</h2>",
         '<p>Formen är anfangen från sajten, förstorad: ett rundat block med AGA i omvända '
         "färger och fem tunna strängar tvärs över. Strängarna läser som ett notsystem utan "
         "att stava ut det. Efter blocket står <i>-trion</i> i vanlig textfärg.</p>",
         '<figure class="visning">',
         '<img src="/media/bild/logotyp.svg" alt="AGA-trion" width="420">',
         "<figcaption>Liggande logotyp. Förstahandsvalet.</figcaption></figure>",
         '<div class="par">',
         '<figure class="visning"><img src="/media/bild/logotyp-block.svg" alt="AGA" '
         'width="150"><figcaption>Blocket ensamt, när namnet redan står i sammanhanget.'
         "</figcaption></figure>",
         '<figure class="visning"><img src="/favicon.svg" alt="AGA-trion" width="96">'
         "<figcaption>Märket. Favicon, profilbild, stämpel.</figcaption></figure>",
         "</div>",

         "<h3>Regler</h3>",
         "<ul>",
         "<li><b>Fri yta.</b> Håll minst en halv blockhöjd tom runt om. Logotypen ska aldrig "
         "trängas mot en bild- eller sidkant.</li>",
         "<li><b>Minsta storlek.</b> Liggande logotyp minst 120 pixlar bred, märket minst "
         "24. Under det försvinner strängarna.</li>",
         "<li><b>Färgerna byter själva.</b> SVG-filerna innehåller en mediefråga och vänder "
         "till ljus accent mot mörk botten. Rör den inte.</li>",
         "<li><b>Töj inte.</b> Skala proportionellt. Luta den inte, lägg ingen skugga, byt "
         "inte ut blockets färg mot en bild.</li>",
         "<li><b>Bokstäverna är banor</b>, inte text. Filen ser likadan ut oavsett vilka "
         "typsnitt mottagaren har — och därför ska texten heller inte skrivas om i filen. "
         "Behövs en ändring, kör om <code>verktyg/bygg-logotyp.py</code>.</li>",
         "</ul>",

         "<h2>Färger</h2>",
         '<p>Sju värden, alla i två versioner: ett för ljust läge och ett för mörkt. '
         "Originalet står i <code>docs/css/style.css</code>, och den här tabellen läses "
         "därifrån.</p>",
         rutor(ljus, mork),

         "<h2>Typografi</h2>",
         '<p>Sajten laddar inga typsnitt utifrån. Rubriker och brödtext sätts i det som '
         "råkar finnas på besökarens dator, i den här ordningen:</p>",
         '<dl class="typ">',
         "<dt>Serif — rubriker, ingresser, spårtitlar</dt>",
         '<dd><span class="serifprov">Iowan Old Style</span> · Palatino Linotype · Palatino '
         "· Book Antiqua · Georgia</dd>",
         "<dt>Sans — meny, meta, knappar, speltider</dt>",
         '<dd><span class="sansprov">system-ui</span> · -apple-system · Segoe UI · Roboto '
         "· Helvetica Neue · Arial</dd>",
         "<dt>AGA Anfang — enbart anfangerna</dt>",
         '<dd><span class="anfangprov">ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ</span></dd>',
         "</dl>",
         "<p>Det enda typsnitt vi levererar själva är <b>AGA Anfang</b> — en delmängd med "
         "bara versaler, 3,5 kB, från vår egen domän. Den finns för att anfangerna ska ha "
         "exakt logotypens bokstavsformer även på en dator utan Palatino.</p>",

         "<h2>Anfangen</h2>",
         "<p>Det bärande greppet. En namninledande versal i en ruta med omvända färger: "
         "sidans bottenfärg som text, accentfärgen som botten. Den används på tre ställen "
         "— i logotypen, på musikernas namn i hero, och som stor initial vid porträtten, "
         "där brödtexten flyter runt.</p>",
         '<div class="anfangvisning">',
         '<p class="stor"><span class="anfang">G</span>östa Nylund spelar piano i trion '
         'och skriver arrangemangen. Så här ser den stora anfangen ut i bruk: bokstaven '
         'flyter till vänster och brödtexten lägger sig runt den, i stället för att börja '
         'om under. Meningen fortsätter direkt ur rutan — namnet står aldrig två '
         'gånger.</p>',
         "</div>",
         "<ul>",
         "<li>Meningen fortsätter direkt ur bokstaven. Skriv aldrig ut namnet en gång till "
         "efter anfangen.</li>",
         "<li>Rutan har samma bredd oavsett bokstav, så att A och G linjerar under "
         "varandra.</li>",
         "<li>Stor variant flyter i texten (<code>float: left</code>), liten variant sitter "
         "på raden.</li>",
         "</ul>",

         "<h2>Sajtens principer</h2>",
         "<ul>",
         "<li>Inga tredjepartsanrop vid sidladdning. Inga kakor, ingen mätning, inga "
         "inbäddningar som laddar av sig själva — YouTube hämtas först när någon klickar.</li>",
         "<li>Ren HTML och CSS utan byggsteg. Filerna i <code>docs/</code> är exakt det som "
         "serveras.</li>",
         "<li>Ljud och video ligger i objektlagring utanför git, med ett års cache. En "
         "ändrad inspelning måste därför byta filnamn.</li>",
         "</ul>",

         "<h2>Ursprung och licenser</h2>",
         "<p>Bokstavsformerna i logotypen och i AGA Anfang kommer ur <b>TeX Gyre Pagella "
         "Bold</b>, en fri Palatino från polska TeX-användargruppen, byggd på URW:s "
         "Palladio. Den får både användas och ändras under "
         '<a href="/media/typsnitt/GUST-FONT-LICENSE.txt">GUST Font License</a> (LPPL 1.3c). '
         "Licensen ber om att härledda verk byter namn, vilket är skälet till att vår "
         "delmängd heter AGA Anfang och inte Pagella.</p>",
         "<p>Logotypen är ritad ur samma konturer av "
         "<code>verktyg/bygg-logotyp.py</code>. Vill du ha den i ett annat format än SVG, "
         "öppna filen i Inkscape eller Figma — den innehåller inga typsnittsberoenden.</p>",

         "</main>", "</body></html>"]
    return "\n".join(d)


STIL = """
body { padding: 2rem 0 6rem }
main.prose { max-width: 46rem }
h2 { margin-top: 3rem } h3 { margin-top: 2rem }
.visning { margin: 1.5rem 0; padding: 1.5rem; background: var(--bg-soft);
  border-radius: 6px; text-align: center }
.visning img { max-width: 100%; height: auto }
.visning figcaption { margin-top: .9rem; font-size: .85rem; color: var(--muted) }
.par { display: flex; gap: 1rem; flex-wrap: wrap }
.par .visning { flex: 1 1 14rem }
table.palett { width: 100%; border-collapse: collapse; margin: 1.2rem 0; font-size: .9rem }
table.palett th { text-align: left; font-family: var(--sans); font-size: .78rem;
  text-transform: uppercase; letter-spacing: .06em; color: var(--muted);
  border-bottom: 1px solid var(--rule); padding: .4rem .6rem .4rem 0 }
table.palett td { padding: .7rem .6rem .7rem 0; border-bottom: 1px solid var(--rule);
  vertical-align: top }
table.palett code { font-size: .82em; color: var(--muted) }
span.prov { display: inline-block; width: 1.5rem; height: 1.5rem; border-radius: 3px;
  vertical-align: -.4rem; margin-right: .4rem; box-shadow: inset 0 0 0 1px rgba(0,0,0,.12) }
dl.typ dt { font-family: var(--sans); font-size: .78rem; text-transform: uppercase;
  letter-spacing: .06em; color: var(--muted); margin-top: 1.2rem }
dl.typ dd { margin: .3rem 0 0; color: var(--muted); font-size: .9rem }
.serifprov { font-family: var(--serif); font-size: 1.4rem; color: var(--fg) }
.sansprov { font-family: var(--sans); font-size: 1.3rem; color: var(--fg) }
.anfangprov { font-family: "AGA Anfang", var(--serif); font-size: 1.5rem; color: var(--fg);
  letter-spacing: .02em }
.anfangvisning { padding: 1.5rem 1.5rem .5rem; background: var(--bg-soft);
  border-radius: 6px; margin: 1.5rem 0; display: flow-root }
.anfangvisning .stor { font-size: 1.05rem }
"""


if __name__ == "__main__":
    os.makedirs(UT, exist_ok=True)
    with open(os.path.join(UT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(sida())
    print("Skrev docs/profil/index.html")
