#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cifra.py - cifratura, firme e hash con impostazioni sicure (libreria "cryptography").

Comandi principali:
  cifra    (--testo T | --file F) [--chiave K] [--out F] [--kdf scrypt]
  decifra  (--testo TOKEN | --file F) [--chiave K] [--out F]
  chiave                                   genera una chiave casuale a 256 bit
  coppia --nome N                          coppia di chiavi ibrida post-quantum (X25519 + ML-KEM-768)
  cifra-per   --pubblica P (--testo | --file) [--out]     cifra per il proprietario della chiave pubblica
  decifra-con --privata FILE (--testo | --file) [--out]
  firma-coppia --nome N                    coppia di chiavi Ed25519 per firmare
  firma    --privata FILE (--testo | --file)
  verifica --pubblica P --firma S (--testo | --file)
  hash     (--testo | --file) [--algoritmo sha256] [--atteso VALORE]
  casuale  [--tipo password|token|hex|pin] [--lunghezza N]
  valuta-password                          stima la robustezza della password in CRIT_PASSWORD
  autotest                                 verifica che cifratura, autenticazione e firme funzionino

Password: dalla variabile d'ambiente CRIT_PASSWORD (consigliato in modo non interattivo),
oppure --password-stdin, oppure richiesta a terminale. --password funziona ma resta nella cronologia.

Formati (documentati per poterli decifrare anche senza questo script):
  simmetrico  "crit1." + base64url( "CRT1" | modo | parametri KDF | sale | nonce | AES-256-GCM(dati) )
              l'intestazione e' autenticata come dati associati (AAD): non si puo' alterare.
  pubblico    "crithp1." + base64url( "CRH1" | 0x01 | HPKE(KEM X25519+ML-KEM-768, HKDF-SHA256, AES-256-GCM) )
Per file molto grandi o uso professionale preferisci strumenti consolidati come age o GnuPG.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import string
import sys
import time
import unicodedata
from collections import Counter

try:
    from cryptography.exceptions import InvalidSignature, InvalidTag
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
except ImportError:
    sys.exit("Serve la libreria 'cryptography':  pip install cryptography  (oppure aggiungi --break-system-packages)")

MAGIC, MAGIC_H = b"CRT1", b"CRH1"
MODO_ARGON2ID, MODO_SCRYPT, MODO_CHIAVE = 1, 2, 3
ARGON2_M_KIB, ARGON2_T, ARGON2_P = 64 * 1024, 3, 4          # RFC 9106, seconda configurazione raccomandata
SCRYPT_LN, SCRYPT_R, SCRYPT_P = 17, 8, 1                     # N = 2^17 (OWASP)
INFO_HPKE = b"crittografia-skill/hpke/v1"
LIMITE_FILE = 512 * 1024 * 1024


class ErroreDecifratura(Exception):
    pass


# --------------------------------------------------------------------------- utilita'
def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def da_b64u(s: str) -> bytes:
    s = re.sub(r"\s+", "", s)
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def da_token(s: str, prefisso: str) -> bytes:
    s = re.sub(r"\s+", "", s)
    if s.startswith(prefisso + "."):
        s = s[len(prefisso) + 1:]
    return da_b64u(s)


def entropia(b: bytes) -> float:
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in Counter(b).values()) if n else 0.0


def argon2_disponibile() -> bool:
    try:
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
        Argon2id(salt=b"0" * 16, length=32, iterations=1, lanes=1, memory_cost=8).derive(b"x")
        return True
    except Exception:
        return False


def hpke_disponibile() -> bool:
    try:
        from cryptography.hazmat.primitives import hpke  # noqa: F401
        from cryptography.hazmat.primitives.asymmetric import mlkem
        mlkem.MLKEM768PrivateKey.generate()
        return True
    except Exception:
        return False


def normalizza_password(pw: str) -> bytes:
    # NFC: la stessa password con accenti deve dare la stessa chiave su ogni sistema
    return unicodedata.normalize("NFC", pw).encode("utf-8")


def leggi_password(a, nuova: bool = False) -> str:
    if getattr(a, "password", None):
        print("Attenzione: una password passata come argomento resta nella cronologia della shell.", file=sys.stderr)
        return a.password
    if os.environ.get("CRIT_PASSWORD"):
        return os.environ["CRIT_PASSWORD"]
    if getattr(a, "password_stdin", False):
        return sys.stdin.readline().rstrip("\r\n")
    if sys.stdin.isatty():
        pw = getpass.getpass("Password: ")
        if nuova and getpass.getpass("Ripeti la password: ") != pw:
            sys.exit("Le password non coincidono.")
        return pw
    sys.exit("Serve una password: imposta CRIT_PASSWORD, usa --password-stdin o un terminale interattivo.")


