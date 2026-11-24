# Valutare l'affidabilità

Due domande diverse, da tenere separate nel verdetto:
- **Parte A**: il contenuto (messaggio, link, allegato, comando) è sicuro?
- **Parte B**: la protezione crittografica (di un file, un prodotto, uno schema) regge?

## Indice
- A1. Procedura
- A2. Segnali di phishing e truffa
- A3. Link
- A4. Allegati e file
- A5. Script e comandi
- A6. Cosa fare (prima e dopo un clic)
- A7. Livelli di rischio e come comunicarli
- B1. Domande chiave su un sistema cifrato
- B2. Campanelli d'allarme
- B3. Affermazioni comuni e come leggerle
- B4. Verificare che un file scaricato sia autentico
- B5. Scala di robustezza della protezione

---

## A1. Procedura

1. Decodifica in modo statico (`analizza.py`), senza aprire o eseguire nulla.
2. Leggi strati, formati, contenuti nascosti, indicatori e segnali.
3. Valuta il contesto: chi ha mandato il contenuto, da quale canale, se era atteso, che cosa chiede di fare e con quanta urgenza.
4. Confronta con i segnali delle sezioni seguenti.
5. Dai il verdetto nel formato di `SKILL.md`, con i passi pratici e i limiti.

## A2. Segnali di phishing e truffa

Il meccanismo è quasi sempre lo stesso: **urgenza o paura** + **richiesta di agire subito** (cliccare, pagare, inserire dati, installare, incollare un comando) + **mittente che imita qualcuno di fidato**.

Esempi frequenti in Italia:
- SMS del "pacco in giacenza" o della "consegna non riuscita" (finti corrieri o Poste) con link a pagine che chiedono pochi euro e i dati della carta.
- Finte comunicazioni di INPS o Agenzia delle Entrate su rimborsi o pratiche da completare.
- "Accesso anomalo" o "conto sospeso" a nome della banca, con link per "verificare" e richiesta del codice OTP. Nessuna banca chiede codici OTP, PIN o password via SMS, email o telefono.
- Multe, abbonamenti in scadenza (streaming, domini, caselle email), "spazio esaurito".
- Il messaggio "Ciao mamma, ho cambiato numero" su WhatsApp, seguito da una richiesta di bonifico.
- Investimenti miracolosi in criptovalute o trading, spesso con testimonial famosi falsi.
- Richiesta della **frase di recupero** (seed phrase) di un portafoglio di criptovalute: è sempre una truffa.
- Finto supporto tecnico che chiede di installare programmi di controllo remoto.
- QR code incollati su parcometri, volantini o email ("quishing") che portano a pagine di pagamento false.
- **Falsi CAPTCHA** che chiedono di premere Win+R (o aprire il Terminale) e incollare un comando: è un modo per far eseguire malware alla vittima stessa.

Segnali nel testo: saluti generici ("Gentile cliente"), errori o traduzioni strane, scadenze strette ("entro 24 ore"), minacce (blocco, multa, denuncia), premi inattesi, richiesta di dati che il mittente dovrebbe già avere.

## A3. Link

**Leggere un indirizzo**: il dominio che conta è quello subito prima della prima `/`, letto da destra. In `https://poste.it.verifica-account.top/login` il dominio è `verifica-account.top`, non Poste.

Trucchi comuni:
- marchio nel sottodominio o nel percorso: `paypal.sicurezza-conto.com`, `esempio.top/poste/accedi`;
- lettere sosia: `rn` al posto di `m`, `0` al posto di `o`, caratteri cirillici identici a quelli latini (dominio in punycode `xn--...`);
- `@` nell'indirizzo: tutto ciò che precede la `@` viene ignorato (`https://www.banca.it@sito-truffa.com`);
- link accorciati che nascondono la destinazione;
- reindirizzamenti: un dominio affidabile con un parametro che porta altrove (`...?url=https://truffa...`);
- domini `.zip` e `.mov`, che sembrano nomi di file;
- indirizzi IP al posto dei nomi; porte insolite;
- il lucchetto HTTPS: dice solo che la connessione è cifrata, non che il sito sia onesto.

**Controllare senza cliccare**: espandere i link accorciati con un servizio di anteprima; verificare l'età del dominio (i siti truffa hanno spesso pochi giorni); usare servizi di reputazione come VirusTotal o urlscan, sapendo che gli indirizzi inviati possono diventare visibili ad altri (non inviare link personali che contengono token); raggiungere il servizio vero digitando l'indirizzo a mano o dall'app ufficiale.

## A4. Allegati e file

