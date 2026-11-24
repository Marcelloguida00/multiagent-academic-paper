# Implementazione sicura

## Indice
1. Regole d'oro
2. Python
3. JavaScript (browser e Node.js)
4. Go
5. Java
6. C# / .NET
7. PHP
8. Riga di comando
9. Errori comuni e correzioni
10. Checklist per rivedere codice crittografico

---

## 1. Regole d'oro

1. **Usa librerie di alto livello e ben mantenute** (libsodium, Tink, `cryptography` per Python, WebCrypto, le librerie standard di Go e .NET). Non implementare AES, RSA o curve ellittiche da zero.
2. **Cifra sempre con un AEAD** (AES-GCM, ChaCha20-Poly1305): confidenzialità e integrità insieme.
3. **Nonce unici, chiavi casuali**: nonce mai ripetuti con la stessa chiave; chiavi e nonce dal CSPRNG del sistema.
4. **Le password non sono chiavi**: trasformale con Argon2id o scrypt (o PBKDF2 con molte iterazioni) e un sale casuale.
5. **Le password degli utenti non si cifrano**: si conservano con un hash lento e con sale, così nemmeno tu puoi recuperarle.
6. **Confronti a tempo costante** per MAC, token e hash (`hmac.compare_digest`, `crypto.timingSafeEqual`, `hash_equals`).
7. **Niente segreti nel codice o nel repository**: variabili d'ambiente, gestori di segreti, KMS o HSM; ruota le chiavi.
8. **Una chiave, uno scopo**: chiavi distinte per cifrare, autenticare e firmare; derivale con HKDF usando contesti diversi.
9. **Gestisci gli errori di autenticazione come attacchi**: se la decifratura fallisce, scarta tutto; non usare dati parziali e non rivelare il motivo esatto all'esterno.
10. **Verifica sempre TLS e le firme**: mai disattivare la verifica dei certificati, nemmeno "solo per ora".

## 2. Python

Libreria `cryptography` (`pip install cryptography`).

**Cifratura autenticata con chiave casuale (AES-256-GCM)**
```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

chiave = AESGCM.generate_key(bit_length=256)   # 32 byte casuali: conservala in modo sicuro
aead = AESGCM(chiave)
aad = b"intestazione-v1"                       # facoltativo: autenticato ma non cifrato
nonce = os.urandom(12)                         # unico per ogni cifratura con questa chiave
messaggio = nonce + aead.encrypt(nonce, b"dati segreti", aad)   # il nonce non e' segreto

# decifratura: solleva cryptography.exceptions.InvalidTag se qualcosa e' stato alterato
chiaro = aead.decrypt(messaggio[:12], messaggio[12:], aad)
```

**Chiave derivata da una password**
```python
import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id   # disponibile nelle versioni recenti

sale = os.urandom(16)
chiave = Argon2id(salt=sale, length=32, iterations=3, lanes=4, memory_cost=64 * 1024).derive(
    "password scelta dall'utente".encode("utf-8"))
# Salva sale e parametri insieme al cifrato. Con versioni vecchie della libreria:
# from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
# chiave = Scrypt(salt=sale, length=32, n=2**17, r=8, p=1).derive(password_bytes)
```

**Conservare le password degli utenti**
```python
from argon2 import PasswordHasher, exceptions   # pip install argon2-cffi

ph = PasswordHasher()                  # Argon2id con parametri sicuri predefiniti
h = ph.hash("password dell'utente")    # salva solo h: contiene algoritmo, parametri e sale
try:
    ph.verify(h, "tentativo")
except exceptions.VerifyMismatchError:
    print("password errata")
if ph.check_needs_rehash(h):           # al login riuscito, aggiorna se i parametri sono cambiati
    h = ph.hash("password dell'utente")
```

**Messaggi autenticati (HMAC) e token casuali**
```python
import hashlib, hmac, secrets

chiave_mac = secrets.token_bytes(32)
tag = hmac.new(chiave_mac, b"importo=100&a=mario", hashlib.sha256).digest()
valido = hmac.compare_digest(tag, tag)             # confronto a tempo costante
token_sessione = secrets.token_urlsafe(32)        # mai random.random() per i segreti
```

**Firme Ed25519**
```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sk = Ed25519PrivateKey.generate()
firma = sk.sign(b"documento")
sk.public_key().verify(firma, b"documento")       # solleva InvalidSignature se non valida
```

