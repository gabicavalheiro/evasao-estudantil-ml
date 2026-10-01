# Previsão de evasão estudantil

Pipeline de Machine Learning para classificação binária (evadiu / não evadiu) a partir de dados de desempenho acadêmico, com aplicação Streamlit para consulta ao modelo.

## Como executar

Requer Python 3.11 ou superior.

```bash
# 1. ambiente
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. base de dados: já incluída em data/StudentsPrepared.xlsx
#    (para outra base, copiar o arquivo .csv/.xlsx/.xls para data/)

# 3. treinamento (gera modelo, métricas, gráficos e relatórios)
python -m src.train
#   python -m src.train --rapido   -> busca de hiperparâmetros reduzida (teste rápido)

# 4. aplicação
streamlit run app/app.py

# 5. testes automatizados (opcional)
pip install pytest && pytest -q
```

### Ajustes pela base de dados

A base incluída (`StudentsPrepared.xlsx`) roda sem nenhum ajuste: a coluna `Target` é identificada automaticamente e `Desistente` é tratado como evasão. Para outras bases, o código identifica a coluna alvo pelo nome e trata como evasão valores como `evadiu`, `dropout`, `desistente`, `sim` e `1`. Se a base usar outros nomes, defina variáveis de ambiente antes do treino (ou edite `src/config.py`):

| Variável | Uso | Exemplo |
|---|---|---|
| `DATA_PATH` | caminho da base, se não estiver em `data/` | `data/alunos.csv` |
| `TARGET_COLUMN` | nome da coluna alvo | `Situacao` |
| `POSITIVE_VALUES` | valores da coluna alvo que significam evasão (separados por vírgula) | `inativo,cancelado` |
| `EXCLUDE_VALUES` | valores do alvo cujas linhas devem ser removidas (ex.: alunos ainda matriculados) | `matriculado` |
| `DROP_COLUMNS` | colunas a descartar (identificadores, campos que revelam o resultado) | `matricula,data_saida` |
| `CATEGORICAL_COLUMNS` | colunas numéricas que na verdade são códigos de categoria | `curso,estado_civil` |
| `NUMERIC_COLUMNS` | colunas a forçar como numéricas | `nota_ingresso` |
| `CAT_MAX_UNIQUE_INT` | inteiros com até N valores distintos viram categorias (0 = desligado) | `10` |
| `N_ITER_BUSCA` | combinações testadas na busca de hiperparâmetros | `30` |
| `OUTPUT_DIR` | pasta onde gravar `models/` e `reports/` | `/tmp/saida` |

Exemplo (Linux/macOS):

```bash
TARGET_COLUMN=Situacao POSITIVE_VALUES=evadido CATEGORICAL_COLUMNS=curso python -m src.train
```

No Windows (PowerShell): `$env:TARGET_COLUMN="Situacao"; python -m src.train`.

### Publicação no Streamlit Community Cloud

1. Enviar o repositório (incluindo `models/` e `reports/` gerados pelo treino) para o GitHub.
2. Em share.streamlit.io, criar um novo app apontando para o repositório, branch `main` e arquivo principal `app/app.py`.
3. Nas configurações avançadas, escolher Python 3.11 ou superior.

## Estrutura

```
.
├── app/
│   └── app.py                  aplicação Streamlit
├── src/
│   ├── config.py               parâmetros e configurações (caminhos, alvo, semente, limiares)
│   ├── data.py                 leitura da base, identificação do alvo, limpeza inicial
│   ├── features.py             transformadores de feature engineering
│   ├── modeling.py             montagem da pipeline e dos modelos candidatos
│   ├── reporting.py            métricas, gráficos e diagnóstico de ajuste
│   ├── train.py                orquestra todo o treinamento
│   └── predict.py              carrega o modelo salvo e faz previsões
├── tests/
│   └── test_pipeline.py        testes com dados sintéticos
├── pytest.ini                  configuração do pytest (raiz do projeto no caminho de importação)
├── data/                       base de dados (entrada)
├── models/                     model.joblib, metadata.json, exemplos.csv (gerados)
├── reports/                    relatórios e gráficos (gerados)
│   └── figures/
├── docs/
│   ├── adr/                    decisões de arquitetura
│   ├── glossario.md            termos usados no projeto
│   ├── roteiro.md              passo a passo de execução e roteiro resumido do vídeo
│   └── roteiro-detalhado.md    roteiro do vídeo com fala sugerida e ações de tela
├── requirements.txt
└── entrega.txt                 modelo do arquivo com os links da entrega
```