def password_opzionale(a):
    if getattr(a, "password", None) or os.environ.get("CRIT_PASSWORD") or getattr(a, "password_stdin", False):
        return leggi_password(a)
    return None


# --------------------------------------------------------------------------- cifratura simmetrica
def _deriva(modo: int, pw: bytes, par: bytes, sale: bytes) -> bytes:
    if modo == MODO_ARGON2ID:
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
        m, t, p = int.from_bytes(par[0:4], "big"), par[4], par[5]
        if not (8 <= m <= 2 * 1024 * 1024 and 1 <= t <= 10 and 1 <= p <= 16):
            raise ErroreDecifratura("parametri Argon2id fuori dai limiti (file danneggiato o malevolo)")
        return Argon2id(salt=sale, length=32, iterations=t, lanes=p, memory_cost=m).derive(pw)
    if modo == MODO_SCRYPT:
        ln, r, p = par[0], par[1], par[2]
        if not (10 <= ln <= 22 and 1 <= r <= 32 and 1 <= p <= 16):
            raise ErroreDecifratura("parametri scrypt fuori dai limiti (file danneggiato o malevolo)")
        return Scrypt(salt=sale, length=32, n=2 ** ln, r=r, p=p).derive(pw)
    raise ErroreDecifratura("modo sconosciuto")


def cifra_simmetrico(dati: bytes, password: str | None = None, chiave: bytes | None = None, kdf: str = "argon2id") -> bytes:
    nonce = os.urandom(12)
    if chiave is not None:
        if len(chiave) != 32:
            raise ValueError("la chiave deve essere di 32 byte (256 bit)")
        intest, k = MAGIC + bytes([MODO_CHIAVE]) + nonce, chiave
    else:
        if password is None:
            raise ValueError("serve una password o una chiave")
        sale = os.urandom(16)
        if kdf == "argon2id" and argon2_disponibile():
            par = ARGON2_M_KIB.to_bytes(4, "big") + bytes([ARGON2_T, ARGON2_P])
            modo = MODO_ARGON2ID
        else:
            par, modo = bytes([SCRYPT_LN, SCRYPT_R, SCRYPT_P]), MODO_SCRYPT
        intest = MAGIC + bytes([modo]) + par + sale + nonce
        k = _deriva(modo, normalizza_password(password), par, sale)
    return intest + AESGCM(k).encrypt(nonce, dati, intest)


def decifra_simmetrico(blob: bytes, password: str | None = None, chiave: bytes | None = None) -> bytes:
    if len(blob) < 5 + 12 + 16 or blob[:4] != MAGIC:
        raise ErroreDecifratura("non e' un cifrato crit1")
    modo = blob[4]
    if modo == MODO_CHIAVE:
        if chiave is None:
            raise ErroreDecifratura("questo cifrato richiede una chiave (--chiave), non una password")
        fine = 5 + 12
        k = chiave
    else:
        lp = 6 if modo == MODO_ARGON2ID else 3
        fine = 5 + lp + 16 + 12
        if password is None:
            raise ErroreDecifratura("questo cifrato richiede una password")
        k = _deriva(modo, normalizza_password(password), blob[5:5 + lp], blob[5 + lp:5 + lp + 16])
    intest, nonce = blob[:fine], blob[fine - 12:fine]
    try:
        return AESGCM(k).decrypt(nonce, blob[fine:], intest)
    except InvalidTag:
        raise ErroreDecifratura("password/chiave errata oppure dati alterati: decifratura rifiutata")


# --------------------------------------------------------------------------- chiave pubblica (HPKE ibrido post-quantum)
def _suite():
    from cryptography.hazmat.primitives import hpke
    return hpke.Suite(hpke.KEM.MLKEM768_X25519, hpke.KDF.HKDF_SHA256, hpke.AEAD.AES_256_GCM)


def genera_coppia():
    from cryptography.hazmat.primitives import hpke
    from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
    km, kx = mlkem.MLKEM768PrivateKey.generate(), x25519.X25519PrivateKey.generate()
    priv = {"formato": "crit-hpke-privata-v1", "kem": "X25519+ML-KEM-768",
            "mlkem_seme": b64u(km.private_bytes_raw()), "x25519": b64u(kx.private_bytes_raw())}
    pub = "critpk1." + b64u(km.public_key().public_bytes_raw() + kx.public_key().public_bytes_raw())
    priv["pubblica"] = pub
    return priv, pub, hpke.MLKEM768X25519PrivateKey(km, kx)


