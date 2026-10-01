# ADR-007 – Diagnóstico de overfitting e underfitting

- **Status:** Aceito
- **Contexto:** O enunciado exige justificar se houve overfitting ou underfitting, e a justificativa precisa ser baseada em evidência, não em impressão.
- **Decisão:** Comparar o F1 de treino e de validação nas dobras, o F1 do teste e o ROC-AUC, e gerar a curva de aprendizado. Critérios (`config.py`):
  - underfitting: F1 de treino e de validação abaixo de 0,70;
  - overfitting: F1 de treino maior que o de validação em mais de 0,10 (entre 0,05 e 0,10 é tratado como leve);
  - bom ajuste: nenhum dos casos acima.
  Um F1 de teste próximo ao da validação indica que a estimativa se sustentou em dados nunca vistos.
- **Alternativas consideradas:** olhar apenas o gráfico (subjetivo); usar apenas o teste (não separa overfitting de outros problemas).
- **Consequências:** O relatório `reports/diagnostico.md` traz números e texto prontos. Os limites são heurísticos: em problemas intrinsecamente difíceis, um F1 abaixo de 0,70 com treino e validação próximos pode refletir limite dos dados, e não falta de capacidade do modelo. A conclusão final deve combinar a tabela com a curva de aprendizado.
