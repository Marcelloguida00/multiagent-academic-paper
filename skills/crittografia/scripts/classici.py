#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
classici.py - cifrari classici e crittoanalisi (didattica, CTF, verifica di robustezza).

Mostra perche' i cifrari "fatti in casa" non proteggono: li rompe senza conoscere la chiave.

Comandi (TESTO tra virgolette, oppure --file percorso):
  auto TESTO                       prova gli attacchi piu' comuni e mostra i candidati migliori
  frequenze TESTO                  frequenze, indice di coincidenza, ripetizioni (Kasiski)
  cesare TESTO [--chiave N] [--cifra]      senza chiave: prova tutte le rotazioni
  atbash TESTO
  affine TESTO [--a A --b B] [--cifra]     senza chiavi: prova tutte le 312 combinazioni
  vigenere TESTO --chiave PAROLA [--cifra]
  vigenere-attacco TESTO [--max 20]
  sostituzione-attacco TESTO [--riavvii 25]
  rail TESTO [--binari N] [--cifra]        senza N: prova da 2 a 12 binari
  rot47 TESTO
  xor-attacco (--hex H | --base64 B | --file F) [--max-chiave 40]
Opzione: --lingua it|en|auto (default auto)

Dipendenze: solo libreria standard.
"""
from __future__ import annotations

import argparse
import base64
import math
import random
import re
import sys
import unicodedata
from collections import Counter

ALFA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FREQ = {
    "it": {"A": 11.74, "B": 0.92, "C": 4.50, "D": 3.73, "E": 11.79, "F": 0.95, "G": 1.64, "H": 1.54, "I": 11.28,
           "J": 0.03, "K": 0.03, "L": 6.51, "M": 2.51, "N": 6.88, "O": 9.83, "P": 3.05, "Q": 0.51, "R": 6.37,
           "S": 4.98, "T": 5.62, "U": 3.01, "V": 2.10, "W": 0.03, "X": 0.03, "Y": 0.03, "Z": 0.49},
    "en": {"A": 8.17, "B": 1.49, "C": 2.78, "D": 4.25, "E": 12.70, "F": 2.23, "G": 2.02, "H": 6.09, "I": 6.97,
           "J": 0.15, "K": 0.77, "L": 4.03, "M": 2.41, "N": 6.75, "O": 7.51, "P": 1.93, "Q": 0.10, "R": 5.99,
           "S": 6.33, "T": 9.06, "U": 2.76, "V": 0.98, "W": 2.36, "X": 0.15, "Y": 1.97, "Z": 0.07},
}

# Testi originali usati solo per stimare le statistiche di trigrammi delle due lingue.
CORPUS = {"it": """
La crittografia e' l'arte di scrivere messaggi che solo il destinatario puo' leggere. Per secoli e' stata usata da re,
generali e mercanti, che avevano bisogno di comunicare senza che i nemici potessero capire il contenuto delle loro lettere.
Oggi la usiamo tutti, ogni giorno, spesso senza accorgercene: quando apriamo il sito della banca, quando mandiamo un
messaggio a un amico o quando paghiamo con la carta in un negozio. Il principio di base e' semplice. Si prende un testo in
chiaro, si applica una trasformazione che dipende da una chiave segreta e si ottiene un testo cifrato. Chi conosce la
chiave puo' fare il percorso inverso e tornare al messaggio originale; chi non la conosce vede soltanto una sequenza di
simboli senza senso. La sicurezza non deve dipendere dal fatto che il metodo resti nascosto, ma soltanto dalla segretezza
della chiave. Nel Rinascimento gli studiosi italiani diedero un contributo importante a questa disciplina. Leon Battista
Alberti descrisse un disco cifrante con due anelli di lettere che permetteva di cambiare alfabeto durante la scrittura,
un'idea che rendeva molto piu' difficile l'analisi delle frequenze. Qualche decennio piu' tardi Giovan Battista Bellaso
propose un sistema basato su una parola chiave che ancora oggi molti attribuiscono per errore al francese Vigenere.
L'analisi delle frequenze nasce da un'osservazione molto concreta: in ogni lingua alcune lettere compaiono piu' spesso di
altre. In italiano le vocali sono frequentissime e la lettera e, la lettera a e la lettera i si contendono il primo posto,
mentre lettere come la q o la zeta sono piuttosto rare. Se un cifrario sostituisce sempre una lettera con lo stesso
simbolo, basta contare i simboli per avere un primo indizio su quale lettera si nasconde dietro ciascuno di essi. Con
l'arrivo dei calcolatori le cose sono cambiate profondamente. I cifrari moderni lavorano sui bit e non sulle lettere,
mescolano i dati per molti giri e sono progettati in modo che il testo cifrato sembri del tutto casuale. Un buon
algoritmo, usato nel modo corretto e con una chiave abbastanza lunga, non puo' essere forzato nemmeno con tutti i computer
del mondo che lavorano insieme per migliaia di anni. Questo non significa che i sistemi reali siano invulnerabili. Molto
spesso il punto debole non e' la matematica ma le persone e il software: una password troppo corta, una chiave lasciata in
un file condiviso, un programma scritto in fretta che riutilizza lo stesso numero casuale. Per questo chi si occupa di
sicurezza deve controllare con attenzione ogni dettaglio, dalla generazione delle chiavi fino al modo in cui vengono
conservate e distrutte. Anche la firma digitale e' una conquista recente. Permette di dimostrare che un documento e' stato
scritto da una certa persona e che nessuno lo ha modificato dopo la firma. Si basa su una coppia di chiavi: quella privata
resta al proprietario e serve per firmare, quella pubblica puo' essere data a tutti e serve per verificare. Negli ultimi
anni si parla molto dei computer quantistici, che in futuro potrebbero rompere gli algoritmi a chiave pubblica usati
oggi. Per questo motivo gli esperti hanno preparato nuovi algoritmi e stanno lavorando perche' aziende e amministrazioni
li adottino per tempo. La mattina il mercato del paese si riempie di voci e di colori. I bambini corrono tra i banchi
della frutta, le nonne contrattano sul prezzo dei pomodori e il fornaio saluta tutti per nome. Quando arriva mezzogiorno
la piazza si svuota, le persiane si chiudono e per qualche ora si sente soltanto il rumore lontano delle campane. Domani
partiamo presto per andare in montagna con gli amici; ci fermeremo in un rifugio per mangiare qualcosa di caldo e poi
torneremo a casa prima che faccia buio, perche' le strade sono strette e piene di curve.
""", "en": """
Cryptography is the practice of writing messages that only the intended reader can understand. For thousands of years it
was a tool of kings, generals and merchants, who needed to send letters without their enemies learning what was inside.
Today almost everyone uses it every day without noticing: when we open a banking website, when we send a message to a
friend, or when we pay for groceries with a card. The basic idea is simple. You take a plain message, apply a
transformation that depends on a secret key, and obtain a ciphertext. Anyone who knows the key can reverse the process and
recover the original text, while anyone who does not know it sees only a meaningless string of symbols. The security of
the system should never depend on keeping the method hidden, but only on keeping the key secret. Frequency analysis comes
from a very practical observation. In every language some letters appear much more often than others. In English the
letter e is the most common, followed by t, a and o, while letters such as q, x and z are quite rare. If a cipher always
replaces a letter with the same symbol, counting the symbols gives the analyst a strong first clue about which letter
hides behind each of them. During the Second World War the breaking of the German Enigma machine showed how mathematics,
engineering and patience could change the course of history. Polish mathematicians made the first breakthroughs, and later
the team at Bletchley Park built machines that tested thousands of possible settings every day. Their work remained secret
for decades after the war had ended. Modern ciphers work on bits rather than letters. They mix the data through many
rounds and are designed so that the output looks completely random. A good algorithm, used correctly and with a long
enough key, cannot be broken even if every computer in the world worked together for thousands of years. That is why
attackers usually look for easier targets. This does not mean that real systems are perfect. Very often the weak point
is not the mathematics but the people and the software around it: a short password, a key stored in a shared folder, or a
program written in a hurry that reuses the same random number twice. Anyone who works in security has to check every
detail, from the moment a key is created until the day it is finally destroyed. Digital signatures are another important
invention. They let us prove that a document was written by a particular person and that nobody has changed it since it
was signed. The scheme uses a pair of keys: the private key stays with its owner and is used to sign, while the public
key can be shared with everyone and is used to check the signature. In recent years people have started to worry about
quantum computers, which might one day break the public key algorithms that protect the internet today. On a quiet
morning the small town market slowly comes to life. Children run between the stalls, old friends stop to talk about the
weather, and the baker greets each customer by name. By the middle of the afternoon the square is almost empty again, and
the only sounds are the church bells and the wind moving through the trees. We will leave early tomorrow and drive to the
mountains with some friends, stop at a little cabin for something warm to eat, and come back home before it gets dark.
"""}

IC_LINGUA = {"it": 0.0738, "en": 0.0667}
IC_CASUALE = 1 / 26


def normalizza(testo: str) -> str:
    return unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode("ascii")


def indici(testo: str) -> list:
    return [ord(c) - 65 for c in normalizza(testo).upper() if "A" <= c <= "Z"]


def ic(idx: list) -> float:
    n = len(idx)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in Counter(idx).values()) / (n * (n - 1))


class Modello:
    """Modello a trigrammi interpolato: stima quanto una sequenza di lettere 'sembra' italiano o inglese."""

    def __init__(self, lingua: str):
        self.lingua = lingua
        f = FREQ[lingua]
        tot = sum(f.values())
        self.uni = [f[c] / tot for c in ALFA]
        idx = indici(CORPUS[lingua])
        un, bi, tri = [0] * 26, [0] * 676, [0] * 17576
        for i, x in enumerate(idx):
            un[x] += 1
            if i >= 1:
                bi[idx[i - 1] * 26 + x] += 1
            if i >= 2:
                tri[idx[i - 2] * 676 + idx[i - 1] * 26 + x] += 1
        T = [0.0] * 17576
        for a in range(26):
            for b in range(26):
                cab = bi[a * 26 + b]
                for c in range(26):
                    p3 = tri[a * 676 + b * 26 + c] / cab if cab else 0.0
                    p2 = bi[b * 26 + c] / un[b] if un[b] else 0.0
                    T[a * 676 + b * 26 + c] = math.log(0.55 * p3 + 0.30 * p2 + 0.15 * self.uni[c])
        self.T = T
        self.log_uni = [math.log(p) for p in self.uni]
        meta = len(idx) // 2
        self.rif_buono = self.punteggio(idx[meta:])
        rnd = random.Random(7)
        self.rif_casuale = self.punteggio([rnd.randrange(26) for _ in range(3000)])

    def punteggio(self, idx: list) -> float:
        if len(idx) < 3:
            return sum(self.log_uni[i] for i in idx) / max(1, len(idx))
        T = self.T
        return sum(T[a * 676 + b * 26 + c] for a, b, c in zip(idx, idx[1:], idx[2:])) / (len(idx) - 2)

    def plausibilita(self, idx: list) -> float:
        x = (self.punteggio(idx) - self.rif_casuale) / (self.rif_buono - self.rif_casuale)
        return max(0.0, min(1.0, x))

    def chi2(self, idx: list) -> float:
        n = len(idx)
        if not n:
            return 1e9
        c = Counter(idx)
        return sum((c.get(i, 0) - n * p) ** 2 / (n * p) for i, p in enumerate(self.uni))


_MODELLI: dict = {}


def modello(lingua: str) -> Modello:
    if lingua not in _MODELLI:
        _MODELLI[lingua] = Modello(lingua)
    return _MODELLI[lingua]


def lingue(scelta: str) -> list:
    return ["it", "en"] if scelta == "auto" else [scelta]


def migliore_lingua(testo: str, scelta: str):
    idx = indici(testo)
    return max(((modello(l).plausibilita(idx), l) for l in lingue(scelta)))


# --------------------------------------------------------------------------- trasformazioni che preservano il formato
def mappa_lettere(testo: str, f) -> str:
    """Applica f(indice_lettera, posizione_tra_le_lettere) solo alle lettere A-Z, mantenendo maiuscole e punteggiatura."""
    out, pos = [], 0
    for ch in testo:
        base = normalizza(ch)
        if len(base) == 1 and base.isascii() and base.isalpha():
            maiusc = base.isupper()
            v = f(ord(base.upper()) - 65, pos)
            pos += 1
            c = chr(v + 65)
            out.append(c if maiusc else c.lower())
        else:
            out.append(ch)
    return "".join(out)


def cesare(testo, k):
    return mappa_lettere(testo, lambda x, _: (x + k) % 26)


def atbash(testo):
    return mappa_lettere(testo, lambda x, _: 25 - x)


def affine_decifra(testo, a, b):
    inv = pow(a, -1, 26)
    return mappa_lettere(testo, lambda x, _: (inv * (x - b)) % 26)


def affine_cifra(testo, a, b):
    return mappa_lettere(testo, lambda x, _: (a * x + b) % 26)


def chiave_indici(parola: str) -> list:
    k = indici(parola)
    if not k:
        raise ValueError("la chiave deve contenere lettere")
    return k


def vigenere(testo, chiave, cifra=False):
    k = chiave_indici(chiave)
    s = 1 if cifra else -1
    return mappa_lettere(testo, lambda x, p: (x + s * k[p % len(k)]) % 26)


def sostituzione(testo, chiave: list):
    return mappa_lettere(testo, lambda x, _: chiave[x])


def rot47(testo):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in testo)


def rail_cifra(testo, n):
    righe = [[] for _ in range(n)]
    r, d = 0, 1
    for ch in testo:
        righe[r].append(ch)
        if n > 1:
            if r == 0:
                d = 1
            elif r == n - 1:
                d = -1
            r += d
    return "".join("".join(x) for x in righe)


def rail_decifra(testo, n):
    if n < 2 or n >= len(testo):
        return testo
    schema, r, d = [], 0, 1
    for _ in testo:
        schema.append(r)
        if r == 0:
            d = 1
        elif r == n - 1:
            d = -1
        r += d
    conteggi = Counter(schema)
    pezzi, i = {}, 0
    for riga in range(n):
        pezzi[riga] = list(testo[i:i + conteggi[riga]])
        i += conteggi[riga]
    return "".join(pezzi[riga].pop(0) for riga in schema)


# --------------------------------------------------------------------------- attacchi
def attacco_cesare(testo, scelta):
    res = []
    for k in range(26):
        cand = cesare(testo, -k)
        p, l = migliore_lingua(cand, scelta)
        res.append((p, "Cesare", "spostamento %d (%s)" % (k, ALFA[k]), l, cand))
    return res


def attacco_affine(testo, scelta):
    res = []
    for a in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        for b in range(26):
            if a == 1:
                continue        # e' un Cesare, gia' provato
            cand = affine_decifra(testo, a, b)
            p, l = migliore_lingua(cand, scelta)
            res.append((p, "affine", "a=%d b=%d" % (a, b), l, cand))
    return res


def lunghezze_vigenere(idx, massimo, lingua):
    stime = []
    for L in range(1, massimo + 1):
        colonne = [idx[i::L] for i in range(L)]
        if min(len(c) for c in colonne) < 6 and L > 1:
            break
        stime.append((sum(ic(c) for c in colonne) / L, L))
    target = IC_LINGUA[lingua]
    stime.sort(key=lambda t: abs(t[0] - target))
    return stime


def attacco_vigenere(testo, scelta, massimo=20):
    idx = indici(testo)
    risultati = []
    for l in lingue(scelta):
        M = modello(l)
        stime = lunghezze_vigenere(idx, massimo, l)
        provate = []
        for _, L in stime[:5]:
            colonne = [idx[i::L] for i in range(L)]
            chiave = []
            for col in colonne:
                chiave.append(min(range(26), key=lambda k: M.chi2([(x - k) % 26 for x in col])))
            for _ in range(2):              # affinamento con il modello a trigrammi
                for pos in range(L):
                    def fit(k):
                        prova = chiave[:pos] + [k] + chiave[pos + 1:]
                        return M.punteggio([(x - prova[i % L]) % 26 for i, x in enumerate(idx)])
                    chiave[pos] = max(range(26), key=fit)
            for p in range(1, L + 1):        # riduci chiavi ripetute (ABCABC -> ABC)
                if L % p == 0 and chiave == chiave[:p] * (L // p):
                    chiave = chiave[:p]
                    break
            parola = "".join(ALFA[k] for k in chiave)
            if parola in provate:
                continue
            provate.append(parola)
            cand = vigenere(testo, parola)
            risultati.append((M.plausibilita(indici(cand)), "Vigenere/Bellaso", "chiave %s" % parola, l, cand))
    return risultati


def attacco_sostituzione(testo, scelta, riavvii=25, seme=1):
    idx = indici(testo)
    if len(idx) < 40:
        return []
    risultati = []
    tri = Counter(zip(idx, idx[1:], idx[2:]))
    voci = [(a, b, c, n) for (a, b, c), n in tri.items()]
    presenti = sorted(set(idx))
    for l in lingue(scelta):
        M = modello(l)
        T = M.T

        def fit(k):
            return sum(n * T[k[a] * 676 + k[b] * 26 + k[c]] for a, b, c, n in voci)

        ordine_cif = [x for x, _ in Counter(idx).most_common()] + [x for x in range(26) if x not in idx]
        ordine_lin = sorted(range(26), key=lambda i: -M.uni[i])
        iniziale = [0] * 26
        for c, p in zip(ordine_cif, ordine_lin):
            iniziale[c] = p
        rnd = random.Random(seme)
        migliore, migliore_fit = iniziale[:], fit(iniziale)
        for r in range(riavvii):
            k = migliore[:] if r else iniziale[:]
            if r:
                for _ in range(rnd.randint(2, 8)):
                    i, j = rnd.randrange(26), rnd.randrange(26)
                    k[i], k[j] = k[j], k[i]
            f = fit(k)
            migliorato = True
            while migliorato:
                migliorato = False
                for i in presenti:
                    for j in range(26):
                        if i == j:
                            continue
                        k[i], k[j] = k[j], k[i]
                        nf = fit(k)
                        if nf > f + 1e-9:
                            f, migliorato = nf, True
                        else:
                            k[i], k[j] = k[j], k[i]
            if f > migliore_fit:
                migliore, migliore_fit = k[:], f
        cand = sostituzione(testo, migliore)
        tab = " ".join("%s>%s" % (ALFA[c], ALFA[migliore[c]].lower()) for c in presenti)
        risultati.append((M.plausibilita(indici(cand)), "sostituzione monoalfabetica", "tabella " + tab, l, cand))
    return risultati


def attacco_rail(testo, scelta, binari=None):
    compatto = re.sub(r"\s+", "", testo)
    res = []
    for n in ([binari] if binari else range(2, min(13, len(compatto)))):
        cand = rail_decifra(compatto, n)
        p, l = migliore_lingua(cand, scelta)
        res.append((p, "rail fence (zig-zag)", "%d binari" % n, l, cand))
    return res


def kasiski(idx, minimo=3):
    pos = {}
    for i in range(len(idx) - minimo + 1):
        pos.setdefault(tuple(idx[i:i + minimo]), []).append(i)
    distanze = [b - a for v in pos.values() if len(v) > 1 for a, b in zip(v, v[1:])]
    fattori = Counter(f for d in distanze for f in range(2, 21) if d % f == 0)
    return distanze, fattori


# --------------------------------------------------------------------------- XOR
def _freq_caratteri():
    testo = (CORPUS["it"] + CORPUS["en"]).lower()
    c = Counter(testo.encode("ascii", "ignore"))
    tot = sum(c.values())
    tab = [math.log(0.01 / tot)] * 256          # caratteri mai visti: molto improbabili
    for b in b"0123456789,.;:'\"!?()-/%&@#*+=_":   # cifre e punteggiatura: rare ma normali
        tab[b] = math.log(0.002)
    for b, n in c.items():
        tab[b] = max(tab[b], math.log(n / tot))
    for b in range(65, 91):                     # maiuscole come le minuscole, un po' meno probabili
        tab[b] = tab[b + 32] - 1.0
    for b in list(range(0, 9)) + list(range(14, 32)) + list(range(127, 256)):
        tab[b] = math.log(1e-7)
    return tab


_FC = None


def punteggio_bytes(b: bytes) -> float:
    global _FC
    if _FC is None:
        _FC = _freq_caratteri()
    return sum(_FC[x] for x in b) / max(1, len(b))


def xor_byte_singolo(b: bytes):
    return max(((punteggio_bytes(bytes(x ^ k for x in b)), k) for k in range(256)))


def hamming(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


def attacco_xor(b: bytes, max_chiave=40):
    risultati = []
    s, k = xor_byte_singolo(b)
    risultati.append((s, bytes([k])))
    stime = []
    for L in range(2, min(max_chiave, max(2, len(b) // 8)) + 1):   # almeno ~8 campioni per byte di chiave
        blocchi = [b[i:i + L] for i in range(0, len(b) - L + 1, L)][:12]
        if len(blocchi) < 2:
            continue
        d = [hamming(blocchi[i], blocchi[i + 1]) / L for i in range(len(blocchi) - 1)]
        stime.append((sum(d) / len(d), L))
    for _, L in sorted(stime)[:5]:
        chiave = bytes(xor_byte_singolo(b[i::L])[1] for i in range(L))
        piano = bytes(x ^ chiave[i % L] for i, x in enumerate(b))
        risultati.append((punteggio_bytes(piano), chiave))
    risultati.sort(key=lambda t: -(t[0] - 0.01 * len(t[1])))   # a parita' di qualita' vince la chiave piu' corta
    uniche, viste = [], set()
    for s, k in risultati:
        for p in range(1, len(k) + 1):           # riduci chiavi ripetute
            if len(k) % p == 0 and k == k[:p] * (len(k) // p):
                k = k[:p]
                break
        if k not in viste:
            viste.add(k)
            uniche.append((s, k, bytes(x ^ k[i % len(k)] for i, x in enumerate(b))))
    return uniche


# --------------------------------------------------------------------------- uscita
def etichetta(p: float) -> str:
    if p >= 0.8:
        return "molto plausibile"
    if p >= 0.6:
        return "plausibile"
    if p >= 0.4:
        return "dubbio"
    return "improbabile"


def mostra(risultati, n=6, anteprima=220):
    risultati = sorted(risultati, key=lambda t: -t[0])
    viste, k = set(), 0
    for p, metodo, chiave, lingua, testo in risultati:
        if testo in viste:
            continue
        viste.add(testo)
        k += 1
        print("%d. [%3.0f%% %s] %s, %s, lingua %s" % (k, p * 100, etichetta(p), metodo, chiave, lingua))
        t = testo if len(testo) <= anteprima else testo[:anteprima] + "..."
        print("   " + t.replace("\n", " "))
        if k >= n:
            break


def cmd_frequenze(testo, scelta):
    idx = indici(testo)
    n = len(idx)
    if not n:
        print("Nessuna lettera A-Z da analizzare.")
        return
    c = Counter(idx)
    print("Lettere: %d | indice di coincidenza: %.4f (casuale %.4f, italiano ~%.4f, inglese ~%.4f)"
          % (n, ic(idx), IC_CASUALE, IC_LINGUA["it"], IC_LINGUA["en"]))
    print("Frequenze (cifrato vs attese):")
    attese_it = sorted(ALFA, key=lambda x: -FREQ["it"][x])
    attese_en = sorted(ALFA, key=lambda x: -FREQ["en"][x])
    print("  cifrato : " + " ".join("%s %.1f%%" % (ALFA[i], 100 * v / n) for i, v in c.most_common(12)))
    print("  italiano: " + " ".join(attese_it[:12]))
    print("  inglese : " + " ".join(attese_en[:12]))
    v = ic(idx)
    for l in lingue(scelta):
        if v > IC_CASUALE + 0.002:
            stima = (IC_LINGUA[l] - IC_CASUALE) / (v - IC_CASUALE)
            print("  stima di Friedman della lunghezza della chiave (%s): ~%.1f" % (l, stima))
    dist, fatt = kasiski(idx)
    if dist:
        print("  Kasiski: %d ripetizioni di trigrammi; fattori piu' comuni delle distanze: %s"
              % (len(dist), ", ".join("%d (x%d)" % t for t in fatt.most_common(6))))
    if v >= 0.058:
        print("Interpretazione: IC simile a una lingua naturale -> sostituzione monoalfabetica (Cesare, affine, tabella) "
              "o trasposizione. Se le frequenze coincidono gia' con la lingua, e' una trasposizione.")
    elif v >= 0.042:
        print("Interpretazione: IC intermedio -> probabile polialfabetico (Vigenere/Bellaso) con chiave corta o media.")
    else:
        print("Interpretazione: IC quasi casuale -> polialfabetico con chiave lunga, cifrario moderno o testo troppo breve.")


def cmd_auto(testo, scelta):
    idx = indici(testo)
    if len(idx) < 8:
        print("Testo troppo breve per un'analisi affidabile (servono almeno 8 lettere; meglio 50+).")
    v = ic(idx)
    print("Lettere: %d | IC %.4f -> %s" % (len(idx), v, "monoalfabetico/trasposizione" if v >= 0.058 else
                                            "polialfabetico o testo breve" if v >= 0.042 else "quasi casuale"))
    ris = []
    p, l = migliore_lingua(testo, scelta)
    ris.append((p, "nessuna cifratura", "-", l, testo))
    inv = testo[::-1]
    p, l = migliore_lingua(inv, scelta)
    ris.append((p, "testo invertito", "-", l, inv))
    ris += attacco_cesare(testo, scelta)
    a = atbash(testo)
    p, l = migliore_lingua(a, scelta)
    ris.append((p, "Atbash", "-", l, a))
    ris += attacco_affine(testo, scelta)
    if re.search(r"[!-@\[-`{-~]", testo) and not re.search(r"\s{2,}", testo):
        r = rot47(testo)
        p, l = migliore_lingua(r, scelta)
        ris.append((p, "ROT47", "-", l, r))
    ris += attacco_rail(testo, scelta)
    if len(idx) >= 30:
        ris += attacco_vigenere(testo, scelta)
    migliore = max(r[0] for r in ris)
    if migliore < 0.7 and len(idx) >= 60 and v >= 0.055:
        print("(provo anche la sostituzione monoalfabetica con hill climbing: qualche secondo...)")
        ris += attacco_sostituzione(testo, scelta)
    print("\nCandidati migliori:")
    mostra(ris)
    top = max(ris, key=lambda t: t[0])
    print()
    if top[0] >= 0.6 and top[1] != "nessuna cifratura":
        print("Verdetto: cifrario %s ROTTO senza conoscere la chiave (%s). Protezione: NULLA contro chiunque abbia un computer."
              % (top[1], top[2]))
    elif top[1] == "nessuna cifratura" and top[0] >= 0.6:
        print("Verdetto: il testo sembra gia' in chiaro.")
    else:
        print("Verdetto: nessun attacco classico ha dato un testo plausibile. Possibili cause: testo troppo breve, "
              "cifrario diverso (Playfair, trasposizione a colonne, Enigma...), lingua diversa, o cifratura moderna. "
              "Prova 'frequenze' per orientarti; con testi brevi controlla comunque i primi candidati a occhio.")


def leggi_input(a) -> str:
    if getattr(a, "file", None):
        return open(a.file, encoding="utf-8", errors="replace").read()
    if a.testo == "-" or a.testo is None:
        return sys.stdin.read()
    return a.testo


def main():
    ap = argparse.ArgumentParser(description="Cifrari classici e crittoanalisi.")
    ap.add_argument("comando", choices=["auto", "frequenze", "cesare", "atbash", "affine", "vigenere", "vigenere-attacco",
                                        "sostituzione-attacco", "rail", "rot47", "xor-attacco"])
    ap.add_argument("testo", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--lingua", default="auto", choices=["auto", "it", "en"])
    ap.add_argument("--chiave")
    ap.add_argument("--cifra", action="store_true", help="cifra invece di decifrare")
    ap.add_argument("--a", type=int)
    ap.add_argument("--b", type=int)
    ap.add_argument("--binari", type=int)
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--riavvii", type=int, default=25)
    ap.add_argument("--hex")
    ap.add_argument("--base64")
    ap.add_argument("--max-chiave", type=int, default=40)
    a = ap.parse_args()
    c = a.comando

    if c == "xor-attacco":
        if a.hex:
            dati = bytes.fromhex(re.sub(r"[\s:]", "", a.hex))
        elif a.base64:
            dati = base64.b64decode(a.base64 + "=" * (-len(a.base64) % 4))
        elif a.file:
            dati = open(a.file, "rb").read()
        else:
            print("Serve --hex, --base64 o --file")
            return 2
        print("XOR: %d byte analizzati" % len(dati))
        for i, (s, k, piano) in enumerate(attacco_xor(dati, a.max_chiave)[:4], 1):
            leggibile = k.decode("latin-1") if all(32 <= x < 127 for x in k) else ""
            print("%d. chiave %s%s (lunghezza %d, punteggio %.2f)" % (i, k.hex(), " = '%s'" % leggibile if leggibile else "",
                                                                     len(k), s))
            print("   " + piano[:240].decode("utf-8", "replace").replace("\n", " "))
        print("\nUn XOR con chiave corta e ripetuta non e' cifratura sicura: si rompe con l'analisi statistica. "
              "Solo una chiave casuale lunga quanto il messaggio e mai riusata (one-time pad) e' sicura.")
        return 0

    testo = leggi_input(a)
    if c == "auto":
        cmd_auto(testo, a.lingua)
    elif c == "frequenze":
        cmd_frequenze(testo, a.lingua)
    elif c == "cesare":
        if a.chiave is not None:
            k = int(a.chiave) if a.chiave.lstrip("-").isdigit() else ALFA.index(a.chiave.upper()[0])
            print(cesare(testo, k if a.cifra else -k))
        else:
            mostra(attacco_cesare(testo, a.lingua), n=26 if len(indici(testo)) < 12 else 5)
    elif c == "atbash":
        print(atbash(testo))
    elif c == "affine":
        if a.a is not None and a.b is not None:
            if math.gcd(a.a, 26) != 1:
                print("'a' deve essere coprimo con 26 (1,3,5,7,9,11,15,17,19,21,23,25)")
                return 2
            print(affine_cifra(testo, a.a, a.b) if a.cifra else affine_decifra(testo, a.a, a.b))
        else:
            mostra(attacco_affine(testo, a.lingua) + attacco_cesare(testo, a.lingua))
    elif c == "vigenere":
        if not a.chiave:
            print("Serve --chiave (per l'attacco senza chiave usa: vigenere-attacco)")
            return 2
        print(vigenere(testo, a.chiave, cifra=a.cifra))
    elif c == "vigenere-attacco":
        idx = indici(testo)
        for l in lingue(a.lingua):
            st = lunghezze_vigenere(idx, a.max, l)[:5]
            print("Lunghezze di chiave piu' probabili (%s): %s" % (l, ", ".join("%d (IC %.3f)" % (L, v) for v, L in st)))
        mostra(attacco_vigenere(testo, a.lingua, a.max))
    elif c == "sostituzione-attacco":
        print("Hill climbing sulla tabella di sostituzione (servono almeno ~150 lettere per buoni risultati)...")
        mostra(attacco_sostituzione(testo, a.lingua, a.riavvii), anteprima=600)
    elif c == "rail":
        if a.binari and a.cifra:
            print(rail_cifra(re.sub(r"\s+", "", testo), a.binari))
        else:
            mostra(attacco_rail(testo, a.lingua, a.binari))
    elif c == "rot47":
        print(rot47(testo))
    return 0


if __name__ == "__main__":
    try:
        import signal
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:
        pass
    sys.exit(main())
