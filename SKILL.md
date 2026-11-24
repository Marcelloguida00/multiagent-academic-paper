---
name: agenzia-multiagente
description: Orchestra un'agenzia multi-agente per Claude per la ricerca bibliografica avanzata, la formalizzazione concettuale e la redazione di paper scientifici formali, con filtro anti-AI (/sembra-ai) integrato.
---

# agenzia-multiagente — Skill per Claude

Questa skill trasforma Claude in un'agenzia autonoma multi-agente per condurre ricerche approfondite su letteratura scientifica verificata e redigere paper accademici di livello peer-reviewed.

## Trigger e Comandi
- `/agenzia-multiagente`: Avvia l'orchestratore, la ricerca bibliografica e la stesura del paper accademico.
- `/sembra-ai`: Revisiona il testo eliminando ogni pattern stilistico artificiale degli LLM (de-slopping, burstiness, tono critico).

## Workflow Operativo in Claude

1. **Fase 1: Mappatura SOTA e Bonifica Terminologica**
   - Raccoglie fonti autentiche da ArXiv, IEEE, ACM, NeurIPS con metadati completi (DOI, anno, autori).
   - Genera la tabella di conversione: converte gergo informale in lessico accademico rigoroso.

2. **Fase 2: Strutturazione e Formalizzazione Architetturale**
   - Redige outline dettagliato in formato IMRaD e definisce diagrammi concettuali.
   - Formalizza le comunicazioni inter-agente (blackboard pattern, dynamic consensus).

3. **Fase 3: Stesura con Zero Tool Leakage**
   - Nessun riferimento a prompt, runtime, skill software o tool interni nel paper. Tutto è descritto come formalismo scientifico.

4. **Fase 4: Filtro di De-slopping (/sembra-ai)**
   - Riscrive ogni paragrafo alternando periodi ampi a frasi secche e assertive.
   - Elimina formule trite (*"nel panorama odierno"*, *"è cruciale notare"*, elenchi simmetrici a 3 punti).

5. **Fase 5: Validazione Bibliografica e Tipografica**
   - Verifica la rispondenza di ogni citazione e imposta la compilazione per LaTeX (Computer Modern o Times New Roman).
