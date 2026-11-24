---
name: ricerca-accademica
description: Esegue la ricerca bibliografica specialistica su repository scientifici (ArXiv, IEEE, ACM, NeurIPS, Semantic Scholar), estrae paper seminali e convalida citazioni reali con DOI e BibTeX.
---

# ricerca-accademica — Skill per Claude

Questa skill gestisce la fase di **ricerca bibliografica avanzata e fact-checking accademico** per la redazione di paper scientifici.

---

## 🔍 Obiettivi della Skill

1. **Scansione SOTA (State of the Art)**:
   - Identificare la letteratura seminale e gli articoli di frontiera nel settore dei sistemi multi-agente e dell'AI autonoma.
   - Esplorare repository accademici di riferimento: ArXiv, IEEE Xplore, ACM Digital Library, NeurIPS, ICML, ICLR, ACL.

2. **Tracciamento e Verifica delle Fonti**:
   - Zero allucinazioni: ogni articolo citato deve esistere realmente e disporre di identificatore univoco (DOI o ArXiv ID).
   - Generazione automatica delle schede bibliografiche complete in formato BibTeX:
     - `author`
     - `title`
     - `journal` / `booktitle`
     - `year`
     - `doi` o `eprint`

3. **Mappatura Tematica e Tassonomia delle Scuole di Pensiero**:
   - Classificare i lavori correlati in cluster tematici (es. *Actor Model*, *Blackboard Systems*, *Cooperative Swarms*, *Consensus Mechanisms*, *Memory Augmented Architectures*).
   - Estrarre metriche quantitative, benchmark e risultati empirici dichiarati dagli autori originali.

---

## 🚫 Regola Inviolabile
Non citare mai la skill `ricerca-accademica` o i tool di query all'interno del testo finale del paper. La ricerca deve essere documentata esclusivamente attraverso la rassegna critica della letteratura scientifica e l'elenco delle referenze.
