# agenzia-multiagente — Skill e Plugin per Claude

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill%20%26%20Plugin-orange.svg)](https://claude.com/claude-code)
[![Slash Command](https://img.shields.io/badge/Slash%20Command-%2Fagenzia--multiagente-blueviolet.svg)]()
[![Anti-AI Quality Gate](https://img.shields.io/badge/Quality%20Gate-%2Fsembra--ai-brightgreen.svg)]()

Una skill per **Claude Code** ([claude.com/claude-code](https://claude.com/claude-code)) e **Claude.ai** che trasforma Claude in un'**agenzia autonoma multi-agente** di ricerca accademica. 

Conduce la scansione dello stato dell'arte (SOTA), normalizza la terminologia scientifica, formalizza i modelli computazionali e redige **paper scientifici peer-reviewed** (in stile IEEE / ACM / LaTeX), sottoponendo obbligatoriamente ogni paragrafo al filtro di humanization e de-slopping **`/sembra-ai`** per eliminare ogni impronta artificiale di scrittura.

---

## ⚡ Comandi Slash Nativi per Claude Code

| Comando | Descrizione |
| :--- | :--- |
| **`/agenzia-multiagente`** | Avvia il coordinatore multi-agente per la ricerca SOTA, la bonifica lessicale, la redazione IMRaD e la verifica delle citazioni. |
| **`/sembra-ai`** | Filtro anti-AI: elimina formule trite, cliché degli LLM, regolarità di punteggiatura e varia il ritmo (burstiness) per garantire una voce accademica umana. |

---

## 📦 Installazione Rapida (1 Click / 1 Comando)

### Windows (PowerShell)
Apri PowerShell ed esegui:
```powershell
irm https://raw.githubusercontent.com/Marcelloguida00/multiagent-academic-paper/main/install.ps1 | iex
```

Oppure manualmente se hai già clonato:
```powershell
# 1. Copia sembra-ai come skill autonoma di primo livello
mkdir "$HOME\.claude\skills\sembra-ai" -Force
copy "$HOME\.claude\skills\agenzia-multiagente\skills\sembra-ai\SKILL.md" "$HOME\.claude\skills\sembra-ai\SKILL.md"

# 2. Copia i comandi slash globali
mkdir "$HOME\.claude\commands" -Force
copy "$HOME\.claude\skills\agenzia-multiagente\.claude\commands\*.md" "$HOME\.claude\commands\"
```

---

### Mac / Linux (Terminal)
Apri il terminale ed esegui:
```bash
curl -fsSL https://raw.githubusercontent.com/Marcelloguida00/multiagent-academic-paper/main/install.sh | bash
```

Oppure manualmente se hai già clonato:
```bash
# 1. Copia sembra-ai come skill autonoma di primo livello
mkdir -p ~/.claude/skills/sembra-ai ~/.claude/commands
cp ~/.claude/skills/agenzia-multiagente/skills/sembra-ai/SKILL.md ~/.claude/skills/sembra-ai/
cp ~/.claude/skills/agenzia-multiagente/.claude/commands/*.md ~/.claude/commands/
```

> ⚠️ **Importante**: Dopo aver installato o aggiornato le skill, **riavvia Claude Code** o avvia una **nuova sessione** per far rilevare a Claude i nuovi comandi e le skill.

---

## 👥 I Ruoli dell'Agenzia Multi-Agente

Claude suddivide autonomamente il lavoro tra 5 ruoli specializzati:

1. **Lead Academic Researcher & Fact-Checker**: Scansiona la letteratura (ArXiv, IEEE Xplore, ACM, NeurIPS, ICLR). Cataloga solo fonti autentiche con DOI e metadati verificabili.
2. **System Ontologist**: Bonifica il lessico: sostituisce termini colloquiali o gergali con una tassonomia accademica formale (*Decentralized Coordination Protocols*, *Asynchronous Blackboard Memory*, *Hierarchical Supervisor-Worker Topologies*).
3. **Academic Author**: Redige il testo secondo lo standard scientifico IMRaD. **Regola aurea**: zero menzioni di tool interni, prompt o skill software nel paper.
4. **Anti-AI Quality Gatekeeper (`/sembra-ai`)**: Revisiona ogni sezione prima del rilascio per eliminare cliché e cadenze artificiali.
5. **Meta-Tool Engineer**: Formalizza componenti e script analitici come moduli algoritmici all'interno del manoscritto.

---

## 🛡️ Regole Operative Inviolabili

- **Nessun leakage di tool o prompt**: Il testo finale descrive solo metodologie formali, architetture computazionali e modelli teorici. Nessuna menzione di Claude, skill software o prompt di sistema.
- **Font e Tipografia Accademica**: Strutturato per la compilazione in LaTeX con i font standard delle conferenze (Computer Modern / Times New Roman).
- **Controllo Bibliografico Reale**: Tutte le fonti citate devono essere reali e rintracciabili tramite DOI o ArXiv ID.
- **Passaggio Obbligatorio in `/sembra-ai`**: Nessun paragrafo viene finalizzato senza aver superato il de-slopping stilistico.

---

## 📋 Master Prompt di Avvio Rapido

Incolla questo prompt in Claude Code o Claude.ai per iniziare:

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

Rilasciato sotto licenza MIT.