- **Estensioni pericolose**: exe, scr, bat, cmd, com, pif, ps1, vbs, js, jse, wsf, hta, lnk, iso, img, vhd, msi, jar, dll, cpl, apk; documenti con macro (docm, xlsm, pptm); OneNote (one).
- **Doppia estensione**: `Fattura.pdf.exe`, spesso con l'estensione vera nascosta da Windows.
- **Firma diversa dall'estensione**: un ".pdf" che inizia con `MZ` è un eseguibile.
- **Office con macro**: un documento che chiede di "abilitare il contenuto" per essere letto è un classico; le versioni recenti di Office bloccano le macro dei file scaricati da Internet.
- **PDF con JavaScript eseguito all'apertura, azioni /Launch o file incorporati.**
- **Allegati HTML**: possono ricostruire pagine di login false o scaricare file (HTML smuggling).
- **Archivi protetti da password con la password nel testo dell'email**: servono a non farsi controllare dall'antivirus.
- **ISO, IMG, VHD**: contenitori usati per aggirare le protezioni di Windows sui file scaricati.

## A5. Script e comandi

Gruppi di segnali (tutti rilevati da `analizza.py`):
- **Scarica ed esegue**: `curl ... | sh`, `IEX (New-Object Net.WebClient).DownloadString(...)`, `certutil -urlcache`, `mshta http...`, `regsvr32 /i:http...`.
- **Si nasconde**: finestre nascoste (`-w hidden`), comandi codificati (`-enc`), offuscamento, decodifica a runtime.
- **Resta sul sistema**: attività pianificate, chiavi di registro di avvio (`...\Run`), crontab, servizi.
- **Disattiva le difese**: AMSI, esclusioni di Defender, cancellazione dei punti di ripristino (tipico del ransomware).
- **Ruba dati**: accesso a password dei browser, portafogli, cookie; invio di dati a server esterni.
- **Controllo remoto**: reverse shell (`/dev/tcp/`, `nc -e`).

Un comando che qualcuno chiede di incollare in un terminale, dentro "Esegui" o nella console del browser va considerato ad alto rischio finché non è stato letto e capito riga per riga.

## A6. Cosa fare (prima e dopo un clic)

Se non hai ancora cliccato o aperto:
- non aprire, non rispondere, non chiamare i numeri indicati nel messaggio;
- verifica dal canale ufficiale (app, numero sul retro della carta, sito digitato a mano);
- segnala: alla banca o all'azienda imitata, al proprio fornitore di posta o al proprio operatore come spam, alla Polizia Postale (commissariatodips.it); poi elimina.

Se hai cliccato e inserito dati:
- password: cambiala subito da un dispositivo pulito, e ovunque sia riutilizzata; attiva l'autenticazione a più fattori o le passkey;
- dati della carta o codici OTP: chiama subito il numero ufficiale della banca per bloccare carta e operazioni;
- controlla movimenti e accessi recenti; esci da tutte le sessioni attive.

Se hai eseguito un file o un comando:
- scollega il dispositivo dalla rete;
- non inserire password su quel dispositivo finché non è stato controllato;
- fai una scansione completa con un antivirus aggiornato o fatti aiutare da un tecnico; in ambito aziendale avvisa subito l'IT o il team di sicurezza;
- cambia le password importanti da un altro dispositivo.

Se è un ricatto ("ho registrato la tua webcam", richiesta di pagamento in criptovalute): di solito è una truffa di massa; non pagare, non rispondere, segnala.

## A7. Livelli di rischio e come comunicarli

