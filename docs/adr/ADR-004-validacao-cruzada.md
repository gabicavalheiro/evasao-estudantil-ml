# ADR-004 – Validação cruzada estratificada em 5 dobras

- **Status:** Aceito
- **Contexto:** É preciso estimar desempenho e estabilidade sem tocar no conjunto de teste, e com dados suficientes em cada dobra para a classe minoritária.
- **Decisão:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` sobre o conjunto de treino, para a comparação de modelos, a busca de hiperparâmetros e a curva de aprendizado. São registradas média e desvio padrão de treino e validação.
- **Alternativas consideradas:** hold-out simples (estimativa instável); 10 dobras (custo maior sem ganho relevante para o tamanho da base); validação cruzada aninhada (mais rigorosa, porém cara e além do escopo).
- **Consequências:** A estimativa é mais robusta que um único hold-out. A comparação entre treino e validação de cada dobra alimenta o diagnóstico de overfitting (ADR-007). A nota de validação do melhor modelo da busca é levemente otimista por ter sido escolhida entre várias combinações, o que é conferido com o conjunto de teste.
