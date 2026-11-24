---
name: design-scientifico
description: Progetta figure scientifiche, diagrammi architetturali per sistemi multi-agente (TikZ, Mermaid, SVG), grafici di benchmark, tabelle professionali e layout visivo per paper accademici.
---

# design-scientifico — Skill per Claude

Questa skill gestisce l'intero comparto **visivo, grafico e architetturale** per la redazione di paper scientifici e presentazioni per eventi/conferenze.

---

## 🎨 Aree di Intervento

### 1. Diagrammi di Architettura Multi-Agente
Genera diagrammi concettuali e tecnici ad alta fedeltà rappresentanti:
- **Topologie di rete agentica**: Hub-and-Spoke, Blackboard asincrona, grafi di consenso decentralizzato, cluster gerarchici.
- **Diagrammi di sequenza temporale**: Protocolli di handshake, negoziazione, task decomposition e ricongiungimento dei risultati.
- **Formati supportati**:
  - **LaTeX TikZ**: codice vettoriale nativo compilabile direttamente nel documento senza perdita di risoluzione.
  - **Mermaid**: diagrammi dinamici visualizzabili in anteprima Markdown, GitHub e web.
  - **DOT / Graphviz**: rappresentazioni formali di grafi di dipendenza tra agenti.

### 2. Tabelle Accademico-Scientifiche
- Struttura tabelle eleganti per confrontare architetture, metriche e benchmark secondo lo standard tipografico `booktabs` (senza linee verticali, con gerarchia chiara tra header, dati e sintesi).

### 3. Grafici di Benchmark & Prestazioni
- Progetta grafici vettoriali (PGFPlots per LaTeX o schemi di benchmark) che illustrano:
  - Latenza vs numero di agenti cooperanti.
  - Consumo di token e overhead di comunicazione.
  - Tasso di convergenza e riduzione dell'entropia di allucinazione.

### 4. Graphical Abstract & Materiale per l'Evento
- **Graphical Abstract**: Sintesi visiva in una singola figura riassuntiva ad alto impatto per il comitato di revisione dell'evento.
- **Slide & Poster Layout**: Schemi grafici pronti per la presentazione scientifica sul palco dell'evento.

---

## 📐 Standard Tipografici e Norme di Pubblicazione
- **Color Palette**: Palette accademica sobria, ottimizzata per la stampa monocromatica o conforme agli standard di accessibilità per daltonici (*Colorblind-safe* come Viridis o Tol).
- **Dimensionamento**: Figure dimensionate esattamente per colonne singole (3.5 pollici / ~88 mm) o doppie colonne (7.0 pollici / ~180 mm) secondo gli standard IEEE/ACM.
- **Didascalie (Captions)**: Didascalie auto-consistenti e descrittive che spiegano simboli, frecce e acronimi senza costringere il lettore a cercare nel testo.
