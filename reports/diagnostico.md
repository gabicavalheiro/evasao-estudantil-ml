# Diagnóstico de overfitting e underfitting

Modelo final: **Regressão Logística** | hiperparâmetros: `{'C': 0.0745934328572655}`

| Conjunto | F1 | Recall | Precisão | ROC-AUC | Acurácia |
|---|---|---|---|---|---|
| Treino (média das dobras) | 0.793 | 0.810 | 0.777 | 0.919 | 0.864 |
| Validação cruzada (5 dobras) | 0.785 | 0.803 | 0.768 | 0.912 | 0.858 |
| Treino completo (após refit) | 0.793 | 0.808 | 0.778 | 0.918 | 0.864 |
| Teste (dados nunca vistos) | 0.815 | 0.838 | 0.793 | 0.936 | 0.878 |

**Resultado: bom ajuste.**

O F1 no treino (0.793) e na validação (0.785) são próximos (diferença de 0.008) e acima de 0.70. Não há evidência de overfitting nem de underfitting. No ROC-AUC, a diferença treino-validação é 0.007. O F1 no teste (0.815) difere 0.031 da validação cruzada, o que indica que a estimativa da validação se manteve em dados nunca vistos.

## Critérios usados
- Underfitting: F1 de treino e de validação abaixo de 0.70.
- Overfitting: F1 de treino maior que o de validação em mais de 0.10; entre 0.05 e 0.10 é considerado leve.
- Esses limites são heurísticos; a leitura deve ser feita junto da curva de aprendizado (`figures/06_curva_aprendizado.png`).
