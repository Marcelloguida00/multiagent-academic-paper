# Decodifica e riconoscimento dei formati

## Indice
1. Strategia
2. Riconoscere una codifica
3. Prefissi base64 rivelatori
4. Firme dei file (magic number)
5. Hash e formati delle password
6. Token e credenziali
7. Chiavi, certificati e contenitori cifrati
8. Tecniche di offuscamento nel codice malevolo
9. Falsi positivi e trappole

---

## 1. Strategia

1. **Mai eseguire**: si decodifica e si legge, basta. Niente browser, niente interprete, niente apertura di allegati.
2. **A strati**: togli una codifica alla volta (es. URL encoding, poi base64, poi gzip) finché ottieni testo leggibile, un formato noto o dati opachi. `scripts/analizza.py` lo fa in automatico e prova anche XOR a un byte, ROT13, Morse e altro.
3. **Cerca anche dentro**: un testo leggibile può contenere blob codificati (un comando dopo `-enc`, una stringa dentro `atob("...")`, un `data:` URI). L'analizzatore li estrae e li decodifica a parte.
4. **Estrai gli indicatori**: URL, domini, IP, indirizzi email, nomi di file, indirizzi di criptovaluta.
5. **Giudica**: protezione (nessuna, debole, robusta) e rischio del contenuto. Vedi `valutazione-affidabilita.md`.

Strumenti esterni utili per chi vuole approfondire: CyberChef (anche in locale, offline), dCode.fr per i cifrari classici.

## 2. Riconoscere una codifica

| Codifica | Alfabeto e indizi | Esempio | Dove si trova |
|---|---|---|---|
| Base64 | A–Z a–z 0–9 + / e `=` finali; lunghezza multipla di 4; a capo ogni 64 o 76 caratteri | `Q2lhbw==` = "Ciao" | email, allegati, script, configurazioni |
| Base64url | come base64 ma `-` e `_` al posto di `+` e `/`, spesso senza `=` | `eyJhbGciOi...` | JWT, URL, cookie |
| Base32 | A–Z e 2–7, `=` finali; lunghezza multipla di 8 | `KNSWG4TFOQ======` = "Secret" | segreti TOTP delle app di autenticazione, indirizzi .onion |
| Base58 | niente 0, O, I, l | `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` | indirizzi Bitcoin, IPFS (`Qm...`) |
| Base85 / Ascii85 | `<~ ... ~>` oppure caratteri come `!#$%&` | `<~6YTtI~>` = "Ciao" | PDF, patch di git |
| Esadecimale | 0–9 a–f, lunghezza pari; varianti `0x41`, `\x41`, `41:42` | `4369616f` = "Ciao" | dump, malware, hash |
| Binario | gruppi di 8 cifre 0/1 | `01000011` = "C" | enigmi, didattica |
| Codici decimali | numeri 0–255 separati | `67 105 97 111` | `String.fromCharCode`, `Chr()` |
| URL encoding | `%20`, `%2F`; `+` per lo spazio nei moduli | `https%3A%2F%2F` | link nelle email e negli SMS |
| Entità HTML | `&#67;`, `&#x43;`, `&amp;` | `&#67;&#105;&#97;&#111;` | pagine di phishing |
| Escape | `\x41`, `\u00e8`, `\101` | `\x68\x74\x74\x70` = "http" | JavaScript, Python, C |
| Quoted-printable | `=C3=A8`, `=20`, `=` a fine riga | `perch=C3=A9` | sorgente delle email |
| UTF-16LE | un byte nullo ogni due | `I\0E\0X\0` | PowerShell `-EncodedCommand` |
| Punycode | `xn--` nei domini | `xn--pypal-4ve.com` | domini internazionalizzati (anche falsi) |
| Morse | punti, linee, `/` tra le parole | `... --- ...` | enigmi |
| ROT13 / ROT47 | forma delle parole conservata ma illeggibile; ROT47 cambia anche simboli e cifre | `Pvnb` = "Ciao" | forum, offuscamento leggero |

## 3. Prefissi base64 rivelatori

L'inizio di una stringa base64 spesso tradisce il contenuto prima ancora di decodificarlo:

| Inizio | Contenuto decodificato |
|---|---|
| `eyJ` | `{"` cioè JSON; un JWT comincia con `eyJhbGci` (`{"alg`) |
| `H4sI` | dati compressi gzip |
| `UEsDB` | archivio ZIP (anche docx, xlsx, pptx, jar, apk) |
| `JVBERi0` | documento PDF (`%PDF-`) |
| `TVqQ` | eseguibile Windows (`MZ`): massima attenzione |
| `f0VMR` | eseguibile Linux (ELF) |
| `iVBORw0KGgo` | immagine PNG |
| `/9j/` | immagine JPEG |
| `R0lGOD` | immagine GIF |
| `PD94bWwg` | `<?xml ` |
| `PGh0bWw` / `PHNjcmlwdD` | `<html` / `<script` |
| `aHR0cDovL` / `aHR0cHM6Ly` | `http://` / `https://` |
| `cG93ZXJzaGVsbC` | `powershell` |
| `SQBFAFgA` | `IEX` in UTF-16LE (comando PowerShell) |
| `IyEvYmluL` | `#!/bin/` (script Unix) |
| `LS0tLS1CRUdJTi` | `-----BEGIN` (blocco PEM) |
| `MII` | struttura DER/ASN.1 (certificati, chiavi) |
| `AAAAB3NzaC1yc2E` / `AAAAC3NzaC1lZDI1NTE5` | chiave pubblica SSH RSA / Ed25519 |
| `U2FsdGVkX1` | `Salted__`: cifrato con `openssl enc` |
| `gAAAAA` | token Fernet (cifrato) |

