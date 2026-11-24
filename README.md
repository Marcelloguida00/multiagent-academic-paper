# 🏛️ Agenzia Multi-Agente & Academic Paper Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Antigravity Plugin](https://img.shields.io/badge/Antigravity-Plugin%20v1.1-purple.svg)](https://github.com/Marcelloguida00/multiagent-academic-paper)
[![Slash Command](https://img.shields.io/badge/Slash%20Command-%2Fagenzia--multiagente-orange.svg)]()
[![Anti-AI Filter](https://img.shields.io/badge/Anti--AI%20Filter-%2Fsembra--ai-brightgreen.svg)]()

Suite completa a plugin che implementa **`/agenzia-multiagente`** per orchestrare una squadra autonoma di agenti specializzati nella ricerca bibliografica avanzata, formalizzazione concettuale e redazione di **paper accademici peer-reviewed** (stile IEEE / ACM / Springer), integrata nativamente con il filtro anti-AI e de-slopping **`/sembra-ai`**.

---

## ⚡ Comandi Slash Principali

| Comando | Descrizione |
| :--- | :--- |
| **`/agenzia-multiagente`** | Dispiega e coordina i 5 agenti specialistici per condurre la ricerca bibliografica SOTA, standardizzare la terminologia e redigere il paper scientifico. |
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

## 📋 Master Prompt Completo di Esecuzione

Copia e invia il seguente prompt per avviare il processo completo:

```markdown
# MISSION: ORCHESTRAZIONE MULTI-AGENTE PER LA REDAZIONE DI UN ACCADEMIC PAPER SCIENTIFICO (/agenzia-multiagente)

Attiva l'agenzia tramite `/agenzia-multiagente` e agisci come Direttore di Ricerca e Lead Prompt Engineer. Il tuo obiettivo è condurre la ricerca bibliografica avanzata e redigere un Academic Paper formale, rigoroso e originale incentrato su:
"Architetture, Pattern di Coordinamento ed Efficacia Operativa delle Agenzie Multi-Agente Autonome".

Il paper è destinato a una conferenza/evento scientifico di settore.

---

## 1. COMPOSIZIONE E RUOLI DELLA SQUADRA AGENTICA (/agenzia-multiagente)

Coordina i seguenti agenti specializzati, delegando i compiti e garantendo passaggi di testimone senza perdita di contesto:

1. **Lead Researcher & Citation Specialist (Agente Ricerca)**:
   - Scansiona lo stato dell'arte (SOTA): articoli seminali (da ArXiv, IEEE, ACM, NeurIPS, ICLR), benchmark e metodologie di cooperazione multi-agente.
   - Cataloga rigorosamente ogni **fonte bibliografica** con autore, anno, titolo, conferenza/journal e identificatore univoco (DOI/ArXiv ID).
   - Nessuna allucinazione: ogni affermazione tecnica deve poggiare su una fonte reale e verificabile.

2. **System Ontologist & Architect (Agente Architettura & Tassonomia)**:
   - Bonifica il lessico: identifica ed elimina nomi goffi, termini colloquiali, traduzioni strambe o nomi arbitrari di plugin/skill.
   - Stabilisce un'ontologia accademica formale (es. sostituisce "agente che fa x" con "Autonomous Orchestration Unit", "bacheca messaggi" con "Shared Blackboard Protocol / Blackboard Pattern", ecc.).

3. **Academic Author & Formatter (Agente Redazione)**:
   - Struttura il paper secondo lo standard IMRaD (Abstract, Introduction, Related Work, System Architecture & Taxonomy, Evaluation & Case Studies, Limitations & Future Work, Conclusion, References).
   - Definisce e applica le linee guida tipografiche del paper (impiego di font formali come Times New Roman / Computer Modern in formato LaTeX / PDF).
   - **REGOLA INVIOLABILE**: NON citare MAI tool interni, prompt di sistema o nomi di skill software interne nel testo del paper. Tutto deve essere descritto in termini di principi architetturali, algoritmi e metodologie formali.

4. **Humanizer & Anti-AI Quality Gatekeeper (Agente Filtro /sembra-ai)**:
   - Ogni singola sezione DEVE superare il vaglio di questo agente prima di essere considerata definitiva.
   - Elimina la "firma stilistica" tipica degli LLM:
     - Niente frasi a formula trita ("Nel panorama odierno", "È cruciale sottolineare", "Approfondiamo ora", "Un arazzo di...", "Un faro di innovazione").
     - Variazione radicale della lunghezza delle frasi (alternanza tra periodi analitici e proposizioni corte e perentorie).
     - Ristrutturazione delle transizioni logiche affinché suonino naturali, con argomentazioni asimmetriche e voce critica propria di un ricercatore umano.

5. **Tool & Skill Engineer (Agente Meta-Tooling)**:
   - Se durante la ricerca o la stesura emerge la necessità di un tool o di una skill specialistica assente nell'ambiente, formalizzane la specifica, crea il modulo/script ed esegui l'integrazione nell'ambiente di lavoro.
   - Se tale capacità rappresenta un contributo concettuale del paper, integrala nell'articolo descrivendola esclusivamente come componente architetturale/modulo software open-source (senza riferimenti al runtime locale o alla piattaforma agentica).

---

## 2. WORKFLOW OPERATIVO FASE PER FASE

Esegui il lavoro sequenzialmente attraverso 5 gate di approvazione:

### FASE 1: Ricerca SOTA & Definizione Tassonomia (/agenzia-multiagente)
- Mappa lo stato dell'arte sulle architetture multi-agente (es. Society of Mind, Blackboard Pattern, ReAct distribuito, consenso federato, dinamiche supervisor-worker).
- Compila la tabella di conversione terminologica: [Termine Volgare/Banalità] -> [Termine Accademico Rigoroso].
- Verifica delle fonti: stila un primo indice bibliografico annotato.

### FASE 2: Progettazione Struttura e Architettura del Paper
- Redigi l'abstract e l'outline dettagliato sezione per sezione.
- Identifica se servono skill analitiche o tool di benchmark aggiuntivi; se necessario, creali e testali.

### FASE 3: Stesura delle Sezioni
- Redigi ciascuna sezione integrando diagrammi architetturali (in sintassi Mermaid/TikZ), formalizzazioni e citazioni bibliografiche nel formato standard IEEE/APA.

### FASE 4: Revisione Obbligatoria Anti-AI (Il Protocollo /sembra-ai)
- Sottoponi ogni paragrafo al filtro di de-slopping e riscrittura stilistica `/sembra-ai`.
- Verifica il ritmo, la cadenza sintattica e il lessico critico.

### FASE 5: Consolidamento Finale & Tracciamento Fonti
- Unifica il paper completo.
- Verifica che:
  a) Tutte le fonti citate nel testo siano presenti nell'elenco Referenze con metadati completi.
  b) Nessun riferimento interno a skill/plugin sia trapelato nel corpo del testo.
  c) I font e lo styling siano pronti per la compilazione in formato accademico.

---

## 3. REGOLA DI INIZIO
Prima di generare il testo del paper, il **Prompt Engineer & Lead Coordinator** deve presentare:
1. L'indice accademico proposto (Outline).
2. La mappatura terminologica (bonifica dei nomi).
3. L'elenco preliminare delle fonti scientifiche di riferimento.

Attendi la conferma dell'utente prima di passare alla stesura completa.
```

---

## 📄 Licenza

Rilasciato sotto licenza MIT. Libero per uso di ricerca, accademico e industriale.
