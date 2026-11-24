#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizza.py - identifica, decodifica a strati e valuta stringhe, token e file sospetti.

SOLO ANALISI STATICA: lo script non esegue, non apre link e non scarica nulla di cio'
che decodifica. Le valutazioni sono euristiche: "nessun segnale noto" NON vuol dire "sicuro".

Uso:
  python analizza.py "stringa"            analizza una stringa
  python analizza.py --file percorso      analizza un file (testo o binario)
  python analizza.py -                    legge da standard input
Opzioni:
  --json              stampa il rapporto in JSON
  --profondita N      massimo numero di strati da togliere (default 12)
  --completo          mostra tutto il contenuto decodificato (default: anteprima)
  --salva PERCORSO    salva i byte dell'ultimo strato decodificato (non eseguirli!)

Dipendenze: solo libreria standard. Se e' installato "cryptography" mostra anche i
dettagli dei certificati X.509.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import bz2
import codecs
import hashlib
import html
import io
import ipaddress
import json
import lzma
import math
import quopri
import re
import sys
import unicodedata
import urllib.parse
import zipfile
import zlib
from collections import Counter
from datetime import datetime, timezone

MAX_OUT = 20 * 1024 * 1024        # limite contro le "bombe" di decompressione
MAX_INPUT = 25 * 1024 * 1024
LUNGHEZZE_HASH = {16, 20, 28, 32, 48, 64}

# --------------------------------------------------------------------------- parole comuni
_PAROLE_IT = """di il la che per un in non una sono si mi ma lo ho ti le ha con cosa da del della al come se io gli alla
questo bene no piu ci qui mio era nel tu sei solo me dei lei perche essere fatto lui quando molto anche delle tutto ora hai
cosi suo sua cui gia dove chi tra su poi nella degli dal dalla sul sulla ai agli alle quella quello questa questi loro noi voi
stato stata fare puo ogni tutti prima dopo ancora sempre mai oggi anni anno casa tempo vita giorno parte modo uomo mondo grazie
ciao buongiorno sera notte messaggio segreto chiave codice testo password conto banca pagamento cliente gentile servizio
verifica accesso clicca entro ore dati tuo tua tuoi suoi nostro vostro siamo siete hanno fa va vuoi devi deve possono caro
cara saluti cordiali domani ieri subito qualcosa niente nulla tanto poco grande piccolo nuovo vecchio primo ultimo altro altra
altri stesso proprio dentro fuori sopra sotto contro senza verso durante mentre quindi pero invece infatti allora adesso
insieme lavoro scuola amico amici famiglia citta paese italia italiano lingua parola lettera numero storia questa ecco""".split()
_PAROLE_EN = """the be to of and in that have it for not on with he as you do at this but his by from they we say her she or an
will my one all would there their what so up out if about who get which go me when make can like time no just him know take
people into year your good some could them see other than then now look only come its over think also back after use two how
our work first well way even new want because any these give day most us is are was were has had been being am does did done
said made very more much many such here where why hello dear please thanks thank regards message secret key code text password
account bank payment customer service click link login sign verify update confirm within hours today tomorrow yesterday quick
brown fox jumps lazy dog world life home hand part place case week company system program question number night point water
room money story fact month lot right study book job word business file data user name""".split()
PAROLE = set(_PAROLE_IT) | set(_PAROLE_EN)


def _senza_accenti(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def punteggio_parole(t: str) -> float:
    """Frazione di parole (2+ lettere) che sono parole comuni italiane o inglesi."""
    campione = t[:4000].lower()
    tok = re.findall(r"[^\W\d_]{2,}", campione)[:400]
    lettere = sum(ch.isalpha() for ch in campione)
    if not tok or not lettere:
        return 0.0
    quota = sum(1 for w in tok if _senza_accenti(w) in PAROLE) / len(tok)
    copertura = min(1.0, sum(len(w) for w in tok) / lettere)   # lettere sparse = non sono parole
    fiducia = min(1.0, len(tok) / 6)                             # 1-2 "parole" non bastano
    return quota * copertura * fiducia


def qualita_testo(t: str) -> float:
    lett = sum(ch.isalpha() for ch in t) / max(1, len(t))
    return min(1.0, 0.6 * punteggio_parole(t) + 0.4 * min(1.0, lett / 0.6))


def entropia(b: bytes) -> float:
    if not b:
        return 0.0
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in Counter(b).values())


def quota_stampabile(t: str) -> float:
    if not t:
        return 0.0
    return sum(1 for ch in t if ch.isprintable() or ch in "\t\n\r") / len(t)


def seg_(gravita: int, messaggio: str, area: str = "contenuto") -> dict:
    """area 'contenuto' = pericolo per chi riceve il dato; area 'protezione' = debolezza crittografica."""
    return {"gravita": gravita, "messaggio": messaggio, "area": area}


def seg_p(gravita: int, messaggio: str) -> dict:
    return seg_(gravita, messaggio, "protezione")


def bytes_a_testo(b: bytes):
    """Interpreta dei byte come testo, se possibile. Restituisce (testo, codifica) o (None, None)."""
    if not b:
        return None, None
    if b.startswith(b"\xef\xbb\xbf"):
        try:
            return b[3:].decode("utf-8"), "utf-8-sig"
        except UnicodeDecodeError:
            pass
    if b.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return b.decode("utf-16"), "utf-16"
        except UnicodeDecodeError:
            pass
    if len(b) >= 4 and len(b) % 2 == 0:            # UTF-16LE senza BOM (es. PowerShell -EncodedCommand)
        meta = len(b) // 2
        if b[1::2].count(0) / meta > 0.6 and b[0::2].count(0) / meta < 0.1:
            try:
                return b.decode("utf-16-le"), "utf-16-le"
            except UnicodeDecodeError:
                pass
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        pass
    ascii_ok = sum(1 for x in b if 32 <= x < 127 or x in (9, 10, 13)) / len(b)
    if ascii_ok >= 0.95:
        return b.decode("latin-1"), "latin-1"
    return None, None


# --------------------------------------------------------------------------- tipi di file
MAGIC = [
    (0, b"Salted__", "cifrato OpenSSL enc (con salt)", "cifrato"),
    (0, b"age-encryption.org/v1", "file cifrato con age", "cifrato"),
    (0, b"CRT1", "cifrato crit1 (cifra.py di questa skill)", "cifrato"),
    (0, b"CRH1", "cifrato a chiave pubblica crit (cifra.py, HPKE)", "cifrato"),
    (0, b"LUKS\xba\xbe", "volume cifrato LUKS", "cifrato"),
    (3, b"-FVE-FS-", "volume cifrato BitLocker", "cifrato"),
    (0, b"\x1f\x8b", "compresso gzip", "compresso"),
    (0, b"BZh", "compresso bzip2", "compresso"),
    (0, b"\xfd7zXZ\x00", "compresso xz", "compresso"),
    (0, b"\x28\xb5\x2f\xfd", "compresso zstd", "compresso"),
    (0, b"PK\x03\x04", "archivio ZIP (anche docx/xlsx/pptx/jar/apk)", "archivio"),
    (0, b"PK\x05\x06", "archivio ZIP vuoto", "archivio"),
    (0, b"7z\xbc\xaf\x27\x1c", "archivio 7z", "archivio"),
    (0, b"Rar!\x1a\x07", "archivio RAR", "archivio"),
    (0, b"%PDF", "documento PDF", "documento"),
    (0, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "documento Office legacy o MSI (OLE2)", "documento"),
    (0, b"{\\rtf", "documento RTF", "documento"),
    (0, b"MZ", "eseguibile Windows (EXE/DLL)", "eseguibile"),
    (0, b"\x7fELF", "eseguibile Linux (ELF)", "eseguibile"),
    (0, b"\xcf\xfa\xed\xfe", "eseguibile macOS (Mach-O)", "eseguibile"),
    (0, b"\xce\xfa\xed\xfe", "eseguibile macOS (Mach-O)", "eseguibile"),
    (0, b"\xca\xfe\xba\xbe", "Java class o eseguibile macOS universale", "eseguibile"),
    (0, b"L\x00\x00\x00\x01\x14\x02\x00", "collegamento Windows (LNK)", "eseguibile"),
    (0, b"\x00asm", "modulo WebAssembly", "eseguibile"),
    (0, b"\x89PNG\r\n\x1a\n", "immagine PNG", "immagine"),
    (0, b"\xff\xd8\xff", "immagine JPEG", "immagine"),
    (0, b"GIF87a", "immagine GIF", "immagine"),
    (0, b"GIF89a", "immagine GIF", "immagine"),
    (0, b"SQLite format 3\x00", "database SQLite", "dati"),
    (0x8001, b"CD001", "immagine disco ISO", "disco"),
]
ZLIB_HEADERS = (b"\x78\x01", b"\x78\x5e", b"\x78\x9c", b"\x78\xda")


def tipo_file(b: bytes):
    for off, sig, nome, cat in MAGIC:
        if len(b) >= off + len(sig) and b[off:off + len(sig)] == sig:
            if sig == b"MZ":
                if len(b) < 64:
                    continue
                e = int.from_bytes(b[0x3C:0x40], "little")
                if e + 4 <= len(b) and b[e:e + 4] != b"PE\x00\x00":
                    continue
            return nome, cat
    if b[:2] in ZLIB_HEADERS and len(b) > 8:
        try:
            if zlib.decompressobj().decompress(b, 64):
                return "compresso zlib", "compresso"
        except zlib.error:
            pass
    return None, None


def decomprimi(b: bytes):
    try:
        if b[:2] == b"\x1f\x8b":
            return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(b, MAX_OUT), "gzip"
        if b[:2] in ZLIB_HEADERS:
            return zlib.decompressobj().decompress(b, MAX_OUT), "zlib"
        if b[:3] == b"BZh":
            return bz2.BZ2Decompressor().decompress(b, max_length=MAX_OUT), "bzip2"
        if b[:6] == b"\xfd7zXZ\x00":
            return lzma.LZMADecompressor().decompress(b, max_length=MAX_OUT), "xz"
    except Exception:
        pass
    return None, None


# --------------------------------------------------------------------------- decodificatori di testo
B64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
B64URL_RE = re.compile(r"^[A-Za-z0-9_-]+={0,2}$")
B32_RE = re.compile(r"^[A-Z2-7]+=*$")
HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
B58_RE = re.compile("^[" + B58 + "]+$")
ESC_RE = re.compile(r"\\(x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|[0-7]{3})")


def _compatta(s: str) -> str:
    return s.strip().replace("\r", "").replace("\n", "")


def dec_base64(s):
    t = _compatta(s)
    if len(t) < 8 or not B64_RE.match(t):
        return None
    stretto = len(t) % 4 == 0
    if not stretto:
        if len(t) % 4 == 1:
            return None
        t += "=" * (-len(t) % 4)
    try:
        return base64.b64decode(t, validate=True), stretto
    except (binascii.Error, ValueError):
        return None


