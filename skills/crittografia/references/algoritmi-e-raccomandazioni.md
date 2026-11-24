# Algoritmi e raccomandazioni (stato a novembre 2026)

La crittografia evolve: se la domanda riguarda lo stato più recente degli standard e hai la ricerca web, verifica le novità (soprattutto su FN-DSA, HQC e calendari nazionali) prima di rispondere.

## Indice
1. Tabella rapida
2. Cifratura simmetrica
3. Hash e MAC
4. Password e derivazione delle chiavi
5. Chiave pubblica oggi
6. Post-quantum: algoritmi e stato
7. Calendario della transizione (NIST, Stati Uniti, UE, Italia)
8. Protocolli e strumenti consigliati
9. Lunghezze di chiave equivalenti
10. Fonti autorevoli

---

## 1. Tabella rapida

| Scopo | Usa | Accettabile con cautela | Evita |
|---|---|---|---|
| Cifrare dati | AES-256-GCM, ChaCha20-Poly1305, XChaCha20-Poly1305 | AES-128-GCM; AES-CBC + HMAC (encrypt-then-MAC); AES-GCM-SIV | AES-ECB, CBC o CTR senza MAC, DES, 3DES, RC4, Blowfish, XOR "fatti in casa" |
| Hash | SHA-256, SHA-384, SHA-512, SHA-3, BLAKE2, BLAKE3 | SHA-224 | MD5, SHA-1 (per scopi di sicurezza) |
| Autenticare messaggi | HMAC-SHA256, KMAC, AEAD | Poly1305 solo dentro un AEAD | hash(chiave + messaggio), CRC, checksum non crittografici |
| Conservare password | Argon2id | scrypt, bcrypt (limite 72 byte), PBKDF2-HMAC-SHA256 con molte iterazioni | MD5, SHA-1, SHA-256 semplici o senza sale, cifratura reversibile |
| Derivare chiavi da segreti robusti | HKDF | | Usare direttamente il segreto Diffie-Hellman come chiave |
| Scambio di chiavi | X25519MLKEM768 (ibrido), X25519, ECDH P-256 | ML-KEM-768 da solo; RSA-OAEP 3072+ | RSA con padding PKCS#1 v1.5 per cifrare, DH a 1024 bit, RSA "nudo" |
| Firme | Ed25519, ECDSA P-256 deterministico, RSA-PSS 3072+, ML-DSA | RSA PKCS#1 v1.5 per firme | DSA, RSA sotto i 2048 bit, ECDSA con nonce non casuali |
| Numeri casuali | CSPRNG del sistema operativo | | Math.random, random di Python, rand(), semi basati sull'ora |

## 2. Cifratura simmetrica

- **AES-256-GCM**: veloce con l'accelerazione hardware (presente su quasi tutte le CPU moderne). Nonce da 96 bit mai ripetuto con la stessa chiave; con nonce casuali NIST limita a 2^32 cifrature per chiave; ogni messaggio al massimo circa 64 GiB. Tag da 128 bit, da non troncare.
- **ChaCha20-Poly1305** (RFC 8439): stessa sicurezza, ottimo in software e su dispositivi senza AES hardware. **XChaCha20-Poly1305** ha un nonce da 192 bit: generarlo a caso è sicuro anche per moltissimi messaggi (libsodium).
- **AES-GCM-SIV / AES-SIV**: utili quando non si può garantire l'unicità dei nonce.
- **Ascon** (NIST SP 800-232): famiglia leggera per dispositivi molto limitati (IoT, sensori), aggiunta tra le primitive approvate.
- **AES-128 o AES-256?** AES-128 è tuttora sicuro; AES-256 offre margine contro l'algoritmo di Grover ed è la scelta naturale per dati da proteggere a lungo.
- 3DES non è più ammesso da NIST per cifrare (dal 2024); le poche primitive simmetriche a 112 bit rimaste saranno vietate dal 2030.

## 3. Hash e MAC

- SHA-256 per impronte e checksum; SHA-384/512 dove serve più margine; SHA-3 per diversità di progetto; BLAKE3 per velocità.
- NIST ritirerà definitivamente SHA-1 entro il 31 dicembre 2030; MD5 e SHA-1 vanno bene solo contro errori accidentali, mai contro un avversario.
- Per autenticare usa HMAC (o un AEAD). Confronta sempre i tag con funzioni a tempo costante.

## 4. Password e derivazione delle chiavi

Parametri minimi OWASP per la conservazione delle password (scegline uno):
- **Argon2id**: memoria 19 MiB, 2 iterazioni, parallelismo 1 (oppure più memoria e meno iterazioni, es. 46 MiB e 1 iterazione).
- **scrypt**: N = 2^17, r = 8, p = 1.
- **bcrypt**: costo almeno 10; considera solo i primi 72 byte della password.
- **PBKDF2-HMAC-SHA256**: almeno 600.000 iterazioni (quando serve conformità FIPS).