def carica_privata(dati_json: dict):
    from cryptography.hazmat.primitives import hpke
    from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
    km = mlkem.MLKEM768PrivateKey.from_seed_bytes(da_b64u(dati_json["mlkem_seme"]))
    kx = x25519.X25519PrivateKey.from_private_bytes(da_b64u(dati_json["x25519"]))
    return hpke.MLKEM768X25519PrivateKey(km, kx)


def carica_pubblica(testo: str):
    from cryptography.hazmat.primitives import hpke
    from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
    raw = da_token(testo, "critpk1")
    if len(raw) != 1184 + 32:
        raise ValueError("chiave pubblica non valida (lunghezza inattesa)")
    return hpke.MLKEM768X25519PublicKey(mlkem.MLKEM768PublicKey.from_public_bytes(raw[:1184]),
                                        x25519.X25519PublicKey.from_public_bytes(raw[1184:]))


def cifra_pubblico(dati: bytes, pub) -> bytes:
    intest = MAGIC_H + b"\x01"
    return intest + _suite().encrypt(dati, pub, info=INFO_HPKE + intest)


def decifra_privato(blob: bytes, priv) -> bytes:
    if blob[:4] != MAGIC_H or blob[4:5] != b"\x01":
        raise ErroreDecifratura("non e' un cifrato crithp1")
    try:
        return _suite().decrypt(blob[5:], priv, info=INFO_HPKE + blob[:5])
    except Exception:
        raise ErroreDecifratura("chiave privata sbagliata oppure dati alterati: decifratura rifiutata")


def leggi_file_chiave_privata(percorso: str, a):
    contenuto = open(percorso, encoding="utf-8").read().strip()
    if contenuto.startswith("crit1."):
        pw = leggi_password(a)
        contenuto = decifra_simmetrico(da_token(contenuto, "crit1"), password=pw).decode("utf-8")
    return json.loads(contenuto)


def leggi_pubblica_arg(valore: str) -> str:
    if os.path.isfile(valore):
        return open(valore, encoding="utf-8").read().strip()
    return valore


# --------------------------------------------------------------------------- valutazione password
COMUNI = set("""123456 123456789 12345678 12345 1234567 1234567890 111111 000000 123123 654321 password password1 password123
qwerty qwerty123 qwertyuiop asdfghjkl zxcvbnm 1q2w3e4r 1qaz2wsx abc123 iloveyou admin admin123 welcome letmein monkey dragon
master sunshine princess football baseball superman batman trustno1 passw0rd ciao ciaociao ciao123 amore amoremio tiamo
juventus napoli milan inter roma lazio forzajuve forzanapoli forzainter forzamilan francesco alessandro andrea giuseppe
martina giulia chiara federica cambiami segreto benvenuto estate inverno italia password! 112233 121212 159753 147258369
sole luna stella principessa tesoro""".split())
PAROLE_DIZ = sorted(set("""password admin ciao amore tesoro juventus napoli milan inter roma lazio italia francesco alessandro
andrea giuseppe marco luca matteo lorenzo martina giulia chiara federica sara anna maria laura paolo giovanni stefano
roberto davide simone valentina elena silvia estate inverno primavera autunno sole luna stella mare casa gatto cane
calcio forza qwerty welcome dragon monkey master shadow summer winter love football baseball soccer hello secret segreto
princess sunshine iloveyou letmein michael jennifer jordan superman batman pokemon""".split()), key=len, reverse=True)


