# agenzia-multiagente — Suite Completa di Skill per Claude

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-10%20Skills%20Included-orange.svg)](https://claude.com/claude-code)
[![Slash Command](https://img.shields.io/badge/Slash%20Commands-10%20Included-blueviolet.svg)]()
[![Anti-AI Quality Gate](https://img.shields.io/badge/Quality%20Gate-%2Fsembra--ai-brightgreen.svg)]()

Una suite modulare per **Claude Code** ([claude.com/claude-code](https://claude.com/claude-code)) e **Claude.ai** che fornisce **10 skill specializzate** (ricerca, design architetturale, stesura, sicurezza, crittografia, audit legale e filtro anti-AI) coordinate da un orchestratore multi-agente per la redazione di paper scientifici formali.

---

## ⚡ La Suite delle 10 Skill & Comandi Slash

| Skill & Comando Slash | Ruolo Operativo |
| :--- | :--- |
| **`/agenzia-multiagente`** | **Master Orchestrator**: coordina tutte le squadre, assegna i task e supervisiona l'intero ciclo scientifico. |
| **`/ricerca-accademica`** | **Fact-Checker & Researcher**: ricerca paper seminali su ArXiv, IEEE, ACM, NeurIPS con metadati e DOI reali. |
| **`/bonifica-tassonomia`** | **Ontologist**: bonifica termini informali, traduzioni goffe o gergali in una rigorosa ontologia scientifica formale. |
| **`/design-scientifico`** | **Visual Designer**: progetta diagrammi di sistema (TikZ, Mermaid, SVG), topologie multi-agente, grafici di benchmark, tabelle `booktabs` e Graphical Abstract. |
| **`/scrittura-paper`** | **Academic Writer**: redige il paper in formato IMRaD (LaTeX / IEEE / ACM), con formule matematiche e zero tool-leakage. |
| **`/sembra-ai`** | **Anti-AI Quality Gate**: filtro obbligatorio di de-slopping, burstiness e riscrittura critica in voce accademica umana. |
| **`/security-audit`** | **Security Reviewer**: audit di sicurezza difensivo, analisi delle trust boundaries e protezione da prompt injection tra agenti. |
| **`/crittografia`** | **Crypto Specialist**: protocolli di cifratura inter-agente (AES-GCM, Ed25519, X25519), canali sicuri E2EE e firme crittografiche. |
| **`/legal-audit`** | **Compliance & AI Act**: conformità normativa (EU AI Act, GDPR, accountability, catena di responsabilità degli agenti autonomi). |
| **`/ig-audit`** | **Dissemination & Impact**: metriche di impatto, post-mortem e strategie di divulgazione dei risultati per l'evento. |

---

## 📦 Installazione Rapida in 1 Comando

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Marcelloguida00/multiagent-academic-paper/main/install.ps1 | iex
```

### Mac / Linux (Terminal)
```bash
curl -fsSL https://raw.githubusercontent.com/Marcelloguida00/multiagent-academic-paper/main/install.sh | bash
```

> Lo script installa automaticamente **tutte e 10 le skill** in `~/.claude/skills/` e **tutti e 10 i comandi slash** in `~/.claude/commands/`.

---

## 📋 Master Prompt Autonomo (Paper Auto-Referenziale sull'Agenzia)

Incolla questo prompt in Claude Code:

```markdown
/agenzia-multiagente

Agisci come Direttore di Ricerca e Lead Prompt Engineer di un'Agenzia Multi-Agente Autonoma.
Il tuo obiettivo è redigere un Academic Paper formale, rigoroso e originale che descrive scientificamente L'AGENZIA STESSA (architettura auto-referenziale di un'agenzia autonoma multi-agente a 20 squadre e 80 agenti).

---

### SCELTA DEL TITOLO:
Scegli tu autonomamente il titolo scientifico definitivo, proponendo 3 alternative di alto profilo accademico (stile IEEE / ACM) incentrate su scalabilità, crittografia inter-agente, conformità legale AI Act e orchestrazione a memoria condivisa, e seleziona la più autorevole.

---

### ATTIVAZIONE DI TUTTE LE SQUADRE E DELLE SKILL:
1. **Ricerca SOTA (/ricerca-accademica)**: Mappa la letteratura (Actor Model di Hewitt, Society of Mind di Minsky, architetture a lavagna Blackboard, protocolli FIPA-ACL, consenso distribuito e benchmark recenti). Cita solo fonti reali con DOI o ArXiv ID.
2. **Bonifica Lessicale (/bonifica-tassonomia)**: Elimina qualsiasi gergo informale (es. converti "bot/agenti" in "Specialized Autonomous Units", "bacheca" in "Asynchronous Shared-Memory Blackboard Protocol", "supervisore" in "Hierarchical Dispatcher").
3. **Sicurezza & Crittografia (/security-audit + /crittografia)**: Formalizza nel paper i canali di comunicazione sicuri tra agenti (firme digitali Ed25519, canali cifrati a chiave asimmetrica per evitare prompt injection e man-in-the-middle).
4. **Conformità Normativa (/legal-audit)**: Dedica una sottosezione all'analisi di conformità con l'EU AI Act (sistemi ad alto rischio, tracciabilità dei log decisionali, supervisione umana e accountability).
5. **Visual Architecture & Design (/design-scientifico)**: Disegna i diagrammi architetturali vettoriali completi in LaTeX TikZ e Mermaid, le tabelle comparative in stile booktabs e il Graphical Abstract dell'agenzia.
6. **Redazione Scientifica (/scrittura-paper)**: Struttura il paper secondo lo standard IMRaD completo (Title & Abstract, Introduction, Related Work, Formal Multi-Squad Architecture, Cryptographic & Security Protocols, Empirical Overhead Analysis, Legal & Ethical Governance, Limitations, Conclusion, References).
7. **Filtro Anti-AI (/sembra-ai)**: Sottoponi ogni paragrafo a de-slopping obbligatorio: varia la lunghezza delle frasi (burstiness), rimuovi i cliché degli LLM ("Nel panorama odierno", "È fondamentale notare", elenchi simmetrici a 3 punti) e mantieni una voce accademica critica e umana.

---

### REGOLE INVIOLABILI:
1. **ZERO TOOL LEAKAGE**: Non citare mai Claude, prompt o nomi di file interni nel corpo del paper. L'agenzia deve essere descritta come sistema computazionale teorico e applicato.
2. **OUTPUT COMPLETI SU DISCO**: Scrivi e genera direttamente nella directory:
   - `paper.tex` (sorgente LaTeX completo in stile IEEE a due colonne)
   - `PAPER.md` (versione Markdown completa per lettura immediata)
   - `references.bib` (database BibTeX verificato al 100%)

Inizia subito proponendo le 3 opzioni di titolo e l'outline delle sezioni prima della redazione completa.
```

---

## 📄 Licenza
MIT License.