RFC 9106 raccomanda per Argon2id, quando le risorse lo permettono, 2 GiB di memoria con 1 iterazione e 4 corsie, oppure 64 MiB con 3 iterazioni e 4 corsie (quest'ultima è l'impostazione di `cifra.py`). Scegli i parametri in modo che una verifica richieda nell'ordine di qualche centinaio di millisecondi sul server reale.

Sempre: sale casuale unico per password (almeno 16 byte), memorizzato con l'hash e con i parametri; eventuale pepe in un HSM o in un archivio segreti separato; ricalcolo dell'hash con parametri più forti al login successivo quando si aggiornano.

Politiche sulle password (NIST SP 800-63B, revisione 4 del 2025): lunghezza minima (15 caratteri se la password è l'unico fattore), nessuna regola di composizione obbligatoria, nessuna scadenza periodica senza motivo, controllo contro elenchi di password note o compromesse, possibilità di incollare e di usare gestori di password. Meglio ancora: autenticazione a più fattori e passkey.

**In Italia**: le *Linee guida funzioni crittografiche – conservazione delle password* di ACN e Garante privacy (dicembre 2023) indicano come funzioni adeguate PBKDF2, scrypt, bcrypt e Argon2, con sale ed eventuale pepe, e i relativi parametri. La legge 90/2024 (articolo 9) chiede ai soggetti interessati di verificare che i programmi che usano crittografia rispettino le linee guida adottate da ACN e Garante.

## 5. Chiave pubblica oggi

- **Scambio di chiavi**: X25519 (RFC 7748), oppure ECDH su P-256; nelle nuove implementazioni preferisci la versione ibrida con ML-KEM.
- **Firme**: Ed25519 (RFC 8032, approvato anche in FIPS 186-5); ECDSA P-256 con nonce deterministici (RFC 6979); RSA-PSS da 3072 bit se serve compatibilità.
- **Cifratura a chiave pubblica**: HPKE (RFC 9180) invece di schemi su misura; RSA solo con OAEP.
- **Chiavi RSA**: 2048 bit è il minimo ancora accettato; per nuove chiavi 3072 o, meglio, curve ellittiche.
- Tutti questi algoritmi sono vulnerabili a un futuro computer quantistico: vedi le sezioni 6 e 7.

## 6. Post-quantum: algoritmi e stato

| Algoritmo | Tipo | Standard | Stato a novembre 2026 |
|---|---|---|---|
| ML-KEM (da CRYSTALS-Kyber) | Incapsulamento di chiavi | FIPS 203 | Definitivo (agosto 2024). NIST indica ML-KEM-768 come parametro predefinito raccomandato |
| ML-DSA (da CRYSTALS-Dilithium) | Firma | FIPS 204 | Definitivo (agosto 2024) |
| SLH-DSA (da SPHINCS+) | Firma basata su hash | FIPS 205 | Definitivo (agosto 2024); firme grandi ma ipotesi molto conservative |
| FN-DSA (da Falcon) | Firma compatta | FIPS 206 | Ancora bozza; versione definitiva attesa tra fine 2026 e 2027 |
| HQC | Incapsulamento (basato su codici) | in preparazione | Scelto a marzo 2025 come riserva di ML-KEM con matematica diversa; standard atteso nel 2027 |
| LMS, XMSS | Firme basate su hash con stato | SP 800-208 | In uso, soprattutto per firmare firmware; richiedono di non riusare mai lo stato |

NIST sta valutando altre firme post-quantum in un percorso separato, per avere alternative non basate sui reticoli. SP 800-227 (2025) dà le raccomandazioni generali per i KEM.

**Ibrido**: si combinano un algoritmo classico e uno post-quantum, così la protezione regge se almeno uno dei due regge. È la via scelta da quasi tutti per lo scambio di chiavi.

Dove è già in uso:
- TLS: X25519MLKEM768 è predefinito nei principali browser (Chrome, Edge, Firefox) e nelle grandi CDN; supportato da OpenSSL 3.5 e successivi, BoringSSL, Go dalla versione 1.24.
- SSH: OpenSSH 10 usa per impostazione predefinita lo scambio ibrido mlkem768x25519-sha256.
- Messaggistica: Signal (PQXDH dal 2023 e ratchet post-quantum dal 2025), iMessage con PQ3 (2024).
- Librerie: OpenSSL 3.5+, Java 24+ (ML-KEM e ML-DSA), Go (crypto/mlkem), Python `cryptography` (ML-KEM, ML-DSA, HPKE ibrido), liboqs.

## 7. Calendario della transizione

**NIST IR 8547, versione definitiva (27 ottobre 2026)**:
- Tutti gli algoritmi a chiave pubblica vulnerabili ai computer quantistici (RSA, ECDSA, EdDSA, Diffie-Hellman, ECDH) sono **deprecati dopo il 2030** e **non ammessi dopo il 2035**, a qualsiasi lunghezza di chiave. La bozza del 2024 lasciava RSA-3072, P-256 ed Ed25519 validi fino al 2035; la versione definitiva non più.
- "Deprecato" significa utilizzabile ma con un rischio che il titolare dei dati deve valutare e accettare; "non ammesso" significa vietato negli standard NIST.
- Lo scambio di chiavi ibrido è ammesso nella validazione FIPS 140 se almeno una delle componenti è approvata.
- Per la firma del firmware sono indicati LMS e XMSS.

**Stati Uniti**: l'Executive Order 14412 (giugno 2026) e il memorandum OMB M-26-15 chiedono ai sistemi federali ad alto impatto di usare la PQC per lo scambio di chiavi entro il 31 dicembre 2030 e per le firme entro il 31 dicembre 2031, e il supporto a TLS 1.3 entro gennaio 2030. Attraverso gli appalti queste scadenze si estendono ai fornitori.

**Unione europea**: la roadmap coordinata degli Stati membri (giugno 2025) prevede l'avvio della transizione entro la fine del 2026, la migrazione dei casi ad alto rischio entro il 2030 e del maggior numero possibile di sistemi entro il 2035.

**Italia**: l'ACN ha aggiornato l'11 giugno 2026 le linee guida sulle funzioni crittografiche, con indicazioni sulla transizione post-quantum, sulle firme digitali, su TLS e sulla crypto-agility. Restano valide le linee guida ACN-Garante sulle password.

**Cosa consigliare in pratica**:
1. Inventario: sapere dove e come si usa la crittografia (anche librerie e dispositivi).
2. Crypto-agility: algoritmi configurabili, non scolpiti nel codice.
3. Priorità ai dati che devono restare riservati a lungo ("raccogli ora, decifra dopo").
4. Prima lo scambio di chiavi ibrido (oggi già disponibile), poi le firme, che richiedono di rifare certificati e catene di fiducia.
5. Chiedere ai fornitori una roadmap con date, distinguendo "supporta" da "attivo per impostazione predefinita".

## 8. Protocolli e strumenti consigliati

- **Web**: TLS 1.3 (TLS 1.2 ancora accettabile solo con ECDHE e cifrari AEAD); TLS 1.0 e 1.1 sono deprecati (RFC 8996).
- **Accesso remoto**: SSH con chiavi Ed25519 protette da passphrase; niente accesso con password esposto a Internet.
- **VPN**: WireGuard, IPsec/IKEv2 moderni.
- **Messaggi**: Signal; per l'email cifrata OpenPGP moderno (RFC 9580) o S/MIME, sapendo che oggetto e destinatari restano visibili.
- **File**: age (semplice, moderno), GnuPG; 7-Zip con AES-256 e password robusta per archivi (lo ZIP "classico" ZipCrypto è debole).
- **Dischi**: BitLocker (meglio con TPM più PIN), FileVault, LUKS2 (che usa Argon2id).
- **Password**: un gestore di password (es. Bitwarden, KeePassXC, 1Password) e, dove possibile, passkey FIDO2/WebAuthn, che resistono al phishing.
- **Firme di software**: Sigstore, minisign, GnuPG; per gli sviluppatori, firma dei commit e dei rilasci.

## 9. Lunghezze di chiave equivalenti (NIST SP 800-57)

| Sicurezza | Simmetrica | RSA / DH | Curve ellittiche | Hash (collisioni) |
|---|---|---|---|---|
| 112 bit | 3DES (non più ammesso) | 2048 | 224 | SHA-224 |
| 128 bit | AES-128 | 3072 | 256 (P-256, Curve25519) | SHA-256 |
| 192 bit | AES-192 | 7680 | 384 | SHA-384 |
| 256 bit | AES-256 | 15360 | 512 (P-521) | SHA-512 |

Le colonne RSA e curve ellittiche valgono solo contro computer classici.

## 10. Fonti autorevoli

- NIST Computer Security Resource Center (FIPS, SP 800, IR 8547).
- IETF RFC: 8446 (TLS 1.3), 8439 (ChaCha20-Poly1305), 9106 (Argon2), 9180 (HPKE), 7748 (X25519), 8032 (EdDSA), 9580 (OpenPGP).
- Agenzie europee: BSI (TR-02102), ANSSI, ENISA; in Italia ACN (acn.gov.it) e Garante per la protezione dei dati personali.
- OWASP Cheat Sheet Series (Cryptographic Storage, Password Storage, Key Management).
- keylength.com per confrontare le raccomandazioni di diversi enti.
