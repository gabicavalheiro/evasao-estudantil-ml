# ADR-005 – Métrica principal e tratamento do desbalanceamento

- **Status:** Aceito
- **Contexto:** Acurácia engana quando as classes são desbalanceadas, e deixar de identificar um aluno em risco costuma custar mais do que um alarme falso.
- **Decisão:** F1 da classe "evadiu" como métrica de seleção, acompanhada de recall, precisão, ROC-AUC e acurácia. O desbalanceamento é tratado com `class_weight` balanceado nos modelos, sem reamostragem. O limiar de decisão é 0,5 (`config.THRESHOLD`).
- **Alternativas consideradas:** otimizar apenas recall (gera muitos falsos positivos); SMOTE ou subamostragem (podem criar dados artificiais ou descartar informação, e precisariam ficar dentro da pipeline).
- **Consequências:** A seleção equilibra precisão e recall. Se a instituição preferir priorizar a identificação de todos os alunos em risco, o limiar pode ser reduzido em `config.py`, aceitando mais falsos positivos.
