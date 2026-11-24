# Teoria e storia della crittografia

## Indice
1. Gli obiettivi (e cosa la crittografia non fa)
2. Parole che si confondono
3. Il principio di Kerckhoffs
4. Sicurezza perfetta, sicurezza computazionale, modelli di attacco
5. Crittografia simmetrica
6. Hash, MAC e derivazione di chiavi
7. Crittografia asimmetrica e infrastrutture a chiave pubblica
8. La casualità
9. Protocolli: come si combinano i mattoni
10. Il computer quantistico
11. Lezioni dagli attacchi famosi
12. Breve storia, con i contributi italiani
13. Glossario rapido

---

## 1. Gli obiettivi (e cosa la crittografia non fa)

- **Riservatezza**: solo chi ha la chiave legge.
- **Integrità**: ogni modifica, anche di un bit, viene scoperta.
- **Autenticità**: si sa chi ha prodotto il dato (o almeno che possiede una certa chiave).
- **Non ripudio**: l'autore non può negare di aver firmato. Lo danno le firme digitali, non i MAC (con un MAC entrambe le parti conoscono la chiave, quindi entrambe potrebbero aver prodotto il dato).

Cosa NON fa: non protegge un dispositivo già compromesso (un malware che legge lo schermo vede il testo in chiaro), non nasconde i metadati (chi parla con chi, quando, quanto), non garantisce la disponibilità dei dati, non rende onesto chi possiede la chiave.

## 2. Parole che si confondono

| Termine | Che cos'è | Serve una chiave? | Reversibile? |
|---|---|---|---|
| Codifica (base64, esadecimale, URL encoding, Morse) | Rappresentazione diversa degli stessi dati, per trasportarli | No | Sì, da chiunque |
| Cifratura | Trasformazione che solo chi ha la chiave può invertire | Sì | Sì, con la chiave |
| Hash | Impronta di lunghezza fissa | No | No, si può solo confrontare o indovinare l'input |
| MAC (es. HMAC) | Impronta con chiave segreta condivisa | Sì (condivisa) | No |
| Firma digitale | Impronta con chiave privata, verificabile con quella pubblica | Sì (coppia) | No |
| Offuscamento | Rendere difficile la lettura di codice o dati | No (o banale) | Sì, con pazienza |
| Steganografia | Nascondere l'esistenza del messaggio (es. in un'immagine) | A volte | Sì |

Nota d'uso in italiano: **cifrare/decifrare** si fa con la chiave; **decrittare** significa ricavare il testo senza la chiave, cioè rompere la protezione (crittoanalisi). "Criptare/decriptare" sono diffusi nel parlato. "Crittografare" è comune ma meno preciso.

## 3. Il principio di Kerckhoffs

Auguste Kerckhoffs (1883): un sistema deve restare sicuro anche se il nemico conosce tutto tranne la chiave. Claude Shannon lo riassunse in "il nemico conosce il sistema". I motivi sono pratici: gli algoritmi trapelano (reverse engineering, dipendenti, documenti), le chiavi si cambiano facilmente mentre gli algoritmi no, e solo la revisione pubblica scova i difetti. "Algoritmo segreto proprietario" è quindi un campanello d'allarme, non una garanzia.

## 4. Sicurezza perfetta, sicurezza computazionale, modelli di attacco

**One-time pad** (Vernam 1917, dimostrazione di Shannon 1949): sicurezza perfetta se la chiave è davvero casuale, lunga quanto il messaggio, usata una sola volta e tenuta segreta. Se si riusa, crolla: gli Stati Uniti decifrarono parte delle comunicazioni sovietiche (progetto Venona) proprio perché alcuni blocchi di chiave erano stati riusati. Il problema pratico è distribuire chiavi così lunghe.

