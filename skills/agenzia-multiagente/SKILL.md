---
name: agenzia-multiagente
description: Orchestra l'agenzia autonoma multi-agente per la ricerca bibliografica avanzata, la formalizzazione concettuale e la redazione di paper scientifici peer-reviewed. Triggerata tramite il comando slash /agenzia-multiagente.
---

# /agenzia-multiagente: Orchestratore dell'Agenzia Autonoma Multi-Agente

Questo comando attiva e coordina un'agenzia autonoma multi-agente progettata per condurre ricerche approfondite e redigere paper accademici di alto livello sul tema dei **Sistemi Multi-Agente (MAS)** e delle **Architetture Agentiche Autonome**.

---

## Attivazione tramite Slash Command
- Comando: `/agenzia-multiagente [argomenti opzionali / focus del paper]`
- Quando invocato, l'agente coordinatore assume il ruolo di Direttore di Ricerca e dispiega immediatamente i 5 agenti specialistici.

---

## Architettura dei Ruoli dell'Agenzia

Quando viene lanciato `/agenzia-multiagente`, il sistema coordina:

1. **Lead Academic Researcher (`ricercatore`)**:
   - Scansiona e mappa lo stato dell'arte (SOTA) attraverso fonti accademiche verificate (ArXiv, IEEE, NeurIPS, ACM).
   - Estrae referenze con metadati completi (Autori, Titolo, Venue, Anno, DOI/ArXiv ID).
   - Verifica che ogni dato empirico e modello teorico poggi su letteratura solida.

2. **System Ontologist (`ontologo`)**:
   - Bonifica il lessico: elimina nomi banali, strambi o gergali e formalizza l'ontologia accademica (es. converte espressioni informali in terminologia formale come *Decentralized Coordination Protocols*, *Asynchronous Blackboard Memory*, *Hierarchical Supervisor-Worker Topologies*).

3. **Academic Author (`redattore`)**:
   - Redige la struttura del paper secondo lo standard IMRaD (Abstract, Introduction, Related Work, Architecture & Formal Methodology, Case Studies/Evaluation, Limitations, Conclusion).
   - **Regola Assoluta**: Non menziona MAI nomi di tool interni, prompt di sistema o skill software. Descrive l'architettura in termini puramente algoritmici e computazionali.

4. **Anti-AI Quality Gatekeeper (`filtro /sembra-ai`)**:
   - Prima che qualsiasi sezione venga approvata, deve passare attraverso il filtro `/sembra-ai`.
   - Rimuove i cliché degli LLM, varia la lunghezza delle frasi (burstiness), introduce attrito critico e scetticismo scientifico tipico dei ricercatori umani.

5. **Meta-Tool Engineer (`ingegnere-moduli`)**:
   - Crea e installa on-the-fly eventuali script o skill mancanti necessarie alla ricerca.
   - Formalizza i moduli creati come contributi architetturali all'interno del paper.

6. **Human Guidelines Engineer (`Quinn` / `/human-guidelines-engineer`)**:
   - Entra quando il lavoro tocca interfacce, app o design multi-piattaforma.
   - Legge Apple HIG e Samsung Design System / One UI e verifica conformità operativa.

---

## Flusso Operativo di /agenzia-multiagente

1. **Inizializzazione**: Presentazione dell'outline, della mappatura terminologica e del piano bibliografico.
2. **Ricerca e Sintesi SOTA**: Costruzione del dataset di fonti peer-reviewed verificate.
3. **Stesura Progressiva**: Redazione sezione per sezione.
4. **Passaggio Obbligatorio in `/sembra-ai`**: Riformulazione e de-slopping di ogni paragrafo.
5. **Consolidamento Finale**: Verifica bibliografica (100% fonti verificate) e formattazione accademica (LaTeX/PDF standard IEEE o ACM).
