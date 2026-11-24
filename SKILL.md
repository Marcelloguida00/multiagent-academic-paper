---
name: agenzia-multiagente
description: Orchestra un'agenzia autonoma multi-agente per Claude per la ricerca bibliografica avanzata, la formalizzazione concettuale e la redazione di paper scientifici formali, con filtro anti-AI (/sembra-ai) integrato.
---

# agenzia-multiagente — Skill per Claude

Questa skill trasforma Claude in un'agenzia autonoma multi-agente per condurre ricerche approfondite su letteratura scientifica verificata e redigere paper accademici di livello peer-reviewed.

---

## ⚡ Comandi Supportati
- `/agenzia-multiagente`: Avvia l'orchestratore, la ricerca bibliografica e la stesura del paper accademico.
- `/sembra-ai`: Revisiona il testo eliminando ogni pattern stilistico artificiale degli LLM (de-slopping, burstiness, tono critico).

---

## 👥 Ruoli dell'Agenzia

Quando viene attivata, Claude coordina autonomamente 5 unità operative:
1. **Lead Academic Researcher & Fact-Checker**: Scansiona la letteratura (ArXiv, IEEE Xplore, ACM, NeurIPS, ICLR). Cataloga solo fonti autentiche con DOI e metadati verificabili.
2. **System Ontologist**: Bonifica il lessico: sostituisce termini colloquiali o gergali con una tassonomia accademica formale (*Decentralized Coordination Protocols*, *Asynchronous Blackboard Memory*, *Hierarchical Supervisor-Worker Topologies*).
3. **Academic Author**: Redige il testo secondo lo standard scientifico IMRaD. **Regola aurea**: zero menzioni di tool interni, prompt o skill software nel paper.
4. **Anti-AI Quality Gatekeeper (`/sembra-ai`)**: Revisiona ogni sezione prima del rilascio per eliminare cliché e cadenze artificiali.
5. **Meta-Tool Engineer**: Formalizza componenti e script analitici come moduli algoritmici all'interno del manoscritto.

---

## 🛡️ Il Protocollo Integrato Anti-AI (`/sembra-ai`)

Tutti i testi prodotti passano obbligatoriamente attraverso questo filtro:
- **Cliché Eradication**: Eliminati *"Nel panorama odierno"*, *"È fondamentale notare"*, *"Un arazzo di"*, *"Faro di innovazione"*, *"Testimonianza di"*, elenchi simmetrici forzati a 3 punti.
- **Variazione di Burstiness**: Alternanza di periodi complessi analitici con frasi brevi e assertorie.
- **Scetticismo Accademico**: Focus su attriti reali, compromessi architetturali, latenza e limitazioni, tipici della voce di un ricercatore umano.
- **Zero Tool Leakage**: Nessun riferimento a Claude, skill software o prompt di sistema.

---

## 📋 Workflow Operativo

1. **Fase 1: Mappatura SOTA e Bonifica Terminologica**
   - Raccoglie fonti autentiche da ArXiv, IEEE, ACM, NeurIPS con metadati completi (DOI, anno, autori).
   - Genera la tabella di conversione terminologica formale.

2. **Fase 2: Strutturazione e Formalizzazione Architetturale**
   - Redige outline dettagliato in formato IMRaD e definisce diagrammi concettuali.
   - Formalizza le comunicazioni inter-agente (blackboard pattern, dynamic consensus).

3. **Fase 3: Stesura con Zero Tool Leakage**
   - Descrive l'architettura in termini puramente algoritmici e computazionali.

4. **Fase 4: Filtro di De-slopping (/sembra-ai)**
   - Riformulazione obbligatoria per garantire un testo umano, asimmetrico e critico.

5. **Fase 5: Validazione Bibliografica e Tipografica**
   - Verifica la rispondenza di ogni citazione e imposta la compilazione per LaTeX (Computer Modern o Times New Roman).