def stima_password(pw: str) -> dict:
    n, problemi = len(pw), []
    pool = 26 * bool(re.search(r"[a-z]", pw)) + 26 * bool(re.search(r"[A-Z]", pw)) + 10 * bool(re.search(r"\d", pw)) \
        + 33 * bool(re.search(r"[^A-Za-z0-9]", pw) and all(ord(c) < 128 for c in pw)) + 100 * any(ord(c) > 127 for c in pw)
    bit = n * math.log2(pool) if pool else 0.0
    low = pw.lower()
    leet = low.translate(str.maketrans("4@3!10$57", "aaeiiosst"))
    parole = [w for w in re.split(r"[\s\-_.,;:+/]+", pw) if w]
    passphrase = len(parole) >= 3 and all(w.isalpha() for w in parole)
    if low in COMUNI or leet in COMUNI or re.sub(r"[\d!.?*#@$]+$", "", low) in COMUNI or re.sub(r"[\d!.?*#@$]+$", "", leet) in COMUNI:
        problemi.append("e' tra le password piu' usate (o una sua variante): si indovina in pochi tentativi")
        bit = min(bit, 12.0)
    elif passphrase:
        # frase di parole: conta le parole, non i caratteri (~11 bit a parola se scelte davvero a caso)
        bit = min(bit, 11.0 * len(parole))
        if len(parole) < 5:
            problemi.append("frase di sole %d parole: per una protezione forte ne servono 5-6 scelte a caso" % len(parole))
        if len(set(w.lower() for w in parole)) < len(parole):
            problemi.append("parole ripetute")
            bit -= 11
    else:
        for w in PAROLE_DIZ:
            if len(w) >= 4 and (w in low or w in leet):
                problemi.append('contiene una parola o un nome comune ("%s")' % w)
                bit -= max(0.0, len(w) * math.log2(max(pool, 26)) - 14)     # una parola vale ~14 bit, non ~5 per lettera
                break
        coda = re.search(r"[\d!?.*#@$&%]*$", low).group(0)
        nucleo = low[:len(low) - len(coda)].translate(str.maketrans("4@3!10$57", "aaeiiosst"))
        vocali = sum(c in "aeiou" for c in nucleo) / max(1, len(nucleo))
        if 5 <= len(nucleo) <= 14 and nucleo.isalpha() and 0.28 <= vocali <= 0.65 \
                and not re.search(r"[^aeiou]{4,}", nucleo) and not problemi:
            problemi.append("sembra una parola pronunciabile (forse di dizionario) con sostituzioni prevedibili "
                            "(a->4, o->0...) e simboli in coda: gli attacchi provano proprio queste varianti")
            bit = min(bit, 28.0 + 4 * len(coda))
        if re.search(r"0123|1234|2345|3456|4567|5678|6789|9876|8765|abcd|qwer|wert|asdf|sdfg|zxcv|azer|uiop", low):
            problemi.append("contiene sequenze da tastiera o numeriche")
            bit -= 10
        if re.search(r"(.)\1\1", pw):
            problemi.append("contiene caratteri ripetuti")
            bit -= 6
        if re.search(r"(19[3-9]\d|20[0-3]\d)", pw):
            problemi.append("contiene un anno (spesso di nascita: facile da indovinare)")
            bit -= 6
        if re.fullmatch(r"[A-Za-z][a-z]+[\d]{1,4}[!.?*]?", pw):
            problemi.append("schema prevedibile: parola + numeri (+ simbolo finale)")
            bit = min(bit, 32.0)
    if n < 12:
        problemi.append("troppo corta: punta ad almeno 14-16 caratteri, oppure 5-6 parole scelte a caso")
    bit = max(0.0, bit)
    giudizio = ("molto debole" if bit < 28 else "debole" if bit < 45 else "discreta" if bit < 60
                else "forte" if bit < 80 else "molto forte")

    def durata(secondi):
        for soglia, nome in ((60, "secondi"), (3600, "minuti"), (86400, "ore"), (31557600, "giorni")):
            if secondi < soglia:
                div = {"secondi": 1, "minuti": 60, "ore": 3600, "giorni": 86400}[nome]
                return "%.0f %s" % (max(secondi / div, 0), nome) if nome != "secondi" else ("meno di un minuto")
        anni = secondi / 31557600
        if anni > 1.4e10:
            return "piu' dell'eta' dell'universo"
        return "%.0f anni" % anni if anni < 1e6 else "%.1e anni" % anni

    tentativi = 2 ** max(bit - 1, 0)
    return {"bit": round(bit, 1), "giudizio": giudizio, "problemi": problemi, "tempi": {
        "online (sito con limite di tentativi, ~10/s)": durata(tentativi / 10),
        "offline, hash veloce rubato (es. MD5, ~10^11/s)": durata(tentativi / 1e11),
        "offline, hash lento (Argon2id/bcrypt, ~10^4/s)": durata(tentativi / 1e4)}}


def avvisa_se_debole(pw: str):
    s = stima_password(pw)
    if s["bit"] < 50:
        print("Attenzione: password %s (~%.0f bit). %s. La cifratura e' robusta quanto la password."
              % (s["giudizio"], s["bit"], "; ".join(s["problemi"]) or "aumenta lunghezza e casualita'"), file=sys.stderr)


# --------------------------------------------------------------------------- comandi
def _dati_input(a) -> bytes:
    if getattr(a, "file", None):
        if os.path.getsize(a.file) > LIMITE_FILE:
            sys.exit("File oltre 512 MB: per file grandi usa 'age' o GnuPG, che cifrano a flusso.")
        return open(a.file, "rb").read()
    if a.testo is not None:
        return a.testo.encode("utf-8")
    return sys.stdin.buffer.read()


