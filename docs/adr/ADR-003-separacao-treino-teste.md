# ADR-003 – Separação treino/teste estratificada

- **Status:** Aceito
- **Contexto:** A evasão costuma ser a classe minoritária, e uma divisão aleatória simples pode distorcer a proporção entre treino e teste. Linhas duplicadas presentes nos dois conjuntos também inflariam o resultado.
- **Decisão:** Remover linhas duplicadas e dividir em 80% treino e 20% teste com `train_test_split(stratify=y, random_state=42)`.
- **Alternativas consideradas:** 70/30 (menos dados para treinar); divisão temporal (não há campo de data garantido na base).
- **Consequências:** A proporção das classes é preservada e o resultado é reproduzível. O conjunto de teste é usado uma única vez, na avaliação final, e nunca para escolher modelo ou hiperparâmetros.
