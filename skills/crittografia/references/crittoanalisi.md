# Crittoanalisi

## Indice
1. Quando si fa
2. Metodo in cinque passi
3. Statistiche di italiano e inglese
4. Cifrari monoalfabetici
5. Cifrari polialfabetici
6. Cifrari a trasposizione
7. Altri cifrari classici
8. XOR
9. Crittografia moderna: che cosa si può verificare davvero
10. Strumenti e palestre

---

## 1. Quando si fa

Rompere un cifrario serve a dimostrare che una protezione è debole, a risolvere enigmi e CTF, a studiare, a recuperare dati propri. Non si usa per leggere comunicazioni o file di altre persone senza autorizzazione (vedi i limiti in `SKILL.md`).

`scripts/classici.py` automatizza quasi tutto ciò che segue:
```bash
python scripts/classici.py auto "TESTO CIFRATO"        # prova tutto e ordina i candidati
python scripts/classici.py frequenze "TESTO"           # IC, frequenze, Kasiski, Friedman
python scripts/classici.py vigenere-attacco --file cifrato.txt
python scripts/classici.py sostituzione-attacco --file cifrato.txt
python scripts/classici.py xor-attacco --hex 1b37373331363f78...
```
Lo script valuta i candidati con un modello statistico di italiano e inglese e indica una "plausibilità": controlla comunque a occhio i primi risultati, soprattutto con testi brevi.

## 2. Metodo in cinque passi

