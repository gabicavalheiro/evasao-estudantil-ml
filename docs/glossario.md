# Glossário

| Termo | Definição |
|---|---|
| Evasão | Saída do aluno da instituição antes de concluir o curso; é a variável alvo do projeto |
| Classificação binária | Problema com duas classes possíveis (evadiu / não evadiu) |
| Classe positiva | A classe que se quer identificar; aqui, a evasão (valor 1) |
| Variável alvo | Coluna que o modelo aprende a prever |
| Feature | Variável de entrada usada pelo modelo |
| Feature engineering | Criação, transformação e seleção de variáveis para melhorar o modelo |
| Variável numérica | Valor quantitativo (notas, idade, unidades aprovadas) |
| Variável categórica | Valor em categorias (curso, turno, estado civil) |
| Variável derivada | Variável criada a partir de outras, como a taxa de aprovação (aprovadas ÷ matriculadas) |
| One-Hot Encoding | Transforma cada categoria em uma coluna binária (0/1) |
| Categoria rara | Categoria com poucas ocorrências; é agrupada para evitar colunas com pouca informação |
| Imputação | Preenchimento de valores ausentes (mediana para numéricas, moda para categóricas) |
| Mediana | Valor central de uma variável, pouco sensível a extremos |
| Moda | Valor mais frequente |
| Padronização | Reescala para média 0 e desvio padrão 1 |
| Outlier | Valor muito distante do padrão dos demais |
| Winsorização | Limitar valores extremos aos percentis 1% e 99% em vez de removê-los |
| Percentil | Valor abaixo do qual está uma dada porcentagem dos dados |
| Data leakage | Vazamento de informação do teste ou da validação para o treino, inflando o desempenho |
| Pipeline | Encadeamento de etapas de pré-processamento e modelo em um único objeto |
| ColumnTransformer | Aplica transformações diferentes a grupos diferentes de colunas |
| Conjunto de treino | Parte dos dados usada para o modelo aprender |
| Conjunto de teste | Parte reservada, usada uma única vez para a avaliação final |
| Estratificação | Divisão que mantém a proporção das classes em cada parte |
| Semente (random state) | Número que fixa o sorteio e torna o resultado reproduzível |
| Validação cruzada (k-fold) | Divide o treino em k partes, treinando em k−1 e validando em 1, repetidamente |
| Dobra (fold) | Cada uma das partes da validação cruzada |
| Overfitting | Modelo decora o treino e generaliza mal; o desempenho no treino é muito melhor que na validação |
| Underfitting | Modelo simples demais, com desempenho ruim até no treino |
| Generalização | Capacidade do modelo de acertar em dados que nunca viu |
| Curva de aprendizado | Desempenho de treino e validação em função da quantidade de dados de treino |
| Regularização | Técnica que limita a complexidade do modelo para reduzir overfitting |
| Hiperparâmetro | Configuração do modelo definida antes do treino (profundidade máxima, taxa de aprendizado) |
| Randomized Search | Busca de hiperparâmetros sorteando combinações em vez de testar todas |
| Regressão Logística | Modelo linear que estima a probabilidade de uma classe; serve como referência |
| Random Forest | Conjunto de muitas árvores de decisão cujas respostas são combinadas |
| Gradient Boosting | Conjunto de árvores construídas em sequência, cada uma corrigindo os erros da anterior |
| Desbalanceamento | Quando uma classe é muito menos frequente que a outra |
| class_weight | Parâmetro que dá mais peso à classe minoritária durante o treino |
| Limiar (threshold) | Probabilidade a partir da qual o modelo classifica o aluno como evasão (0,5 por padrão) |
| Acurácia | Proporção de acertos totais |
| Precisão | Dos alunos previstos como evasão, quantos realmente evadiram |
| Recall (sensibilidade) | Dos alunos que evadiram, quantos o modelo identificou |
| F1-score | Média harmônica entre precisão e recall |
| ROC-AUC | Capacidade do modelo de separar as classes considerando todos os limiares; 0,5 equivale a sorte e 1,0 a separação perfeita |
| Matriz de confusão | Tabela de acertos e erros por classe (verdadeiros/falsos positivos e negativos) |
| Falso positivo | Aluno previsto como evasão que não evadiu |
| Falso negativo | Aluno que evadiu e que o modelo não identificou |
| Importância por permutação | Mede o quanto o desempenho cai ao embaralhar uma variável; quanto maior a queda, mais importante |
| Serialização (joblib) | Salvar o modelo treinado em arquivo para reutilização |
| Streamlit | Framework Python para criar aplicações web de dados |
| Deploy | Publicação da aplicação para uso externo |
| ADR | Architecture Decision Record: registro curto de uma decisão técnica, com contexto, alternativas e consequências |