def dec_base64url(s):
    t = _compatta(s)
    if len(t) < 8 or not B64URL_RE.match(t) or not re.search(r"[-_]", t):
        return None
    core = t.rstrip("=")
    if len(core) % 4 == 1:
        return None
    try:
        return base64.urlsafe_b64decode(core + "=" * (-len(core) % 4)), len(t) >= 16
    except (binascii.Error, ValueError):
        return None


def dec_base32(s):
    t = _compatta(s)
    if t.islower():
        t = t.upper()
    if len(t) < 8 or not B32_RE.match(t):
        return None
    core = t.rstrip("=")
    if len(core) % 8 in (1, 3, 6):
        return None
    try:
        return base64.b32decode(core + "=" * (-len(core) % 8)), len(t) % 8 == 0
    except (binascii.Error, ValueError):
        return None


def dec_hex(s):
    t = s.strip()
    if re.search(r"(?i)(^|[\s,])0x[0-9a-f]", t):
        t = re.sub(r"(?i)0x", "", t)
    t = re.sub(r"[\s:,\-]", "", t.replace("\\x", ""))
    if len(t) < 8 or len(t) % 2 or not HEX_RE.match(t):
        return None
    return bytes.fromhex(t), True


def dec_binario(s):
    t = re.sub(r"[\s,]", "", s)
    if len(t) < 16 or len(t) % 8 or set(t) - {"0", "1"}:
        return None
    return int(t, 2).to_bytes(len(t) // 8, "big"), True


def dec_decimali(s):
    if not re.fullmatch(r"\s*\d{1,3}(?:[\s,;]+\d{1,3}){3,}\s*", s):
        return None
    vals = [int(x) for x in re.findall(r"\d+", s)]
    if max(vals) > 255:
        return None
    return bytes(vals), False


def dec_url(s):
    if not re.search(r"%[0-9A-Fa-f]{2}", s):
        return None
    return urllib.parse.unquote_to_bytes(s.strip()), False


def dec_html(s):
    if not re.search(r"&(#\d{2,7}|#[xX][0-9a-fA-F]{2,6}|[a-zA-Z]{2,8});", s):
        return None
    return html.unescape(s).encode("utf-8"), False


def dec_escape(s):
    if len(ESC_RE.findall(s)) < 2:
        return None
    out = bytearray()
    i, n = 0, len(s)
    semplici = {"n": 10, "t": 9, "r": 13, "\\": 92, "'": 39, '"': 34}
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n:
            nx = s[i + 1]
            if nx == "x" and re.fullmatch(r"[0-9a-fA-F]{2}", s[i + 2:i + 4]):
                out.append(int(s[i + 2:i + 4], 16))
                i += 4
                continue
            if nx == "u" and re.fullmatch(r"[0-9a-fA-F]{4}", s[i + 2:i + 6]):
                cp = int(s[i + 2:i + 6], 16)
                if 0xD800 <= cp <= 0xDBFF and s[i + 6:i + 8] == "\\u" and re.fullmatch(r"[0-9a-fA-F]{4}", s[i + 8:i + 12]):
                    lo = int(s[i + 8:i + 12], 16)
                    cp = 0x10000 + ((cp - 0xD800) << 10) + (lo - 0xDC00)
                    i += 6
                out += chr(cp).encode("utf-8", "replace")
                i += 6
                continue
            if nx == "U" and re.fullmatch(r"[0-9a-fA-F]{8}", s[i + 2:i + 10]):
                cp = int(s[i + 2:i + 10], 16)
                if cp <= 0x10FFFF:
                    out += chr(cp).encode("utf-8", "replace")
                    i += 10
                    continue
            if re.fullmatch(r"[0-7]{3}", s[i + 1:i + 4]) and int(s[i + 1:i + 4], 8) < 256:
                out.append(int(s[i + 1:i + 4], 8))
                i += 4
                continue
            if nx in semplici:
                out.append(semplici[nx])
                i += 2
                continue
        out += ch.encode("utf-8")
        i += 1
    return bytes(out), False


def dec_qp(s):
    if len(re.findall(r"=[0-9A-F]{2}", s)) < 3 and "=\n" not in s:
        return None
    if re.fullmatch(r"[A-Za-z0-9+/]+=*", s.strip()):
        return None
    return quopri.decodestring(s.encode("utf-8", "replace")), False


MORSE = {".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F", "--.": "G", "....": "H", "..": "I",
         ".---": "J", "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
         "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y", "--..": "Z",
         "-----": "0", ".----": "1", "..---": "2", "...--": "3", "....-": "4", ".....": "5", "-....": "6",
         "--...": "7", "---..": "8", "----.": "9", ".-.-.-": ".", "--..--": ",", "..--..": "?", "-.-.--": "!",
         "-..-.": "/", "-.--.": "(", "-.--.-": ")", "---...": ":", "-...-": "=", ".-.-.": "+", "-....-": "-",
         ".--.-.": "@", ".----.": "'"}


def dec_morse(s):
    t = s.strip().replace("·", ".").replace("•", ".").replace("−", "-").replace("—", "-").replace("_", "-")
    if not re.fullmatch(r"[.\-/|\s]+", t) or "." not in t or "-" not in t:
        return None
    parole = [p for p in re.split(r"\s*[/|]\s*|\s{3,}", t) if p.strip()]
    res = " ".join("".join(MORSE.get(c, "?") for c in p.split()) for p in parole)
    if not res or res.count("?") > len(res) * 0.2:
        return None
    return res.encode(), False


def _rot47(s):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in s)


def dec_rot13(s):
    if sum(ch.isalpha() for ch in s) < 8:
        return None
    r = codecs.encode(s, "rot_13")
    if punteggio_parole(r) >= 0.35 and punteggio_parole(r) > punteggio_parole(s) + 0.25:
        return r.encode("utf-8"), False
    return None


def dec_rot47(s):
    if len(s) < 8 or any(ord(c) > 126 for c in s):
        return None
    r = _rot47(s)
    if punteggio_parole(r) >= 0.35 and punteggio_parole(r) > punteggio_parole(s) + 0.25:
        return r.encode("utf-8"), False
    return None


def dec_inverti(s):
    t = s.strip()
    if len(t) < 8:
        return None
    r = t[::-1]
    if (t.startswith("=") and B64_RE.match(_compatta(r))) or r.lower().startswith(("http://", "https://")) \
            or (punteggio_parole(r) >= 0.4 and punteggio_parole(r) > punteggio_parole(t) + 0.3):
        return r.encode("utf-8"), False
    return None


def dec_base58(s):
    t = s.strip()
    if len(t) < 6 or not B58_RE.match(t):
        return None
    n = 0
    for ch in t:
        n = n * 58 + B58.index(ch)
    lead = len(t) - len(t.lstrip("1"))
    corpo = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * lead + corpo, False


def dec_base85(s):
    t = s.strip()
    if t.startswith("<~") and t.endswith("~>"):
        try:
            return base64.a85decode(t, adobe=True), True
        except Exception:
            return None
    if len(t) >= 10 and re.fullmatch(r"[0-9A-Za-z!#$%&()*+\-;<=>?@^_`{|}~]+", t) and re.search(r"[!#$%&()*+;<=>?@^_`{|}~]", t):
        try:
            return base64.b85decode(t), False
        except Exception:
            return None
    return None


DECODER_TESTO = [
    ("URL encoding (%XX)", dec_url), ("entita HTML", dec_html), ("sequenze di escape (\\x, \\u)", dec_escape),
    ("quoted-printable", dec_qp), ("base64", dec_base64), ("base64url", dec_base64url), ("esadecimale", dec_hex),
    ("base32", dec_base32), ("binario", dec_binario), ("codici decimali", dec_decimali), ("Morse", dec_morse),
    ("base85", dec_base85), ("base58", dec_base58), ("testo invertito", dec_inverti), ("ROT13", dec_rot13),
    ("ROT47", dec_rot47),
]
STRETTI = {"base64", "base64url", "base32", "esadecimale", "binario", "base85"}


def aspetto_codificato(sorgente: str, nome: str) -> bool:
    """Evita di scambiare testo normale (es. un cifrario classico in maiuscolo) per base64/base32 binario."""
    t = _compatta(sorgente)
    if nome in ("base64", "base64url"):
        classi = sum([bool(re.search(r"[a-z]", t)), bool(re.search(r"[A-Z]", t)), bool(re.search(r"\d", t)),
                      bool(re.search(r"[+/_-]", t)), t.endswith("=")])
        return classi >= 3
    if nome == "base32":
        return bool(re.search(r"[2-7]", t)) or t.endswith("=")
    if nome == "esadecimale":
        return bool(re.search(r"\d", t)) and bool(re.search(r"[a-fA-F]", t))
    return True


def valuta_output(out: bytes, nome: str, stretto: bool, sorgente: str):
    if not out or len(out) < 2:
        return 0.0, None
    if tipo_file(out)[0]:
        return 0.97, "file"
    t, _ = bytes_a_testo(out)
    if t is not None:
        if t.strip() == sorgente.strip():
            return 0.0, None
        pr = quota_stampabile(t)
        if pr >= 0.97 and len(t.strip()) >= 3:
            return 0.75 + 0.2 * qualita_testo(t), "testo"
        if pr >= 0.85 and len(t) >= 16:
            return 0.55, "testo"
    if stretto and nome in STRETTI and len(out) >= 16 and aspetto_codificato(sorgente, nome):
        if nome == "esadecimale" and len(out) in LUNGHEZZE_HASH:
            return 0.0, None
        return 0.5, "binario"
    return 0.0, None


def xor_singolo(b: bytes):
    """Cerca una chiave XOR di un solo byte che renda leggibili i dati (protezione nulla, molto usata nel malware)."""
    if len(b) < 8:
        return None
    campione = b[:4096]
    if entropia(campione) > 6.5:
        return None
    migliore = None
    for k in range(1, 256):
        c = bytes(v ^ k for v in campione)
        t, _ = bytes_a_testo(c)
        if t is None or quota_stampabile(t) < 0.97:
            continue
        q = qualita_testo(t)
        if q >= 0.45 and (migliore is None or q > migliore[0]):
            migliore = (q, k)
    if not migliore:
        return None
    k = migliore[1]
    return "XOR con chiave di 1 byte (0x%02x)" % k, bytes(v ^ k for v in b), False


def decoder_binari(b: bytes):
    cand = []
    out, nome = decomprimi(b)
    if out:
        cand.append((nome, out, True))
    try:
        d = zlib.decompressobj(-15)
        out = d.decompress(b, MAX_OUT)
        if out and d.eof:
            cand.append(("deflate grezzo", out, False))
    except zlib.error:
        pass
    x = xor_singolo(b)
    if x:
        cand.append(x)
    return cand