1. **Identifica**: è davvero un cifrario o solo una codifica? (Prima passa da `analizza.py`.) Che alfabeto usa? Ci sono spazi e punteggiatura conservati?
2. **Misura**: lunghezza, frequenze delle lettere, indice di coincidenza (IC), ripetizioni e loro distanze, lettere doppie, entropia per i dati binari.
3. **Formula un'ipotesi**: IC simile alla lingua significa monoalfabetico o trasposizione; IC basso significa polialfabetico o cifratura moderna; frequenze identiche a quelle della lingua ma testo illeggibile significano trasposizione.
4. **Attacca**: forza bruta dove le chiavi sono poche (Cesare: 25; affine: 312 combinazioni), statistica dove sono tante (sostituzione: 26! ≈ 4·10^26 tabelle, ma l'hill climbing la risolve in pochi secondi).
5. **Verifica**: il testo ottenuto deve avere senso compiuto. Uno spezzone plausibile su un testo brevissimo può essere una coincidenza.

## 3. Statistiche di italiano e inglese

**Lettere più frequenti**
- Italiano: E 11,8% · A 11,7% · I 11,3% · O 9,8% · N 6,9% · L 6,5% · R 6,4% · T 5,6% · S 5,0% · C 4,5% · D 3,7% · P 3,1% · U 3,0% · M 2,5% · V 2,1% · G 1,6% · H 1,5%. Rare: F, B, Q, Z; quasi assenti J, K, W, X, Y.
- Inglese: E 12,7% · T 9,1% · A 8,2% · O 7,5% · I 7,0% · N 6,7% · S 6,3% · H 6,1% · R 6,0% · D 4,3% · L 4,0% · C 2,8% · U 2,8% · M 2,4% · W 2,4% · F 2,2%.

**Indice di coincidenza** (probabilità che due lettere prese a caso siano uguali): testo casuale 0,0385; inglese circa 0,067; italiano circa 0,073-0,075. Su meno di 100-150 lettere la stima oscilla molto.

**Bigrammi, trigrammi e doppie** (valori indicativi, ricavati da testi di esempio):
- Italiano, bigrammi: ER RE ON ES TO AN CO AL TA NO IA TE LA TT EN EL CH RI. Trigrammi: PER CON CHE ERE ETT ARE EST CHI ONO ELL. Doppie frequenti: TT SS LL GG NN ZZ (in italiano le doppie sono molto comuni).
- Inglese, bigrammi: TH HE ER AN ES IN ND RE ST AT EN. Trigrammi: THE AND ING THA TER HAT ERS ITH. Doppie: TT SS EE LL OO.

**Parole brevi utili per indovinare** (se gli spazi sono conservati):
- Italiano: a una lettera "e", "a", "i", "o"; a due "di", "il", "la", "in", "un", "che", "non", "per", "con".
- Inglese: a una lettera "a", "I"; a due "of", "to", "in", "is", "it"; "the" e "and" dominano.
- Schemi di ripetizione: in italiano "della" (D-E-L-L-A, doppia al centro), "questo", "anche".

**Indizi tipici dell'italiano**: molte parole finiscono in vocale; Q è sempre seguita da U; H compare quasi solo in CH, GH e nelle forme di "avere".

## 4. Cifrari monoalfabetici

Ogni lettera è sempre sostituita dalla stessa lettera: l'IC resta quello della lingua.

- **Cesare / ROT13**: spostamento fisso (Cesare usava 3; ROT13 è lo spostamento di 13, che si inverte da solo). Si rompe provando le 25 chiavi.
- **Atbash**: alfabeto rovesciato (A↔Z, B↔Y...). Nessuna chiave.
- **Affine**: E(x) = (a·x + b) mod 26, con a coprimo con 26 (12 valori) e b da 0 a 25: 312 combinazioni, si provano tutte.
- **Sostituzione con tabella o parola chiave**: 26! tabelle possibili, ma la statistica la rompe. Metodi: abbinare le lettere più frequenti del cifrato a quelle della lingua, cercare parole brevi e schemi (doppie, finali in vocale), poi migliorare la tabella scambiando coppie di lettere finché il testo diventa più simile alla lingua (hill climbing, come fa `classici.py`). Servono almeno 150-200 lettere per una soluzione automatica affidabile.

## 5. Cifrari polialfabetici

Più alfabeti in rotazione: l'IC scende verso quello casuale.

- **Vigenère / Bellaso**: la chiave ripetuta dice di quanto spostare ogni lettera. Attacco:
  1. trovare la lunghezza della chiave: **Kasiski** (le distanze tra sequenze ripetute sono spesso multiple della lunghezza), **Friedman** (stima dalla formula dell'IC), oppure provando lunghezze da 1 a 20 e cercando quella per cui le colonne hanno IC da lingua naturale;
  2. dividere il testo in colonne (una per lettera della chiave): ogni colonna è un semplice Cesare;
  3. risolvere ogni colonna con le frequenze (test del chi quadro) e rifinire con il modello di lingua.
- **Beaufort**: variante con sottrazione (chiave meno testo); si attacca allo stesso modo.
- **Autochiave**: la chiave prosegue con il testo stesso; più robusto, ma cade con parole probabili o con statistiche più fini.
- **Chiave lunga quanto il testo (running key)**: se la chiave è un testo naturale, si attacca sfruttando che sia testo che chiave sono lingua; se è casuale e mai riusata è un one-time pad, quindi imbattibile.
- **Disco di Alberti**: l'antenato di tutti questi; cambia alfabeto a intervalli scelti dal mittente.

## 6. Cifrari a trasposizione

Le lettere restano le stesse ma cambiano posto: frequenze e IC identici alla lingua, testo illeggibile.

- **Scitala e rail fence** (zig-zag su N righe): si provano tutti i numeri di righe.
- **Trasposizione a colonne**: il testo scritto in righe sotto una parola chiave e letto per colonne nell'ordine alfabetico della chiave. Si attacca provando larghezze diverse e riordinando le colonne finché compaiono bigrammi frequenti (anagrammi multipli); più difficile da automatizzare.
- **Doppia trasposizione**: ben più robusta, fu usata in guerra.

## 7. Altri cifrari classici

| Cifrario | Come riconoscerlo | Punto debole |
|---|---|---|
| Playfair | lunghezza pari, mai due lettere uguali nella stessa coppia, niente J (o niente W) | statistica dei bigrammi |
| Hill | algebra lineare su blocchi; frequenze appiattite | basta un pezzo di testo in chiaro noto |
| ADFGVX / ADFGX | solo le lettere A D F G V X | analisi delle coppie e trasposizione |
| Polibio | coppie di cifre da 11 a 55 | diventa una sostituzione monoalfabetica |
| Bacone | gruppi di 5 simboli di due tipi (A/B, maiuscole/minuscole) | si legge come binario |
| Pigpen (dei frammassoni) | simboli a griglie e punti | sostituzione monoalfabetica |
| Cifrario a libro | numeri che rimandano a pagine, righe, parole di un testo | trovare il libro |
| Enigma | nessuna lettera è mai cifrata in se stessa | posizionamento di parole probabili, procedure ripetitive |

## 8. XOR

- **Chiave di un byte**: 255 possibilità; si prova ogni chiave e si tiene il risultato che sembra testo. Molto usato nel malware per nascondere stringhe: è offuscamento, non protezione.
- **Chiave corta ripetuta**: si stima la lunghezza con la distanza di Hamming normalizzata tra blocchi consecutivi; poi ogni posizione della chiave è un XOR a un byte, risolto con la statistica dei caratteri. Classico esercizio "cryptopals".
- **Riuso della chiave (two-time pad)**: XOR di due cifrati con lo stesso flusso dà lo XOR dei due testi in chiaro; indovinando una parola in un testo ("crib dragging") si rivela il pezzo corrispondente dell'altro. È lo stesso errore che rompe CTR e GCM quando si ripete il nonce.

## 9. Crittografia moderna: che cosa si può verificare davvero

AES, ChaCha20, curve ellittiche e ML-KEM, usati correttamente, non hanno scorciatoie note: non si "decifrano" senza chiave. Quello che si può e si deve controllare è l'uso:

- **Modalità ECB**: blocchi da 16 byte ripetuti nel cifrato (`analizza.py` li conta).
- **Nonce o IV ripetuti**: più messaggi con lo stesso nonce in GCM o CTR sono gravissimi; IV uguali o prevedibili in CBC rivelano prefissi comuni.
- **Mancanza di autenticazione**: CBC o CTR senza MAC permettono di alterare i dati (bit flipping) o di indovinarli con un padding oracle.
- **Derivazione debole della password**: `openssl enc` senza `-pbkdf2`, ZIP con ZipCrypto, PDF con RC4, hash veloci. Qui la cifratura regge ma la password si indovina; per i *propri* file si può stimare quanto è robusta la password con `cifra.py valuta-password`.
- **Chiavi deboli o mal generate**: RSA sotto i 2048 bit, chiavi DSA, fattori condivisi tra chiavi, chiavi colpite da ROCA (esistono strumenti per controllare le proprie), ECDSA con nonce riusati.
- **JWT**: `alg: none`, algoritmo non fissato dal server, segreti HMAC deboli (da testare solo sui propri sistemi).
- **Lunghezza e metadati**: la cifratura nasconde il contenuto, non quanto è lungo né quando viene inviato.
- **Implementazione**: confronti non a tempo costante, segreti nei log, errori diversi per motivi diversi.

Se tutto questo è a posto, il verdetto onesto è: "non decifrabile senza la chiave; la sicurezza dipende da come la chiave viene custodita".

## 10. Strumenti e palestre

- CyberChef (codifiche e trasformazioni, anche offline), dCode.fr (cifrari classici), quipqiup (sostituzioni con spazi).
- CrypTool (didattica, disponibile anche online).
- Le sfide "cryptopals" e le competizioni CTF per allenarsi in modo lecito.
