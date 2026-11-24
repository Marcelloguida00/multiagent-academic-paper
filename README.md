# 🎓 Multi-Agent Academic Paper & Research Agency

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Antigravity Plugin](https://img.shields.io/badge/Antigravity-Plugin%20v1.0-purple.svg)](https://github.com/Marcelloguida00/multiagent-academic-paper)
[![Humanized Output](https://img.shields.io/badge/Anti--AI%20Filter-Active%20(%2Fsembra--ai)-brightgreen.svg)]()

Un'architettura completa a plugin per orchestrare un'**agenzia autonoma multi-agente** specializzata nella ricerca bibliografica scientifica, formalizzazione teorica e redazione di **paper accademici** (stile IEEE / ACM / Springer), integrata con un motore di de-slopping e humanization (`/sembra-ai`) per garantire un testo autentico, critico e privo dei cliché tipici dell'AI.

---

## ⚡ Perché un Plugin è più potente di una singola Skill?

Una singola skill offre solo istruzioni operative. Questo **Plugin** raggruppa in un unico modulo inscindibile:
1. **Due Skill Specializzate**:
   - `multiagent-academic-paper`: Orchestrazione della ricerca, disegno architetturale, stesura IMRaD, citazioni bibliografiche verificate e compilazione LaTeX.
   - `sembra-ai`: Motore di revisione anti-AI, humanization e de-slopping stilistico.
2. **Regole Operative Globali (`rules/AGENTS.md`)**:
   - Regola ferrea: **nessuna menzione di tool interni o skill** nel testo scientifico.
   - Bonifica sistematica della terminologia (traduzione automatica da gergo informale a tassonomia accademica).
   - Verifica obbligatoria delle fonti (DOI, ArXiv, conferenze peer-reviewed).
3. **Template Pronti all'Uso**: Template LaTeX (`.tex`) e Markdown (`.md`) preimpostati secondo gli standard di conferenza IEEE.

---

## 👥 La Squadra Agenti Specializzata

| Ruolo Agente | Responsabilità Primaria | Standard di Qualità |
| :--- | :--- | :--- |
| **Lead Researcher** | Scansione SOTA su ArXiv, IEEE, NeurIPS, ACM. | Solo fonti reali e verificabili con DOI. |
| **System Ontologist** | Bonifica terminologica e standardizzazione della tassonomia. | Eliminazione di termini ingenui o gergali. |
| **Academic Author** | Stesura del manoscritto scientifico in formato IMRaD. | Zero leakage di tool interni o prompt. |
| **Anti-AI Gatekeeper (`/sembra-ai`)** | De-slopping, variazione di ritmo (burstiness) e tono critico. | Testo indistinguibile da scrittura umana esperta. |
| **Meta-Tool Engineer** | Creazione dinamica di moduli o script analitici mancanti. | Formalizzazione algoritmica nel paper. |

---

## 🛡️ Il Protocollo Anti-AI (`/sembra-ai`)

Tutti i testi prodotti passano obbligatoriamente attraverso il filtro di de-slopping:
- ❌ **Rimozione cliché LLM**: Eliminati *"Nel panorama odierno"*, *"È fondamentale notare"*, *"Un arazzo di"*, *"Faro di innovazione"*, *"Testimonianza di"*, elenchi simmetrici forzati a 3 punti.
- ✍️ **Variazione di Burstiness**: Alternanza di periodi complessi analitici con frasi brevi e assertorie.
- 🔬 **Scetticismo Accademico**: Focus su attriti reali, compromessi architetturali, latenza e limitazioni, tipici della voce di un ricercatore umano.

---

## 🚀 Come Installare il Plugin

### Installazione Diretta (Antigravity)
Clona la repository direttamente nella cartella dei plugin globali o del tuo workspace:

```bash
# Installazione globale in Antigravity
git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git ~/.gemini/config/plugins/multiagent-academic-paper
```

Oppure in un progetto specifico:
```bash
git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git .gemini/plugins/multiagent-academic-paper
```

Il plugin verrà rilevato e caricato automaticamente.

### Utilizzo con altri Agenti (Claude Code / Cursor / Codex)
I file in `skills/` e `rules/AGENTS.md` sono compatibili con qualsiasi ambiente basato su agenti di programmazione o LLM.

---

## 📋 Master Prompt di Avvio

Una volta installato il plugin, incolla questo prompt nel tuo assistente o coordinatore:

```markdown
Avvia l'agenzia autonoma multi-agente per condurre la ricerca scientifica e redigere il paper accademico sul tema:
"Architetture e Pattern di Coordinamento nelle Agenzie Multi-Agente Autonome".

Vincoli operativi:
1. Esegui la bonifica terminologica di ogni termine informale.
2. Cita esclusivamente fonti bibliografiche reali con DOI o ArXiv ID.
3. Applica formalmente i font accademici (Computer Modern / Times New Roman) nei template.
4. Nessun riferimento a skill, tool software o prompt deve apparire nel paper.
5. Sottoponi ogni paragrafo al filtro di revisione /sembra-ai prima del consolidamento finale.
```

---

## 📄 Licenza

Rilasciato sotto licenza MIT. Libero per uso di ricerca, accademico e industriale.
