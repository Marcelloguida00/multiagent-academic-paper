---
name: scrittura-paper
description: Redige l'academic paper in formato scientifico formale IMRaD (IEEE/ACM/LaTeX), formalizza modelli computazionali e diagrammi architetturali con zero tool-leakage.
---

# scrittura-paper — Skill per Claude

Questa skill gestisce la **redazione formale del manoscritto accademico** strutturato secondo gli standard internazionali delle conferenze e dei journal scientifici.

---

## 📝 Struttura del Manoscritto (Formato IMRaD)

1. **Titolo & Abstract**:
   - Titolo rigoroso ed esplicativo dell'architettura e del contributo metodologico.
   - Abstract sintetico (150-250 parole): contesto, problema di coordinamento, architettura proposta, risultati empirici, conclusioni.
2. **1. Introduction**:
   - Motivazione teorica del passaggio da modelli monolitici a sistemi agentici distribuiti.
   - Definizione formale degli obiettivi e contributi originali dell'articolo.
3. **2. Related Work**:
   - Analisi critica della letteratura SOTA suddivisa per paradigmi di coordinamento.
4. **3. System Architecture & Formal Methodology**:
   - Formalizzazione matematica dei componenti (stati, transizioni, topologie di comunicazione).
   - Diagrammi architetturali concettuali (Mermaid / TikZ).
5. **4. Empirical Evaluation & Case Studies**:
   - Benchmark su carichi di lavoro complessi: latenza, propagazione degli errori, consumo computazionale.
6. **5. Limitations & Future Directions**:
   - Analisi trasparente dei limiti intrinseci (non-determinismo, stallo comunicativo).
7. **6. Conclusion**:
   - Sintesi delle implicazioni teoriche e prospettive future.
8. **References**:
   - Bibliografia completa conforme agli standard IEEE o ACM.

---

## 🎨 Linee Guida Tipografiche e Font
- Impostazione per compilazione LaTeX (font accademici: *Computer Modern* o *Times New Roman* tramite `\usepackage{times}`).
- Dicitura formule matematiche con notazione formale.

---

## 🚫 Regola Inviolabile: Zero Tool Leakage
Nessuna menzione di runtime, prompt di sistema, framework locali o nomi di skill software. Tutto deve essere descritto come principio algoritmico, protocollo di rete o architettura computazionale.