## Como funciona

O comando `python -m src.train` executa as etapas abaixo, nesta ordem.

1. **Carga e limpeza (`data.py`)**: lê CSV ou Excel, padroniza nomes de colunas, identifica o alvo e o converte para 0/1, corrige notas que perderam o separador decimal (ADR-011), remove linhas duplicadas e descarta colunas inúteis (identificadores, constantes, vazias e textos com cardinalidade muito alta). Textos que na verdade são números (inclusive com vírgula decimal) são convertidos.
2. **Análise exploratória**: grava o resumo da base (`reports/eda_resumo.md`), a distribuição das classes e a correlação das variáveis numéricas com a evasão.
3. **Separação treino/teste**: 80% / 20%, estratificada pela classe e com semente fixa. O teste só é usado na avaliação final.
4. **Pipeline (`features.py` e `modeling.py`)**: um único objeto do scikit-learn com três blocos:
   - `FeaturesDerivadas`: ajusta tipos, cria a taxa de aprovação por semestre (aprovadas ÷ inscritas), a variação do 1º para o 2º semestre em unidades aprovadas e em nota, razões definidas em `config.RATIOS` e a contagem de campos ausentes (se houver ausentes).
   - Pré-processamento: numéricas recebem imputação pela mediana, limitação de extremos (percentis 1% e 99%) e padronização; categóricas recebem imputação pela moda e One-Hot Encoding, agrupando categorias raras e tolerando categorias novas.
   - Modelo classificador.
5. **Validação cruzada**: três modelos (Regressão Logística, Random Forest e Gradient Boosting) são comparados com `StratifiedKFold` de 5 dobras sobre o conjunto de treino, registrando métricas de treino e de validação. Como o pré-processamento está na pipeline, ele é reajustado a cada dobra, sem vazamento de dados.
6. **Escolha do modelo e ajuste de hiperparâmetros**: vale a regra de um desvio padrão (entre os modelos empatados com o melhor F1 de validação, o mais simples; ADR-006). O escolhido passa por `RandomizedSearchCV` com as mesmas dobras.
7. **Avaliação final**: métricas no teste, matriz de confusão e curva ROC.
8. **Diagnóstico de ajuste**: compara treino, validação cruzada e teste, gera a curva de aprendizado e classifica o resultado como bom ajuste, overfitting (leve ou não) ou underfitting, segundo os critérios de `config.py`. O texto fica em `reports/diagnostico.md`.
9. **Importância das variáveis**: importância por permutação, calculada sobre o teste.
10. **Artefatos**: modelo serializado com `joblib`, esquema das colunas de entrada (`metadata.json`) e alguns alunos do teste (`exemplos.csv`) usados na demonstração do app.

### Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `models/model.joblib` | pipeline completa treinada |
| `models/metadata.json` | modelo escolhido, hiperparâmetros, métricas, diagnóstico e esquema das colunas de entrada |
| `models/exemplos.csv` | alunos do conjunto de teste para carregar no app |
| `reports/eda_resumo.md` | resumo da base, colunas descartadas e ausentes |
| `reports/comparacao_modelos.csv` | métricas de treino e validação dos três modelos |
| `reports/busca_hiperparametros_top10.csv` | melhores combinações da busca |
| `reports/diagnostico.md` | tabela treino × validação × teste e conclusão sobre ajuste |
| `reports/metricas.json` | métricas em formato estruturado |
| `reports/figures/` | gráficos numerados de 01 a 07 |

### Aplicação

O app lê `models/model.joblib` e `models/metadata.json` e monta o formulário a partir do esquema salvo (campos numéricos com a faixa observada no treino, campos categóricos com as opções conhecidas). Possui três abas:

- **Previsão individual**: formulário com os dados do aluno, opção de carregar um aluno do conjunto de teste, e resultado com probabilidade e classe.
- **Previsão em lote**: envio de CSV/Excel e download das previsões.
- **Sobre o modelo**: métricas, diagnóstico de ajuste e gráficos.

### Reprodutibilidade

A semente (`RANDOM_STATE = 42`), as versões de `requirements.txt` e a separação estratificada tornam o treino reproduzível. O modelo salvo depende da versão do scikit-learn; por isso as versões estão fixadas e o app avisa quando detecta diferença.
