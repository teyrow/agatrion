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

`media/ljud` och `media/video` ligger **inte i git** utan i en S3-bucket hos GleSYS
(`agatrion-media`, endpoint `objects.dc-fbg1.glesys.net`). Filerna finns kvar lokalt och synkas upp med
`verktyg/publicera-media.sh`; `verktyg/satt-mediabas.py` växlar sajtens länkar mellan
bucketen och lokala filer. Bilder ligger kvar i repot — de är små och Open Graph-taggarna
kräver samma domän som sidan. Se README för uppsättningen.

Tre saker att veta:
- **ffmpeg på den här maskinen är trasigt** (`/usr/local/bin/ffmpeg` saknar `libjxl.0.11`).
  Därför använder skriptet Python + `lame`, och `afconvert` för m4a-källor.
- **Använd aldrig Git LFS för media.** GitHub Pages serverar LFS-pekarfiler i stället för
  innehållet, så ljudet skulle sluta fungera. Filerna ska ligga som vanliga binärer.

Filerna cachas med `immutable` i ett år, så **en ändrad inspelning måste byta filnamn**.

`<audio>`-element måste ha `preload="none"`, annars laddar `lyssna.html` ner hundratals
megabyte vid varje besök.

## Vilket verk är vilket

Sidorna ska ange **verk, sats och tonsättare** för varje spår, men filnamnen gör det inte —
flera spår heter bara `01-mendelsohn.mp3`. Kopplingen mellan mp3-fil och verk bor i
`verktyg/verk.py` (`VERK` beskriver verken, `SPAR` kopplar filerna, `KONSERTER` platser och
datum). Varje koppling bär en säkerhetsnivå: `belagd`, `analys`, `sannolik` eller `gissning`.
**Hitta inte på verk för att fylla luckorna** — spår som är `gissning` ska förbli gissningar
tills någon lyssnat.

- `verktyg/satt-verktitlar.py` skriver om spårlistorna på `lyssna.html` och `arkiv.html`
  utifrån katalogen. Idempotent, och vägrar skriva om ett block den inte kunnat läsa i sin
  helhet. `bygg-arkiv.py` kör den automatiskt sist.
- `verktyg/jamfor-inspelningar.py` parar ihop spår som är samma musik genom att jämföra
  kromagram (DTW, plus delsträcksökning som hittar en sats inuti en hel trio). Tröskeln
  0,147 är kalibrerad mot de 85 kända paren. Kromagrammen mellanlagras i `verktyg/.kroma/`,
  som inte ligger i git.
- `verktyg/bygg-urval.py` bygger den lokala sidan `urval/index.html` där man lyssnar igenom
  allt och bekräftar verk via rullgardiner. Den spelar filerna i `media/ljud` direkt.

## Publicering

Push till `main` publicerar direkt. `CNAME` innehåller `agatrion.se`; DNS pekar apex med
A/AAAA till GitHubs adresser och `www` via CNAME till `teyrow.github.io`.

Kontrollera lokalt före push:

```
python3 -m http.server 8000
```