**Scambio di chiavi X25519 + HKDF**
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
segreto = a.exchange(b.public_key())              # identico per entrambe le parti
chiave = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"app v1 cifratura").derive(segreto)
# Mai usare il segreto grezzo come chiave; e autentica le chiavi pubbliche, altrimenti
# un intermediario puo' sostituirle (attacco man-in-the-middle).
```

**Cifratura a chiave pubblica ibrida post-quantum (HPKE con X25519 + ML-KEM-768)**
```python
from cryptography.hazmat.primitives import hpke
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519

priv = hpke.MLKEM768X25519PrivateKey(mlkem.MLKEM768PrivateKey.generate(), x25519.X25519PrivateKey.generate())
suite = hpke.Suite(hpke.KEM.MLKEM768_X25519, hpke.KDF.HKDF_SHA256, hpke.AEAD.AES_256_GCM)
cifrato = suite.encrypt(b"segreto", priv.public_key(), info=b"app v1")
chiaro = suite.decrypt(cifrato, priv, info=b"app v1")
```
API recente: verifica che la versione installata la offra (`hpke` e `mlkem` sono presenti nelle versioni 2026 della libreria). Altrimenti usa HPKE classico o lo strumento `age`.

**Soluzione rapida per chi non vuole scegliere nulla**: `cryptography.fernet.Fernet` (AES-128-CBC con HMAC-SHA256, IV casuale, formato versionato) è sicura e semplice per piccoli dati.

## 3. JavaScript (browser e Node.js)

**Browser: WebCrypto con password (PBKDF2 + AES-GCM)**
```js
const enc = new TextEncoder();

async function chiaveDaPassword(password, sale) {
  const base = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "PBKDF2", salt: sale, iterations: 600000, hash: "SHA-256" },
    base, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
}

async function cifra(password, testo) {
  const sale = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const chiave = await chiaveDaPassword(password, sale);
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, chiave, enc.encode(testo)));
  return { sale, iv, ct };            // salva tutti e tre; il tag GCM e' in coda a ct
}

async function decifra(password, { sale, iv, ct }) {
  const chiave = await chiaveDaPassword(password, sale);
  const pt = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, chiave, ct);   // errore se alterato
  return new TextDecoder().decode(pt);
}
```
WebCrypto non offre Argon2: per le password usa PBKDF2 con almeno 600.000 iterazioni oppure una libreria affidabile (libsodium.js). La crittografia nel browser protegge solo se il codice servito è affidabile.

**Node.js: AES-256-GCM**
```js
const crypto = require("node:crypto");

const chiave = crypto.randomBytes(32);
const iv = crypto.randomBytes(12);
const c = crypto.createCipheriv("aes-256-gcm", chiave, iv);
const ct = Buffer.concat([c.update("dati segreti", "utf8"), c.final()]);
const tag = c.getAuthTag();                       // salva iv, ct e tag

const d = crypto.createDecipheriv("aes-256-gcm", chiave, iv);
d.setAuthTag(tag);
const chiaro = Buffer.concat([d.update(ct), d.final()]).toString("utf8");   // final() lancia se alterato
```
Chiave da password con scrypt: `crypto.scryptSync(password, sale, 32, { N: 2 ** 17, r: 8, p: 1, maxmem: 256 * 1024 * 1024 })` (serve alzare `maxmem`, perché questi parametri richiedono 128 MiB). Confronti: `crypto.timingSafeEqual(a, b)` con buffer della stessa lunghezza. Token: `crypto.randomBytes(32).toString("base64url")`.

## 4. Go

```go
import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"golang.org/x/crypto/argon2"
)

func cifra(chiave, chiaro, aad []byte) ([]byte, error) {   // chiave: 32 byte
	blocco, err := aes.NewCipher(chiave)
	if err != nil {
		return nil, err
	}
	gcm, err := cipher.NewGCM(blocco)
	if err != nil {
		return nil, err
	}
	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return nil, err
	}
	return gcm.Seal(nonce, nonce, chiaro, aad), nil         // nonce in testa al cifrato
}

func decifra(chiave, msg, aad []byte) ([]byte, error) {
	blocco, _ := aes.NewCipher(chiave)
	gcm, _ := cipher.NewGCM(blocco)
	n := gcm.NonceSize()
	return gcm.Open(nil, msg[:n], msg[n:], aad)             // errore se alterato
}

