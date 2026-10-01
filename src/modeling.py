"""Montagem da pipeline e dos modelos candidatos."""
from scipy.stats import loguniform
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import config
from .features import FeaturesDerivadas, Winsorizador, colunas_categoricas, colunas_numericas


def montar_preprocessamento():
    numerico = Pipeline(
        [
            ("imputacao", SimpleImputer(strategy="median")),
            ("winsorizacao", Winsorizador(0.01, 0.99)),
            ("padronizacao", StandardScaler()),
        ]
    )
    categorico = Pipeline(
        [
            ("imputacao", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=5, sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        [("num", numerico, colunas_numericas), ("cat", categorico, colunas_categoricas)],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def montar_pipeline(estimador):
    return Pipeline(
        [
            (
                "derivadas",
                FeaturesDerivadas(
                    categoricas=config.CATEGORICAL_COLUMNS,
                    numericas=config.NUMERIC_COLUMNS,
                    razoes=config.RATIOS,
                ),
            ),
            ("preprocessamento", montar_preprocessamento()),
            ("modelo", estimador),
        ]
    )


def modelos_candidatos(seed=config.RANDOM_STATE):
    """nome -> (estimador base, espaço de busca de hiperparâmetros)"""
    return {
        "Regressão Logística": (
            LogisticRegression(max_iter=3000, class_weight="balanced"),
            {"modelo__C": loguniform(1e-3, 1e2)},
        ),
        "Random Forest": (
            RandomForestClassifier(n_estimators=300, class_weight="balanced_subsample", random_state=seed),
            {
                "modelo__n_estimators": [200, 300],
                "modelo__max_depth": [4, 6, 8, 10, None],
                "modelo__min_samples_leaf": [1, 3, 5, 10, 20],
                "modelo__max_features": ["sqrt", 0.3, 0.5],
            },
        ),
        "Gradient Boosting": (
            HistGradientBoostingClassifier(class_weight="balanced", random_state=seed),
            {
                "modelo__learning_rate": loguniform(0.02, 0.3),
                "modelo__max_iter": [100, 200, 300],
                "modelo__max_depth": [3, 4, 6, None],
                "modelo__max_leaf_nodes": [8, 15, 31],
                "modelo__min_samples_leaf": [10, 20, 40],
                "modelo__l2_regularization": loguniform(1e-3, 10),
            },
        ),
    }
