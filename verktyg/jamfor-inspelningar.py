#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hitta vilka inspelade spår som är samma musik.

Nästan alla verk trion spelat förekommer på flera konserter, men spåren är
namngivna olika — ibland bara "Haydn" eller "Mendelsohn". Skriptet räknar fram
ett kromagram (hur energin fördelar sig på de tolv tonstegen över tid) för varje
mp3 och jämför spåren med varandra. Två inspelningar av samma sats får nästan
samma harmoniska förlopp även om tempot skiljer, så de kan paras ihop.

    python3 verktyg/jamfor-inspelningar.py --drag       # 1. räkna fram kromagram
    python3 verktyg/jamfor-inspelningar.py --jamfor     # 2. para ihop spåren
    python3 verktyg/jamfor-inspelningar.py --grupper    # 3. skriv ut grupperna

Kromagrammen mellanlagras i verktyg/.kroma/ (ligger inte i git). Steg 1 tar en
kvart för hela materialet; steg 2 några minuter.

Jämförelsen görs på två sätt:
  * lika långa spår paras med DTW över hela förloppet
  * ett kort spår söks som delsträcka i ett långt, vilket hittar enskilda satser
    inuti en hel trio som spelats in i ett stycke

Mätt mot de 124 par vi känner till hittar 0,25 som gräns 123 av dem, utan att
para ihop något som inte hör ihop. Det var så vi upptäckte att de sex spår som
hette Meditation respektive Romance om vartannat allihop är Bridges Romance.
"""
import argparse
import glob
import json
import os
import subprocess
import tempfile
import wave

import numpy as np

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sajten ligger i docs/ — allt utanför den mappen publiceras aldrig
SAJT = os.path.join(ROT, "docs")
KROMA = os.path.join(ROT, "verktyg", ".kroma")
N, HOP, SR = 4096, 2048, 11025
RAMAR_PER_SEK = SR / HOP          # ~5,4
DTW_SEK = 2.0                     # upplösning i jämförelsen


# ------------------------------------------------------------------ steg 1
def las_wav(path):
    with wave.open(path, "rb") as w:
        sr, kanaler, bredd = w.getframerate(), w.getnchannels(), w.getsampwidth()
        rå = w.readframes(w.getnframes())
    if bredd != 2:
        raise SystemExit("oväntat bitdjup %d i %s" % (bredd * 8, path))
    x = np.frombuffer(rå, dtype="<i2").astype(np.float32) / 32768.0
    if kanaler > 1:
        x = x.reshape(-1, kanaler).mean(axis=1)
    faktor = int(round(sr / SR))
    if faktor > 1:
        x = x[: len(x) // faktor * faktor].reshape(-1, faktor).mean(axis=1)
    return x


def kroma(x):
    if len(x) < N:
        return np.zeros((0, 12), np.float32)
    fönster = np.hanning(N).astype(np.float32)
    steg = (len(x) - N) // HOP + 1
    ramar = np.lib.stride_tricks.as_strided(
        x, shape=(steg, N), strides=(x.strides[0] * HOP, x.strides[0]))
    frek = np.fft.rfftfreq(N, 1.0 / SR)
    giltig = (frek > 60) & (frek < 2200)
    tonhojd = np.zeros(len(frek), np.int64)
    tonhojd[giltig] = np.round(69 + 12 * np.log2(frek[giltig] / 440.0)).astype(np.int64) % 12
    masker = [(tonhojd == pk) & giltig for pk in range(12)]
    ut = np.zeros((steg, 12), np.float32)
    for i in range(0, steg, 512):
        blk = np.abs(np.fft.rfft(ramar[i:i + 512] * fönster, axis=1)).astype(np.float32)
        for pk, m in enumerate(masker):
            ut[i:i + 512, pk] = blk[:, m].sum(axis=1)
    return ut / np.maximum(np.linalg.norm(ut, axis=1, keepdims=True), 1e-9)


def rakna_drag():
    os.makedirs(KROMA, exist_ok=True)
    filer = sorted(glob.glob(os.path.join(SAJT, "media", "ljud", "*", "*.mp3")))
    for i, mp3 in enumerate(filer, 1):
        namn = "%s__%s" % (os.path.basename(os.path.dirname(mp3)), os.path.basename(mp3)[:-4])
        mål = os.path.join(KROMA, namn + ".npz")
        if os.path.exists(mål):
            continue
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
            tmp = t.name
        try:
            subprocess.run(["lame", "--quiet", "--decode", mp3, tmp], check=True)
            x = las_wav(tmp)
            np.savez_compressed(mål, kroma=kroma(x), langd=np.float32(len(x) / SR))
            print("%3d/%d  %-58s %6.1f s" % (i, len(filer), namn, len(x) / SR), flush=True)
        finally:
            os.unlink(tmp)


# ------------------------------------------------------------------ steg 2
def forbered(k):
    """Logkomprimera, dra bort ramens medelvärde och normera.

    Kromavektorer är idel positiva tal, så rå cosinuslikhet hamnar mellan 0,8
    och 1 även för musik som inte har med varandra att göra. Genom att centrera
    varje ram kring sitt eget medelvärde mäter vi i stället *formen* på
    ackordet, och skalan blir användbar."""
    k = np.log1p(100.0 * k)
    k = k - k.mean(axis=1, keepdims=True)
    return k / np.maximum(np.linalg.norm(k, axis=1, keepdims=True), 1e-9)


def las_alla():
    spar = []
    klump = max(1, int(round(DTW_SEK * RAMAR_PER_SEK)))
    for f in sorted(glob.glob(os.path.join(KROMA, "*.npz"))):
        d = np.load(f)
        k = d["kroma"]
        n = len(k) // klump * klump
        grov = k[:n].reshape(-1, klump, 12).mean(axis=1) if n >= klump else k
        grov = forbered(grov)
        konsert, titel = os.path.basename(f)[:-4].split("__", 1)
        medel = forbered(k.mean(axis=0, keepdims=True))[0]
        spar.append({
            "namn": os.path.basename(f)[:-4], "konsert": konsert, "titel": titel,
            "langd": float(d["langd"]), "grov": grov.astype(np.float32), "medel": medel,
        })
    for s in spar:                       # 12×12: hur tonstegen samvarierar
        c = s["grov"].T @ s["grov"]
        c = c - c.mean()
        s["kov"] = c / max(np.linalg.norm(c), 1e-9)
    return spar


def basta_skift(kov_a, kov_b):
    """Hur många halvtoner b ligger från a, och hur väl de stämmer där.

    Råssnäsinspelningen 2023 ligger en halvton från allt annat material — om det
    beror på instrumentens stämning eller på filernas väg genom Dropbox vet vi
    inte, men utan kompensation matchar den ingenting. Att söka skiftet i
    12×12-matrisen är gratis; först därefter är det värt att köra DTW.
    """
    bäst = (-2.0, 0)
    for k in range(12):
        r = np.roll(np.roll(kov_b, k, axis=0), k, axis=1)
        v = float((kov_a * r).sum())
        if v > bäst[0]:
            bäst = (v, k)
    return bäst[1] if bäst[1] <= 6 else bäst[1] - 12, bäst[0]


def dtw(a, b, delstrack=False):
    """Kostnad per ram. delstrack=True låter a börja och sluta var som helst i b."""
    kost = 0.5 * (1.0 - a @ b.T)
    n, m = kost.shape
    inf = 1e9
    forra = np.full(m, inf, np.float64)
    if delstrack:
        forra[:] = kost[0]               # fri start längs b
    else:
        forra[0] = kost[0, 0]
        for j in range(1, m):
            forra[j] = forra[j - 1] + kost[0, j]
    for i in range(1, n):
        nu = np.empty(m, np.float64)
        nu[0] = forra[0] + kost[i, 0] if not delstrack else inf
        rad = kost[i]
        f = forra
        for j in range(1, m):
            b3 = f[j] if f[j] < f[j - 1] else f[j - 1]
            if nu[j - 1] < b3:
                b3 = nu[j - 1]
            nu[j] = rad[j] + b3
        forra = nu
    slut = forra.min() if delstrack else forra[-1]
    return slut / n


def jamfor():
    spar = las_alla()
    print("%d spår" % len(spar), flush=True)
    träffar = []
    for i in range(len(spar)):
        for j in range(i + 1, len(spar)):
            a, b = spar[i], spar[j]
            if a["konsert"] == b["konsert"]:
                continue
            kort, lang = (a, b) if a["langd"] <= b["langd"] else (b, a)
            kvot = kort["langd"] / lang["langd"]
            skift, kov = basta_skift(a["kov"], b["kov"])
            medel = float(a["medel"] @ np.roll(b["medel"], skift))
            # skiftet gäller b relativt a; i delsträcksfallet jämför vi kort mot lång
            vand = -skift if kort is b else skift
            if kvot > 0.72:
                if kov < 0.35 or medel < 0.3:
                    continue
                d = dtw(a["grov"], np.roll(b["grov"], skift, axis=1))
                typ = "hel"
            else:
                if kvot < 0.12 or kov < 0.15:
                    continue
                d = dtw(kort["grov"], np.roll(lang["grov"], vand, axis=1), delstrack=True)
                typ = "del"
            träffar.append({"a": a["namn"], "b": b["namn"], "typ": typ,
                            "dtw": round(d, 4), "skift": skift, "kov": round(kov, 3),
                            "kvot": round(kvot, 3),
                            "langd_a": round(a["langd"]), "langd_b": round(b["langd"])})
        print("  %d/%d" % (i + 1, len(spar)), end="\r", flush=True)
    träffar.sort(key=lambda t: t["dtw"])
    with open(os.path.join(KROMA, "traffar.json"), "w") as fh:
        json.dump(träffar, fh, ensure_ascii=False, indent=1)
    print("\n%d kandidatpar, skrev traffar.json" % len(träffar))


# ------------------------------------------------------------------ steg 3
def grupper(tak_hel=0.25, tak_del=0.25):
    with open(os.path.join(KROMA, "traffar.json")) as fh:
        träffar = json.load(fh)
    far = {}

    def rot(x):
        far.setdefault(x, x)
        while far[x] != x:
            far[x] = far[far[x]]
            x = far[x]
        return x

    kanter = [t for t in träffar
              if t["dtw"] <= (tak_hel if t["typ"] == "hel" else tak_del)]
    for t in kanter:
        if t["typ"] != "hel":
            continue
        ra, rb = rot(t["a"]), rot(t["b"])
        if ra != rb:
            far[ra] = rb
    grupp = {}
    for namn in list(far):
        grupp.setdefault(rot(namn), []).append(namn)
    for g in sorted(grupp.values(), key=len, reverse=True):
        if len(g) < 2:
            continue
        print("── grupp om %d" % len(g))
        for namn in sorted(g):
            print("   %s" % namn)
        print()
    print("Delsträckor (kort spår funnet inuti ett långt):")
    for t in kanter:
        if t["typ"] == "del":
            kort, lang = (t["a"], t["b"]) if t["langd_a"] < t["langd_b"] else (t["b"], t["a"])
            print("   %-52s  i  %-52s  %.3f" % (kort, lang, t["dtw"]))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--drag", action="store_true")
    p.add_argument("--jamfor", action="store_true")
    p.add_argument("--grupper", action="store_true")
    a = p.parse_args()
    if a.drag:
        rakna_drag()
    if a.jamfor:
        jamfor()
    if a.grupper:
        grupper()
    if not (a.drag or a.jamfor or a.grupper):
        p.print_help()


if __name__ == "__main__":
    main()
