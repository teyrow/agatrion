# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Vad det här är

Webbplatsen för AGA-trion — en klassisk pianotrio (Anna Ighe Ramqvist violin, Gösta Nylund piano,
Andreas Josephson cello) verksam sedan 2009. Publiceras via GitHub Pages från branchen
`main` på domänen agatrion.se. Allt innehåll är på svenska.

**Ren HTML och CSS, inget byggsteg.** Filerna i repot är exakt det som serveras. Lägg inte
till en statisk sajtgenerator, npm-beroenden eller CI-bygg utan att fråga — poängen med
upplägget är att sajten ska gå att uppdatera om fem år utan verktygskedja. Den förra sajten
(Octopress/Jekyll 0.12, arkiverad i taggarna `octopress-arkiv-*`) dog av just det.

## Struktur

Fem sidor: `index.html`, `konserter.html`, `repertoar.html`, `lyssna.html`, `kontakt.html`,
plus `404.html`. Sidhuvud, navigation och sidfot är kopierade i varje fil — det är det
medvetna priset för att slippa byggsteg. **Ändras navigationen måste alla sex filerna
uppdateras**, och `aria-current="page"` sitta på rätt länk i varje.

All styling ligger i `css/style.css` (CSS-variabler i `:root`, mörkt läge via
`prefers-color-scheme`). Inga externa typsnitt, skript eller CDN — sajten gör inga
tredjepartsanrop alls vid sidladdning, och det ska den fortsätta att inte göra.
`js/player.js` är de enda tio raderna JavaScript: pausar övriga ljudspelare och laddar
YouTube-iframen först vid klick.

## Innehåll under arbete

Sök efter `FYLL I` — HTML-kommentarer markerar allt som trion själva ska fylla i
(musikerbios, exakta konsertdatum, vilka Schubert- och Mendelssohnverk som spelades,
kontaktadress). Hitta inte på uppgifter för att fylla luckorna: verk, datum och platser
måste komma från användaren eller från etikettfilerna i `/Users/aj/code/music-convert/sources`.

## Ljud

`media/ljud/<konsert>/NN-tonsattare-titel.mp3` — liveinspelningar klippta ur långa
wav-filer. Källmaterialet ligger utanför repot i `/Users/aj/code/music-convert/sources`
(32-bitars PCM, 48/96 kHz, med Audacity-etiketter i `.txt`-filerna som anger spårgränser).

`verktyg/klipp-konsert.py` gör klippningen: normaliserar hela konserten till -1,5 dBFS med
samma gain, decimerar 96 → 48 kHz, konverterar till 16 bitar och kodar via `lame -V 3`.
Spårlistorna står i `CONCERTS` överst i skriptet.

Två saker att veta:
- **ffmpeg på den här maskinen är trasigt** (`/usr/local/bin/ffmpeg` saknar `libjxl.0.11`).
  Därför använder skriptet Python + `lame`, och `afconvert` för m4a-källor.
- **Använd aldrig Git LFS för media.** GitHub Pages serverar LFS-pekarfiler i stället för
  innehållet, så ljudet skulle sluta fungera. Filerna ska ligga som vanliga binärer.

`<audio>`-element måste ha `preload="none"`, annars laddar `lyssna.html` ner hundratals
megabyte vid varje besök.

## Publicering

Push till `main` publicerar direkt. `CNAME` innehåller `agatrion.se`; DNS pekar apex med
A/AAAA till GitHubs adresser och `www` via CNAME till `teyrow.github.io`.

Kontrollera lokalt före push:

```
python3 -m http.server 8000
```
