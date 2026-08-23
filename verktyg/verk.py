#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Katalog över musiken: vilket verk och vilken sats varje inspelat spår är.

Sidorna ska ange verk, sats och tonsättare, men filnamnen gör det inte — flera
spår heter bara "Haydn" eller "Mendelsohn". Här bor kopplingen mellan mp3-fil
och verk, och här bor uppgifterna om verken.

`saker` säger hur väl belagd kopplingen är:

    belagd     står i etikettfilen, på affischen eller i filnamnet
    analys     ihopparad med ett belagt spår av verktyg/jamfor-inspelningar.py
    sannolik   följer entydigt av något belagt (samma sats, annan konsert)
    gissning   behöver bekräftas genom lyssning — visas som förslag på urvalssidan

Verk med `fragor` är sådana där själva verket är oklart, inte bara satsen.
Använd urvalssidan (verktyg/bygg-urval.py) för att lyssna igenom och bekräfta.
"""

# ------------------------------------------------------------------- verken
# id: tonsättare, titel, satser, ev. fotnot, ev. öppen fråga
VERK = {
    "clara-op17": dict(
        tonsattare="Clara Schumann", titel="Pianotrio i g-moll, op. 17",
        satser=["Allegro moderato", "Scherzo. Tempo di menuetto", "Andante", "Allegretto"]),
    "maier-ess": dict(
        tonsattare="Amanda Maier-Röntgen", titel="Pianotrio i Ess-dur",
        satser=["Allegro", "Scherzo", "Andante", "Finale. Allegro con fuoco"]),
    "schumann-op80": dict(
        tonsattare="Robert Schumann", titel="Pianotrio nr 2 i F-dur, op. 80",
        satser=["Sehr lebhaft", "Mit innigem Ausdruck \u2013 Lebhaft",
                "In m\u00e4ssiger Bewegung", "Nicht zu rasch"]),
    "schumann-op73": dict(
        tonsattare="Robert Schumann", titel="Fantasiest\u00fccke, op. 73",
        satser=["Zart und mit Ausdruck", "Lebhaft, leicht", "Rasch und mit Feuer"],
        fotnot="F\u00f6r cello och piano"),
    "chaminade-op11": dict(
        tonsattare="C\u00e9cile Chaminade", titel="Pianotrio nr 1 i g-moll, op. 11",
        satser=["Allegro", "Andante", "Scherzo", "Finale"]),
    "haydn-c": dict(
        tonsattare="Joseph Haydn", titel="Pianotrio i C-dur", satser=[],
        fragor="Vilket Hob-nummer? Hob. XV:27 \u00e4r den vanligaste C-durtrion."),
    "haydn-g": dict(
        tonsattare="Joseph Haydn", titel="Pianotrio nr 39 i G-dur, Hob. XV:25",
        satser=["Andante", "Poco adagio. Cantabile", "Rondo all\u2019Ongarese. Presto"]),
    "mendelssohn-op49": dict(
        tonsattare="Felix Mendelssohn", titel="Pianotrio nr 1 i d-moll, op. 49",
        satser=["Molto allegro ed agitato", "Andante con moto tranquillo",
                "Scherzo. Leggiero e vivace", "Finale. Allegro assai appassionato"]),
    "gliere-op39": dict(
        tonsattare="Reinhold Gli\u00e8re", titel="\u00c5tta duetter f\u00f6r violin och cello, op. 39",
        satser=["Preludium", "Gavott", "Vaggvisa", "Canzonetta",
                "Intermezzo", "Impromptu", "Scherzo", "Etyd"]),
    "juon-reverie": dict(
        tonsattare="Paul Juon", titel="R\u00eaverie", satser=[],
        fotnot="Nr 1 ur Trio-miniatyrer"),
    "bridge-meditation": dict(
        tonsattare="Frank Bridge", titel="Meditation", satser=[],
        fotnot="Nr 1 ur Fyra korta stycken, H 104"),
    # Ingen inspelning \u00e4r Meditation. Sex spår hette det eller Romance om vartannat;
    # ljudj\u00e4mf\u00f6relsen visade att alla sex \u00e4r samma musik, och Andreas har avgjort
    # att det \u00e4r Romance. Filnamnen under media/ljud s\u00e4ger fortfarande "meditation" på
    # fyra av dem \u2014 de r\u00f6rs inte, eftersom filerna cachas ett \u00e5r på sina URL:er.
    "bridge-romance": dict(
        tonsattare="Frank Bridge", titel="Romance", satser=[],
        fotnot="Nr 4 ur Miniatyrer f\u00f6r pianotrio"),
    "pb-sommarsang": dict(
        tonsattare="Wilhelm Peterson-Berger", titel="Sommars\u00e5ng", satser=[],
        fotnot="Nr 2 ur Fr\u00f6s\u00f6blomster I"),
    "pb-lawn-tennis": dict(
        tonsattare="Wilhelm Peterson-Berger", titel="Lawn tennis", satser=[],
        fotnot="Nr 3 ur Fr\u00f6s\u00f6blomster I"),
    "lotta": dict(
        tonsattare="Jan Sandstr\u00f6m", titel="S\u00e5ng till Lotta", satser=[],
        fotnot="Arrangemang f\u00f6r pianotrio av G\u00f6sta Nylund"),
    "oblivion": dict(tonsattare="Astor Piazzolla", titel="Oblivion", satser=[]),
    "schindler": dict(
        tonsattare="John Williams", titel="Tema ur Schindler\u2019s List", satser=[],
        fotnot="Arrangemang f\u00f6r pianotrio av G\u00f6sta Nylund"),
    "saint-saens-op43": dict(
        tonsattare="Camille Saint-Sa\u00ebns", titel="Allegro appassionato, op. 43", satser=[],
        fotnot="F\u00f6r cello och piano"),
    "koch-variationer": dict(
        tonsattare="Erland von Koch",
        titel="Sju variationer \u00f6ver \u201dJag vet en dejlig rosa\u201d", satser=[]),
    "mendelssohn-preludium": dict(
        tonsattare="Felix Mendelssohn", titel="Preludium och fuga i f-moll", satser=[],
        fragor="Sannolikt op. 35 nr 5 f\u00f6r piano \u2014 bekr\u00e4fta."),
    "schubert-d898": dict(
        tonsattare="Franz Schubert", titel="Pianotrio nr 1 i B-dur, D 898",
        satser=["Allegro moderato", "Andante un poco mosso",
                "Scherzo. Allegro", "Rondo. Allegro vivace"]),
}


# -------------------------------------------------------------------- spåren
# "konsert/filnamn.mp3": (verk-id, sats, säkerhet)   sats 0 = hela verket
SPAR = {
    "bjarka-saby-2021/01-joseph-haydn-pianotrio-i-c-dur.mp3":         ("haydn-c", 0, "belagd"),
    "bjarka-saby-2021/02-wilhelm-peterson-berger-sommarsang.mp3":     ("pb-sommarsang", 0, "belagd"),
    "bjarka-saby-2021/03-wilhelm-peterson-berger-lawn-tennis.mp3":    ("pb-lawn-tennis", 0, "belagd"),
    "bjarka-saby-2021/04-robert-schumann-fantasiestucke.mp3":         ("schumann-op73", 1, "belagd"),
    "bjarka-saby-2021/05-frank-bridge-meditation.mp3":                ("bridge-romance", 0, "belagd"),
    "bjarka-saby-2021/06-amanda-maier-rontgen-pianotrio-i-ess-dur.mp3": ("maier-ess", 0, "belagd"),
    "bjarka-saby-2021/07-jan-sandstrom-sang-till-lotta.mp3":          ("lotta", 0, "belagd"),
    "bjarka-saby-2022/01-romance-ur-3-miniatyrer-for-pianotrio-av-frank-bridge.mp3": ("bridge-romance", 0, "belagd"),
    "bjarka-saby-2022/02-sju-variationer-over-jag-vet-en-dejlig-rosa-av-erland-von-ko.mp3": ("koch-variationer", 0, "belagd"),
    "bjarka-saby-2022/03-allegro-appassionato-op-43-av-camille-saint-saens.mp3": ("saint-saens-op43", 0, "belagd"),
    "bjarka-saby-2022/04-preludium-och-fuga-i-f-moll-av-felix-mendelssohn.mp3": ("mendelssohn-preludium", 0, "belagd"),
    "bjarka-saby-2022/05-prelude-ur-8-duetter-for-violin-och-cello-op-39-av-reinhold-.mp3": ("gliere-op39", 1, "belagd"),
    "bjarka-saby-2022/06-berceuse-ur-8-duetter-for-violin-och-cello-op-39-av-reinhold.mp3": ("gliere-op39", 3, "belagd"),
    "bjarka-saby-2022/07-sehr-lebhaft-pianotrio-nr-2-i-f-dur-op-80-av-robert-schumann.mp3": ("schumann-op80", 1, "belagd"),
    "bjarka-saby-2022/08-mit-innigem-ausdruck-lebhaft-pianotrio-nr-2-i-f-dur-op-80-av.mp3": ("schumann-op80", 2, "belagd"),
    "bjarka-saby-2022/09-in-massiger-bewegung-pianotrio-nr-2-i-f-dur-op-80-av-robert-.mp3": ("schumann-op80", 3, "belagd"),
    "bjarka-saby-2022/10-nicht-zu-rasch-pianotrio-nr-2-i-f-dur-op-80-av-robert-schuma.mp3": ("schumann-op80", 4, "belagd"),
    "bjarka-saby-2022/11-sang-till-lotta-arr-for-pianotrio-g-nylund-av-jan-sandstrom.mp3": ("lotta", 0, "belagd"),
    "brannestad-2024/01-clara-schumann-allegro-moderato.mp3":         ("clara-op17", 1, "belagd"),
    "brannestad-2024/02-clara-schumann-scherzo-och-trio.mp3":         ("clara-op17", 2, "belagd"),
    "brannestad-2024/03-clara-schumann-andante.mp3":                  ("clara-op17", 3, "belagd"),
    "brannestad-2024/04-clara-schumann-allegretto.mp3":               ("clara-op17", 4, "belagd"),
    "brannestad-2024/05-amanda-maier-rontgen-allegro.mp3":            ("maier-ess", 1, "belagd"),
    "brannestad-2024/06-amanda-maier-rontgen-scherzo.mp3":            ("maier-ess", 2, "belagd"),
    "brannestad-2024/07-amanda-maier-rontgen-andante.mp3":            ("maier-ess", 3, "belagd"),
    "brannestad-2024/08-amanda-maier-rontgen-finale-allegro-con-fuoco.mp3": ("maier-ess", 4, "belagd"),
    "brannestad-2024/09-cecile-chaminade-andante-ur-pianotrio-nr-1.mp3": ("chaminade-op11", 2, "belagd"),
    "ekeby-2023/01-mendelsohn.mp3":                                   ("mendelssohn-op49", 2, "belagd"),
    "ekeby-2023/02-sang-till-lotta.mp3":                              ("lotta", 0, "belagd"),
    "ekeby-2023/03-bridge.mp3":                                       ("bridge-romance", 0, "belagd"),
    "ekeby-2023/04-piazolla.mp3":                                     ("oblivion", 0, "belagd"),
    "ekeby-2023/05-haydn.mp3":                                        ("haydn-g", 2, "analys"),
    "ekeby-2023/06-schindler-s-list.mp3":                             ("schindler", 0, "belagd"),
    "ekeby-2023/07-chaminade.mp3":                                    ("chaminade-op11", 2, "belagd"),
    "ekeby-2023/08-haydn-ii.mp3":                                     ("haydn-g", 1, "belagd"),
    "landeryd-2022/01-sehr-lebhaft.mp3":                              ("schumann-op80", 1, "belagd"),
    "landeryd-2022/02-mit-innigem-ausdruck-lebhaft.mp3":              ("schumann-op80", 2, "belagd"),
    "landeryd-2022/03-prelude.mp3":                                   ("gliere-op39", 1, "analys"),
    "landeryd-2022/04-cradle-song.mp3":                               ("gliere-op39", 3, "analys"),
    "landeryd-2022/05-romance.mp3":                                   ("bridge-romance", 0, "belagd"),
    "landeryd-2022/06-sang-till-lotta.mp3":                           ("lotta", 0, "belagd"),
    "landeryd-2022/07-schindler-s-list.mp3":                          ("schindler", 0, "belagd"),
    "landeryd-2022/08-in-massiger-bewegung.mp3":                      ("schumann-op80", 3, "belagd"),
    "landeryd-2022/09-nicht-zu-rasch.mp3":                            ("schumann-op80", 4, "belagd"),
    "lillkyrkan-2021/01-joseph-haydn-pianotrio-i-c-dur.mp3":          ("haydn-c", 0, "belagd"),
    "lillkyrkan-2021/02-wilhelm-peterson-berger-sommarsang.mp3":      ("pb-sommarsang", 0, "belagd"),
    "lillkyrkan-2021/03-wilhelm-peterson-berger-lawn-tennis.mp3":     ("pb-lawn-tennis", 0, "belagd"),
    "lillkyrkan-2021/04-robert-schumann-fantasiestucke.mp3":          ("schumann-op73", 1, "belagd"),
    "lillkyrkan-2021/05-frank-bridge-meditation.mp3":                 ("bridge-romance", 0, "belagd"),
    "lillkyrkan-2021/06-amanda-maier-rontgen-pianotrio-i-ess-dur.mp3": ("maier-ess", 1, "analys"),
    "lillkyrkan-2021/07-jan-sandstrom-sang-till-lotta.mp3":           ("lotta", 0, "belagd"),
    "motala-2022/01-robert-schumann-sehr-lebhaft.mp3":                ("schumann-op80", 1, "belagd"),
    "motala-2022/02-robert-schumann-mit-innigem-ausdruck-lebhaft.mp3": ("schumann-op80", 2, "belagd"),
    "motala-2022/03-robert-schumann-in-massiger-bewegung.mp3":        ("schumann-op80", 3, "belagd"),
    "motala-2022/04-robert-schumann-nicht-zu-rasch.mp3":              ("schumann-op80", 4, "belagd"),
    "rassnas-2023/01-joseph-haydn-pianotrio-i-g-dur.mp3":             ("haydn-g", 0, "belagd"),
    "rassnas-2023/02-frank-bridge-meditation.mp3":                    ("bridge-romance", 0, "belagd"),
    "rassnas-2023/03-astor-piazzolla-oblivion.mp3":                   ("oblivion", 0, "belagd"),
    "rassnas-2023/04-jan-sandstrom-sang-till-lotta.mp3":              ("lotta", 0, "belagd"),
    "rassnas-2023/05-felix-mendelssohn-pianotrio-tredje-satsen.mp3":  ("mendelssohn-op49", 2, "belagd"),
    "skanninge-2024/01-sehr-lebhaft.mp3":                             ("schumann-op80", 1, "belagd"),
    "skanninge-2024/02-mit-innigem-ausdruck-lebhaft.mp3":             ("schumann-op80", 2, "belagd"),
    "skanninge-2024/03-in-massiger-bewegung.mp3":                     ("schumann-op80", 3, "belagd"),
    "skanninge-2024/04-nicht-zu-rasch.mp3":                           ("schumann-op80", 4, "belagd"),
    "skanninge-2024/05-oblivion-piazzolla.mp3":                       ("oblivion", 0, "belagd"),
    "tranas-2024/01-amanda-maier-rontgen-andante-sats-3.mp3":         ("maier-ess", 3, "belagd"),
    "tranas-2024/02-clara-schumann-allegro-moderato.mp3":             ("clara-op17", 1, "belagd"),
    "tranas-2024/03-clara-schumann-scherzo-och-trio.mp3":             ("clara-op17", 2, "belagd"),
    "tranas-2024/04-clara-schumann-andante.mp3":                      ("clara-op17", 3, "belagd"),
    "tranas-2024/05-clara-schumann-allegretto.mp3":                   ("clara-op17", 4, "belagd"),
    "tranas-2024/06-cecile-chaminade-andante-ur-pianotrio-nr-1.mp3":  ("chaminade-op11", 2, "belagd"),
    "tranas-2024/07-jan-sandstrom-sang-till-lotta.mp3":               ("lotta", 0, "belagd"),
    "tranas-2026/01-franz-schubert-schubert.mp3":                     ("schubert-d898", 2, "belagd"),
    "tranas-2026/02-felix-mendelssohn-mendelssohn.mp3":               ("mendelssohn-op49", 2, "belagd"),
    "tranas-2026/03-clara-schumann-clara-schumann.mp3":               ("clara-op17", 3, "analys"),
    "tranas-2026/04-reinhold-gliere-vaggvisa.mp3":                    ("gliere-op39", 3, "belagd"),
    "tranas-2026/05-reinhold-gliere-canzonetta.mp3":                  ("gliere-op39", 4, "belagd"),
    "tranas-2026/06-paul-juon-reverie.mp3":                           ("juon-reverie", 0, "belagd"),
    "tranas-2026/07-cecile-chaminade-andante-ur-pianotrio-nr-1.mp3":  ("chaminade-op11", 2, "belagd"),
    "tranas-2026/08-john-williams-tema-ur-schindler-s-list.mp3":      ("schindler", 0, "belagd"),
    "vastra-ryd-2021/01-amanda-maier-rontgen-pianotrio-i-ess-dur.mp3": ("maier-ess", 0, "belagd"),
    "vastra-ryd-2021/02-clara-schumann-andante.mp3":                  ("clara-op17", 3, "belagd"),
    "vastra-ryd-2021/03-clara-schumann-scherzo.mp3":                  ("clara-op17", 2, "analys"),
    "vastra-ryd-2021/04-cecile-chaminade-ur-pianotrion.mp3":          ("chaminade-op11", 2, "analys"),
    "vastra-ryd-2021/05-jan-sandstrom-sang-till-lotta.mp3":           ("lotta", 0, "belagd"),
    "vreta-2021/01-clara-schumann-allegro-moderato.mp3":              ("clara-op17", 1, "belagd"),
    "vreta-2021/02-clara-schumann-scherzo-och-trio.mp3":              ("clara-op17", 2, "belagd"),
    "vreta-2021/03-clara-schumann-andante.mp3":                       ("clara-op17", 3, "belagd"),
    "vreta-2021/04-clara-schumann-allegretto.mp3":                    ("clara-op17", 4, "belagd"),
    "vreta-2021/05-amanda-maier-rontgen-allegro.mp3":                 ("maier-ess", 1, "belagd"),
    "vreta-2021/06-amanda-maier-rontgen-scherzo.mp3":                 ("maier-ess", 2, "belagd"),
    "vreta-2021/07-amanda-maier-rontgen-andante.mp3":                 ("maier-ess", 3, "belagd"),
    "vreta-2021/08-amanda-maier-rontgen-finale-allegro-con-fuoco.mp3": ("maier-ess", 4, "belagd"),
    "vreta-2021/09-jan-sandstrom-sang-till-lotta.mp3":                ("lotta", 0, "belagd"),
}


# ---------------------------------------------------------------- konserter
# slug: plats, datum, var inspelningen ligger i dag
KONSERTER = {
    "tranas-2026": ("Tran\u00e5s kyrka", "7 mars 2026", "lyssna"),
    "brannestad-2024": ("Br\u00e4nnestad musikatelj\u00e9, Huar\u00f6d", "10 november 2024", "lyssna"),
    "tranas-2024": ("Tran\u00e5s kyrka", "3 november 2024", "lyssna"),
    "skanninge-2024": ("R\u00e5dhuset, Sk\u00e4nninge", "4 februari 2024", "arkiv"),
    "ekeby-2023": ("Ekeby kyrka, Boxholm", "11 mars 2023", "arkiv"),
    "rassnas-2023": ("R\u00e5ssn\u00e4skyrkan, Motala", "1 januari 2023", "arkiv"),
    "bjarka-saby-2022": ("Nya Slottet Bj\u00e4rka-S\u00e4by", "14 juli 2022", "arkiv"),
    "landeryd-2022": ("Landeryds kyrka, Link\u00f6ping", "10 juli 2022", "arkiv"),
    "motala-2022": ("Motala kyrka", "26 februari 2022", "arkiv"),
    "vreta-2021": ("Vreta klosters kyrka", "12 september 2021", "arkiv"),
    "vastra-ryd-2021": ("V\u00e4stra Ryds kyrka, Rydsn\u00e4s", "25 juli 2021", "arkiv"),
    "bjarka-saby-2021": ("Nya Slottet Bj\u00e4rka-S\u00e4by", "22 juli 2021", "arkiv"),
    "lillkyrkan-2021": ("Lillkyrkan, Motala", "18 juli 2021", "arkiv"),
}


# ------------------------------------------------------------------- urvalet
# Vilken inspelning ett verk ska länkas till från repertoarsidan. Nyckeln är
# "verk:sats" — samma sträng som rullgardinerna på urvalssidan använder.
# Ligger inspelningen inte på lyssnasidan hamnar den under "Enstaka stycken"
# där, så att repertoarlänkarna aldrig pekar in i det olänkade arkivet.
VAL = {
    "schubert-d898:2": "tranas-2026/01-franz-schubert-schubert.mp3",
    "mendelssohn-op49:2": "tranas-2026/02-felix-mendelssohn-mendelssohn.mp3",
    "schindler:0": "tranas-2026/08-john-williams-tema-ur-schindler-s-list.mp3",
    "bridge-romance:0":
        "bjarka-saby-2022/01-romance-ur-3-miniatyrer-for-pianotrio-av-frank-bridge.mp3",
    "koch-variationer:0":
        "bjarka-saby-2022/02-sju-variationer-over-jag-vet-en-dejlig-rosa-av-erland-von-ko.mp3",
    "gliere-op39:1": "landeryd-2022/03-prelude.mp3",
    "gliere-op39:3": "landeryd-2022/04-cradle-song.mp3",
}


def ankare(nyckel):
    """"gliere-op39:3" -> "v-gliere-op39-3", id:t repertoarsidan länkar till."""
    return "v-" + nyckel.replace(":", "-")


def uppgift(fil):
    """(tonsättare, verktitel, satstext, säkerhet) för en mp3 under media/ljud."""
    if fil not in SPAR:
        return None
    vid, sats, saker = SPAR[fil]
    v = VERK[vid]
    if sats and sats <= len(v["satser"]):
        romersk = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"][sats - 1]
        satstext = "%s. %s" % (romersk, v["satser"][sats - 1])
    elif sats:
        satstext = "Sats %d" % sats
    else:
        satstext = ""
    return v["tonsattare"], v["titel"], satstext, saker


def alternativ():
    """Alla (värde, etikett) som rullgardinerna på urvalssidan kan innehålla."""
    ut = []
    for vid, v in VERK.items():
        if v["satser"]:
            for i, sats in enumerate(v["satser"], 1):
                ut.append(("%s:%d" % (vid, i),
                           "%s \u00b7 %s \u00b7 %s" % (v["tonsattare"], v["titel"], sats)))
            ut.append(("%s:0" % vid,
                       "%s \u00b7 %s \u00b7 hela verket" % (v["tonsattare"], v["titel"])))
        else:
            ut.append(("%s:0" % vid, "%s \u00b7 %s" % (v["tonsattare"], v["titel"])))
    return ut
