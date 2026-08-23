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

**Allt som publiceras ligger i `docs/`.** GitHub Pages är inställt på att servera den
mappen, så `verktyg/`, `CLAUDE.md` och `README.md` ligger kvar i roten och når aldrig
webben. Det kostar inget byggsteg — samma filer, bara en nivå ner. Lägger du en ny sida
utanför `docs/` blir den osynlig; lägger du en hjälpfil inuti `docs/` blir den publik.

Fem sidor: `docs/index.html`, `konserter.html`, `repertoar.html`, `lyssna.html`,
`kontakt.html`, plus `404.html`. Sidhuvud, navigation och sidfot är kopierade i varje fil — det är det
medvetna priset för att slippa byggsteg. **Ändras navigationen måste alla sex filerna
uppdateras**, och `aria-current="page"` sitta på rätt länk i varje.

All styling ligger i `docs/css/style.css` (CSS-variabler i `:root`, mörkt läge via
`prefers-color-scheme`). Inga skript eller CDN — sajten gör inga tredjepartsanrop alls
vid sidladdning, och det ska den fortsätta att inte göra. Det enda typsnitt som laddas är
`docs/media/typsnitt/aga-anfang.woff2`, 3,5 kB från vår egen domän, och det används bara
till anfangerna.
`docs/js/player.js` är de enda tio raderna JavaScript: pausar övriga ljudspelare och laddar
YouTube-iframen först vid klick.

## Innehåll under arbete

Sök efter `FYLL I` — HTML-kommentarer markerar allt som trion själva ska fylla i
(musikerbios, exakta konsertdatum, vilka Schubert- och Mendelssohnverk som spelades,
kontaktadress). Hitta inte på uppgifter för att fylla luckorna: verk, datum och platser
måste komma från användaren eller från etikettfilerna i `/Users/aj/code/music-convert/sources`.

## Ljud

`docs/media/ljud/<konsert>/NN-tonsattare-titel.mp3` — liveinspelningar klippta ur långa
wav-filer. Källmaterialet ligger utanför repot i `/Users/aj/code/music-convert/sources`
(32-bitars PCM, 48/96 kHz, med Audacity-etiketter i `.txt`-filerna som anger spårgränser).

`verktyg/klipp-konsert.py` gör klippningen: normaliserar hela konserten till -1,5 dBFS med
samma gain, decimerar 96 → 48 kHz, konverterar till 16 bitar och kodar via `lame -V 3`.
Spårlistorna står i `CONCERTS` överst i skriptet.

`docs/media/ljud` och `docs/media/video` ligger **inte i git** utan i en S3-bucket hos GleSYS
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
  allt och bekräftar verk via rullgardiner. Sidan hamnar i `docs/urval/`, som är
  gitignorerad, och spelar filerna i `docs/media/ljud` direkt.
- `verktyg/bygg-granska.py` bygger `docs/granska/index.html` — samma material men skrivet
  för Anna och Gösta: bara verk, sats, tonsättare, en spelare och en kommentarsruta.
  Den publiceras med sajten men är `noindex` och länkas inte från menyn, och spelar
  ljudet från objektlagringen så att den fungerar för den som inte har filerna.

## Grafisk profil

Logotypen, färgerna och anfangen är dokumenterade på `docs/profil/` — en olänkad
`noindex`-sida, som arkivet. Tre saker att inte tappa bort:

- **Logotypens bokstäver är banor, inte text.** `verktyg/bygg-logotyp.py` ritar
  `docs/media/bild/logotyp.svg`, `logotyp-block.svg` och `docs/favicon.svg` ur konturerna i
  `verktyg/logotyp/glyfer.json`. Redigera aldrig SVG-filerna för hand — kör om skriptet.
- **Konturerna kommer ur TeX Gyre Pagella Bold**, en fri Palatino under GUST Font License.
  Licensen ber om att härledda verk byter namn, och det är därför typsnittsdelmängden heter
  AGA Anfang. Licenstexten ligger i `docs/media/typsnitt/`.
- **Färgerna har ett enda original**, `:root` i `style.css`. Profilsidan läser därifrån, så
  `verktyg/bygg-profil.py` måste köras om när paletten ändras.

## Granskning

`python3 verktyg/kolla-sajten.py` går igenom alla nio sidor och letar efter det Lighthouse
inte tar: obalanserad HTML, dubbla `h1`, rubriknivåer som hoppar, meny som glidit isär
mellan sidorna, `aria-current` på fel länk, interna länkar och ankare som pekar i tomma
luften, `<audio>` utan `preload="none"`, bilder utan `alt` eller mått, kontraster under
WCAG AA i båda lägena. `--natet` kollar dessutom
att de externa länkarna svarar. Inga utskrivna rader betyder att allt är i sin ordning.

Det finns ingen `sitemap.xml`. Alla fem sidor står i menyn på varenda sida, så en robot
som hittar startsidan har hittat allt — Google säger själva att sajtkartor är onödiga under
500 sidor. Lägg inte tillbaka en; den skulle bara bli ännu en fil att hålla i synk.

Kör granskningen innan varje push. Lighthouse körs vid behov:

```
nvm use 22.2.0
npx lighthouse http://localhost:8765/ --preset=desktop --view
```

Två anmärkningar från Lighthouse lämnas medvetet obesvarade: **Minify CSS** (stilmallen ska
gå att läsa — det är hela poängen med att slippa byggsteg) och **Use efficient cache
lifetimes** (GitHub Pages sätter sina egna svarshuvuden, vi når dem inte).

## Publicering

Push till `main` publicerar direkt, från mappen `docs/`. `docs/CNAME` innehåller
`agatrion.se`; DNS pekar apex med A/AAAA till GitHubs adresser och `www` via CNAME till
`teyrow.github.io`.

Kontrollera lokalt före push — servern ska stå i `docs`, annars stämmer inte de absoluta
sökvägarna:

```
cd docs && python3 -m http.server 8000
```
