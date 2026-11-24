# agenzia-multiagente — Suite Completa di Skill per Claude

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-6%20Skills%20Included-orange.svg)](https://claude.com/claude-code)
[![Slash Command](https://img.shields.io/badge/Slash%20Commands-6%20Included-blueviolet.svg)]()
[![Anti-AI Quality Gate](https://img.shields.io/badge/Quality%20Gate-%2Fsembra--ai-brightgreen.svg)]()

Una suite modulare per **Claude Code** ([claude.com/claude-code](https://claude.com/claude-code)) e **Claude.ai** che fornisce **6 skill specializzate** coordinate da un orchestratore multi-agente per la ricerca bibliografica, il design delle figure/architetture e la stesura di paper accademici scientifici formali.

---

## ⚡ Le 6 Skill & Comandi Slash Inclusi

| Skill & Comando Slash | Ruolo e Funzione |
| :--- | :--- |
| **`/agenzia-multiagente`** | **Master Orchestrator**: coordina l'intero team, distribuisce i compiti e gestisce il workflow dall'outline alla chiusura. |
| **`/design-scientifico`** | **Architectural & Visual Designer**: progetta diagrammi di sistema (TikZ, Mermaid, SVG), topologie multi-agente, grafici di benchmark, tabelle `booktabs` e il *Graphical Abstract* per l'evento. |
| **`/ricerca-accademica`** | **Fact-Checker & Researcher**: ricerca paper seminali su ArXiv, IEEE, ACM, NeurIPS, estraendo metadati e DOI reali. |
| **`/bonifica-tassonomia`** | **Ontologist**: bonifica termini informali, traduzioni goffe o gergali in una rigorosa ontologia scientifica. |
| **`/scrittura-paper`** | **Academic Writer**: redige il paper in formato IMRaD (LaTeX / IEEE / ACM), con zero tool leakage e formule matematiche. |
| **`/sembra-ai`** | **Anti-AI Quality Gate**: filtro obbligatorio di de-slopping, variazione di burstiness e riscrittura in tono accademico umano. |

---

## 🎨 Cosa fa la Skill di Design (`/design-scientifico`)?

La skill di design è stata creata appositamente per dare al paper una veste visiva e grafica impeccabile conforme agli standard delle conferenze:
1. **Diagrammi di Architettura Multi-Agente**: genera il codice vettoriale nativo in LaTeX TikZ o Mermaid per rappresentare grafi di cooperazione tra agenti, scambi di messaggi asincroni (blackboard pattern) e flussi di consenso.
2. **Graphical Abstract & Poster per l'Evento**: crea la sintesi visuale del paper pronta per essere presentata al comitato scientifico o proiettata durante l'evento.
3. **Tabelle e Grafici di Benchmark**: formatta tabelle conformi allo standard `booktabs` e genera grafici comparativi su latenza, scalabilità del numero di agenti e riduzione degli errori.
4. **Layout Tipografico IEEE/ACM**: gestisce l'impaginazione a doppia colonna, la risoluzione delle figure (300 DPI) e le palette accessibili *colorblind-friendly*.

---

## 📦 Installazione Rapida in 1 Comando

### Windows (PowerShell)
Apri PowerShell ed esegui:
```powershell
irm https://raw.githubusercontent.com/Marcelloguida00/multiagent-academic-paper/main/install.ps1 | iex
```

### Mac / Linux (Terminal)
Apri il terminale ed esegui:
```bash
curl -fsSL https://raw.githubusercontent.com/Marcelloguida00/multiagent-academic-paper/main/install.sh | bash
```

> Lo script installa automaticamente **tutte e 6 le skill** in `~/.claude/skills/` e **tutti e 6 i comandi slash** in `~/.claude/commands/`.

---

## 🔄 Come Avviare dopo l'Installazione

1. Chiudi la sessione corrente di Claude Code (`/exit`).
2. Riapri Claude Code digitando:
   ```bash
   claude
   ```
3. Digita il comando desiderato, oppure avvia la missione completa:
   ```markdown
   /agenzia-multiagente Ricerca e scrivi un paper accademico sui sistemi multi-agente autonomi, includendo i diagrammi architetturali e il graphical abstract con /design-scientifico.
   ```

---

## 🛡️ Regole Operative Inviolabili

- **Nessun leakage di tool o prompt**: Il testo finale descrive solo metodologie formali, architetture computazionali e modelli teorici. Nessuna menzione di Claude, skill software o prompt di sistema.
- **Font e Tipografia Accademica**: Strutturato per la compilazione in LaTeX con i font standard delle conferenze (Computer Modern / Times New Roman).
- **Controllo Bibliografico Reale**: Tutte le fonti citate devono essere reali e rintracciabili tramite DOI o ArXiv ID.
- **Passaggio Obbligatorio in `/sembra-ai`**: Nessun paragrafo viene finalizzato senza aver superato il de-slopping stilistico.

---

## 📄 Licenza
MIT License.
