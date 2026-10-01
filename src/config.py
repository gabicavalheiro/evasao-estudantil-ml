"""Configurações centrais do projeto.

Tudo que depende da base de dados (nome da coluna alvo, valores que
representam evasão, colunas a descartar) fica aqui ou pode ser definido por
variável de ambiente, sem precisar mexer no restante do código.
"""
import os
from pathlib import Path

# ---------------------------------------------------------------- caminhos
CODE_ROOT = Path(__file__).resolve().parents[1]
# OUTPUT_DIR permite gravar modelo e relatórios fora da pasta do projeto
ROOT = Path(os.getenv("OUTPUT_DIR", CODE_ROOT))

DATA_DIR = CODE_ROOT / "data"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

MODEL_PATH = MODELS_DIR / "model.joblib"
METADATA_PATH = MODELS_DIR / "metadata.json"
EXAMPLES_PATH = MODELS_DIR / "exemplos.csv"


def _lista(nome, padrao=""):
    bruto = os.getenv(nome, padrao)
    return [item.strip() for item in bruto.split(",") if item.strip()]


# ------------------------------------------------------------------- dados
# Caminho da base. Se vazio, usa o primeiro .csv/.xlsx/.xls encontrado em data/
DATA_PATH = os.getenv("DATA_PATH", "")

# Nome da coluna alvo. Se vazio, o código tenta identificar pelo nome
# (evasao, evadiu, dropout, status, target...) e avisa qual escolheu.
TARGET_COLUMN = os.getenv("TARGET_COLUMN", "")

# Valores da coluna alvo que significam "evadiu" (classe positiva = 1).
# A comparação ignora maiúsculas/minúsculas e espaços. Qualquer outro valor
# vira 0. Ex.: em uma coluna com Dropout/Enrolled/Graduate, só "Dropout" é 1.
POSITIVE_VALUES = [
    v.lower()
    for v in _lista(
        "POSITIVE_VALUES",
        "1,true,sim,s,yes,y,evadiu,evadido,evasao,evasão,dropout,abandono,abandonou,desistente,desistiu,desligado",
    )
]

# Valores da coluna alvo cujas linhas devem ser removidas antes do treino
# (ex.: alunos ainda matriculados, cujo desfecho final não é conhecido).
# Vazio = todos os valores que não são evasão contam como "não evadiu".
EXCLUDE_VALUES = _lista("EXCLUDE_VALUES")
EXCLUDE_VALUES = [v.lower() for v in EXCLUDE_VALUES]

# Colunas a descartar (identificadores, datas, campos que vazam o resultado)
DROP_COLUMNS = _lista("DROP_COLUMNS")

# Forçar o tipo de colunas específicas (útil para códigos inteiros que
# representam categorias, como "curso = 9500")
CATEGORICAL_COLUMNS = _lista("CATEGORICAL_COLUMNS")
NUMERIC_COLUMNS = _lista("NUMERIC_COLUMNS")

# Inteiros com poucos valores distintos podem ser tratados como categorias.
# 0 desativa a regra (só as listas acima e o tipo do dado decidem).
CAT_MAX_UNIQUE_INT = int(os.getenv("CAT_MAX_UNIQUE_INT", "0"))

# Colunas de texto com mais valores distintos que isso são descartadas
HIGH_CARDINALITY_MAX = int(os.getenv("HIGH_CARDINALITY_MAX", "50"))

# Razões adicionais para feature engineering: (numerador, denominador, nome)
RATIOS = []

# ------------------------------------------------------------------ modelo
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5
SCORING_PRINCIPAL = "f1"
# Regra de um desvio padrão: entre os modelos cujo F1 de validação está a no
# máximo 1 desvio padrão do melhor, escolhe-se o mais simples desta lista.
ORDEM_SIMPLICIDADE = ["Regressão Logística", "Gradient Boosting", "Random Forest"]
N_ITER_BUSCA =int(os.getenv("N_ITER_BUSCA", "15"))
THRESHOLD = 0.5

# Critérios (heurísticos) usados no diagnóstico automático de ajuste
LIMIAR_GAP_OVERFIT = 0.10      # diferença treino - validação em F1
LIMIAR_GAP_LEVE = 0.05
LIMIAR_UNDERFIT_F1 = 0.70      # F1 de treino e validação abaixo disso