- **ALTO**: imitazione di un marchio, richiesta di credenziali o pagamenti, eseguibili nascosti, comandi che scaricano ed eseguono, segreti esposti. Messaggio: "non aprire / non usare", con i passi di A6.
- **MEDIO**: più segnali sospetti senza prova di malevolenza (link accorciato più linguaggio d'urgenza; pagina che chiede una password su un dominio poco noto). Messaggio: "molto sospetto, verifica dal canale ufficiale".
- **BASSO**: singoli segnali deboli. Messaggio: "probabilmente innocuo, ma..." con il dettaglio.
- **NESSUN SEGNALE NOTO**: niente di sospetto nell'analisi statica. Messaggio: "non ho trovato segnali di pericolo", mai "è sicuro", e ricorda il contesto.

Scrivi i link pericolosi in forma non cliccabile (`hxxps://esempio[.]top`).

## B1. Domande chiave su un sistema cifrato

1. Quali algoritmi e modalità usa? Sono standard (sezione 1 di `algoritmi-e-raccomandazioni.md`)?
2. **Chi possiede le chiavi?** Se il fornitore può recuperare i dati quando dimentichi la password, allora può leggerli (o qualcuno può costringerlo a farlo).
3. I dati sono autenticati (AEAD, firme) o solo cifrati?
4. Come diventano chiavi le password? Con Argon2id, scrypt o simili?
5. C'è segretezza in avanti? Cosa succede se una chiave viene rubata?
6. Che cosa resta visibile: metadati, nomi dei file, dimensioni, contatti, backup?
7. Il codice o il protocollo è pubblico e verificato da terzi? Ci sono audit indipendenti recenti?
8. Gli algoritmi si possono aggiornare? C'è un piano per la transizione post-quantum?

## B2. Campanelli d'allarme

- "Algoritmo proprietario segreto", "inviolabile", "impossibile da decifrare".
- Lunghezze di chiave assurde ("chiave da 1 milione di bit") o "one-time pad" con chiavi riutilizzabili.
- "Cifratura militare" usato come argomento principale.
- Possibilità di recuperare la password o di farsela rimandare per email (le password vanno conservate con hash, non in modo reversibile).
- "End-to-end" che però permette al fornitore di cercare nei contenuti o di ripristinarli senza la tua chiave.
- Assenza di documentazione tecnica, di audit e di un modo per segnalare vulnerabilità.
- Buzzword quantistiche senza nomi di algoritmi standard.

## B3. Affermazioni comuni e come leggerle

| Affermazione | Cosa vuol dire davvero |
|---|---|
| "Cifratura AES-256 di livello militare" | AES-256 è ottimo, ma è solo un mattone: contano gestione delle chiavi, modalità, autenticazione |
| "Cifrato end-to-end" | Solo i dispositivi delle persone coinvolte hanno le chiavi. Verifica i backup e ricorda che i metadati restano |
| "Zero-knowledge" | Il fornitore non conosce le tue chiavi: dimenticando la password perdi i dati. Se non li perdi, non è davvero zero-knowledge |
| "I dati sono cifrati sui nostri server" | Cifratura a riposo con chiavi del fornitore: protegge dal furto dei dischi, non dal fornitore stesso |
| "Sito sicuro, c'è il lucchetto" | La connessione è cifrata; il sito può comunque essere una truffa |
| "Con la VPN sei anonimo" | Sposti la fiducia dal fornitore di connessione al fornitore della VPN |
| "Le password sono criptate" | Dovrebbero essere trasformate con un hash lento e con sale, non cifrate in modo reversibile |
| "Resistente ai computer quantistici" | Chiedi quali algoritmi: ML-KEM o ibridi come X25519MLKEM768 sono una risposta seria |
| "WhatsApp/Signal è cifrato" | Messaggi e chiamate sì, end-to-end; per WhatsApp i backup lo sono solo se attivi la cifratura dei backup; i metadati restano visibili al fornitore |

## B4. Verificare che un file scaricato sia autentico

1. Scarica solo dal sito ufficiale o dallo store ufficiale.
2. Confronta l'hash con quello pubblicato: `python scripts/cifra.py hash --file file --atteso VALORE` (o `sha256sum`, `Get-FileHash`). Vale solo se il valore atteso viene da una fonte affidabile, separata dal file.
3. Meglio ancora, verifica la firma: GnuPG (`gpg --verify`, controllando l'impronta della chiave dell'autore), minisign, Sigstore; per i programmi Windows e macOS, la firma del produttore e la notarizzazione.
4. Se l'hash non corrisponde: non usare il file, scaricalo di nuovo dalla fonte ufficiale e, se si ripete, segnalalo.

## B5. Scala di robustezza della protezione

| Livello | Esempi | Messaggio |
|---|---|---|
| NESSUNA | base64, esadecimale, URL encoding, Morse, JWT firmato (per la riservatezza) | "È solo codificato: chiunque lo legge." |
| NULLA / ROTTA | Cesare, Vigenère, sostituzione, XOR con chiave corta, cifrari fatti in casa | "Si rompe senza chiave: ecco il testo." |
| DEBOLE | ECB, CBC senza MAC, `openssl enc` senza `-pbkdf2`, ZipCrypto, RC4, DES, MD5 per password, password brevi | "Protezione apparente: ecco come si aggira e come rimediare." |
| ACCETTABILE | standard moderni con qualche limite (RSA-2048, bcrypt con costo basso, AES-128-CBC con HMAC) | "Regge oggi; ecco cosa migliorare." |
| ROBUSTA | AES-GCM o ChaCha20-Poly1305 con chiavi casuali o Argon2id e password forte, age, Signal, TLS 1.3 | "Non decifrabile senza la chiave: la sicurezza dipende da come la custodisci." |
