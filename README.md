# 🏛️ Agenzia Multi-Agente & Academic Paper Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Antigravity Plugin](https://img.shields.io/badge/Antigravity-Plugin%20v1.1-purple.svg)](https://github.com/Marcelloguida00/multiagent-academic-paper)
[![Slash Command](https://img.shields.io/badge/Slash%20Command-%2Fagenzia--multiagente-orange.svg)]()
[![Anti-AI Filter](https://img.shields.io/badge/Anti--AI%20Filter-%2Fsembra--ai-brightgreen.svg)]()

Un'architettura completa a plugin che implementa il comando principale **`/agenzia-multiagente`** per orchestrare una squadra autonoma di agenti specializzati nella ricerca bibliografica scientifica, formalizzazione concettuale e redazione di **paper accademici** (stile IEEE / ACM / Springer), integrata nativamente con il filtro di humanization e de-slopping **`/sembra-ai`**.

---

## ⚡ Comandi Slash Principali

| Comando | Descrizione |
| :--- | :--- |
| **`/agenzia-multiagente`** | Dispiega e coordina i 5 agenti specialistici per condurre la ricerca bibliografica, standardizzare la terminologia e redigere il paper scientifico. |
| **`/sembra-ai`** | Filtro di qualità anti-AI: revisiona ed elimina cliché, formule fisse, pattern simmetrici e regolarità tipiche degli LLM, garantendo uno stile autentico, critico e umano. |

---

## 👥 Ruoli dell'Agenzia (`/agenzia-multiagente`)

1. **Lead Academic Researcher**: Scansione SOTA su repository ufficiali (ArXiv, IEEE Xplore, NeurIPS, ACM). Tracciamento di fonti reali con DOI e metadati verificabili.
2. **System Ontologist**: Bonifica della nomenclatura. Conversione di gergo o termini informali in rigorosa tassonomia accademica (*Decentralized Coordination Protocols*, *Asynchronous Blackboard Memory*, ecc.).
3. **Academic Author**: Redazione formale secondo lo standard IMRaD. **Regola aurea**: zero menzioni di tool interni, prompt o skill software nel testo scientifico.
4. **Anti-AI Quality Gatekeeper (`/sembra-ai`)**: Revisione stilistica obbligatoria prima di approvare qualsiasi sezione.
5. **Meta-Tool Engineer**: Generazione e integrazione di script analitici o skill mancanti necessarie alla ricerca.

---

## 🛡️ Regole Operative Globali (`rules/AGENTS.md`)

- **Nessuna menzione di tool interni**: L'architettura e la metodologia del paper vengono descritte unicamente in termini algoritmici, computazionali e matematici.
- **Font e Tipografia Accademica**: Formattazione rigorosa per compilazione LaTeX (font Computer Modern o Times New Roman).
- **Controllo Bibliografico Rigoroso**: Ogni affermazione deve essere supportata da una fonte reale e verificabile.
- **Passaggio obbligatorio in `/sembra-ai`**: Nessun paragrafo viene considerato definitivo senza aver superato il controllo di de-slopping.

---

## 🚀 Installazione Rapida

Clona la repository nella cartella dei plugin globali di Antigravity:

```bash
git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git ~/.gemini/config/plugins/multiagent-academic-paper
```

Oppure all'interno di un singolo progetto:
```bash
git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git .gemini/plugins/multiagent-academic-paper
```

---

## 📋 Prompt Rapido di Avvio

Una volta caricato il plugin, digita semplicemente:

```markdown
/agenzia-multiagente Ricerca e scrivi un paper accademico approfondito sulle architetture dei sistemi multi-agente autonomi.

Assicurati che:
1. Ogni termine informale o strambo sia convertito in tassonomia formale.
2. Vengano citate unicamente fonti bibliografiche reali con DOI o ArXiv ID.
3. Il paper sia predisposto con font formali per LaTeX (Times / Computer Modern).
4. Nessun riferimento a tool, prompt o skill software interne appaia nel testo.
5. Ogni sezione passi attraverso la revisione di /sembra-ai per eliminare qualunque traccia di stile AI.
```