def _chiave_arg(valore: str) -> bytes:
    k = da_token(leggi_pubblica_arg(valore), "critk1")
    if len(k) != 32:
        sys.exit("Chiave non valida: servono 32 byte (usa 'cifra.py chiave' per generarne una).")
    return k


def cmd_cifra(a):
    dati = _dati_input(a)
    if a.chiave:
        blob = cifra_simmetrico(dati, chiave=_chiave_arg(a.chiave))
    else:
        pw = leggi_password(a, nuova=True)
        avvisa_se_debole(pw)
        blob = cifra_simmetrico(dati, password=pw, kdf=a.kdf)
    if a.file:
        out = a.out or a.file + ".crit"
        open(out, "wb").write(blob)
        print("Cifrato in %s (%d byte). Senza la password/chiave il contenuto non e' recuperabile." % (out, len(blob)))
    else:
        tok = "crit1." + b64u(blob)
        if a.out:
            open(a.out, "w").write(tok + "\n")
            print("Token cifrato salvato in %s" % a.out)
        else:
            print(tok)


def cmd_decifra(a):
    if a.file:
        raw = open(a.file, "rb").read()
        blob = raw if raw[:4] == MAGIC else da_token(raw.decode("ascii", "ignore"), "crit1")
    else:
        blob = da_token(a.testo if a.testo is not None else sys.stdin.read(), "crit1")
    try:
        if blob[4:5] == bytes([MODO_CHIAVE]):
            if not a.chiave:
                sys.exit("Questo cifrato richiede --chiave.")
            dati = decifra_simmetrico(blob, chiave=_chiave_arg(a.chiave))
        else:
            dati = decifra_simmetrico(blob, password=leggi_password(a))
    except ErroreDecifratura as e:
        sys.exit("ERRORE: %s" % e)
    _scrivi_uscita(a, dati, ".crit")


def _scrivi_uscita(a, dati: bytes, estensione: str):
    if a.out or (a.file and a.file.endswith(estensione)):
        out = a.out or a.file[:-len(estensione)]
        if os.path.exists(out) and not a.out:
            out += ".decifrato"
        open(out, "wb").write(dati)
        print("Decifrato in %s (%d byte). Integrita' verificata." % (out, len(dati)))
    else:
        try:
            print(dati.decode("utf-8"))
        except UnicodeDecodeError:
            sys.exit("Il contenuto e' binario: usa --out per salvarlo su file.")


def cmd_chiave(a):
    print("critk1." + b64u(secrets.token_bytes(32)))
    print("Conservala come una password: chi la possiede legge i dati, e se la perdi i dati sono persi.", file=sys.stderr)


def _scrivi_privato(percorso: str, contenuto: str):
    with open(percorso, "w", encoding="utf-8") as fh:
        fh.write(contenuto + "\n")
    try:
        os.chmod(percorso, 0o600)
    except OSError:
        pass


def cmd_coppia(a):
    if not hpke_disponibile():
        sys.exit("La tua versione di 'cryptography' non supporta ML-KEM/HPKE: aggiornala (pip install -U cryptography) "
                 "oppure usa 'age' (age-keygen) per la cifratura a chiave pubblica.")
    priv, pub, _ = genera_coppia()
    pw = password_opzionale(a)
    contenuto = json.dumps(priv, indent=2)
    if pw:
        avvisa_se_debole(pw)
        contenuto = "crit1." + b64u(cifra_simmetrico(contenuto.encode(), password=pw))
    _scrivi_privato(a.nome + ".privata", contenuto)
    open(a.nome + ".pubblica", "w").write(pub + "\n")
    print("Chiave privata: %s %s" % (a.nome + ".privata", "(protetta da password)" if pw else
                                     "(NON protetta: imposta CRIT_PASSWORD per proteggerla)"))
    print("Chiave pubblica: %s (puoi darla a chiunque)" % (a.nome + ".pubblica"))
    print("KEM ibrido X25519 + ML-KEM-768: resta sicuro se anche uno solo dei due regge (protegge dai futuri computer quantistici).")


def cmd_cifra_per(a):
    if not hpke_disponibile():
        sys.exit("Serve una versione recente di 'cryptography' con HPKE/ML-KEM (pip install -U cryptography).")
    pub = carica_pubblica(leggi_pubblica_arg(a.pubblica))
    blob = cifra_pubblico(_dati_input(a), pub)
    if a.file:
        out = a.out or a.file + ".crith"
        open(out, "wb").write(blob)
        print("Cifrato per il destinatario in %s. Solo la sua chiave privata puo' aprirlo." % out)
    else:
        print("crithp1." + b64u(blob))