def formato_completo(t: str) -> bool:
    """Formati strutturati che vanno analizzati come tali, non 'sbucciati'."""
    s = t.strip()
    return bool(
        re.fullmatch(r"eyJ[\w-]+\.[\w-]+\.[\w-]*(\.[\w-]+\.[\w-]+)?", s)
        or re.fullmatch(r"-----BEGIN [A-Z0-9 ]+-----.*-----END [A-Z0-9 ]+-----", s, re.S)
        or re.fullmatch(r"(crit1|crithp1|critpk1)\.[\w-]+", s)
        or re.fullmatch(r"v[1-4]\.(local|public)\.[\w-]+(\.[\w-]+)?", s)
        or re.fullmatch(r"gAAAAA[\w-]{60,}={0,2}", s)
        or re.fullmatch(r"\$[0-9a-z]+\$.+", s)
        or re.fullmatch(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{40}|[0-9a-fA-F]{56}|[0-9a-fA-F]{64}|[0-9a-fA-F]{96}|[0-9a-fA-F]{128}", s)
    )


def sbuccia(dati: bytes, max_strati: int):
    """Toglie uno strato di codifica alla volta finche' trova qualcosa di leggibile o si ferma."""
    strati, corrente = [], dati
    visti = {hashlib.sha256(dati).digest()}
    for _ in range(max_strati):
        t, _ = bytes_a_testo(corrente)
        cand = []
        if t is not None and quota_stampabile(t) >= 0.85:
            if formato_completo(t):
                break
            for prio, (nome, fn) in enumerate(DECODER_TESTO):
                try:
                    r = fn(t)
                except Exception:
                    r = None
                if not r:
                    continue
                out, stretto = r
                punti, tipo = valuta_output(out, nome, stretto, t)
                if punti > 0:
                    cand.append((punti, -prio, nome, out, tipo))
            if not cand and strati and len(t) >= 8 and qualita_testo(t) < 0.25:
                x = xor_singolo(corrente)          # testo stampabile ma senza senso: forse XOR
                if x:
                    xt, _ = bytes_a_testo(x[1])
                    if xt and qualita_testo(xt) > qualita_testo(t) + 0.3:
                        cand.append((0.9, 0, x[0], x[1], "testo"))
        else:
            for nome, out, stretto in decoder_binari(corrente):
                punti, tipo = valuta_output(out, nome, stretto, "")
                if punti > 0:
                    cand.append((punti, 0, nome, out, tipo))
        if not cand:
            break
        cand.sort(key=lambda c: (c[0], c[1]), reverse=True)
        punti, _, nome, out, tipo = cand[0]
        h = hashlib.sha256(out).digest()
        if h in visti:
            break
        visti.add(h)
        strati.append({"decodifica": nome, "byte": len(out), "tipo": tipo,
                       "alternative": [c[2] for c in cand[1:4]], "_dati": out})
        corrente = out
    return strati, corrente


# --------------------------------------------------------------------------- formati riconosciuti
def _b64url(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def _json_b64url(seg: str):
    try:
        return json.loads(_b64url(seg).decode("utf-8"))
    except Exception:
        return None


def analizza_jwt(m):
    parti = m.group(0).split(".")
    if len(parti) == 5:
        h = _json_b64url(parti[0])
        return {"tipo": "JWE (token cifrato)", "dettagli": {"header": h},
                "note": ["Il contenuto e' cifrato: non e' leggibile senza la chiave."], "segnali": []}
    h, p = _json_b64url(parti[0]), _json_b64url(parti[1])
    if not isinstance(h, dict):
        return None
    det, note, seg = {"header": h}, [], []
    alg = str(h.get("alg", "?"))
    if isinstance(p, dict):
        det["payload"] = p
        for k in ("exp", "nbf", "iat"):
            if isinstance(p.get(k), (int, float)):
                try:
                    det[k + "_leggibile"] = datetime.fromtimestamp(p[k], tz=timezone.utc).isoformat()
                except (OverflowError, OSError, ValueError):
                    pass
        if isinstance(p.get("exp"), (int, float)):
            note.append("Token SCADUTO." if p["exp"] < datetime.now(timezone.utc).timestamp() else "Token non ancora scaduto.")
        else:
            seg.append(seg_p(1, "JWT senza scadenza (exp): se rubato resta valido a tempo indeterminato"))
        sens = [k for k in p if re.search(r"pass|pwd|secret|segret|card|carta|iban|fiscale|ssn", k, re.I)]
        if sens:
            seg.append(seg_p(2, "il payload contiene campi sensibili (%s): un JWT firmato NON e' cifrato" % ", ".join(sens)))
    note.append("Header e payload sono solo codificati (base64url): chiunque li legge. La firma protegge "
                "l'integrita' solo se il server la verifica con la chiave giusta.")
    if alg.lower() == "none":
        seg.append(seg_p(3, 'alg "none": token senza firma, chiunque puo\' falsificarlo'))
    elif alg.upper().startswith("HS"):
        note.append("Firma HMAC (%s): se il segreto condiviso e' debole, il token si puo' falsificare." % alg)
    if len(parti) > 2 and not parti[2] and alg.lower() != "none":
        seg.append(seg_p(2, "firma mancante"))
    return {"tipo": "JWT (JSON Web Token)", "dettagli": det, "note": note, "segnali": seg}


def analizza_certificato(pem: str, r: dict) -> dict:
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
    except ImportError:
        r["note"].append('Per i dettagli del certificato installa "cryptography".')
        return {}
    try:
        cert = x509.load_pem_x509_certificate(pem.encode())
    except Exception as e:
        r["note"].append("Certificato non leggibile: %s" % e)
        return {}
    det = {"soggetto": cert.subject.rfc4514_string(), "emittente": cert.issuer.rfc4514_string()}
    nb = getattr(cert, "not_valid_before_utc", None) or cert.not_valid_before.replace(tzinfo=timezone.utc)
    na = getattr(cert, "not_valid_after_utc", None) or cert.not_valid_after.replace(tzinfo=timezone.utc)
    det["valido_dal"], det["valido_fino_al"] = nb.isoformat(), na.isoformat()
    ora = datetime.now(timezone.utc)
    if na < ora:
        r["segnali"].append(seg_p(2, "certificato SCADUTO"))
    if nb > ora:
        r["segnali"].append(seg_p(2, "certificato non ancora valido"))
    pk = cert.public_key()
    if isinstance(pk, rsa.RSAPublicKey):
        det["chiave"] = "RSA %d bit" % pk.key_size
        if pk.key_size < 2048:
            r["segnali"].append(seg_p(3, "chiave RSA sotto i 2048 bit: debole"))
    elif isinstance(pk, ec.EllipticCurvePublicKey):
        det["chiave"] = "ECDSA " + pk.curve.name
    elif isinstance(pk, ed25519.Ed25519PublicKey):
        det["chiave"] = "Ed25519"
    else:
        det["chiave"] = type(pk).__name__
    try:
        h = cert.signature_hash_algorithm
        det["hash_firma"] = h.name if h else "incluso nell'algoritmo"
        if h and h.name in ("md5", "sha1"):
            r["segnali"].append(seg_p(3, "firmato con %s: algoritmo rotto" % h.name.upper()))
    except Exception:
        det["hash_firma"] = "n/d"
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        det["nomi_dns"] = san.get_values_for_type(x509.DNSName)[:20]
    except Exception:
        pass
    if cert.issuer == cert.subject:
        r["note"].append("Autofirmato: nessuna autorita' lo garantisce (normale per test/uso interno, sospetto su siti pubblici).")
    det["impronta_sha256"] = cert.fingerprint(hashes.SHA256()).hex(":")
    return det


def analizza_pem(tipo: str, blocco: str) -> dict:
    r = {"tipo": "blocco PEM: " + tipo, "dettagli": {}, "note": [], "segnali": []}
    if "PRIVATE KEY" in tipo and "PGP" not in tipo:
        if "ENCRYPTED" in tipo or "Proc-Type: 4,ENCRYPTED" in blocco:
            r["note"].append("Chiave privata protetta da password: resta comunque un dato riservato.")
        else:
            r["segnali"].append(seg_(3, "CHIAVE PRIVATA IN CHIARO: se e' reale va considerata compromessa e sostituita"))
    elif tipo == "PGP PRIVATE KEY BLOCK":
        r["segnali"].append(seg_(2, "chiave privata PGP condivisa: se e' reale va revocata (di solito e' protetta da passphrase)"))
    elif tipo == "CERTIFICATE":
        r["dettagli"] = analizza_certificato(blocco, r)
    elif tipo == "AGE ENCRYPTED FILE":
        r["note"].append("File cifrato con age (ChaCha20-Poly1305): non decifrabile senza chiave o passphrase.")
    elif tipo == "PGP MESSAGE":
        r["note"].append("Messaggio OpenPGP (cifrato o firmato): serve la chiave privata del destinatario per leggerlo.")
    elif tipo == "PGP SIGNATURE":
        r["note"].append("Firma OpenPGP: si verifica con 'gpg --verify' e la chiave pubblica dell'autore (controllandone l'impronta).")
    elif tipo == "PGP PUBLIC KEY BLOCK":
        r["note"].append("Chiave pubblica OpenPGP: prima di fidarti verifica l'impronta con un canale indipendente.")
    elif tipo == "CERTIFICATE REQUEST":
        r["note"].append("Richiesta di certificato (CSR): contiene solo la chiave pubblica, non e' un segreto.")
    elif "PUBLIC KEY" in tipo:
        r["note"].append("Chiave pubblica: non e' un segreto.")
    return r


def analizza_ssh(tipo: str, b64: str) -> dict:
    r = {"tipo": "chiave pubblica SSH (%s)" % tipo, "dettagli": {}, "note": [], "segnali": []}
    try:
        blob = base64.b64decode(b64 + "=" * (-len(b64) % 4))
        r["dettagli"]["impronta"] = "SHA256:" + base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip("=")
        if tipo == "ssh-rsa":
            def leggi(buf, i):
                n = int.from_bytes(buf[i:i + 4], "big")
                return buf[i + 4:i + 4 + n], i + 4 + n
            _, i = leggi(blob, 0)
            _, i = leggi(blob, i)
            mod, _ = leggi(blob, i)
            bit = int.from_bytes(mod, "big").bit_length()
            r["dettagli"]["bit"] = bit
            if bit < 2048:
                r["segnali"].append(seg_p(3, "RSA a %d bit: troppo corta" % bit))
            elif bit < 3072:
                r["note"].append("RSA a %d bit: accettabile oggi, per nuove chiavi meglio Ed25519." % bit)
    except Exception:
        pass
    if tipo == "ssh-dss":
        r["segnali"].append(seg_p(2, "chiavi DSA (ssh-dss): deprecate e disattivate in OpenSSH moderno"))
    r["note"].append("Non e' un segreto: prima di autorizzarla verifica l'impronta con il proprietario.")
    return r


def analizza_hash_password(s: str) -> list:
    out = []

    def add(tipo, note, segnali=()):
        out.append({"tipo": tipo, "dettagli": {}, "note": note + ["Gli hash non si 'decifrano': si possono solo tentare "
                    "password candidate. La robustezza dipende dall'algoritmo e dalla password."], "segnali": list(segnali)})

    for m in re.finditer(r"\$2[abxy]?\$(\d{2})\$[./A-Za-z0-9]{53}", s):
        c = int(m.group(1))
        add("hash di password bcrypt (costo %d)" % c, ["bcrypt usa solo i primi 72 byte della password."],
            [seg_p(2, "costo bcrypt basso (< 10)")] if c < 10 else [])
    for m in re.finditer(r"\$argon2(id|i|d)\$v=(\d+)\$m=(\d+),t=(\d+),p=(\d+)\$[A-Za-z0-9+/]+\$[A-Za-z0-9+/]+", s):
        v, mem, t, p = m.group(1), int(m.group(3)), int(m.group(4)), int(m.group(5))
        debole = mem < 19456 or (mem < 47104 and t < 2)
        add("hash di password Argon2%s (m=%d KiB, t=%d, p=%d)" % (v, mem, t, p),
            ["Argon2id e' la scelta raccomandata oggi." if v == "id" else "Per le password e' preferibile la variante Argon2id."],
            [seg_p(2, "parametri Argon2 sotto i minimi OWASP (19 MiB e t=2)")] if debole else [])
    for m in re.finditer(r"\$y\$[./A-Za-z0-9]+\$[./A-Za-z0-9]+\$[./A-Za-z0-9]{43}", s):
        add("hash di password yescrypt (Linux moderno)", ["Algoritmo moderno e robusto."])
    for m in re.finditer(r"\$6\$(?:rounds=(\d+)\$)?[./A-Za-z0-9]{1,16}\$[./A-Za-z0-9]{86}", s):
        add("hash di password sha512crypt (%s round)" % (m.group(1) or "5000"),
            ["Accettabile ma datato: meglio yescrypt o Argon2id."])
    for m in re.finditer(r"\$5\$(?:rounds=\d+\$)?[./A-Za-z0-9]{1,16}\$[./A-Za-z0-9]{43}", s):
        add("hash di password sha256crypt", ["Datato: meglio yescrypt o Argon2id."])
    for m in re.finditer(r"\$(1|apr1)\$[./A-Za-z0-9]{1,8}\$[./A-Za-z0-9]{22}", s):
        add("hash di password md5crypt", [], [seg_p(2, "md5crypt e' obsoleto e veloce da attaccare")])
    for m in re.finditer(r"pbkdf2_(sha256|sha1)\$(\d+)\$[^$\s]+\$[A-Za-z0-9+/=]+", s):
        it = int(m.group(2))
        add("hash di password Django PBKDF2-%s (%d iterazioni)" % (m.group(1).upper(), it), [],
            [seg_p(1, "iterazioni PBKDF2 sotto le 600.000 raccomandate da OWASP")] if it < 600000 else [])
    for m in re.finditer(r"\$[PH]\$[./0-9A-Za-z]{31}", s):
        add("hash di password phpass (WordPress/phpBB)", [], [seg_p(1, "phpass si basa su MD5: datato")])
    for m in re.finditer(r"\{(SSHA|SHA|MD5|SMD5|SSHA256|SSHA512|CRYPT)\}[A-Za-z0-9+/=$.]+", s):
        add("hash di password LDAP {%s}" % m.group(1), [], [seg_p(2, "hash veloce: debole per le password")])
    for m in re.finditer(r"(?<![0-9A-Za-z*])\*[0-9A-F]{40}\b", s):
        add("hash di password MySQL 4.1+", [], [seg_p(2, "SHA1 doppio senza salt: debole")])
    return out


def digest_hex(s: str) -> dict:
    n = len(s) // 2
    cand = {16: "MD5, MD4 o NTLM", 20: "SHA-1 o RIPEMD-160", 28: "SHA-224 o SHA3-224",
            32: "SHA-256, SHA3-256, BLAKE2s o BLAKE3", 48: "SHA-384 o SHA3-384",
            64: "SHA-512, SHA3-512 o BLAKE2b"}[n]
    note = ["Puo' essere un hash (impronta) oppure una chiave/token casuale in esadecimale.",
            "Un hash non e' cifratura: non si 'decifra'. Si usa per confrontare (es. checksum di un download)."]
    if n in (16, 20):
        note.append("MD5 e SHA-1 sono rotti per le collisioni: vanno bene solo contro errori accidentali, non per sicurezza.")
    return {"tipo": "probabile hash/digest a %d bit (%s)" % (n * 8, cand), "dettagli": {}, "note": note, "segnali": []}


def analizza_crit(b64: str) -> dict | None:
    try:
        raw = _b64url(b64)
    except Exception:
        return None
    if not raw.startswith(b"CRT1") or len(raw) < 6:
        return None
    modo = raw[4]
    if modo == 1:
        par = "password -> Argon2id (m=%d MiB, t=%d, p=%d)" % (int.from_bytes(raw[5:9], "big") // 1024, raw[9], raw[10])
    elif modo == 2:
        par = "password -> scrypt (N=2^%d, r=%d, p=%d)" % (raw[5], raw[6], raw[7])
    elif modo == 3:
        par = "chiave casuale a 256 bit"
    else:
        par = "modo sconosciuto"
    return {"tipo": "cifrato crit1 (cifra.py): AES-256-GCM", "dettagli": {"chiave": par, "byte": len(raw)},
            "note": ["Cifratura autenticata moderna: senza la password/chiave non si legge e ogni modifica viene rilevata. "
                     "La robustezza reale dipende dalla forza della password."], "segnali": []}


SEGRETI = [
    (r"\bsk-ant-[A-Za-z0-9_-]{20,}", "chiave API Anthropic"),
    (r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}", "chiave API in formato sk- (es. OpenAI)"),
    (r"\bAKIA[0-9A-Z]{16}\b", "chiave di accesso AWS"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "token GitHub"),
    (r"\bgithub_pat_[A-Za-z0-9_]{50,}\b", "token GitHub"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "token Slack"),
    (r"\bsk_live_[0-9a-zA-Z]{20,}\b", "chiave segreta Stripe"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "chiave API Google"),
    (r"\b\d{8,10}:AA[0-9A-Za-z_-]{33}\b", "token di un bot Telegram"),
]


def riconosci_formati(t: str) -> list:
    f, s = [], t
    for m in re.finditer(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)?", s):
        f.append(analizza_jwt(m))
    for m in re.finditer(r"-----BEGIN ([A-Z0-9 ]+?)-----(.*?)-----END \1-----", s, re.S):
        f.append(analizza_pem(m.group(1), m.group(0)))
    if "-----BEGIN PGP SIGNED MESSAGE-----" in s:
        f.append({"tipo": "messaggio PGP firmato in chiaro", "dettagli": {}, "segnali": [],
                  "note": ["Il testo e' leggibile; la firma va verificata con gpg --verify e la chiave dell'autore."]})
    for m in re.finditer(r"\b(ssh-ed25519|ssh-rsa|ssh-dss|ecdsa-sha2-nistp(?:256|384|521)|sk-ssh-ed25519@openssh\.com)\s+(AAAA[0-9A-Za-z+/]+={0,3})", s):
        f.append(analizza_ssh(m.group(1), m.group(2)))
    f += analizza_hash_password(s)
    st = s.strip()
    if re.fullmatch(r"[0-9a-fA-F]+", st) and len(st) % 2 == 0 and len(st) // 2 in LUNGHEZZE_HASH:
        f.append(digest_hex(st))
    for m in re.finditer(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-([1-8])[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b", s):
        v = m.group(1)
        f.append({"tipo": "UUID versione %s" % v, "dettagli": {}, "segnali": [], "note": [
            "Identificativo univoco, non un segreto ne' una cifratura." +
            (" Le versioni 1 contengono data e indirizzo hardware." if v == "1" else "")]})
        break
    for m in re.finditer(r"\bgAAAAA[A-Za-z0-9_-]{60,}={0,2}", s):
        try:
            raw = _b64url(m.group(0))
            quando = datetime.fromtimestamp(int.from_bytes(raw[1:9], "big"), tz=timezone.utc).isoformat()
            f.append({"tipo": "token Fernet (cifrato)", "dettagli": {"creato": quando}, "segnali": [], "note": [
                "Fernet = AES-128-CBC + HMAC-SHA256: robusto se la chiave e' segreta. La data di creazione e' leggibile."]})
        except Exception:
            pass
    if re.search(r"\bU2FsdGVkX1[A-Za-z0-9+/=]{10,}", s):
        f.append({"tipo": "cifrato OpenSSL enc in base64 ('Salted__')", "dettagli": {}, "segnali": [], "note": [
            "Creato con 'openssl enc'. Senza l'opzione -pbkdf2 la password viene trasformata in chiave con MD5 a "
            "un solo passaggio (molto debole contro gli attacchi a dizionario). openssl enc non autentica i dati."]})
    for m in re.finditer(r"\bcrit1\.([A-Za-z0-9_-]{20,})", s):
        f.append(analizza_crit(m.group(1)))
    if re.search(r"\bcrithp1\.[A-Za-z0-9_-]{100,}", s):
        f.append({"tipo": "cifrato a chiave pubblica crithp1 (cifra.py)", "dettagli": {}, "segnali": [], "note": [
            "HPKE con KEM ibrido X25519 + ML-KEM-768 (resistente ai computer quantistici) e AES-256-GCM: "
            "lo legge solo chi ha la chiave privata."]})
    if re.search(r"\bcritpk1\.[A-Za-z0-9_-]{100,}", s):
        f.append({"tipo": "chiave pubblica crit (cifra.py)", "dettagli": {}, "segnali": [],
                  "note": ["Chiave pubblica ibrida X25519 + ML-KEM-768: si puo' condividere liberamente."]})
    for m in re.finditer(r"\bv([1-4])\.(local|public)\.[A-Za-z0-9_-]{20,}", s):
        f.append({"tipo": "token PASETO v%s.%s" % (m.group(1), m.group(2)), "dettagli": {}, "segnali": [], "note": [
            "local = cifrato e autenticato; public = firmato ma leggibile da tutti."]})
    for m in re.finditer(r"data:([\w.+-]+/[\w.+-]+)?((?:;[\w-]+=[\w.-]+)*)(;base64)?,([A-Za-z0-9+/=%._~-]{8,})", s):
        mime, b64, carico = m.group(1) or "text/plain", bool(m.group(3)), m.group(4)
        try:
            raw = base64.b64decode(carico + "=" * (-len(carico) % 4)) if b64 else urllib.parse.unquote_to_bytes(carico)
        except Exception:
            raw = b""
        r = {"tipo": "data URI (%s)" % mime, "dettagli": {"byte": len(raw)}, "note": [], "segnali": [], "_contenuto": raw}
        if re.search(r"html|javascript|svg", mime):
            r["segnali"].append(seg_(2, "pagina o script incorporato in un data URI: tecnica usata per eludere i filtri antiphishing"))
        f.append(r)
    for m in re.finditer(r"(?i)\bbasic\s+([A-Za-z0-9+/]{8,}={0,2})", s):
        try:
            dec = base64.b64decode(m.group(1)).decode("utf-8")
        except Exception:
            continue
        if ":" in dec:
            u, _, pw = dec.partition(":")
            f.append({"tipo": "credenziali HTTP Basic", "dettagli": {"utente": u, "password": "[nascosta, %d caratteri]" % len(pw)},
                      "note": [], "segnali": [seg_(3, "credenziali solo codificate in base64 (non cifrate): se sono reali, cambia la password")]})
    visti = set()
    for rx, nome in SEGRETI:
        for m in re.finditer(rx, s):
            if any(a <= m.start() < b for a, b in visti):
                continue
            visti.add((m.start(), m.end()))
            val = m.group(0)
            f.append({"tipo": "possibile segreto: " + nome, "dettagli": {"valore": val[:8] + "...[mascherato]"}, "note": [],
                      "segnali": [seg_(3, "segreto esposto (%s): se e' reale va revocato e rigenerato subito" % nome)]})
    return [x for x in f if x]


# --------------------------------------------------------------------------- IOC e URL
ACCORCIATORI = {"bit.ly", "bitly.com", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "rebrand.ly",
                "shorturl.at", "tiny.cc", "rb.gy", "t.ly", "s.id", "lnkd.in", "v.gd", "qrco.de", "short.io", "x.co", "u.to", "clck.ru"}
MULTI_TLD = {"co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "co.jp", "com.br", "com.cn", "co.in", "co.za",
             "com.mx", "com.tr", "gov.it", "edu.it"}
MARCHI = {
    "poste": {"poste.it", "posteitaliane.it", "postepay.it"}, "posteitaliane": {"poste.it", "posteitaliane.it"},
    "postepay": {"poste.it", "postepay.it"}, "bancoposta": {"poste.it"},
    "intesa": {"intesasanpaolo.com", "intesasanpaolo.it"}, "intesasanpaolo": {"intesasanpaolo.com", "intesasanpaolo.it"},
    "unicredit": {"unicredit.it", "unicredit.eu", "unicreditgroup.eu"}, "bnl": {"bnl.it"}, "fineco": {"finecobank.com"},
    "inps": {"inps.it"}, "agenziaentrate": {"agenziaentrate.gov.it", "agenziaentrateriscossione.gov.it"},
    "paypal": {"paypal.com", "paypal.it", "paypal.me", "paypalobjects.com"},
    "amazon": {"amazon.it", "amazon.com", "amazon.de", "amazon.fr", "amazon.es", "amazon.co.uk", "amazon.eu",
               "amazonaws.com", "amzn.to", "media-amazon.com"},
    "apple": {"apple.com", "icloud.com", "apple.co"}, "icloud": {"icloud.com", "apple.com"},
    "microsoft": {"microsoft.com", "live.com", "office.com", "outlook.com", "microsoftonline.com", "sharepoint.com",
                  "office365.com", "windows.net", "azure.com", "msn.com", "bing.com"},
    "office365": {"office365.com", "office.com", "microsoft.com"}, "outlook": {"outlook.com", "live.com", "office.com"},
    "google": {"google.com", "google.it", "googleapis.com", "gstatic.com", "youtube.com", "gmail.com", "goo.gl",
               "googleusercontent.com", "g.co"},
    "gmail": {"gmail.com", "google.com"}, "netflix": {"netflix.com"},
    "facebook": {"facebook.com", "fb.com", "fb.me", "meta.com", "fbcdn.net"}, "instagram": {"instagram.com"},
    "whatsapp": {"whatsapp.com", "whatsapp.net", "wa.me"}, "dhl": {"dhl.com", "dhl.it", "dhl.de"}, "brt": {"brt.it"},
    "gls": {"gls-italy.com", "gls-group.eu", "gls-group.com"}, "nexi": {"nexi.it", "nexigroup.com"},
    "satispay": {"satispay.com"}, "aruba": {"aruba.it"}, "enel": {"enel.it", "enel.com"}, "telepass": {"telepass.com"},
    "binance": {"binance.com"}, "coinbase": {"coinbase.com"}, "metamask": {"metamask.io"},
}
PAROLE_ESCA = ("login", "signin", "secure", "verify", "verifica", "account", "update", "aggiorna", "conferma",
               "sicurezza", "accesso", "wallet", "support", "assistenza", "rimborso", "sblocca")
EST_RISCHIOSE = r"exe|scr|bat|cmd|pif|ps1|psm1|vbs|vbe|js|jse|wsf|wsh|hta|lnk|iso|img|vhdx?|msi|msix|appx|jar|dll|cpl|apk|reg|docm|xlsm|pptm|one|sh"


def dominio_registrabile(host: str) -> str:
    p = host.lower().strip(".").split(".")
    if len(p) >= 3 and ".".join(p[-2:]) in MULTI_TLD:
        return ".".join(p[-3:])
    return ".".join(p[-2:])


SOSIA = str.maketrans({"а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ј": "j",
                       "ԁ": "d", "ɡ": "g", "ո": "n", "ѕ": "s", "ԛ": "q", "ԝ": "w", "ı": "i", "ο": "o", "α": "a",
                       "ν": "v", "τ": "t", "ρ": "p", "κ": "k", "ι": "i", "ϲ": "c", "ӏ": "l", "һ": "h", "ʏ": "y"})


def _script(ch):
    try:
        return unicodedata.name(ch).split()[0]
    except ValueError:
        return "?"


def analizza_url(u: str) -> tuple:
    seg = []
    try:
        p = urllib.parse.urlsplit(u)
    except ValueError:
        return {}, seg
    host = (p.hostname or "").lower()
    info = {"url": u, "host": host}
    if not host:
        return info, seg
    if "@" in p.netloc:
        seg.append(seg_(3, "URL con '@': il vero indirizzo e' quello dopo la @ (%s)" % host))
    try:
        ipaddress.ip_address(host.strip("[]"))
        seg.append(seg_(2, "il link punta a un indirizzo IP (%s) invece che a un nome di dominio" % host))
    except ValueError:
        if re.fullmatch(r"\d{8,10}|0x[0-9a-f]{8}", host):
            seg.append(seg_(3, "indirizzo IP offuscato in forma numerica (%s)" % host))
    try:
        if p.port and p.port not in (80, 443):
            seg.append(seg_(1, "porta non standard (%d)" % p.port))
    except ValueError:
        pass
    try:
        uni = ".".join(l.encode("ascii").decode("idna") if l.startswith("xn--") else l for l in host.split("."))
    except Exception:
        uni = host
    if uni != host or any(ord(c) > 127 for c in uni):
        info["host_unicode"] = uni
        alfabeti = {_script(c) for c in uni if c.isalpha()}
        if len(alfabeti) > 1:
            seg.append(seg_(3, "dominio con caratteri di alfabeti diversi (%s): possibile imitazione visiva" % ", ".join(sorted(alfabeti))))
        else:
            seg.append(seg_(1, "dominio internazionalizzato (%s): controlla che non imiti un marchio noto" % uni))
    reg = dominio_registrabile(host)
    info["dominio"] = reg
    if host in ACCORCIATORI or reg in ACCORCIATORI:
        seg.append(seg_(1, "link accorciato (%s): la destinazione reale e' nascosta" % host))
    if host.rsplit(".", 1)[-1] in ("zip", "mov"):
        seg.append(seg_(2, "dominio .%s: si confonde facilmente con un nome di file" % host.rsplit(".", 1)[-1]))
    if host.count(".") >= 4:
        seg.append(seg_(1, "molti sottodomini (%s): tecnica usata per nascondere il dominio reale" % host))
    token = re.split(r"[.\-]", host)
    if "host_unicode" in info:
        token += re.split(r"[.\-]", info["host_unicode"].translate(SOSIA))
    for marchio, ufficiali in MARCHI.items():
        corto = len(marchio) <= 4
        trovato = any(tk == marchio or (not corto and marchio in tk and len(tk) <= len(marchio) + 12) for tk in token)
        if trovato and reg not in ufficiali:
            seg.append(seg_(3, "il dominio richiama «%s» ma appartiene a %s, non al sito ufficiale" % (marchio, reg)))
            break
    else:
        percorso = (p.path + "?" + p.query).lower()
        for marchio, ufficiali in MARCHI.items():
            if len(marchio) > 4 and marchio in percorso and reg not in ufficiali:
                seg.append(seg_(2, "il percorso richiama «%s» ma il dominio e' %s" % (marchio, reg)))
                break
    if any(w in host for w in PAROLE_ESCA) and not any(reg in uff for uff in MARCHI.values()):
        seg.append(seg_(1, "il nome del dominio contiene parole-esca (login, verifica, account...)"))
    if p.scheme == "http" and re.search(r"login|signin|password|account|verifica|accedi|pagamento", u, re.I):
        seg.append(seg_(1, "pagina di accesso/pagamento su connessione non cifrata (http)"))
    for k, vals in urllib.parse.parse_qs(p.query).items():
        for v in vals:
            if re.match(r"(?i)https?://", v):
                dest = urllib.parse.urlsplit(v).hostname or ""
                if dest and dominio_registrabile(dest) != reg:
                    seg.append(seg_(2, "reindirizzamento verso un altro dominio (%s)" % dest))
    if re.search(r"\.(%s)$" % EST_RISCHIOSE, p.path, re.I):
        seg.append(seg_(2, "il link scarica direttamente un file eseguibile o uno script"))
    return info, seg


def estrai_ioc(t: str) -> dict:
    s = re.sub(r"(?i)\bhxxp", "http", t).replace("[.]", ".").replace("(.)", ".").replace("[:]", ":")
    urls = []
    for m in re.finditer(r"(?i)\b(?:https?|ftp)://[^\s<>\"'`\)\]\}]+|\bwww\.[a-z0-9-]+(?:\.[a-z0-9-]+)+[^\s<>\"'`\)\]\}]*", s):
        u = m.group(0).rstrip(".,;:!?")
        if u.lower().startswith("www."):
            u = "http://" + u
        if u not in urls:
            urls.append(u)
    ip = []
    for m in re.finditer(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b", s):
        if m.group(0) not in ip:
            ip.append(m.group(0))
    email = sorted(set(re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", s)))
    file_r = sorted(set(m.group(0).strip() for m in re.finditer(r"[\w\-.]{1,80}\.(?:%s)\b" % EST_RISCHIOSE, s, re.I)
                        if not re.match(r"(?i)www\.", m.group(0))))
    wallet = sorted(set(re.findall(r"\bbc1[ac-hj-np-z02-9]{25,71}\b|\b0x[a-fA-F0-9]{40}\b|\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b", s)))
    hashes = sorted(set(re.findall(r"(?<![0-9a-fA-F])(?:[0-9a-fA-F]{64}|[0-9a-fA-F]{40}|[0-9a-fA-F]{32})(?![0-9a-fA-F])", s)))
    return {"url": urls[:50], "ip": ip[:50], "email": email[:50], "file_rischiosi": file_r[:50],
            "indirizzi_cripto": wallet[:20], "possibili_hash": hashes[:20]}


# --------------------------------------------------------------------------- segnali nel contenuto
REGOLE = [
    (r"(?i)-e(?:nc(?:odedcommand)?)?\s+[A-Za-z0-9+/=]{20,}", 3, "PowerShell con comando codificato (-EncodedCommand)"),
    (r"(?i)\b(iex|invoke-expression)\b", 3, "esecuzione dinamica di codice (Invoke-Expression)"),
    (r"(?i)downloadstring|downloadfile|downloaddata|invoke-webrequest|\biwr\b|invoke-restmethod|net\.webclient|start-bitstransfer|bitsadmin",
     2, "scarica contenuti da Internet"),
    (r"(?i)frombase64string", 1, "decodifica base64 durante l'esecuzione"),
    (r"(?i)-w(?:indowstyle)?\s+h(?:idden)?\b|-nop\b|-noprofile\b|-executionpolicy\s+bypass|-ep\s+bypass", 2,
     "esecuzione nascosta o aggiramento delle policy di PowerShell"),
    (r"(?i)amsiutils|amsiinitfailed|amsiscanbuffer", 3, "tentativo di disattivare l'antimalware di Windows (AMSI)"),
    (r"(?i)set-mppreference|add-mppreference\s+-exclusion", 3, "modifica o esclusioni di Microsoft Defender"),
    (r"(?i)certutil(?:\.exe)?\s+.*(?:-decode|-urlcache)", 3, "uso di certutil per scaricare/decodificare file"),
    (r"(?i)\bmshta(?:\.exe)?\s", 3, "uso di mshta (esegue script da HTML)"),
    (r"(?i)\bregsvr32(?:\.exe)?\s.*(?:/i:|scrobj)", 3, "uso di regsvr32 per eseguire codice remoto"),
    (r"(?i)\brundll32(?:\.exe)?\s", 2, "uso di rundll32"),
    (r"(?i)\b(?:wscript|cscript)(?:\.exe)?\b", 2, "esecuzione di script Windows (wscript/cscript)"),
    (r"(?i)schtasks\s+/create", 2, "crea un'attivita' pianificata (persistenza)"),
    (r"(?i)reg(?:\.exe)?\s+add\s+.*\\run\b", 3, "si aggiunge all'avvio automatico (persistenza)"),
    (r"(?i)vssadmin\s+delete\s+shadows|wbadmin\s+delete|bcdedit.*recoveryenabled\s+no", 3,
     "cancella copie di backup/ripristino (tipico del ransomware)"),
    (r"(?i)\b(?:curl|wget)\b[^|\n]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b", 3, "scarica ed esegue subito uno script"),
    (r"(?i)base64\s+(?:-d|--decode)[^|\n]*\|\s*(?:ba)?sh", 3, "decodifica ed esegue uno script nascosto"),
    (r"(?i)/dev/tcp/|\bnc(?:at)?\b[^\n]*\s-e\s|bash\s+-i\s+>&", 3, "possibile 'reverse shell' (controllo remoto)"),
    (r"(?i)\brm\s+-rf\s+(?:/|~|\*)", 3, "comando distruttivo (cancella file)"),
    (r"(?i)crontab|/etc/cron|systemctl\s+enable|authorized_keys", 2, "modifiche per restare attivo sul sistema (persistenza)"),
    (r"(?i)\beval\s*\(", 2, "esecuzione dinamica di codice (eval)"),
    (r"(?i)new\s+Function\s*\(", 2, "creazione dinamica di codice (new Function)"),
    (r"(?i)\batob\s*\(|unescape\s*\(|String\.fromCharCode", 1, "decodifica di stringhe nascoste nel codice"),
    (r"(?i)document\.write\s*\(", 1, "scrive contenuto nella pagina a runtime"),
    (r"(?i)(?:window|document)\.location(?:\.href)?\s*=|location\.replace\s*\(", 1, "reindirizza automaticamente la pagina"),
    (r"(?i)<iframe[^>]+(?:width|height)\s*=\s*[\"']?0", 2, "iframe invisibile"),
    (r"(?i)<form[^>]+action\s*=\s*[\"']?https?://", 1, "modulo che invia i dati a un server esterno"),
    (r"(?i)type\s*=\s*[\"']?password", 2, "la pagina chiede una password"),
    (r"(?i)child_process|os\.system|subprocess\.(?:popen|call|run)|pty\.spawn|runtime\.getruntime\(\)\.exec", 2,
     "esegue comandi di sistema"),
    (r"(?i)marshal\.loads|exec\s*\(\s*(?:base64|zlib|codecs)", 2, "esegue codice Python nascosto"),
    (r"(?i)auto_?open|document_open|workbook_open", 3, "macro Office ad avvio automatico"),
    (r"(?i)createobject\s*\(\s*[\"']wscript\.shell|urldownloadtofile", 3, "macro che esegue comandi o scarica file"),
    (r"(?i)(?:eval|assert)\s*\(\s*(?:base64_decode|gzinflate|str_rot13)", 3, "webshell PHP offuscata"),
    (r"(?i)seed phrase|frase (?:di )?recupero|recovery phrase|mnemonic phrase|parole di recupero|chiave privata del wallet", 3,
     "richiesta della frase di recupero di un wallet: nessun servizio legittimo la chiede"),
]
FRASI_PHISHING = [
    r"verifica (?:il tuo|del tuo|i tuoi|il suo|i suoi) (?:account|conto|profilo|dati)",
    r"(?:account|conto|carta|profilo) (?:e |e' |e stato |e stata |stato |stata |risulta )?(?:sospes|bloccat|limitat|disattivat)",
    r"(?:accesso|attivita) (?:insolit|sospett|non autorizzat|anomal)",
    r"conferma (?:la tua |la sua |i tuoi |i suoi |i |le |il )?(?:identita|dati|credenziali|indirizzo|pagamento)",
    r"aggiorna (?:i tuoi|i suoi) (?:dati|metodo di pagamento)",
    r"clicca (?:qui|sul link|sul seguente link|il link)",
    r"entro (?:24|48|72) ore",
    r"\burgente\b|\burgentemente\b",
    r"(?:pacco|spedizione|consegna)(?: (?:e|e'|risulta|e stato|e stata))? (?:in giacenza|in sospeso|non riuscita|non consegnat|bloccat)",
    r"(?:rimborso|accredito) (?:in attesa|disponibile|a tuo favore|a suo favore)",
    r"(?:pagamento|addebito) (?:non riuscito|rifiutato|in sospeso|sospetto)",
    r"codice (?:otp|di verifica|di sicurezza|dispositivo|pin)",
    r"(?:inserisci|comunica|conferma) (?:il |la |le )?(?:pin|codice|password|credenziali)",
    r"hai vinto|sei stat[oa] selezionat|premio in denaro|buono regalo",
    r"(?:multa|sanzione|verbale) (?:da pagare|non pagat)",
    r"verify your (?:account|identity|information)",
    r"account (?:has been |was )?(?:suspended|locked|limited|disabled)",
    r"unusual (?:sign-?in|activity)",
    r"click (?:here|the link|below)",
    r"within (?:24|48|72) hours",
    r"(?:update|confirm) your (?:payment|billing|details)",
    r"you have won|gift card|wire transfer",
    r"password (?:expired|will expire|scadut|in scadenza)",
]


def segnali_contenuto(t: str) -> list:
    seg = []
    for rx, g, msg in REGOLE:
        if re.search(rx, t):
            seg.append(seg_(g, msg))
    if re.search(r"(?i)captcha|non sono un robot|i'?m not a robot|verifica umana|human verification|verify you are human", t) \
            and re.search(r"(?i)\b(?:powershell|pwsh|mshta|cmd(?:\.exe)?|curl|wget|iwr|iex|bash|osascript)\b", t):
        seg.append(seg_(3, "falso CAPTCHA che fa incollare un comando (tecnica ClickFix): nessuna verifica legittima lo chiede"))
    norm = _senza_accenti(t.lower())
    trovate = [rx for rx in FRASI_PHISHING if re.search(rx, norm)]
    if len(trovate) >= 3:
        seg.append(seg_(2, "linguaggio tipico del phishing (%d formule di urgenza o richiesta dati)" % len(trovate)))
    elif trovate:
        seg.append(seg_(1, "contiene formule tipiche del phishing (urgenza o richiesta di dati)"))
    return seg


# --------------------------------------------------------------------------- analisi di binari
DOPPIA_EST = r"\.(?:pdf|docx?|xlsx?|pptx?|jpe?g|png|txt|zip|rar)\.(?:exe|scr|bat|cmd|js|jse|vbs|vbe|hta|lnk|ps1|wsf|iso|img|msi)$"


def estrai_stringhe(b: bytes, minimo: int = 6) -> list:
    a = re.findall(rb"[\x20-\x7e]{%d,}" % minimo, b)[:3000]
    u = re.findall(rb"(?:[\x20-\x7e]\x00){%d,}" % minimo, b)[:3000]
    return [x.decode("ascii") for x in a] + [x.decode("utf-16-le") for x in u]


def analizza_binario(b: bytes, nascosto: bool) -> dict:
    r = {"dettagli": {}, "note": [], "segnali": []}
    nome, cat = tipo_file(b)
    r["dettagli"]["tipo"] = nome or "sconosciuto"
    r["dettagli"]["entropia"] = round(entropia(b), 2)
    if cat == "eseguibile":
        r["segnali"].append(seg_(3 if nascosto else 2, ("eseguibile NASCOSTO dentro una codifica: tipico del malware"
                                                         if nascosto else "file eseguibile (%s): non avviarlo se non viene "
                                                         "da una fonte verificata" % nome)))
    elif cat == "disco":
        r["segnali"].append(seg_(2, "immagine disco: spesso usata per aggirare le protezioni di Windows sui file scaricati"))
    elif nome and nome.startswith("archivio ZIP"):
        try:
            z = zipfile.ZipFile(io.BytesIO(b))
            elenco, cifrato = [], False
            for info in z.infolist()[:200]:
                c = bool(info.flag_bits & 0x1)
                cifrato |= c
                elenco.append("%s (%d byte%s)" % (info.filename, info.file_size, ", cifrato" if c else ""))
                low = info.filename.lower()
                if re.search(DOPPIA_EST, low):
                    r["segnali"].append(seg_(3, "doppia estensione nell'archivio: %s" % info.filename))
                elif re.search(r"\.(?:%s)$" % EST_RISCHIOSE, low):
                    r["segnali"].append(seg_(2, "eseguibile o script nell'archivio: %s" % info.filename))
                if low.endswith("vbaproject.bin"):
                    r["segnali"].append(seg_(3, "documento Office con MACRO (vbaProject.bin)"))
            r["dettagli"]["contenuto"] = elenco[:50]
            if "[Content_Types].xml" in z.namelist():
                r["note"].append("E' un documento Office moderno (formato OOXML).")
            if cifrato:
                r["segnali"].append(seg_(1, "archivio protetto da password: tecnica comune per eludere gli antivirus nelle email"))
        except Exception as e:
            r["note"].append("ZIP non leggibile: %s" % e)
    elif cat == "documento" and b.startswith(b"%PDF"):
        trov = [k for k in (b"/JavaScript", b"/JS", b"/OpenAction", b"/AA", b"/Launch", b"/EmbeddedFile", b"/SubmitForm", b"/XFA") if k in b]
        if b"/Launch" in trov:
            r["segnali"].append(seg_(3, "PDF che puo' lanciare programmi (/Launch)"))
        if (b"/JavaScript" in trov or b"/JS" in trov):
            r["segnali"].append(seg_(3 if (b"/OpenAction" in trov or b"/AA" in trov) else 2,
                                     "PDF con JavaScript" + (" eseguito all'apertura" if b"/OpenAction" in trov else "")))
        if b"/EmbeddedFile" in trov:
            r["segnali"].append(seg_(2, "PDF con file incorporati"))
        r["dettagli"]["parole_chiave_pdf"] = [k.decode() for k in trov]
    elif cat == "documento" and b.startswith(b"\xd0\xcf\x11\xe0"):
        if any(k in b for k in (b"_VBA_PROJECT", b"VBA", b"Macros")):
            r["segnali"].append(seg_(3, "documento Office legacy con macro VBA"))
    elif cat == "documento" and b.startswith(b"{\\rtf"):
        if b"\\objupdate" in b or b"Equation.3" in b:
            r["segnali"].append(seg_(3, "RTF con oggetti a esecuzione automatica (vettore di exploit noti)"))
        elif b"\\objdata" in b:
            r["segnali"].append(seg_(2, "RTF con oggetti incorporati"))
    elif cat == "cifrato":
        r["note"].append("Formato cifrato riconosciuto (%s): non leggibile senza la chiave." % nome)
    elif not nome:
        n, e = len(b), entropia(b)
        massima = math.log2(min(n, 256)) if n > 1 else 1
        dup = 0
        if n % 16 == 0 and n >= 32:
            blocchi = [b[i:i + 16] for i in range(0, n, 16)]
            dup = len(blocchi) - len(set(blocchi))
        if dup:
            r["note"].append("Lunghezza multipla di 16 con blocchi identici: cifrario a blocchi in modalita' ECB.")
            r["segnali"].append(seg_p(2, "%d blocchi da 16 byte ripetuti: modalita' ECB, che lascia trapelare gli schemi "
                                     "del testo (testo uguale -> cifrato uguale). Protezione DEBOLE" % dup))
            r["ecb"] = dup
        elif e / massima > 0.9 and n >= 16:
            r["note"].append("Dati ad alta entropia: tipico di cifratura o compressione (oppure di una chiave/hash).")
            if n % 16 == 0:
                r["note"].append("Lunghezza multipla di 16: compatibile con un cifrario a blocchi (es. AES-CBC con IV).")
            else:
                r["note"].append("Lunghezza non multipla di 16: compatibile con cifrario a flusso/AEAD (es. AES-GCM, ChaCha20) o compressione.")
            if n in LUNGHEZZE_HASH:
                r["note"].append("%d byte: lunghezza tipica di un hash o di una chiave." % n)
        else:
            r["note"].append("Entropia media/bassa: formato binario non riconosciuto o protezione debole (prova classici.py xor-attacco).")
    return r


# --------------------------------------------------------------------------- blob nascosti in un testo
STRUTTURE_RE = re.compile(r"eyJ[\w-]{8,}\.[\w-]{2,}\.[\w-]*(?:\.[\w-]+\.[\w-]+)?|-----BEGIN [A-Z0-9 ]+-----.*?-----END [A-Z0-9 ]+-----"
                          r"|\b(?:crit1|crithp1|critpk1)\.[\w-]+|\bv[1-4]\.(?:local|public)\.[\w.-]+|\bgAAAAA[\w-]{60,}={0,2}"
                          r"|\$[0-9a-z]{1,8}\$\S+|(?:ssh-[a-z0-9-]+|ecdsa-sha2-nistp\d+) AAAA[\w+/=]+|data:[^,\s]*,[^\s\"']+", re.S)


def estrai_blob(t: str) -> list:
    t = STRUTTURE_RE.sub(" ", t)
    blob = []
    for m in re.finditer(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{24,}={0,2}(?![A-Za-z0-9+/=])", t):
        blob.append(("base64", m.group(0)))
    for m in re.finditer(r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}){12,}(?![0-9A-Fa-f])", t):
        blob.append(("esadecimale", m.group(0)))
    for m in re.finditer(r"(?:\\x[0-9a-fA-F]{2}){6,}", t):
        blob.append(("escape \\x", m.group(0)))
    for m in re.finditer(r"fromCharCode\s*\(([\d\s,]+)\)", t):
        vals = [int(x) for x in re.findall(r"\d+", m.group(1))]
        if vals and max(vals) < 0x110000:
            blob.append(("String.fromCharCode", "".join(chr(v) for v in vals)))
    codici = re.findall(r"(?i)\bchrw?\(\s*(\d{1,6})\s*\)", t)
    if len(codici) >= 6:
        blob.append(("chr()", "".join(chr(int(c)) for c in codici if int(c) < 0x110000)))
    visti, uniche = set(), []
    for orig, v in blob:
        if v not in visti and len(v) < 0.9 * len(t.strip()):
            visti.add(v)
            uniche.append((orig, v))
    return uniche[:10]


# --------------------------------------------------------------------------- analisi completa
def analizza(dati: bytes, profondita: int = 12, livello: int = 0) -> dict:
    rap = {"input": {"byte": len(dati), "entropia": round(entropia(dati[:MAX_OUT]), 2)},
           "strati": [], "formati": [], "nascosti": [], "ioc": {}, "segnali": [], "finale": {}}
    strati, finale = sbuccia(dati, profondita)
    testi = []
    t0, _ = bytes_a_testo(dati)
    rap["input"]["tipo"] = "testo" if t0 is not None and quota_stampabile(t0) >= 0.85 else (tipo_file(dati)[0] or "binario")
    if t0 is not None:
        testi.append(t0)
    for s in strati:
        t, _ = bytes_a_testo(s["_dati"])
        if t is not None and quota_stampabile(t) >= 0.85:
            testi.append(t)
        rap["strati"].append({k: v for k, v in s.items() if k != "_dati"})

    contenuti_annidati = []
    for t in testi:
        for f in riconosci_formati(t):
            if "_contenuto" in f:
                contenuti_annidati.append(("data URI", f.pop("_contenuto")))
            if f not in rap["formati"]:
                rap["formati"].append(f)
    # blob codificati dentro il testo (es. powershell -enc ..., eval(atob("...")))
    if livello < 2:
        for t in testi[-2:]:
            for orig, blob in estrai_blob(t):
                contenuti_annidati.append((orig, blob.encode("utf-8", "surrogatepass")))
        for orig, raw in contenuti_annidati[:12]:
            sub = analizza(raw, max(3, profondita // 2), livello + 1)
            fin = sub["finale"]
            utile = fin.get("tipo") in ("testo", "file") and (sub["strati"] or orig in ("data URI", "String.fromCharCode", "chr()"))
            if not utile:
                continue
            rap["nascosti"].append({"origine": orig, "strati": [s["decodifica"] for s in sub["strati"]],
                                    "tipo": fin.get("descrizione"), "anteprima": fin.get("anteprima", "")[:300]})
            for k, v in sub["ioc"].items():
                rap["ioc"].setdefault(k, [])
                rap["ioc"][k] += [x for x in v if x not in rap["ioc"][k]]
            rap["segnali"] += sub["segnali"]
            rap["formati"] += [f for f in sub["formati"] if f not in rap["formati"]]

    tf, _ = bytes_a_testo(finale)
    if tipo_file(finale)[0] and tf is not None:
        bi = analizza_binario(finale, nascosto=bool(strati) or livello > 0)
        rap["finale"] = {"tipo": "file", "descrizione": bi["dettagli"]["tipo"], "binario": bi,
                         "hex": finale[:64].hex(" "), "testo": tf}
        rap["segnali"] += bi["segnali"]
    elif tf is not None and quota_stampabile(tf) >= 0.85:
        rap["finale"] = {"tipo": "testo", "descrizione": "testo leggibile", "testo": tf}
    else:
        bi = analizza_binario(finale, nascosto=bool(strati) or livello > 0)
        cat = tipo_file(finale)[1]
        rap["finale"] = {"tipo": "file" if cat else "binario", "descrizione": bi["dettagli"]["tipo"], "binario": bi,
                         "hex": finale[:64].hex(" ")}
        rap["segnali"] += bi["segnali"]
        stringhe = estrai_stringhe(finale)
        if stringhe:
            testi.append("\n".join(stringhe))
            rap["finale"]["stringhe_campione"] = stringhe[:15]
    testo_tot = "\n".join(testi)
    ioc = estrai_ioc(testo_tot)
    for k, v in ioc.items():
        rap["ioc"].setdefault(k, [])
        rap["ioc"][k] = v + [x for x in rap["ioc"][k] if x not in v]
    for u in rap["ioc"].get("url", [])[:30]:
        _, seg = analizza_url(u)
        rap["segnali"] += seg
    if rap["ioc"].get("indirizzi_cripto"):
        rap["segnali"].append(seg_(1, "indirizzi di criptovaluta: se ti chiedono di pagarci e' tipico di truffe ed estorsioni"))
    for fr in rap["ioc"].get("file_rischiosi", []):
        if re.search(DOPPIA_EST, fr.lower()):
            rap["segnali"].append(seg_(3, "nome di file con doppia estensione: %s" % fr))
    for t in testi:
        rap["segnali"] += segnali_contenuto(t)
    for f in rap["formati"]:
        rap["segnali"] += f.get("segnali", [])
    uniche, visti = [], set()
    for s in sorted(rap["segnali"], key=lambda x: -x["gravita"]):
        if s["messaggio"] not in visti:
            visti.add(s["messaggio"])
            uniche.append(s)
    rap["segnali"] = uniche
    if "testo" in rap["finale"]:
        rap["finale"]["anteprima"] = rap["finale"].pop("testo")
    rap["valutazione"] = valuta(rap, finale)
    rap["_finale_bytes"] = finale
    return rap


def indice_coincidenza(lett: str) -> float:
    n = len(lett)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in Counter(lett).values()) / (n * (n - 1))


def _maiuscolo_uniforme(t: str) -> bool:
    """I cifrari classici sono quasi sempre tutti maiuscoli o tutti minuscoli; base64 e simili mescolano i casi."""
    lett = [c for c in t if c.isalpha()]
    if not lett:
        return False
    su = sum(c.isupper() for c in lett) / len(lett)
    return su <= 0.15 or su >= 0.85


def valuta(rap: dict, finale: bytes) -> dict:
    v = {}
    nomi = [s["decodifica"] for s in rap["strati"]]
    tipi_formati = " ".join(f["tipo"] for f in rap["formati"])
    moderni = re.search(r"cifrato|JWE|Fernet|age|PGP MESSAGE|PASETO v\d\.local|AGE ENCRYPTED", tipi_formati)
    fin = rap["finale"]
    jwt_firmato = "JWT (JSON Web Token)" in tipi_formati
    ecb = fin.get("binario", {}).get("ecb")
    if ecb:
        v["protezione"] = ("DEBOLE - cifrario a blocchi in modalita' ECB (%d blocchi ripetuti): non serve la chiave per "
                           "vedere quali parti del messaggio si ripetono; va sostituito con AES-GCM o ChaCha20-Poly1305" % ecb)
    elif any(n.startswith("XOR") for n in nomi):
        v["protezione"] = "NULLA - XOR con chiave di un byte: si rompe in un istante provando 255 chiavi"
    elif moderni:
        v["protezione"] = ("CIFRATURA MODERNA RICONOSCIUTA - non decifrabile senza la chiave; la robustezza reale "
                           "dipende da password/chiave e dalla loro gestione")
    elif jwt_firmato:
        v["protezione"] = ("NESSUNA RISERVATEZZA - un JWT firmato e' solo codificato: chiunque legge il contenuto. "
                           "La firma (se il server la verifica) impedisce le modifiche, non la lettura")
    elif rap.get("nascosti"):
        v["protezione"] = ("NESSUNA - il testo contiene parti solo codificate (%s) che chiunque puo' leggere"
                           % ", ".join(sorted({h["origine"] for h in rap["nascosti"]})))
    elif re.search(r"hash", tipi_formati) and not nomi:
        v["protezione"] = "HASH - non e' cifratura e non si decifra; si valuta l'algoritmo (e la forza della password, se e' un hash di password)"
    elif fin.get("tipo") == "binario" and fin.get("binario", {}).get("dettagli", {}).get("tipo") == "sconosciuto":
        v["protezione"] = "DATI OPACHI - probabile cifratura o compressione non identificata (vedi note su entropia e blocchi)"
    elif fin.get("tipo") == "testo":
        testo = fin.get("anteprima", "")
        lett = re.sub(r"[^A-Z]", "", _senza_accenti(testo).upper())
        pp = punteggio_parole(testo)
        if nomi:
            v["protezione"] = ("NESSUNA - era solo codificato (%s): chiunque lo legge senza chiave" % " -> ".join(nomi))
        elif len(lett) >= 20 and pp < 0.12 and len(lett) / max(1, len(re.sub(r"\s", "", testo))) > 0.7 \
                and _maiuscolo_uniforme(testo) and sum(c.isdigit() for c in testo) < 0.05 * len(testo):
            ic = indice_coincidenza(lett)
            breve = "; testo breve, indice poco affidabile" if len(lett) < 120 else ""
            if ic >= 0.058:
                v["protezione"] = ("PROBABILE CIFRARIO CLASSICO monoalfabetico o a trasposizione (IC=%.3f%s): DEBOLE. "
                                   "Prova: python scripts/classici.py auto \"...\"" % (ic, breve))
            else:
                v["protezione"] = ("PROBABILE CIFRARIO CLASSICO polialfabetico tipo Vigenere, o testo casuale (IC=%.3f%s): "
                                   "DEBOLE se classico. Prova: python scripts/classici.py auto \"...\"" % (ic, breve))
        else:
            v["protezione"] = "NESSUNA - testo in chiaro"
    else:
        v["protezione"] = "file riconosciuto (%s): vedi i segnali" % fin.get("descrizione")
    deboli = [x for x in rap["segnali"] if x.get("area") == "protezione"]
    if "ECB" in v["protezione"]:
        deboli = [x for x in deboli if "ECB" not in x["messaggio"]]
    if deboli:
        v["protezione"] += " | debolezze: " + "; ".join(x["messaggio"] for x in deboli[:4])
    seg = [x for x in rap["segnali"] if x.get("area") != "protezione"]
    if not seg:
        v["rischio"] = "NESSUN SEGNALE NOTO (non equivale a 'sicuro')"
    else:
        mx, tot = max(s["gravita"] for s in seg), sum(s["gravita"] for s in seg)
        v["rischio"] = "ALTO" if mx >= 3 or tot >= 7 else ("MEDIO" if mx == 2 or tot >= 3 else "BASSO")
    v["limiti"] = ("Analisi statica ed euristica: non apre i link, non esegue nulla, non consulta reputazioni online. "
                   "Un contenuto nuovo o ben camuffato puo' sfuggire.")
    return v


# --------------------------------------------------------------------------- stampa
GRAV = {3: "ALTO", 2: "MEDIO", 1: "BASSO"}


def _anteprima(t: str, completo: bool, n: int = 1500) -> str:
    if completo or len(t) <= n:
        return t
    return t[:n] + "\n...[troncato: %d caratteri in totale, usa --completo]" % len(t)


def stampa(rap: dict, completo: bool):
    out = []
    w = out.append
    i = rap["input"]
    w("=== ANALISI (solo statica: nulla e' stato eseguito o aperto) ===")
    w("Input: %d byte | entropia %.2f bit/byte | %s" % (i["byte"], i["entropia"], i["tipo"]))
    w("\n--- Strati di decodifica ---")
    if rap["strati"]:
        for n, s in enumerate(rap["strati"], 1):
            alt = (" (alternative scartate: %s)" % ", ".join(s["alternative"])) if s["alternative"] else ""
            w("  %d. %s -> %d byte (%s)%s" % (n, s["decodifica"], s["byte"], s["tipo"], alt))
    else:
        w("  nessuno: l'input non risulta codificato (o il formato non e' noto)")
    if rap["formati"]:
        w("\n--- Formati riconosciuti ---")
        for f in rap["formati"]:
            w("  * " + f["tipo"])
            for k, v in f.get("dettagli", {}).items():
                txt = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
                w("      %s: %s" % (k, txt[:600]))
            for nota in f.get("note", []):
                w("      nota: " + nota)
    if rap["nascosti"]:
        w("\n--- Contenuti nascosti trovati dentro il testo ---")
        for h in rap["nascosti"]:
            w("  * blob %s decodificato (%s) -> %s" % (h["origine"], " -> ".join(h["strati"]) or "diretto", h["tipo"]))
            w("      " + h["anteprima"].replace("\n", " ")[:300])
    fin = rap["finale"]
    w("\n--- Contenuto finale ---")
    if fin.get("tipo") == "testo":
        w(_anteprima(fin.get("anteprima", ""), completo))
    else:
        if fin.get("anteprima"):
            w(_anteprima(fin["anteprima"], completo, 800))
        w("  %s | primi byte: %s" % (fin.get("descrizione"), fin.get("hex", "")))
        for k, v in fin.get("binario", {}).get("dettagli", {}).items():
            if k != "tipo":
                w("  %s: %s" % (k, v))
        for nota in fin.get("binario", {}).get("note", []):
            w("  nota: " + nota)
        if fin.get("stringhe_campione"):
            w("  stringhe leggibili (campione): " + " | ".join(x[:60] for x in fin["stringhe_campione"]))
    ioc = {k: v for k, v in rap["ioc"].items() if v}
    if ioc:
        w("\n--- Indicatori estratti (IOC) ---")
        for k, v in ioc.items():
            w("  %s: %s" % (k, ", ".join(v[:15]) + (" ..." if len(v) > 15 else "")))
    contenuto = [x for x in rap["segnali"] if x.get("area") != "protezione"]
    deboli = [x for x in rap["segnali"] if x.get("area") == "protezione"]
    w("\n--- Segnali di rischio del contenuto ---")
    if contenuto:
        for x in contenuto:
            w("  [%s] %s" % (GRAV[x["gravita"]], x["messaggio"]))
    else:
        w("  nessun segnale noto")
    if deboli:
        w("\n--- Debolezze della protezione ---")
        for x in deboli:
            w("  [%s] %s" % (GRAV[x["gravita"]], x["messaggio"]))
    v = rap["valutazione"]
    w("\n--- Valutazione ---")
    w("  Protezione: " + v["protezione"])
    w("  Rischio del contenuto: " + v["rischio"])
    w("  Limiti: " + v["limiti"])
    print("\n".join(out))


def _pulisci_json(o):
    if isinstance(o, dict):
        return {k: _pulisci_json(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [_pulisci_json(x) for x in o]
    if isinstance(o, bytes):
        return o.hex()
    return o


def main():
    ap = argparse.ArgumentParser(description="Decodifica a strati e valutazione statica di stringhe e file sospetti.")
    ap.add_argument("testo", nargs="?", help="stringa da analizzare, oppure '-' per leggere da stdin")
    ap.add_argument("--file", help="file da analizzare")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--profondita", type=int, default=12)
    ap.add_argument("--completo", action="store_true")
    ap.add_argument("--salva", help="salva i byte dell'ultimo strato in questo percorso")
    a = ap.parse_args()
    if a.file:
        with open(a.file, "rb") as fh:
            dati = fh.read(MAX_INPUT)
    elif a.testo == "-" or (a.testo is None and not sys.stdin.isatty()):
        dati = sys.stdin.buffer.read(MAX_INPUT)
    elif a.testo is not None:
        dati = a.testo.encode("utf-8", "surrogatepass")
    else:
        ap.print_help()
        return 2
    if not dati.strip():
        print("Input vuoto.")
        return 2
    rap = analizza(dati, a.profondita)
    if a.salva:
        with open(a.salva, "wb") as fh:
            fh.write(rap["_finale_bytes"])
    if a.json:
        print(json.dumps(_pulisci_json(rap), ensure_ascii=False, indent=2, default=str))
    else:
        stampa(rap, a.completo)
        if a.salva:
            print("\n(ultimo strato salvato in %s - NON eseguirlo)" % a.salva)
    return 0


if __name__ == "__main__":
    try:
        import signal
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:
        pass
    sys.exit(main())