// chiave da password: tempo 3, memoria 64 MiB, 4 thread, 32 byte
// chiave := argon2.IDKey([]byte(password), sale, 3, 64*1024, 4, 32)
```
Da Go 1.24 la libreria standard include `crypto/mlkem` e usa lo scambio ibrido post-quantum in TLS.

## 5. Java

```java
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;
import java.security.SecureRandom;

KeyGenerator kg = KeyGenerator.getInstance("AES");
kg.init(256);
SecretKey chiave = kg.generateKey();

byte[] iv = new byte[12];
new SecureRandom().nextBytes(iv);
Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
c.init(Cipher.ENCRYPT_MODE, chiave, new GCMParameterSpec(128, iv));
c.updateAAD(aad);
byte[] cifrato = c.doFinal(chiaro);              // salva iv + cifrato (il tag e' in coda)
```
Attenzione: `Cipher.getInstance("AES")` da solo in molti provider significa AES/ECB/PKCS5Padding, cioè ECB. Specifica sempre modalità e padding. Da Java 24 sono disponibili ML-KEM e ML-DSA.

## 6. C# / .NET

```csharp
using System.Security.Cryptography;

byte[] chiave = RandomNumberGenerator.GetBytes(32);
byte[] nonce = RandomNumberGenerator.GetBytes(12);
byte[] cifrato = new byte[chiaro.Length];
byte[] tag = new byte[16];
using (var aes = new AesGcm(chiave, 16))          // .NET 8+: dimensione del tag esplicita
{
    aes.Encrypt(nonce, chiaro, cifrato, tag, aad);
}
// Decrypt(nonce, cifrato, tag, destinazione, aad) lancia un'eccezione se i dati sono alterati.
// Password: Rfc2898DeriveBytes.Pbkdf2(password, sale, 600000, HashAlgorithmName.SHA256, 32)
// Confronti: CryptographicOperations.FixedTimeEquals(a, b)
```

## 7. PHP

```php
// cifratura autenticata con libsodium (inclusa in PHP)
$chiave = sodium_crypto_aead_xchacha20poly1305_ietf_keygen();
$nonce = random_bytes(SODIUM_CRYPTO_AEAD_XCHACHA20POLY1305_IETF_NPUBBYTES);
$cifrato = sodium_crypto_aead_xchacha20poly1305_ietf_encrypt($messaggio, $aad, $nonce, $chiave);
$chiaro = sodium_crypto_aead_xchacha20poly1305_ietf_decrypt($cifrato, $aad, $nonce, $chiave); // false se alterato

