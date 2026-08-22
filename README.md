# agatrion.se

Webbplatsen för AGA-trion. Ren HTML och CSS utan byggsteg — filerna i den här mappen är
exakt det som ligger på servern. GitHub Pages publicerar `main` automatiskt vid varje push.

## Ändra något

1. Redigera filen.
2. Titta på resultatet lokalt:

   ```
   python3 -m http.server 8000
   ```

   Öppna sedan <http://localhost:8000>.
3. `git add`, `git commit`, `git push`. Sajten är uppdaterad inom ett par minuter.

Sök efter `FYLL I` i filerna — där finns allt som är kvar att fylla i.

## Lägga till en konsert

Öppna `konserter.html`. Kopiera ett `<li>`-block, klistra in det överst under rubriken
*Kommande* och ändra datum, plats och programtext:

```html
<li>
  <article class="concert">
    <time datetime="2026-11-14">14 november 2026</time>
    <div>
      <p class="venue">Tranås kyrka</p>
      <p class="programme">Kort om programmet.</p>
    </div>
  </article>
</li>
```

`datetime`-attributet ska vara i formatet ÅÅÅÅ-MM-DD (det läses av sökmotorer);
texten inuti `<time>` är den som visas. När konserten är spelad flyttas blocket ner
under *Tidigare*.

I toppen av `konserter.html` finns också en färdig mall för `Event`-data (JSON-LD)
som gör att en kommande konsert kan dyka upp i Googles evenemangsvisning.

## Lägga till en inspelning

Ljudfilerna ligger i `media/ljud/<konsert>/` som mp3. Ett spår läggs in i `lyssna.html` så här:

```html
<li>
  <p class="track-title">Allegro moderato <span class="duration">10:40</span></p>
  <audio controls preload="none" src="/media/ljud/kristianstad-2025/01-clara-schumann-allegro-moderato.mp3"></audio>
</li>
```

`preload="none"` gör att filen laddas ner först när någon trycker på play — viktigt,
annars drar sidan hundratals megabyte vid varje besök.

### Klippa en ny konsertinspelning

Inspelningarna klipps från en lång wav-fil med hjälp av etiketter exporterade från
Audacity (starttid, sluttid, titel — en rad per spår). Skriptet
`verktyg/klipp-konsert.py` gör resten: normaliserar hela konserten till samma nivå,
går ner till 16 bitar/48 kHz och kodar mp3 med `lame`.

```
python3 verktyg/klipp-konsert.py
```

Spårlistorna står i början av skriptet — lägg till konserten där och kör.
Kräver `lame` (`brew install lame`) och `numpy` (`pip3 install numpy`).

## Video

Videor bäddas in från YouTube, men först när besökaren klickar på uppspelningsknappen —
inga anrop till Google sker vid vanlig sidladdning. Se `FYLL I`-kommentaren i
`lyssna.html` för hur man lägger in ett video-id.

## Domän

`CNAME` innehåller `agatrion.se`. DNS hos registraren pekar apex (`agatrion.se`) med
A- och AAAA-poster till GitHubs adresser, och `www` med en CNAME till `teyrow.github.io`.
Ändra inte `CNAME`-filen utan att samtidigt ändra DNS.

## Bilder

Bilder ska skalas ner innan de checkas in — max 1800 px bred räcker gott:

```
sips -Z 1800 -s format jpeg -s formatOptions 82 --out media/bild/ny-bild.jpg original.jpg
```

## Historik

Den gamla Octopress-sajten från 2014 finns kvar i taggarna `octopress-arkiv-master`
och `octopress-arkiv-gh-pages`.