## 4. Firme dei file (magic number)

| Byte iniziali (esadecimale) | Tipo |
|---|---|
| `4D 5A` ("MZ") | eseguibile Windows (EXE, DLL) |
| `7F 45 4C 46` | eseguibile Linux (ELF) |
| `CF FA ED FE`, `CA FE BA BE` | eseguibile macOS / classe Java |
| `4C 00 00 00 01 14 02 00` | collegamento Windows (LNK) |
| `50 4B 03 04` ("PK") | ZIP e formati Office moderni |
| `D0 CF 11 E0 A1 B1 1A E1` | Office vecchio formato, MSI |
| `25 50 44 46` ("%PDF") | PDF |
| `7B 5C 72 74 66` ("{\rtf") | RTF |
| `1F 8B` | gzip |
| `78 9C`, `78 DA`, `78 01` | zlib |
| `42 5A 68` ("BZh") | bzip2 |
| `FD 37 7A 58 5A 00` | xz |
| `37 7A BC AF 27 1C` | 7z |
| `52 61 72 21 1A 07` | RAR |
| `89 50 4E 47` | PNG |
| `FF D8 FF` | JPEG |
| `53 61 6C 74 65 64 5F 5F` ("Salted__") | cifrato OpenSSL |
| "age-encryption.org/v1" | cifrato age |
| `4C 55 4B 53 BA BE` | volume LUKS |
| "-FVE-FS-" (dal byte 3) | volume BitLocker |
| "CD001" (all'offset 0x8001) | immagine disco ISO |

Un file che dichiara un'estensione ma ha la firma di un'altra (una "fattura.pdf" che inizia con `MZ`) è un segnale fortissimo di inganno.

## 5. Hash e formati delle password

**Impronte esadecimali**, riconoscibili dalla lunghezza:

| Caratteri esadecimali | Bit | Candidati |
|---|---|---|
| 32 | 128 | MD5, NTLM, MD4 |
| 40 | 160 | SHA-1, RIPEMD-160 |
| 56 | 224 | SHA-224, SHA3-224 |
| 64 | 256 | SHA-256, SHA3-256, BLAKE2s, BLAKE3 |
| 96 | 384 | SHA-384, SHA3-384 |
| 128 | 512 | SHA-512, SHA3-512, BLAKE2b |

La stessa lunghezza può essere anche una chiave o un token casuale in esadecimale.

**Formati delle password memorizzate**:

| Formato | Algoritmo | Giudizio |
|---|---|---|
| `$argon2id$v=19$m=...,t=...,p=...$sale$hash` | Argon2id | ottimo (controlla m e t) |
| `$y$...` | yescrypt (Linux moderni) | ottimo |
| `$2b$12$...` | bcrypt (il numero è il costo) | buono se costo almeno 10 |
| `$scrypt$...`, `$7$...` | scrypt | buono |
| `pbkdf2_sha256$600000$...` | PBKDF2 (Django) | buono con molte iterazioni |
| `$6$...` / `$5$...` | sha512crypt / sha256crypt | datato ma accettabile |
| `$1$...`, `$apr1$...` | md5crypt | debole |
| `$P$...`, `$H$...` | phpass (WordPress) | datato |
| `{SSHA}...`, `{SHA}...`, `{MD5}...` | LDAP con hash veloci | debole |
| `*` + 40 esadecimali | MySQL 4.1+ | debole |

**Un hash non si "decifra"**: non contiene il dato. Si può solo provare a indovinare l'input e confrontare. Va bene per verificare un checksum o la robustezza delle *proprie* password; tentare di risalire alle password di altri non è un'attività che si supporta.

## 6. Token e credenziali

- **JWT** (`xxxxx.yyyyy.zzzzz`, tre parti base64url): header (algoritmo), payload (dati: `sub`, `exp`, `iat`, `iss`, `aud`...), firma. Header e payload sono **leggibili da chiunque**: la firma impedisce di modificarli solo se il server la verifica. Campanelli d'allarme: `alg: none`, assenza di `exp`, dati sensibili nel payload, segreti HS256 corti.
- **JWE** (cinque parti): token davvero cifrato.
- **PASETO** (`v4.local.` cifrato, `v4.public.` firmato e leggibile).
- **Fernet** (`gAAAAA...`): cifrato e autenticato; la data di creazione è leggibile.
- **Authorization: Basic ...**: è `utente:password` in base64, quindi **in chiaro**.
- **Cookie di sessione**: in molti framework (es. Flask) sono JSON in base64 più una firma: leggibili, non modificabili.
- **Secret di Kubernetes**: valori in base64, cioè non cifrati, salvo cifratura a riposo configurata a parte.
- **Chiavi API con prefisso riconoscibile**: `AKIA...` (AWS), `ghp_...` (GitHub), `xoxb-...` (Slack), `sk_live_...` (Stripe), `AIza...` (Google), `sk-...` (vari servizi di IA). Se esposte vanno revocate e rigenerate: cancellarle dal messaggio o dal repository non basta.
- **Segreti TOTP** (base32, spesso dentro un QR `otpauth://`): chi li ha genera i codici a 6 cifre. Sono segreti a tutti gli effetti.

## 7. Chiavi, certificati e contenitori cifrati

- **PEM** (`-----BEGIN ...-----`): CERTIFICATE (pubblico), PUBLIC KEY (pubblica), PRIVATE KEY o RSA/EC PRIVATE KEY (segreto in chiaro!), ENCRYPTED PRIVATE KEY (protetta da password), CERTIFICATE REQUEST (pubblica).
- **DER**: la stessa struttura in binario (spesso inizia con `30 82`, in base64 `MII`).
- **PKCS#12** (`.p12`, `.pfx`): contenitore di certificato e chiave privata protetto da password.
- **SSH**: chiavi pubbliche `ssh-ed25519 AAAA...`; private in `-----BEGIN OPENSSH PRIVATE KEY-----`. Le chiavi `ssh-dss` (DSA) sono obsolete.
- **PGP**: `-----BEGIN PGP MESSAGE-----` (cifrato), `PGP SIGNATURE`, `PGP PUBLIC KEY BLOCK`, `PGP PRIVATE KEY BLOCK` (segreto).
- **Formati cifrati riconoscibili**: age, OpenSSL `Salted__` (senza `-pbkdf2` derivazione debole e nessuna autenticazione), ZIP (ZipCrypto debole; AES-256 robusto), 7z con AES-256 (robusto se la password lo è), PDF (RC4 a 40 bit nei file vecchi = debole; AES-256 = robusto), Office moderno (robusto con password forte), BitLocker e LUKS (intestazioni riconoscibili), VeraCrypt (indistinguibile da dati casuali, nessuna intestazione), `crit1.` e `crithp1.` di `cifra.py`.
- Quando la cifratura è robusta, la vera domanda diventa: **quanto è forte la password e chi possiede le chiavi?**

## 8. Tecniche di offuscamento nel codice malevolo

Riconoscerle aiuta a capire che cosa si ha davanti; lo scopo è smontarle per leggerle, mai per riusarle.

- **PowerShell**: `-EncodedCommand` (base64 di testo UTF-16LE), array di `[char]` uniti con `-join`, accenti gravi dentro le parole (`I`E`X`), stringhe invertite, `-bxor`, `IEX` / `Invoke-Expression`, finestre nascoste (`-w hidden`), `DownloadString`.
- **JavaScript**: `eval(atob("..."))`, `unescape("%u...")`, `String.fromCharCode(...)`, escape `\x..`, nomi come `_0x1a2b` (offuscatori automatici), JSFuck (solo `[]()!+`).
- **VBA (macro Office)**: `AutoOpen`, `Document_Open`, `Workbook_Open`, `Chr()`, `StrReverse`, `Shell`, `CreateObject("WScript.Shell")`.
- **Shell Unix**: `echo ... | base64 -d | sh`, `curl ... | bash`, `$'\x..'`.
- **Python**: `exec(base64.b64decode(...))`, `marshal.loads`, `zlib.decompress`.
- **Pagine di phishing**: HTML intero dentro un `data:` URI, pagine in base64 ricostruite da JavaScript, reindirizzamenti automatici, moduli che inviano le credenziali a un altro dominio.
- **HTML smuggling**: un allegato HTML che, aperto, ricostruisce e scarica un file (spesso ZIP o ISO) da dati incorporati.
- **"Falso CAPTCHA" (ClickFix)**: una pagina chiede di premere Win+R o aprire il Terminale e incollare un comando "di verifica". Il comando è quasi sempre PowerShell o shell offuscata che scarica malware. Nessun CAPTCHA vero lo chiede.

## 9. Falsi positivi e trappole

- Molte stringhe alfanumeriche qualsiasi sono base64 o base58 "valide": decodificano in spazzatura. Conta solo un risultato leggibile o un formato riconoscibile.
- Un hash in esadecimale sembra dati codificati: decodificato dà byte casuali. Si riconosce dalla lunghezza.
- Alta entropia non significa cifratura: anche compressione, immagini e chiavi casuali hanno entropia alta.
- L'indice di coincidenza su testi brevi (meno di 100-150 lettere) è poco affidabile.
- Un testo leggibile senza segnali non è per forza innocuo: conta anche il contesto (chi lo manda, cosa chiede).
- Un dominio "pulito" può ospitare contenuti malevoli (servizi di file sharing, siti compromessi); un link accorciato nasconde la destinazione.
