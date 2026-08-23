#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bygg granskningssidan — den Anna och Gösta får för att rätta uppgifterna.

    python3 verktyg/bygg-granska.py

Sidan hamnar i docs/granska/index.html och publiceras med sajten, men är märkt
noindex och länkas inte från menyn — precis som arkivsidan.

Skillnaden mot urvalssidan (verktyg/bygg-urval.py) är vem den är skriven för.
Urvalssidan är mitt arbetsbord: filnamn, säkerhetsnivåer och avstånd ur
ljudjämförelsen. Den här visar bara verk, sats och tonsättare, en spelare och en
kommentarsruta, och lägger det man skrivit i urklipp så att det kan klistras in
i ett mejl. Ljudet spelas från objektlagringen, inte från disk.
"""
import glob
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verk                                                    # noqa: E402

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAJT = os.path.join(ROT, "docs")
UT = os.path.join(SAJT, "granska")


def mediabas():
    """Samma bas som resten av sajten använder för ljudet."""
    s = open(os.path.join(SAJT, "lyssna.html"), encoding="utf-8").read()
    m = re.search(r'src="(https?://[^"]*?)/ljud/', s)
    if not m:
        raise SystemExit("hittade ingen mediabas i lyssna.html — kör satt-mediabas.py först")
    return m.group(1)


def langder():
    ut = {}
    try:
        import numpy as np
    except ImportError:
        return ut
    for f in glob.glob(os.path.join(ROT, "verktyg", ".kroma", "*.npz")):
        konsert, titel = os.path.basename(f)[:-4].split("__", 1)
        ut["%s/%s.mp3" % (konsert, titel)] = float(np.load(f)["langd"])
    return ut


MANADER = ["januari", "februari", "mars", "april", "maj", "juni",
           "juli", "augusti", "september", "oktober", "november", "december"]


def datumnyckel(konsert):
    dag, manad, ar = verk.KONSERTER[konsert][1].split()
    return (int(ar), MANADER.index(manad) + 1, int(dag))


def skriv():
    bas = mediabas()
    tid = langder()
    filer = {}
    for f in sorted(glob.glob(os.path.join(SAJT, "media", "ljud", "*", "*.mp3"))):
        filer.setdefault(os.path.basename(os.path.dirname(f)), []).append(os.path.basename(f))
    antal = sum(len(v) for v in filer.values())

    d = ["<!DOCTYPE html>", '<html lang="sv">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<meta name="robots" content="noindex, nofollow">',
         "<title>Stämmer det här? — AGA-trion</title>",
         "<style>%s</style>" % STIL, "</head>", "<body>",
         "<h1>Stämmer det här?</h1>",
         '<p class="ingress">Här ligger alla %d inspelningar vi har, med det jag tror att '
         "de är. En hel del är gissat ur filnamn och gamla etiketter, så det finns säkert "
         "fel.</p>" % antal,
         '<p class="ingress">Lyssna på det du känner igen. Ser eller hör du något som inte '
         "stämmer — fel verk, fel sats, fel tonsättare, fel datum — skriv det i rutan under "
         "spåret. Du behöver inte fylla i något annat.</p>",
         '<p class="ingress">Tryck <em>Kopiera</em> längst ner när du är klar, och klistra in '
         "i ett mejl till Andreas. Det du skriver sparas inte här, så låt gärna fliken vara "
         "öppen tills du kopierat.</p>"]

    for konsert in sorted(verk.KONSERTER, key=datumnyckel, reverse=True):
        plats, datum, _ = verk.KONSERTER[konsert]
        spar = filer.get(konsert, [])
        if not spar:
            continue
        d.append('<section class="konsert">')
        d.append("<h2>%s <span class=\"datum\">%s</span></h2>"
                 % (html.escape(plats), html.escape(datum)))
        d.append('<ol class="spar">')
        for nr, namn in enumerate(spar, 1):
            fil = "%s/%s" % (konsert, namn)
            tonsattare, titel, sats, _ = verk.uppgift(fil)
            rad = html.escape(titel)
            if sats:
                rad += ' <span class="sats">%s</span>' % html.escape(sats)
            langd = tid.get(fil)
            d += ["<li>",
                  '  <p class="verk"><span class="nr">%d</span> %s'
                  '<span class="tonsattare">%s</span>%s</p>'
                  % (nr, rad, html.escape(tonsattare),
                     '<span class="tid">%d:%02d</span>' % (int(langd) // 60, int(langd) % 60)
                     if langd else ""),
                  '  <audio controls preload="none" src="%s/ljud/%s"></audio>' % (bas, fil),
                  '  <input type="text" class="kommentar" data-konsert="%s" data-nr="%d" '
                  'data-verk="%s" placeholder="Det här stämmer inte, för…">'
                  % (html.escape(konsert), nr,
                     html.escape("%s, %s%s" % (tonsattare, titel, (", " + sats) if sats else ""))),
                  "</li>"]
        d.append("</ol>")
        d.append("</section>")

    d += ['<div class="panel">',
          '<span id="rakning">Inget skrivet än</span>',
          '<button id="kopiera">Kopiera</button>',
          "</div>",
          '<textarea id="resultat" readonly hidden></textarea>',
          "<script>%s</script>" % SKRIPT,
          "</body></html>"]

    os.makedirs(UT, exist_ok=True)
    with open(os.path.join(UT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(d))
    print("Skrev docs/granska/index.html — %d spår" % antal)


STIL = """
:root { color-scheme: light dark;
  --bg: #faf8f4; --text: #232019; --dim: #5f584c; --linje: #e2dccd; --accent: #2d4a72 }
@media (prefers-color-scheme: dark) { :root {
  --bg: #17150f; --text: #ece7dc; --dim: #a49b89; --linje: #322c22; --accent: #9dbbe6 } }
body { font: 17px/1.6 -apple-system, system-ui, sans-serif; max-width: 46rem;
  margin: 0 auto 7rem; padding: 1.5rem; background: var(--bg); color: var(--text) }
h1 { font-size: 1.7rem; margin-bottom: .8rem }
h2 { font-size: 1.15rem; margin: 0 0 .2rem }
.ingress { color: var(--dim) }
.konsert { border-top: 1px solid var(--linje); padding-top: 1.3rem; margin-top: 2.2rem }
.datum { font-weight: 400; color: var(--dim) }
ol.spar { list-style: none; margin: 1rem 0 0; padding: 0 }
ol.spar li { padding: .7rem 0; border-top: 1px dotted var(--linje) }
.verk { margin: 0 0 .4rem }
.nr { color: var(--dim); font-variant-numeric: tabular-nums; margin-right: .5rem }
.sats { color: var(--dim) } .sats::before { content: " · " }
.tonsattare { display: block; font-size: .9rem; color: var(--dim) }
.tid { font-size: .85rem; color: var(--dim); font-variant-numeric: tabular-nums;
  margin-left: .5rem }
audio { width: 100%; max-width: 26rem; display: block; margin: .3rem 0 }
input.kommentar { width: 100%; padding: .5rem .7rem; font: inherit; font-size: .95rem;
  border: 1px solid var(--linje); border-radius: 4px; background: var(--bg); color: var(--text) }
input.kommentar:not(:placeholder-shown) { border-color: var(--accent) }
.panel { position: fixed; left: 0; right: 0; bottom: 0; display: flex; gap: .8rem;
  align-items: center; justify-content: space-between; padding: .8rem 1.2rem;
  background: var(--accent); color: var(--bg) }
.panel button { padding: .5rem 1.1rem; font: inherit; border: 0; border-radius: 4px;
  background: var(--bg); color: var(--accent); cursor: pointer }
#resultat { width: 100%; height: 16rem; margin-top: 1.5rem;
  font: 13px/1.5 ui-monospace, monospace }
"""

SKRIPT = """
const falt = () => Array.from(document.querySelectorAll('.kommentar'));

document.addEventListener('play', e => {
  document.querySelectorAll('audio').forEach(a => { if (a !== e.target) a.pause(); });
}, true);

function text() {
  const per = new Map();
  falt().forEach(f => {
    if (!f.value.trim()) return;
    const h = f.closest('section').querySelector('h2');
    const rubrik = `${h.firstChild.textContent.trim()}, ${h.querySelector('.datum').textContent}`;
    if (!per.has(rubrik)) per.set(rubrik, []);
    per.get(rubrik).push(`  ${f.dataset.nr}. ${f.dataset.verk}\\n     ${f.value.trim()}`);
  });
  return Array.from(per, ([r, rader]) => `${r}\\n${rader.join('\\n')}`).join('\\n\\n');
}

function rakna() {
  const n = falt().filter(f => f.value.trim()).length;
  document.getElementById('rakning').textContent =
    n === 0 ? 'Inget skrivet än' : n === 1 ? '1 kommentar' : `${n} kommentarer`;
}
document.addEventListener('input', rakna);

document.getElementById('kopiera').onclick = async () => {
  const b = document.getElementById('kopiera');
  const t = text();
  if (!t) { b.textContent = 'Skriv något först'; setTimeout(() => b.textContent = 'Kopiera', 1800); return; }
  try {
    await navigator.clipboard.writeText(t);
    b.textContent = 'Kopierat';
  } catch (e) {
    const r = document.getElementById('resultat');   // t.ex. Safari utan tillstånd
    r.value = t; r.hidden = false; r.select();
    b.textContent = 'Markera och kopiera';
  }
  setTimeout(() => b.textContent = 'Kopiera', 2500);
};
"""


if __name__ == "__main__":
    skriv()