**Sicurezza computazionale**: rompere il sistema è possibile in teoria ma richiede risorse irraggiungibili. Si misura in bit: "128 bit di sicurezza" vuol dire circa 2^128 operazioni. Un ordine di grandezza: un miliardo di miliardi di tentativi al secondo (10^18) per l'intera età dell'universo (circa 4·10^17 secondi) sono circa 2^118 tentativi, mille volte meno di quanti ne servono in media per una chiave a 128 bit.

**Modelli di attacco**, dal più debole al più forte: solo testo cifrato; testo in chiaro noto; testo in chiaro scelto (l'attaccante fa cifrare ciò che vuole); testo cifrato scelto (fa anche decifrare ciò che vuole). La cifratura moderna deve resistere all'ultimo (sicurezza IND-CCA2); le firme alla falsificazione anche dopo aver visto firme su messaggi scelti (EUF-CMA). I cifrari classici cadono già con il solo testo cifrato.

## 5. Crittografia simmetrica

Una sola chiave per cifrare e decifrare. Veloce, usata per tutti i dati veri e propri.

- **Cifrari a blocchi**: AES (Rijndael, di Daemen e Rijmen, standard dal 2001) cifra blocchi di 128 bit con chiavi da 128, 192 o 256 bit.
- **Cifrari a flusso**: ChaCha20 (Bernstein, 2008) genera un flusso pseudocasuale che si combina con i dati in XOR; ottimo dove manca l'accelerazione hardware per AES.
- **Modalità operative** (come usare un cifrario a blocchi su dati lunghi):
  - ECB: blocchi uguali danno cifrati uguali, quindi gli schemi trapelano (il celebre "pinguino" ancora riconoscibile dopo la cifratura). Da non usare mai.
  - CBC: richiede un IV casuale e imprevedibile e un MAC separato; senza, è esposto agli attacchi di tipo padding oracle.
  - CTR: trasforma il cifrario a blocchi in un cifrario a flusso; riusare il nonce è catastrofico.
  - GCM: CTR più autenticazione, cioè un AEAD. Nonce da 96 bit che non deve mai ripetersi con la stessa chiave.
  - ChaCha20-Poly1305: AEAD alternativo a GCM; XChaCha20-Poly1305 ha un nonce da 192 bit, abbastanza grande da poterlo generare a caso senza pensieri.
  - GCM-SIV e AES-SIV: resistono al riuso accidentale del nonce (al massimo rivelano se due messaggi sono identici).
- **AEAD** (cifratura autenticata con dati associati): cifra e autentica in un colpo solo; i "dati associati" (AAD), come un'intestazione, sono autenticati ma restano in chiaro. È la scelta predefinita oggi.
- **Nonce, IV, sale**: il nonce deve essere unico; l'IV di CBC deve essere imprevedibile; il sale è un valore casuale pubblico che rende unico ogni hash o derivazione. Nessuno dei tre è segreto.

## 6. Hash, MAC e derivazione di chiavi

**Proprietà di un hash crittografico**: resistenza alla preimmagine (dato l'hash, non si trova l'input), alla seconda preimmagine e alle collisioni. Per il paradosso del compleanno, un hash da n bit dà circa n/2 bit di resistenza alle collisioni: SHA-256 offre 128 bit.

- Famiglie attuali: SHA-2 (SHA-256, SHA-384, SHA-512), SHA-3 e SHAKE (Keccak, a spugna), BLAKE2 e BLAKE3.
- Rotte: MD5 (collisioni pratiche dal 2004; un certificato fraudolento nel 2008; sfruttato dal malware Flame nel 2012) e SHA-1 (prima collisione pubblica "SHAttered" nel 2017, collisioni a prefisso scelto nel 2020).
- **Estensione di lunghezza**: con SHA-256 e simili, chi conosce hash(chiave || messaggio) può calcolare l'hash di un messaggio allungato senza la chiave. Per questo per autenticare si usa HMAC, non un hash "fatto in casa".
- **MAC**: HMAC-SHA256, Poly1305 (dentro gli AEAD), KMAC.
- **Derivazione di chiavi**: HKDF trasforma un segreto già robusto (es. il risultato di uno scambio Diffie-Hellman) in chiavi per scopi diversi. Le password invece sono deboli e vanno "stirate" con funzioni lente e ad alto consumo di memoria: Argon2id (vincitore della Password Hashing Competition nel 2015, RFC 9106), scrypt, bcrypt, PBKDF2. Il **sale**, unico per ogni password, impedisce gli attacchi con tabelle precalcolate; il **pepe** è un ulteriore segreto conservato altrove (es. in un HSM).

## 7. Crittografia asimmetrica e infrastrutture a chiave pubblica

Una coppia di chiavi: la pubblica si distribuisce, la privata resta al proprietario. Si basa su problemi matematici difficili:

| Problema | Algoritmi | Rotto da un computer quantistico? |
|---|---|---|
| Fattorizzazione | RSA (1977) | Sì (Shor) |
| Logaritmo discreto | Diffie-Hellman (1976), DSA | Sì |
| Logaritmo discreto su curve ellittiche | ECDH, ECDSA, X25519, Ed25519 | Sì |
| Reticoli | ML-KEM, ML-DSA, FN-DSA | Nessun attacco noto |
| Funzioni hash | SLH-DSA, LMS, XMSS | Nessun attacco noto |
| Codici correttori | HQC, Classic McEliece | Nessun attacco noto |

Usi: scambio di chiavi o KEM (incapsulamento di una chiave casuale), firme digitali, raramente cifratura diretta. Nella pratica si usa la **cifratura ibrida**: con la parte asimmetrica si concorda una chiave casuale, con un AEAD simmetrico si cifrano i dati (schema KEM/DEM; standard HPKE, RFC 9180).

**Segretezza in avanti** (forward secrecy): con chiavi effimere per ogni sessione, rubare in futuro la chiave a lungo termine non permette di leggere le sessioni passate. TLS 1.3 e Signal la garantiscono.

**Fidarsi di una chiave pubblica**: il problema vero è sapere a chi appartiene. Tre modelli:
- PKI con autorità di certificazione: un certificato X.509 lega chiave e identità ed è firmato da una CA di cui il sistema si fida; i registri di Certificate Transparency rendono pubblici tutti i certificati emessi; la durata massima dei certificati TLS si sta accorciando per decisione del CA/Browser Forum (verso i 47 giorni entro il 2029).
- Rete di fiducia (PGP): gli utenti firmano le chiavi di chi conoscono.
- Fiducia al primo uso (TOFU): SSH memorizza l'impronta del server; Signal mostra i "numeri di sicurezza" da confrontare di persona.

## 8. La casualità

Chiavi, nonce e sali devono venire da un generatore crittograficamente sicuro (CSPRNG) del sistema operativo: `secrets`/`os.urandom` in Python, `crypto.getRandomValues` nel browser, `crypto/rand` in Go, `SecureRandom` in Java. Mai `Math.random()` o `random`. Errori storici: OpenSSL su Debian (2006-2008, solo 32.768 chiavi possibili), firma della PlayStation 3 con nonce ECDSA costante (2010, chiave privata ricavata), bug di SecureRandom su Android (2013, portafogli Bitcoin svuotati), dispositivi di rete con poca entropia all'avvio che condividevano fattori RSA (2012), generazione difettosa di chiavi RSA nei chip Infineon (ROCA, 2017).

## 9. Protocolli: come si combinano i mattoni

- **TLS 1.3** (RFC 8446, 2018): scambio di chiavi effimero, solo cifrari AEAD, handshake più rapido. I principali browser e CDN usano già lo scambio ibrido post-quantum X25519MLKEM768. Il lucchetto HTTPS dice che la connessione con quel dominio è cifrata, **non** che il sito sia onesto: i siti di phishing hanno certificati validi.
- **Signal**: X3DH, poi PQXDH (2023) con componente post-quantum, più il Double Ratchet che rinnova le chiavi a ogni messaggio (segretezza in avanti e recupero dopo una compromissione); nel 2025 è stato aggiunto un ratchet post-quantum. Lo stesso protocollo è alla base della cifratura end-to-end di WhatsApp.
- **End-to-end**: solo i dispositivi delle persone coinvolte hanno le chiavi; il fornitore trasporta dati che non può leggere. Restano visibili i metadati, e i backup sono protetti solo se la cifratura dei backup è attiva.
- **Altri**: SSH, VPN come WireGuard (basato sul framework Noise) e IPsec, cifratura dei dischi (BitLocker, FileVault, LUKS) che protegge i dati a dispositivo spento o bloccato.

## 10. Il computer quantistico

- **Algoritmo di Shor** (1994): un computer quantistico grande e con correzione d'errore romperebbe RSA, Diffie-Hellman e curve ellittiche, cioè quasi tutta la crittografia a chiave pubblica in uso.
- **Algoritmo di Grover**: accelera la ricerca esaustiva solo in modo quadratico; AES-256 mantiene circa 128 bit di sicurezza, gli hash moderni restano adeguati. Per i dati a lunga scadenza si preferisce comunque la chiave a 256 bit.
- **"Raccogli ora, decifra dopo"**: chi registra oggi traffico cifrato potrebbe leggerlo quando esisterà la macchina. Per questo la migrazione è iniziata prima che la macchina esista; nessuno sa con certezza quando arriverà.
- **Crittografia post-quantum (PQC)**: nuovi algoritmi eseguibili sui computer normali (ML-KEM, ML-DSA, SLH-DSA dal 2024), spesso in modalità ibrida con quelli classici. Non va confusa con la distribuzione quantistica delle chiavi (QKD), che richiede hardware dedicato e che le principali agenzie di sicurezza considerano, per la maggior parte degli usi, meno pratica della PQC.
- Calendario e stato degli standard: vedi `algoritmi-e-raccomandazioni.md`.

## 11. Lezioni dagli attacchi famosi

| Caso | Che cosa è successo | Lezione |
|---|---|---|
| Enigma (anni '30-'40) | Rejewski e i matematici polacchi, poi Turing e Bletchley Park, sfruttarono procedure ripetitive e testi prevedibili | Le abitudini degli operatori rompono anche macchine complesse |
| Venona | Riuso delle chiavi del one-time pad | Una chiave "usa e getta" riusata non protegge |
| WEP (2001) | IV corti e riusati con RC4 | Mai riusare nonce e flussi di chiave |
| Debian OpenSSL (2008) | Una modifica tolse quasi tutta l'entropia | Non toccare il codice crittografico senza capirlo |
| PlayStation 3 (2010) | Nonce ECDSA sempre uguale | Nonce casuali o deterministici (RFC 6979) |
| BEAST, Lucky13, POODLE (2011-2014) | Debolezze di CBC e padding in TLS | Usare AEAD; togliere le opzioni vecchie |
| Heartbleed (2014) | Bug di implementazione in OpenSSL, non nella matematica | Il codice sbaglia più spesso degli algoritmi |
| FREAK e Logjam (2015) | Ritorno forzato a cifrari "da esportazione" deboli | Le opzioni legacy sono un rischio anche se nessuno le sceglie |
| SHAttered (2017) | Prima collisione SHA-1 | Abbandonare in anticipo gli algoritmi indeboliti |
| KRACK (2017) | Riuso del nonce in WPA2 | Il riuso dei nonce si annida nei protocolli |
| ROCA (2017) | Chiavi RSA generate male in milioni di smart card | Anche l'hardware certificato può sbagliare |
| SIKE (2022) | Candidato post-quantum rotto in circa un'ora con un PC | Maturità e diversità delle ipotesi matematiche contano |

La lezione generale: gli algoritmi standard reggono; cadono implementazioni, gestione delle chiavi, opzioni legacy e persone.

## 12. Breve storia, con i contributi italiani

- **Antichità**: la scitala spartana (trasposizione con un bastone); il cifrario di Cesare (spostamento di 3 lettere, descritto da Svetonio); l'Atbash ebraico (alfabeto rovesciato).
- **IX secolo**: al-Kindi descrive per primo l'analisi delle frequenze.
- **Rinascimento italiano**: Leon Battista Alberti, nel *De cifris* (1467), inventa il disco cifrante e l'idea di cambiare alfabeto durante la cifratura (sostituzione polialfabetica): è considerato il padre della crittografia occidentale. Giovanni Soro, al servizio di Venezia nella prima metà del Cinquecento, è tra i primi grandi crittoanalisti. Gerolamo Cardano propone la griglia che porta il suo nome. Giovan Battista Bellaso (1553) descrive il cifrario polialfabetico con parola chiave che oggi chiamiamo "di Vigenère", un errore di attribuzione nato nell'Ottocento. Giambattista Della Porta (1563) studia sostituzioni a coppie di lettere e metodi di crittoanalisi.
- **1586**: Blaise de Vigenère descrive un cifrario autochiave, più forte di quello che porta il suo nome.
- **1863**: Friedrich Kasiski pubblica il metodo per rompere i polialfabetici (Babbage ci era arrivato prima, senza pubblicare).
- **1883**: Kerckhoffs, *La cryptographie militaire*.
- **1917-1918**: Vernam e Mauborgne, cifratura XOR con nastro casuale, cioè il one-time pad.
- **Guerre mondiali**: Enigma, Lorenz e il calcolatore Colossus; la crittoanalisi accelera la nascita dell'informatica.
- **1949**: Shannon fonda la teoria matematica della segretezza.
- **1976-1977**: Diffie ed Hellman pubblicano la crittografia a chiave pubblica (al GCHQ britannico Ellis, Cocks e Williamson ci erano arrivati prima, in segreto); nasce RSA; DES diventa standard.
- **1985**: Koblitz e Miller propongono la crittografia su curve ellittiche.
- **1991**: Phil Zimmermann pubblica PGP.
- **1994**: Shor pubblica l'algoritmo quantistico di fattorizzazione.
- **2001**: AES sostituisce DES.
- **2013-2016**: il protocollo di Signal porta la cifratura end-to-end a miliardi di persone.
- **2016-2024**: concorso NIST per la crittografia post-quantum; nel 2024 escono FIPS 203, 204 e 205.
- **2026**: NIST pubblica la versione definitiva del piano di transizione (IR 8547); l'ACN aggiorna le linee guida italiane sulle funzioni crittografiche.

## 13. Glossario rapido

- **AEAD**: cifratura autenticata con dati associati (AES-GCM, ChaCha20-Poly1305).
- **AAD**: dati associati, autenticati ma non cifrati.
- **Attacco a canale laterale**: ricava segreti da tempi, consumi o emissioni invece che dalla matematica.
- **CA**: autorità di certificazione. **CSR**: richiesta di certificato.
- **CSPRNG**: generatore di numeri casuali adatto alla crittografia.
- **Crypto-agility**: capacità di cambiare algoritmo senza riprogettare il sistema.
- **Entropia**: misura dell'imprevedibilità (di una password, di una sorgente casuale o di un insieme di byte).
- **Forward secrecy**: le sessioni passate restano protette anche se in futuro trapela la chiave a lungo termine.
- **HSM, TPM, enclave**: hardware che conserva le chiavi senza farle uscire.
- **HPKE**: schema standard di cifratura ibrida a chiave pubblica (RFC 9180).
- **KDF**: funzione di derivazione delle chiavi (HKDF; Argon2id per le password).
- **KEM**: meccanismo di incapsulamento di una chiave (ML-KEM).
- **Nonce**: valore da usare una sola volta con una data chiave.
- **PKI**: infrastruttura a chiave pubblica (certificati, CA, revoca).
- **PQC**: crittografia post-quantum.
- **Sale e pepe**: valore casuale pubblico per ogni hash; segreto aggiuntivo conservato a parte.
- **TOFU**: fiducia al primo uso.
