# ADR-002 – Tratamento das variáveis (feature engineering)

- **Status:** Aceito
- **Contexto:** É preciso tratar dados numéricos e categóricos, ausentes e valores extremos, sem perder informação de categorias raras.
- **Decisão:**
  - Numéricas: imputação pela mediana, limitação de extremos nos percentis 1% e 99% (preservando colunas com poucos valores distintos) e padronização (média 0, desvio 1).
  - Categóricas: imputação pela moda e One-Hot Encoding, agrupando categorias com menos de 5 ocorrências e aceitando categorias inéditas na previsão.
  - Códigos inteiros que representam categorias (curso, estado civil) podem ser declarados em `CATEGORICAL_COLUMNS` para não serem tratados como quantidade.
  - Variáveis derivadas: taxa de aprovação por semestre (aprovadas / inscritas), variação do 1º para o 2º semestre em unidades aprovadas e em nota, razões extras em `config.RATIOS` e contagem de campos ausentes (criada apenas se a base tiver ausentes; nesta base não há ausentes). A detecção é automática para nomes em português (`...Aprovado`/`...Inscrito`) e em inglês (`(approved)`/`(enrolled)`).
  - Colunas descartadas: identificadores, constantes, totalmente vazias e textos com mais de 50 categorias distintas.
- **Alternativas consideradas:** imputar pela média (mais sensível a outliers); remover outliers (perde linhas); Label Encoding para categorias sem ordem (impõe uma ordem que não existe).
- **Consequências:** Regressão Logística e demais modelos recebem entradas em escala comparável. O One-Hot aumenta o número de colunas, mas o agrupamento de categorias raras limita esse crescimento. Campos que revelam o resultado (por exemplo, datas de saída) devem ser removidos pelo analista em `DROP_COLUMNS`.