def cmd_decifra_con(a):
    priv = carica_privata(leggi_file_chiave_privata(a.privata, a))
    if a.file:
        raw = open(a.file, "rb").read()
        blob = raw if raw[:4] == MAGIC_H else da_token(raw.decode("ascii", "ignore"), "crithp1")
    else:
        blob = da_token(a.testo if a.testo is not None else sys.stdin.read(), "crithp1")
    try:
        dati = decifra_privato(blob, priv)
    except ErroreDecifratura as e:
        sys.exit("ERRORE: %s" % e)
    _scrivi_uscita(a, dati, ".crith")


def cmd_firma_coppia(a):
    k = ed25519.Ed25519PrivateKey.generate()
    pw = password_opzionale(a)
    cifratura = serialization.BestAvailableEncryption(normalizza_password(pw)) if pw else serialization.NoEncryption()
    pem = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, cifratura).decode()
    _scrivi_privato(a.nome + ".firma-privata.pem", pem.strip())
    pub = "critvk1." + b64u(k.public_key().public_bytes_raw())
    open(a.nome + ".firma-pubblica", "w").write(pub + "\n")
    print("Chiave di firma privata: %s %s" % (a.nome + ".firma-privata.pem", "(protetta da password)" if pw else "(NON protetta)"))
    print("Chiave pubblica di verifica: %s\n%s" % (a.nome + ".firma-pubblica", pub))


def cmd_firma(a):
    pem = open(a.privata, "rb").read()
    try:
        k = serialization.load_pem_private_key(pem, password=None)
    except TypeError:
        k = serialization.load_pem_private_key(pem, password=normalizza_password(leggi_password(a)))
    if not isinstance(k, ed25519.Ed25519PrivateKey):
        sys.exit("Chiave non Ed25519.")
    print("critsig1." + b64u(k.sign(_dati_input(a))))


def cmd_verifica(a):
    pub = ed25519.Ed25519PublicKey.from_public_bytes(da_token(leggi_pubblica_arg(a.pubblica), "critvk1"))
    try:
        pub.verify(da_token(a.firma, "critsig1"), _dati_input(a))
        print("FIRMA VALIDA: il contenuto e' integro ed e' stato firmato con la chiave privata corrispondente.")
        return 0
    except InvalidSignature:
        print("FIRMA NON VALIDA: contenuto modificato, firma sbagliata o chiave pubblica diversa.")
        return 1


ALGORITMI = {"sha256": hashlib.sha256, "sha512": hashlib.sha512, "sha384": hashlib.sha384, "sha3-256": hashlib.sha3_256,
             "sha3-512": hashlib.sha3_512, "blake2b": hashlib.blake2b, "sha1": hashlib.sha1, "md5": hashlib.md5}


def cmd_hash(a):
    h = ALGORITMI[a.algoritmo]()
    if a.file:
        with open(a.file, "rb") as fh:
            for blocco in iter(lambda: fh.read(1 << 20), b""):
                h.update(blocco)
    else:
        h.update(_dati_input(a))
    hexd = h.hexdigest()
    print("%s: %s" % (a.algoritmo.upper(), hexd))
    if a.algoritmo in ("md5", "sha1"):
        print("Nota: %s e' rotto contro le collisioni: va bene solo per confrontare checksum legacy, non per sicurezza."
              % a.algoritmo.upper(), file=sys.stderr)
    if a.atteso:
        att = a.atteso.strip()
        if "-" in att and att.split("-", 1)[0] in ALGORITMI:          # formato SRI: sha256-BASE64
            att = base64.b64decode(att.split("-", 1)[1]).hex()
        att = re.sub(r"[\s:]", "", att).lower()
        if hmac.compare_digest(att, hexd):
            print("CORRISPONDE: il file e' identico a quello del valore pubblicato.")
            print("(Vale solo se il valore atteso viene da una fonte affidabile, es. sito ufficiale in HTTPS o firmato.)")
            return 0
        print("NON CORRISPONDE: file diverso (danneggiato, versione diversa o manomesso). Non usarlo.")
        return 1
    return 0


def cmd_casuale(a):
    n = a.lunghezza
    if a.tipo == "password":
        n = n or 20
        alfabeto = string.ascii_letters + string.digits + "!@#$%^&*-_=+?"
        while True:
            pw = "".join(secrets.choice(alfabeto) for _ in range(n))
            if n < 4 or (re.search(r"[a-z]", pw) and re.search(r"[A-Z]", pw) and re.search(r"\d", pw)
                         and re.search(r"[^A-Za-z0-9]", pw)):
                break
        print(pw)
        print("(~%.0f bit di entropia; salvala in un gestore di password)" % (n * math.log2(len(alfabeto))), file=sys.stderr)
    elif a.tipo == "token":
        print(secrets.token_urlsafe(n or 32))
    elif a.tipo == "hex":
        print(secrets.token_hex(n or 32))
    elif a.tipo == "pin":
        print("".join(secrets.choice(string.digits) for _ in range(n or 6)))


