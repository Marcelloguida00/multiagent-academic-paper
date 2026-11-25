# Human Guidelines — fonti obbligatorie

Documento di lavoro per **Quinn** (Human Guidelines Engineer, squadra DES).  
Data di lettura orchestrata: 2026-11-25. Le linee guida ufficiali restano la fonte normativa; questo file è una sintesi operativa, non un sostituto.

## Fonti primarie (da rileggere quando il brief cambia piattaforma)

| Piattaforma | URL | Stato lettura |
|---|---|---|
| Apple Human Interface Guidelines | https://developer.apple.com/design/human-interface-guidelines | hub + foundations (design principles, accessibility, layout, typography) |
| Apple Design Principles | https://developer.apple.com/design/human-interface-guidelines/design-principles | letto |
| Samsung Design System | https://developer.samsung.com/design-system | letto |
| Samsung One UI (linee guida operative) | https://developer.samsung.com/one-ui/index.html | letto (il Design System rimanda a consistenza cross-device; One UI fornisce i principi UX) |

Se una pagina non è raggiungibile in run, marca i punti come `da_verificare` e indica l’URL esatto.

---

## Apple HIG — principi di design

Fonte: Apple HIG · Design principles.

1. **Purpose** — Progetta con intenzione: identifica ciò che conta di più per le persone e rendilo eccellente.
2. **Agency** — Lascia agire le persone a modo loro: informale sullo stato, recupera dagli errori.
3. **Responsibility** — Agisci nel loro interesse: sicurezza, privacy, trasparenza su cosa fa il prodotto e perché.
4. **Familiarity** — Costruisci su ciò che già conoscono: pattern fisici e digitali consolidati, usati in modo coerente.
5. **Flexibility** — Adatta a contesti e bisogni diversi: dispositivi, tipi di interazione, prospettive.
6. **Simplicity** — Sii chiaro e diretto: ogni elemento deve guadagnarsi il posto.
7. **Craft** e **Delight** — cura e piacere d’uso senza ostacolare il compito.

### Accessibilità (HIG)

Un’interfaccia accessibile è **intuitiva**, **percettibile** (non dipende da un solo canale) e **adattabile** (Dynamic Type, impostazioni di sistema, personalizzazione).

- Supporta Dynamic Type (idealmente fino a ~200% di ingrandimento).
- Contrasto: mira almeno a WCAG AA (4.5:1 testo fino a 17 pt; 3:1 da 18 pt / testo large).
- Non comunicare solo con il colore.
- Verifica con Accessibility Inspector quando disponibile.

### Layout (HIG)

- Gerarchia visiva: contenuto importante in alto / lato leading; allineamento e indentazione per gerarchia.
- Raggruppa elementi correlati; progressive disclosure per ridurre rumore.
- Adatta a size class, orientamento, finestre, safe area, Display Zoom, Dynamic Island dove pertinente.
- Rispetta safe area, margini e guide di sistema.

### Tipografia (HIG) — minimi piattaforma

| Piattaforma | Default | Minimo |
|---|---|---|
| iOS / iPadOS | 17 pt | 11 pt |
| macOS | 13 pt | 10 pt |
| tvOS | 29 pt | 23 pt |
| visionOS | 17 pt | 12 pt |
| watchOS | 16 pt | 12 pt |

Evita pesi Ultralight/Thin/Light per testo piccolo. Pochi typeface. Mantieni gerarchia relativa quando cambia la dimensione del testo.

---

## Samsung Design System + One UI

### Design System (hub)

Fonte: https://developer.samsung.com/design-system

- **Consistenza e chiarezza** su tutta l’esperienza, un unico linguaggio su dispositivi e servizi.
- Esperienza seamless: icone, font, chart condivisi.
- Aree esplicite del sistema: **Icons**, **Fonts** (SamsungOne), **Charts**, **Sound**, **UX Writing**.

### One UI — quattro principi core

Fonte: https://developer.samsung.com/one-ui/index.html

1. **Focus on the task at hand** — Design semplici; percorsi corti e fluidi; priorità al contenuto e alle azioni necessarie.
2. **Interact naturally** — Azioni e motion naturali; schermo diviso in **viewing area** (alto) e **interaction area** (basso) per raggiungere i controlli anche su schermi grandi.
3. **Be visibly comfortable** — Dark mode, tastiera ad alto contrasto, dimensioni/stili di font variabili.
4. **Make things responsive** — Layout che si adattano a device e dimensioni; contenuti/funzioni aggiunti o tolti per usabilità; adattamento alle caratteristiche dell’utente.

Linee guida One UI aggiuntive da consultare quando servono: Structure, Layout, Components, Color, Iconography, Motion, Sound & Haptic, Writing.

### Icone e tipografia Samsung (sintesi da documentazione One UI / SamsungOne)

- Icone: metafore chiare, forme minime e modulari, stroke terminal arrotondati, peso visivo coerente.
- SamsungOne: font universalista, leggibile, localizzato; valori Reliable & Accessible, Contemporary & Innovative, Human & Enduring.

---

## Checklist operativa di Quinn

Per ogni schermata o flusso in revisione:

- [ ] Piattaforma target dichiarata (iOS/iPadOS/macOS/watchOS/visionOS/tvOS / Android·One UI / multi-piattaforma)
- [ ] Principi Apple o One UI applicati esplicitamente (citare quali)
- [ ] Safe area / reachability / viewing vs interaction area rispettati
- [ ] Tipografia entro i minimi; Dynamic Type / font scaling considerati
- [ ] Contrasto e non-dipendenza dal solo colore
- [ ] Coerenza con pattern nativi della piattaforma (non reinventare navigazione di sistema senza motivo)
- [ ] Cross-device: stessa logica, densità e controlli adattati — non lo stesso layout copiato
- [ ] Dissensi rispetto a Irene/Luca/Marta/Nico esplicitati se le guideline di piattaforma confliggono con brand o motion

## Limiti

- Questa sintesi non sostituisce la lettura della pagina HIG/One UI del componente specifico (Navigation bar, Sheets, Pickers, ecc.).
- Non è un’approvazione di conformità App Store / Galaxy Store.
- In caso di conflitto tra HIG e One UI su un prodotto multi-piattaforma: documenta due varianti o un pattern adattivo; non mediare in silenzio.
