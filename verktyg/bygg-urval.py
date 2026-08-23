#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bygg den lokala urvalssidan: lyssna igenom allt och bekräfta vilket verk det är.

Sidan hamnar i docs/urval/index.html (gitignorerad) och spelar upp filerna i
docs/media/ljud direkt, så starta den lokala servern och gå till

    cd docs && python3 -m http.server 8000
    http://localhost:8000/urval/

För varje spår finns en kryssruta (ska det upp på lyssnasidan?), en rullgardin
med förslag på verk och sats, och en liten kommentarsruta. Förslagen kommer ur
verktyg/verk.py; de som är markerade som gissningar står överst med frågetecken.
Har verktyg/jamfor-inspelningar.py körts visas också vilka andra inspelningar
spåret liknar, så en bekräftelse på ett ställe räcker för hela gruppen.

Knappen Kopiera lägger allt du ändrat i urklipp — bara det du rört, med
konsert, spårnummer och kommentar — färdigt att klistra in i chatten.
"""
import glob
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verk                                                    # noqa: E402

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sajten ligger i docs/ — allt utanför den mappen publiceras aldrig
SAJT = os.path.join(ROT, "docs")
UT = os.path.join(SAJT, "urval")
KROMA = os.path.join(ROT, "verktyg", ".kroma")
TROSKEL = 0.25             # kalibrerad mot de 124 kända paren, se jamfor-inspelningar.py


def langder():
    """Speltid per spår, om kromagrammen finns."""
    ut = {}
    try:
        import numpy as np
    except ImportError:
        return ut
    for f in glob.glob(os.path.join(KROMA, "*.npz")):
        konsert, titel = os.path.basename(f)[:-4].split("__", 1)
        ut["%s/%s.mp3" % (konsert, titel)] = float(np.load(f)["langd"])
    return ut


def slaktingar():
    """fil -> [(avstånd, typ, annan fil)] för de par som ligger under tröskeln."""
    bana = os.path.join(KROMA, "traffar.json")
    if not os.path.exists(bana):
        return {}
    ut = {}
    for t in json.load(open(bana)):
        if t["dtw"] > TROSKEL:
            continue
        for x, y in ((t["a"], t["b"]), (t["b"], t["a"])):
            fil = "%s.mp3" % x.replace("__", "/", 1)
            ut.setdefault(fil, []).append((t["dtw"], t["typ"], "%s.mp3" % y.replace("__", "/", 1)))
    for v in ut.values():
        v.sort()
    return ut


def mmss(s):
    return "%d:%02d" % (int(s) // 60, int(s) % 60)


def rullgardin(fil, valt):
    """Alternativen grupperade per tonsättare, med det aktuella förslaget valt."""
    per = {}
    for varde, etikett in verk.alternativ():
        per.setdefault(verk.VERK[varde.split(":")[0]]["tonsattare"], []).append((varde, etikett))
    rader = ['<select class="verkval" data-fil="%s">' % html.escape(fil)]
    rader.append('<option value="">— välj verk och sats —</option>')
    for tonsattare in sorted(per):
        rader.append('<optgroup label="%s">' % html.escape(tonsattare))
        for varde, etikett in per[tonsattare]:
            vald = ' selected' if varde == valt else ''
            # etiketten inleds med tonsättaren, som redan står i optgroup-rubriken
            kort = etikett.split(" · ", 1)[1] if " · " in etikett else etikett
            rader.append('<option value="%s"%s>%s</option>'
                         % (html.escape(varde), vald, html.escape(kort)))
        rader.append('</optgroup>')
    rader.append('</select>')
    return "".join(rader)


MARKE = {
    "belagd": ('<span class="marke belagd" title="står i etikettfil, på affisch '
               'eller i filnamnet">belagd</span>'),
    "analys": ('<span class="marke analys" title="ihopparad med ett belagt spår av '
               'ljudjämförelsen">analys</span>'),
    "sannolik": '<span class="marke sannolik">sannolik</span>',
    "gissning": '<span class="marke gissning" title="behöver bekräftas">gissning?</span>',
}


def skriv_sida():
    tid = langder()
    slakt = slaktingar()
    filer = {}
    for f in sorted(glob.glob(os.path.join(SAJT, "media", "ljud", "*", "*.mp3"))):
        konsert = os.path.basename(os.path.dirname(f))
        filer.setdefault(konsert, []).append(os.path.basename(f))

    ordning = sorted(verk.KONSERTER,
                     key=lambda k: [int(x) for x in reversed(_datum(k))], reverse=True)

    d = ['<!DOCTYPE html>', '<html lang="sv">', '<head>', '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<meta name="robots" content="noindex, nofollow">',
         '<title>Bekräfta verk — AGA-trion</title>', '<style>%s</style>' % STIL,
         '</head>', '<body>']
    d.append('<h1>Vilket verk är det här?</h1>')
    d.append('<p class="ingress">Alla %d inspelade spår. Rullgardinen visar vad jag tror att '
             'spåret är; <span class="marke gissning">gissning?</span> betyder att jag inte vet '
             'och behöver ditt öra. Rätta där det blivit fel, skriv i kommentarsrutan, och tryck '
             '<em>Kopiera</em> — bara det du rört följer med.</p>'
             % sum(len(v) for v in filer.values()))
    d.append('<p class="ingress">Kryssrutan betyder <em>den här ska upp på lyssnasidan</em>. '
             'Tre konserter ligger där i dag, resten i arkivet.</p>')

    öppna = 0
    for konsert in ordning:
        plats, datum, var = verk.KONSERTER[konsert]
        spar = filer.get(konsert, [])
        d.append('<section class="konsert">')
        d.append('<h2>%s <span class="datum">%s</span> <span class="var %s">%s</span></h2>'
                 % (html.escape(plats), html.escape(datum), var,
                    "lyssnasidan" if var == "lyssna" else "arkivet"))
        d.append('<ol class="spar">')
        for nr, namn in enumerate(spar, 1):
            fil = "%s/%s" % (konsert, namn)
            vid, sats, saker = verk.SPAR.get(fil, ("", 0, "gissning"))
            tonsattare, titel, satstext, _ = verk.uppgift(fil)
            if saker == "gissning":
                öppna += 1
            d.append('<li class="%s">' % saker)
            d.append('<div class="rad">')
            d.append('<label class="kryss"><input type="checkbox" class="spar-val" '
                     'data-fil="%s" data-nr="%d"> <span class="nr">%02d</span></label>'
                     % (html.escape(fil), nr, nr))
            d.append('<div class="mitt">')
            d.append('<p class="filnamn">%s <span class="tid">%s</span> %s'
                     '<span class="antal"></span></p>'
                     % (html.escape(namn[3:-4].replace("-", " ")),
                        mmss(tid[fil]) if fil in tid else "", MARKE[saker]))
            d.append(rullgardin(fil, "%s:%d" % (vid, sats) if vid else ""))
            d.append('<input type="text" class="kommentar" data-fil="%s" '
                     'placeholder="kommentar om spår %d">' % (html.escape(fil), nr))
            liknande = slakt.get(fil, [])[:3]
            if liknande:
                bitar = []
                for avst, typ, annan in liknande:
                    ak, an = annan.split("/")
                    bitar.append("%s %s %s (%.2f)"
                                 % ("i" if typ == "del" else "=",
                                    verk.KONSERTER[ak][0].split(",")[0],
                                    an[:2], avst))
                d.append('<p class="liknar">liknar %s</p>' % html.escape(" · ".join(bitar)))
            d.append('</div>')
            d.append('<audio controls preload="none" src="/media/ljud/%s"></audio>' % html.escape(fil))
            d.append('</div>')
            d.append('</li>')
        d.append('</ol>')
        d.append('<label class="konsertkommentar">Kommentar om hela konserten<br>'
                 '<input type="text" class="kommentar-konsert" data-konsert="%s"></label>'
                 % html.escape(konsert))
        d.append('</section>')

    d.append('<div class="panel">')
    d.append('<span id="rakning">%d spår att bekräfta</span>' % öppna)
    d.append('<input type="text" id="allman" placeholder="Allmän kommentar">')
    d.append('<button id="visa">Visa</button><button id="kopiera">Kopiera</button>')
    d.append('</div>')
    d.append('<textarea id="resultat" readonly hidden></textarea>')
    d.append('<script>%s</script>' % SKRIPT)
    d.append('</body></html>')

    os.makedirs(UT, exist_ok=True)
    with open(os.path.join(UT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(d))
    print("Skrev urval/index.html — %d spår, varav %d att bekräfta"
          % (sum(len(v) for v in filer.values()), öppna))


MANADER = ["januari", "februari", "mars", "april", "maj", "juni",
           "juli", "augusti", "september", "oktober", "november", "december"]


def _datum(konsert):
    """(dag, månad, år) som strängar, för sortering."""
    delar = verk.KONSERTER[konsert][1].split()
    return (delar[0], str(MANADER.index(delar[1]) + 1), delar[2])


STIL = """
:root { color-scheme: light }
body { font: 16px/1.5 -apple-system, system-ui, sans-serif; max-width: 60rem;
       margin: 0 auto 8rem; padding: 1.5rem; background: #faf8f4; color: #232019 }
h1 { font-size: 1.6rem } h2 { font-size: 1.15rem; margin: 0 0 .3rem }
.ingress { color: #5f584c; max-width: 44rem }
.konsert { border-top: 1px solid #e2dccd; padding-top: 1.2rem; margin-top: 2rem }
.datum { font-weight: 400; color: #5f584c }
.var { font-size: .75rem; padding: .1rem .45rem; border-radius: 999px; vertical-align: 2px }
.var.lyssna { background: #1d4e6f; color: #fff } .var.arkiv { background: #e2dccd; color: #4a4437 }
ol.spar { list-style: none; margin: .8rem 0 0; padding: 0 }
ol.spar li { padding: .5rem 0; border-top: 1px dotted #e2dccd }
ol.spar li.gissning { background: #fff8e6 }
.rad { display: flex; gap: .8rem; align-items: flex-start }
.kryss { display: flex; align-items: center; gap: .35rem; padding-top: .2rem }
.nr { font-variant-numeric: tabular-nums; color: #8a8272; font-size: .85rem }
.mitt { flex: 1 1 auto; min-width: 0 }
.filnamn { margin: 0 0 .3rem; font-size: .9rem; color: #5f584c }
.tid { font-variant-numeric: tabular-nums; margin-left: .4rem }
.marke { font-size: .7rem; padding: .05rem .4rem; border-radius: 999px; margin-left: .3rem }
.belagd { background: #dce9dc; color: #2c4a2c } .analys { background: #dbe4ef; color: #23415e }
.sannolik { background: #e8e2d2; color: #4a4437 } .gissning { background: #f3d9a0; color: #5c4409 }
select.verkval { width: 100%; max-width: 34rem; padding: .3rem; font: inherit; font-size: .9rem }
input.kommentar { width: 100%; max-width: 34rem; padding: .35rem .5rem; margin-top: .3rem;
                  font: inherit; font-size: .9rem; border: 1px solid #cfc6b4; border-radius: 3px }
.liknar { margin: .25rem 0 0; font-size: .78rem; color: #8a8272 }
.antal { font-size: .78rem; color: #8a8272; margin-left: .4rem }
.antal.en { color: #2c4a2c; font-weight: 600 }
.antal.flera { color: #9a3412; font-weight: 600 }
audio { width: 15rem; flex: 0 0 auto }
.konsertkommentar { display: block; margin-top: .9rem; font-size: .9rem; color: #5f584c }
.konsertkommentar input { width: 100%; max-width: 34rem; padding: .4rem .6rem; margin-top: .25rem;
                          font: inherit; border: 1px solid #cfc6b4; border-radius: 3px }
.panel { position: fixed; left: 0; right: 0; bottom: 0; display: flex; gap: .6rem;
         align-items: center; padding: .7rem 1.2rem; background: #1d4e6f; color: #fff }
#allman { flex: 1 1 12rem; padding: .45rem .6rem; font: inherit; border: 0; border-radius: 3px }
.panel button { padding: .45rem .9rem; font: inherit; border: 0; border-radius: 3px;
                background: #fff; color: #1d4e6f; cursor: pointer }
#resultat { width: 100%; height: 22rem; margin-top: 1.5rem; font: 13px/1.45 ui-monospace, monospace }
"""

SKRIPT = """
const $ = s => Array.from(document.querySelectorAll(s));
const urspr = new Map($('.verkval').map(v => [v.dataset.fil, v.value]));

document.addEventListener('play', e => {
  $('audio').forEach(a => { if (a !== e.target) a.pause(); });
}, true);

function text(sel, fil) {
  const f = document.querySelector(`${sel}[data-fil="${CSS.escape(fil)}"]`);
  return f && f.value.trim();
}

function rader() {
  const per = new Map();
  const lagg = (fil, rad) => {
    const k = fil.split('/')[0];
    if (!per.has(k)) per.set(k, []);
    per.get(k).push(rad);
  };
  $('.verkval').forEach(v => {
    const fil = v.dataset.fil;
    const kryss = document.querySelector(`.spar-val[data-fil="${CSS.escape(fil)}"]`);
    const komm = text('input.kommentar', fil);
    const andrat = v.value !== urspr.get(fil);
    if (!andrat && !komm && !kryss.checked) return;
    const nr = kryss.dataset.nr;
    const namn = v.closest('li').querySelector('.filnamn').firstChild.textContent.trim();
    let rad = `  spår ${nr} "${namn}"` + (kryss.checked ? '  [till lyssnasidan]' : '');
    if (andrat) {
      const o = v.selectedOptions[0];
      const grupp = o.parentElement.label || '';
      rad += `\\n     verk: ${grupp ? grupp + ' · ' : ''}${o.textContent}`;
    }
    if (komm) rad += `\\n     kommentar: ${komm}`;
    lagg(fil, rad);
  });
  $('.kommentar-konsert').forEach(f => {
    if (f.value.trim()) lagg(f.dataset.konsert + '/', `  om konserten: ${f.value.trim()}`);
  });
  const ut = [];
  document.querySelectorAll('section.konsert').forEach(s => {
    const slug = s.querySelector('.kommentar-konsert').dataset.konsert;
    if (!per.has(slug)) return;
    const h = s.querySelector('h2');
    ut.push(`${slug} · ${h.firstChild.textContent.trim()}, ${h.querySelector('.datum').textContent}`);
    ut.push(...per.get(slug), '');
  });
  const allman = document.getElementById('allman').value.trim();
  if (allman) ut.push('Allmänt: ' + allman);
  return ut.join('\\n');
}

function grupper() {
  // ett "verk" är här ett valt alternativ i rullgardinen, alltså verk + sats
  const per = new Map();
  $('.verkval').forEach(v => {
    if (!v.value) return;
    if (!per.has(v.value)) per.set(v.value, []);
    per.get(v.value).push(v);
  });
  let enda = 0, flera = 0;
  per.forEach(lista => {
    const valda = lista.filter(v =>
      document.querySelector(`.spar-val[data-fil="${CSS.escape(v.dataset.fil)}"]`).checked).length;
    if (valda === 1) enda++; else if (valda > 1) flera++;
    lista.forEach(v => {
      const ruta = v.closest('li').querySelector('.antal');
      ruta.textContent = `(${valda} av ${lista.length})`;
      ruta.className = 'antal' + (valda === 1 ? ' en' : valda > 1 ? ' flera' : '');
    });
  });
  $('.verkval').forEach(v => {
    if (v.value) return;
    const ruta = v.closest('li').querySelector('.antal');
    ruta.textContent = ''; ruta.className = 'antal';
  });
  return {enda, flera, verk: per.size};
}

function rakna() {
  const g = grupper();
  const n = $('.spar-val').filter(k => k.checked).length;
  const k = $('input.kommentar, .kommentar-konsert').filter(f => f.value.trim()).length;
  const a = $('.verkval').filter(v => v.value !== urspr.get(v.dataset.fil)).length;
  const s = (n, ett, flera) => `${n} ${n === 1 ? ett : flera}`;
  document.getElementById('rakning').textContent =
    `${s(n, 'valt spår', 'valda spår')} · ${g.enda}/${g.verk} verk med precis ett val` +
    (g.flera ? ` · ${g.flera} med flera` : '') +
    (a ? ` · ${s(a, 'rättelse', 'rättelser')}` : '') +
    (k ? ` · ${s(k, 'kommentar', 'kommentarer')}` : '');
}
rakna();
document.addEventListener('input', rakna);
document.addEventListener('change', rakna);

document.getElementById('visa').onclick = () => {
  const t = document.getElementById('resultat');
  t.value = rader() || 'Inget ändrat än.';
  t.hidden = false;
  t.scrollIntoView({behavior: 'smooth'});
};
document.getElementById('kopiera').onclick = async () => {
  const b = document.getElementById('kopiera');
  await navigator.clipboard.writeText(rader() || '');
  b.textContent = 'Kopierat';
  setTimeout(() => { b.textContent = 'Kopiera'; }, 1500);
};
"""


if __name__ == "__main__":
    skriv_sida()
