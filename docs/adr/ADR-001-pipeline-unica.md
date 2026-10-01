# ADR-001 – Pré-processamento e modelo em uma única pipeline

- **Status:** Aceito
- **Contexto:** A base mistura variáveis numéricas e categóricas. Se imputação, escala ou encoding forem aplicados antes da validação cruzada, estatísticas do conjunto de validação contaminam o treino (data leakage) e as métricas ficam otimistas.
- **Decisão:** Encadear `FeaturesDerivadas` → `ColumnTransformer` → classificador em um único `Pipeline` do scikit-learn (`src/modeling.py`).
- **Alternativas consideradas:** transformar a base inteira antes de separar (simples, mas vaza informação); transformar manualmente dentro de um laço de dobras (correto, porém mais código e mais risco de erro).
- **Consequências:** A validação cruzada reajusta todas as transformações a cada dobra. O mesmo objeto é salvo e usado pelo app, então não há divergência entre treino e produção. O custo é precisar declarar corretamente o tipo de cada coluna, feito de forma automática com possibilidade de ajuste em `config.py`.