def cmd_valuta_password(a):
    pw = leggi_password(a)
    s = stima_password(pw)
    print("Robustezza stimata: %s (~%.0f bit, %d caratteri)" % (s["giudizio"].upper(), s["bit"], len(pw)))
    for p in s["problemi"]:
        print("  - " + p)
    print("Tempo medio per indovinarla:")
    for k, v in s["tempi"].items():
        print("  %s: %s" % (k, v))
    print("Stima euristica: non sa se la password e' gia' finita in un furto di dati (verificalo con servizi come "
          "Have I Been Pwned) e vale solo se la password non e' usata altrove.")


def cmd_autotest(a):
    esiti = []

    def esito(nome, ok, dettaglio=""):
        esiti.append(ok)
        print("[%s] %s%s" % ("OK" if ok else "FALLITO", nome, (" - " + dettaglio) if dettaglio else ""))

    def rifiuta(fn):
        try:
            fn()
            return False
        except (ErroreDecifratura, InvalidSignature):
            return True

    print("Autotest di cifra.py (cryptography %s)\n" % __import__("cryptography").__version__)
    pw = "Autotest-" + secrets.token_hex(6)
    dati = ("Messaggio di prova con accenti: perche', citta', caffe' - 123. " * 30).encode()
    t0 = time.time()
    c1 = cifra_simmetrico(dati, password=pw)
    durata = time.time() - t0
    kdf = "Argon2id 64 MiB" if c1[4] == MODO_ARGON2ID else "scrypt N=2^17"
    esito("cifra/decifra con password (%s + AES-256-GCM)" % kdf, decifra_simmetrico(c1, password=pw) == dati,
          "derivazione della chiave in %.2f s: rallenta chi prova milioni di password" % durata)
    esito("password sbagliata rifiutata", rifiuta(lambda: decifra_simmetrico(c1, password=pw + "x")))
    m = bytearray(c1)
    m[-30] ^= 0x01
    esito("modifica di 1 bit nel cifrato rilevata (autenticazione GCM)", rifiuta(lambda: decifra_simmetrico(bytes(m), password=pw)))
    m = bytearray(c1)
    m[12] ^= 0x01
    esito("modifica dell'intestazione (sale) rilevata", rifiuta(lambda: decifra_simmetrico(bytes(m), password=pw)))
    esito("troncamento rilevato", rifiuta(lambda: decifra_simmetrico(c1[:-1], password=pw)))
    c2 = cifra_simmetrico(dati, password=pw)
    esito("stesso testo cifrato due volte = risultati diversi (sale e nonce casuali)", c1 != c2)
    k = secrets.token_bytes(32)
    zeri = bytes(64 * 1024)
    cz = cifra_simmetrico(zeri, chiave=k)
    corpo = cz[17:-16]
    blocchi = [corpo[i:i + 16] for i in range(0, len(corpo), 16)]
    dup_gcm = len(blocchi) - len(set(blocchi))
    esito("64 KiB di zeri -> cifrato indistinguibile dal caso (entropia %.3f bit/byte, %d blocchi ripetuti)"
          % (entropia(corpo), dup_gcm), entropia(corpo) > 7.99 and dup_gcm == 0)
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    ecb = Cipher(algorithms.AES(k), modes.ECB()).encryptor().update(zeri)
    b_ecb = [ecb[i:i + 16] for i in range(0, len(ecb), 16)]
    esito("controprova: AES in modalita' ECB (da NON usare) ripete %d blocchi su %d" % (len(b_ecb) - len(set(b_ecb)), len(b_ecb)),
          len(set(b_ecb)) == 1)
    esito("cifra/decifra con chiave a 256 bit", decifra_simmetrico(cz, chiave=k) == zeri)
    esito("chiave sbagliata rifiutata", rifiuta(lambda: decifra_simmetrico(cz, chiave=secrets.token_bytes(32))))
    tok = "crit1." + b64u(c1)
    esito("formato testuale crit1 reversibile", decifra_simmetrico(da_token(tok, "crit1"), password=pw) == dati)
    if hpke_disponibile():
        priv_json, pub_txt, priv = genera_coppia()
        pub = carica_pubblica(pub_txt)
        ch = cifra_pubblico(b"segreto per il destinatario", pub)
        esito("HPKE ibrido X25519 + ML-KEM-768: cifra per chiave pubblica, apre solo la privata",
              decifra_privato(ch, carica_privata(priv_json)) == b"segreto per il destinatario")
        _, _, altra = genera_coppia()
        esito("HPKE: un'altra chiave privata viene rifiutata", rifiuta(lambda: decifra_privato(ch, altra)))
        mh = bytearray(ch)
        mh[-5] ^= 0x01
        esito("HPKE: manomissione rilevata", rifiuta(lambda: decifra_privato(bytes(mh), priv)))
    else:
        print("[--] HPKE/ML-KEM non disponibile in questa versione di cryptography (aggiornala per la cifratura a chiave pubblica)")
    sk = ed25519.Ed25519PrivateKey.generate()
    msg = b"Bonifico di 100 euro a Mario Rossi"
    firma = sk.sign(msg)
    esito("firma Ed25519 verificata", not rifiuta(lambda: sk.public_key().verify(firma, msg)))
    esito("firma Ed25519 rifiutata se il messaggio cambia di una cifra",
          rifiuta(lambda: sk.public_key().verify(firma, b"Bonifico di 900 euro a Mario Rossi")))
    esito("SHA-256 conforme al vettore di prova ufficiale ('abc')", hashlib.sha256(b"abc").hexdigest() ==
          "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    tot, ok = len(esiti), sum(esiti)
    print("\n%d/%d controlli superati. %s" % (ok, tot, "La cifratura si comporta come deve." if ok == tot else
                                            "ATTENZIONE: qualcosa non va, non usare lo script finche' non e' chiarito."))
    return 0 if ok == tot else 1


def main():
    ap = argparse.ArgumentParser(description="Cifratura, firme e hash con impostazioni sicure.")
    sub = ap.add_subparsers(dest="comando", required=True)

    def ingresso(p, testo=True):
        g = p.add_mutually_exclusive_group()
        if testo:
            g.add_argument("--testo")
        g.add_argument("--file")
        p.add_argument("--out")

    def pw(p):
        p.add_argument("--password", help="sconsigliato: resta nella cronologia")
        p.add_argument("--password-stdin", action="store_true")

    p = sub.add_parser("cifra"); ingresso(p); pw(p); p.add_argument("--chiave"); p.add_argument("--kdf", default="argon2id", choices=["argon2id", "scrypt"])
    p = sub.add_parser("decifra"); ingresso(p); pw(p); p.add_argument("--chiave")
    sub.add_parser("chiave")
    p = sub.add_parser("coppia"); p.add_argument("--nome", required=True); pw(p)
    p = sub.add_parser("cifra-per"); ingresso(p); p.add_argument("--pubblica", required=True)
    p = sub.add_parser("decifra-con"); ingresso(p); pw(p); p.add_argument("--privata", required=True)
    p = sub.add_parser("firma-coppia"); p.add_argument("--nome", required=True); pw(p)
    p = sub.add_parser("firma"); ingresso(p); pw(p); p.add_argument("--privata", required=True)
    p = sub.add_parser("verifica"); ingresso(p); p.add_argument("--pubblica", required=True); p.add_argument("--firma", required=True)
    p = sub.add_parser("hash"); ingresso(p); p.add_argument("--algoritmo", default="sha256", choices=sorted(ALGORITMI)); p.add_argument("--atteso")
    p = sub.add_parser("casuale"); p.add_argument("--tipo", default="password", choices=["password", "token", "hex", "pin"]); p.add_argument("--lunghezza", type=int)
    p = sub.add_parser("valuta-password"); pw(p)
    sub.add_parser("autotest")
    a = ap.parse_args()
    try:
        signal_pipe()
    except Exception:
        pass
    comandi = {"cifra": cmd_cifra, "decifra": cmd_decifra, "chiave": cmd_chiave, "coppia": cmd_coppia,
               "cifra-per": cmd_cifra_per, "decifra-con": cmd_decifra_con, "firma-coppia": cmd_firma_coppia,
               "firma": cmd_firma, "verifica": cmd_verifica, "hash": cmd_hash, "casuale": cmd_casuale,
               "valuta-password": cmd_valuta_password, "autotest": cmd_autotest}
    try:
        return comandi[a.comando](a) or 0
    except ErroreDecifratura as e:
        print("ERRORE: %s" % e, file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print("ERRORE: %s" % e, file=sys.stderr)
        return 2


def signal_pipe():
    """Uscita silenziosa se l'output viene troncato (es. | head)."""
    import signal
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == "__main__":
    sys.exit(main())