// password degli utenti
$hash = password_hash($password, PASSWORD_ARGON2ID);
if (password_verify($tentativo, $hash)) { /* ok */ }
if (password_needs_rehash($hash, PASSWORD_ARGON2ID)) { /* ricalcola al login */ }
// confronti: hash_equals($atteso, $ricevuto)
```

## 8. Riga di comando

- **age** (consigliato per i file):
  `age-keygen -o chiave.txt` (stampa la chiave pubblica `age1...`), `age -r age1... -o file.age file`, `age -d -i chiave.txt -o file file.age`; con passphrase: `age -p -o file.age file`.
- **GnuPG**: `gpg --symmetric --cipher-algo AES256 file` (crea `file.gpg`), `gpg --decrypt file.gpg > file`; verificare una firma: `gpg --verify file.sig file`, dopo aver controllato l'impronta della chiave con `gpg --fingerprint`.
- **OpenSSL**: `openssl enc` non supporta le modalità autenticate; se proprio serve: `openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -in file -out file.enc` (senza `-pbkdf2` la password diventa chiave con un solo passaggio di MD5). Meglio age.
  Certificati: `openssl x509 -in cert.pem -noout -text`; certificato di un sito: `openssl s_client -connect sito.it:443 -servername sito.it </dev/null | openssl x509 -noout -subject -issuer -dates`.
- **Hash di un file**: Linux `sha256sum file`; macOS `shasum -a 256 file`; Windows PowerShell `Get-FileHash file -Algorithm SHA256`; Windows cmd `certutil -hashfile file SHA256`.
- **SSH**: `ssh-keygen -t ed25519 -C "commento"`; impronta: `ssh-keygen -lf chiave.pub`.
- **minisign**: `minisign -Vm file -P <chiave pubblica>`.

## 9. Errori comuni e correzioni

| Errore | Perché è grave | Correzione |
|---|---|---|
| Modalità ECB | Blocchi uguali, cifrati uguali: gli schemi del testo si vedono | AES-GCM o ChaCha20-Poly1305 |
| IV o nonce fisso, o riusato | Con GCM/CTR rivela lo XOR dei testi e permette di falsificare; con CBC rivela prefissi uguali | Nonce casuale (o contatore) unico per ogni cifratura |
| Cifrare senza autenticare | Bit flipping, attacchi padding oracle | AEAD, oppure encrypt-then-MAC con chiavi separate |
| Chiave = hash veloce della password | Milioni di tentativi al secondo | Argon2id, scrypt o PBKDF2 con sale |
| Password utenti cifrate o in MD5/SHA-1/SHA-256 semplice | Un furto del database le espone tutte | Argon2id con sale (password_hash, argon2-cffi) |
| MD5 o SHA-1 per firme e integrità | Collisioni pratiche | SHA-256 o superiori |
| `Math.random()`, `random`, `rand()` per segreti | Prevedibili | CSPRNG del sistema |
| `==` per confrontare MAC o token | Attacco temporale | Confronto a tempo costante |
| Chiavi nel codice o nel repository | Chiunque legga il codice legge i dati | Gestore di segreti o KMS; rotazione |
| Stessa chiave per scopi diversi | Un errore in un uso compromette gli altri | Chiavi separate, derivate con HKDF |
| RSA senza padding o con PKCS#1 v1.5 per cifrare | Attacchi noti (Bleichenbacher) | OAEP, o meglio HPKE |
| JWT accettati con `alg: none`, firma non verificata, segreto HS256 debole | Token falsificabili | Algoritmi fissati lato server, segreto lungo e casuale o firme asimmetriche |
| Verifica TLS disattivata (`verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true`) | Intercettazione banale | Lasciare la verifica attiva; aggiungere la CA interna se serve |
| Poche iterazioni o memoria nella KDF | Attacchi a dizionario rapidi | Parametri OWASP o superiori |
| Sale assente, fisso o globale | Tabelle precalcolate, password uguali riconoscibili | Sale casuale per ogni password |
| Segreti nei log o nei messaggi d'errore | Fughe di dati silenziose | Mascherare sempre |
| Tag di autenticazione troncato o ignorato | Falsificazione più facile | Tag completo, errore se non valido |
| Chiamare "cifratura" base64 o XOR | Nessuna protezione reale | Cifratura vera con AEAD |

## 10. Checklist per rivedere codice crittografico

Cerca questi schemi (con grep o leggendo il codice) e, per ognuno trovato, indica gravità, motivo e correzione:

- Modalità e algoritmi: `MODE_ECB`, `AES/ECB`, `Cipher.getInstance("AES")`, `DES`, `3DES`, `RC4`, `Blowfish`, `md5(`, `sha1(`.
- Nonce e IV: valori costanti (`b"\x00" * 16`, `"1234567890123456"`), IV derivato dalla chiave, contatori che si azzerano.
- Casualità: `Math.random`, `random.random`, `random.randint`, `rand()`, `new Random(`, semi basati sull'ora.
- Password: hash veloci, `pbkdf2` con poche iterazioni (`iterations=1000`), assenza di sale, cifratura reversibile delle password.
- Confronti: `==` o `equals` su MAC, firme, token, hash.
- Segreti: chiavi o password scritte nel codice (`SECRET_KEY = "..."`, `key = b"..."`), file `.env` nel repository, segreti nei log.
- TLS e firme: `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify`, `CERT_NONE`, `verify_signature: False`, algoritmi JWT non fissati.
- RSA: `PKCS1v15` per cifrare, `RSA/ECB/PKCS1Padding`, chiavi sotto i 2048 bit, esponente 3 senza padding.
- Gestione errori: decifrature fallite ignorate, dati usati prima della verifica, messaggi d'errore diversi che rivelano dove si è fallito.
- Agilità: algoritmi e lunghezze di chiave non configurabili; nessun numero di versione nei formati.

Ricorda all'utente che una revisione del codice non sostituisce l'uso di librerie verificate e, per sistemi critici, un audit professionale.
