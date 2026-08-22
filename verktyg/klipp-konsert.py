#!/usr/bin/env python3
"""Klipp konsertinspelningar i spår och koda till mp3 för agatrion.se.

Källorna är 32-bitars PCM-wav i 48/96 kHz. Vi klipper enligt Audacity-etiketterna,
normaliserar varje konsert till -1,5 dBFS (samma gain för hela konserten, så
dynamiken mellan satserna behålls), går ner till 16 bitar / 48 kHz och kodar med lame.
"""
import os
import subprocess
import sys
import unicodedata
import wave

import numpy as np

# Källinspelningarna ligger utanför repot — de är för stora för git.
SRC = os.environ.get("AGATRION_SOURCES", "/Users/aj/code/music-convert/sources")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media", "ljud")
TARGET_PEAK = 10 ** (-1.5 / 20)  # -1,5 dBFS
CHUNK_SEC = 20

CONCERTS = [
    {
        "slug": "brannestad-2024",
        "wav": "kristianstad.wav",
        "album": "AGA-trion live i Brännestad musikateljé 2024",
        "year": "2024",
        "tracks": [
            (0.05, 640.09, "Allegro moderato", "Clara Schumann"),
            (640.09, 914.66, "Scherzo och Trio", "Clara Schumann"),
            (919.35, 1197.53, "Andante", "Clara Schumann"),
            (1207.47, 1670.59, "Allegretto", "Clara Schumann"),
            (1685.17, 2247.48, "Allegro", "Amanda Maier-Röntgen"),
            (2255.30, 2556.83, "Scherzo", "Amanda Maier-Röntgen"),
            (2565.49, 2841.16, "Andante", "Amanda Maier-Röntgen"),
            (2841.16, 3352.54, "Finale. Allegro con fuoco", "Amanda Maier-Röntgen"),
            (3352.54, 3758.26, "Andante ur Pianotrio nr 1", "Cécile Chaminade"),
        ],
    },
    {
        "slug": "tranas-2024",
        "wav": "2024Tranås.wav",
        "album": "AGA-trion live i Tranås 2024",
        "year": "2024",
        "tracks": [
            (2.94, 278.55, "Andante (sats 3)", "Amanda Maier-Röntgen"),
            (281.53, 919.17, "Allegro moderato", "Clara Schumann"),
            (922.17, 1190.55, "Scherzo och Trio", "Clara Schumann"),
            (1193.53, 1476.69, "Andante", "Clara Schumann"),
            (1479.68, 1926.49, "Allegretto", "Clara Schumann"),
            (1929.48, 2349.60, "Andante ur Pianotrio nr 1", "Cécile Chaminade"),
            (2352.59, 2657.87, "Sång till Lotta", "Jan Sandström"),
        ],
    },
    {
        "slug": "tranas-2026",
        "wav": "Tranås2026.wav",
        "album": "AGA-trion live i Tranås kyrka, mars 2026",
        "year": "2026",
        "tracks": [
            (2.99, 484.60, "Schubert", "Franz Schubert"),
            (487.49, 874.60, "Mendelssohn", "Felix Mendelssohn"),
            (877.59, 1144.34, "Clara Schumann", "Clara Schumann"),
            (1147.33, 1316.60, "Vaggvisa", "Reinhold Glière"),
            (1319.58, 1448.14, "Canzonetta", "Reinhold Glière"),
            (1451.13, 1676.69, "Rêverie", "Paul Juon"),
            (1679.69, 2076.67, "Andante ur Pianotrio nr 1", "Cécile Chaminade"),
            (2079.65, 2294.26, "Tema ur Schindler's List", "John Williams"),
        ],
    },
]


def slug(text):
    text = text.lower().replace("ä", "a").replace("å", "a").replace("ö", "o")
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    out = []
    for ch in text:
        out.append(ch if ch.isalnum() else "-")
    return "-".join(filter(None, "".join(out).split("-")))[:60]


def frames_of(w, start, end):
    rate = w.getframerate()
    return int(start * rate), int(end * rate)


def read_block(w, pos, count):
    w.setpos(pos)
    raw = w.readframes(count)
    a = np.frombuffer(raw, dtype="<i4")
    return a.reshape(-1, 2)


def scan_peak(path, tracks):
    """Toppnivå över de klippta partierna, för normalisering av hela konserten."""
    peak = 1
    with wave.open(path, "rb") as w:
        rate = w.getframerate()
        for start, end, *_ in tracks:
            a, b = frames_of(w, start, end)
            pos = a
            while pos < b:
                n = min(CHUNK_SEC * rate, b - pos)
                block = read_block(w, pos, n)
                if block.size:
                    peak = max(peak, int(np.abs(block).max()))
                pos += n
    return peak


def encode(path, tracks, outdir, album, year, gain):
    os.makedirs(outdir, exist_ok=True)
    results = []
    with wave.open(path, "rb") as w:
        rate = w.getframerate()
        decimate = rate // 48000  # 96 kHz -> 48 kHz, 48 kHz -> oförändrat
        for i, (start, end, title, composer) in enumerate(tracks, 1):
            name = "%02d-%s.mp3" % (i, slug(("%s %s" % (composer, title)).strip()))
            dest = os.path.join(outdir, name)
            a, b = frames_of(w, start, end)
            cmd = [
                "lame", "-r", "-s", "48", "--bitwidth", "16", "--signed",
                "--little-endian", "-m", "j", "-V", "3", "--quiet",
                "--tt", title, "--ta", "AGA-trion", "--tl", album,
                "--ty", year, "--tn", str(i), "--tg", "Classical",
                "-", dest,
            ]
            if composer:
                cmd[-2:-2] = ["--tc", composer]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            pos, carry = a, None
            while pos < b:
                n = min(CHUNK_SEC * rate, b - pos)
                block = read_block(w, pos, n).astype(np.float32) * gain
                pos += n
                if decimate == 2:
                    if carry is not None:
                        block = np.concatenate([carry, block])
                        carry = None
                    if len(block) % 2:
                        carry = block[-1:]
                        block = block[:-1]
                    block = block.reshape(-1, 2, 2).mean(axis=1)
                pcm = np.clip(block, -2147483648, 2147483647).astype(np.int32) >> 16
                proc.stdin.write(pcm.astype("<i2").tobytes())
            proc.stdin.close()
            if proc.wait() != 0:
                sys.exit("lame misslyckades för %s" % dest)
            secs = end - start
            results.append((name, title, composer, secs, os.path.getsize(dest)))
            print("  %-52s %2d:%02d  %5.1f MB" % (name, secs // 60, secs % 60,
                                                  os.path.getsize(dest) / 1e6), flush=True)
    return results


def main():
    total = 0
    for concert in CONCERTS:
        path = os.path.join(SRC, concert["wav"])
        print("%s (%s)" % (concert["slug"], concert["wav"]), flush=True)
        peak = scan_peak(path, concert["tracks"])
        gain = min(TARGET_PEAK * 2147483647 / peak, 8.0)
        print("  topp %.1f dBFS -> gain %+.1f dB" % (
            20 * np.log10(peak / 2147483647), 20 * np.log10(gain)), flush=True)
        rows = encode(path, concert["tracks"], os.path.join(OUT, concert["slug"]),
                      concert["album"], concert["year"], gain)
        total += sum(r[4] for r in rows)
    print("Totalt %.0f MB" % (total / 1e6))


if __name__ == "__main__":
    main()
