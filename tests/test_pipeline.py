"""Testes rápidos da pipeline com dados sintéticos (não dependem da base real).

Execução:  pytest -q
"""
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_score

from src import config
from src.data import codificar_alvo
from src.features import FeaturesDerivadas, Winsorizador
from src.modeling import modelos_candidatos, montar_pipeline


@pytest.fixture(scope="module")
def base():
    rng = np.random.default_rng(0)
    n = 400
    enr = rng.integers(4, 9, n)
    apr = np.clip(enr - rng.poisson(1.5, n), 0, None)
    df = pd.DataFrame(
        {
            "idade": rng.integers(17, 60, n).astype(float),
            "Unidades (enrolled)": enr,
            "Unidades (approved)": apr,
            "turno": rng.choice(["diurno", "noturno"], n),
            "curso": rng.choice([10, 20, 30], n),
        }
    )
    df.loc[rng.random(n) < 0.05, "idade"] = np.nan
    y = pd.Series((apr / enr + rng.normal(0, 0.2, n) < 0.6).astype(int))
    return df, y


def test_codificar_alvo_multiclasse():
    y, positivos, _ = codificar_alvo(pd.Series(["Dropout", "Graduate", "Enrolled", "dropout"]))
    assert y.tolist() == [1, 0, 0, 1]
    assert positivos == ["dropout"]


def test_codificar_alvo_sem_positivo_levanta_erro():
    with pytest.raises(ValueError):
        codificar_alvo(pd.Series(["ativo", "inativo"]))


def test_corrige_escala_decimal_das_notas():
    from src.data import corrigir_escala_notas

    X = pd.DataFrame(
        {
            "nota": [0.0, 14.0, 13875.0, 1.34285714285714e16, 1330625.0, 12.5],
            "admissao": [120.0, 150.5, 99.0, 180.0, 130.0, 110.0],  # escala 0-200, não deve mudar
        }
    )
    info = {}
    saida = corrigir_escala_notas(X.copy(), info)
    assert saida["nota"].between(0, 20).all()
    assert saida["nota"].tolist() == pytest.approx([0.0, 14.0, 13.875, 13.4285714285714, 13.30625, 12.5])
    assert saida["admissao"].tolist() == X["admissao"].tolist()
    assert list(info["correcoes_escala_decimal"]) == ["nota"]


def test_features_derivadas_cria_taxa_de_aprovacao(base):
    X, _ = base
    saida = FeaturesDerivadas().fit(X).transform(X)
    assert "Unidades (taxa de aprovação)" in saida.columns
    assert "qtd_campos_ausentes" in saida.columns
    assert saida["Unidades (taxa de aprovação)"].between(0, 1).all()


def test_features_derivadas_em_nomes_portugueses():
    X = pd.DataFrame(
        {
            "Unid1SemestreInscrito": [6, 5, 0],
            "Unid1SemestreAprovado": [6, 3, 0],
            "Unid1SemestreGrau": [14.0, 11.0, 0.0],
            "Unid2SemestreInscrito": [6, 5, 6],
            "Unid2SemestreAprovado": [5, 5, 0],
            "Unid2SemestreGrau": [13.0, 12.5, 0.0],
        }
    )
    saida = FeaturesDerivadas().fit(X).transform(X)
    assert saida["Unid1Semestre (taxa de aprovação)"].round(2).tolist()[:2] == [1.0, 0.6]
    assert pd.isna(saida["Unid1Semestre (taxa de aprovação)"].iloc[2])  # inscritas = 0
    assert saida["Unid Aprovado (variação 2º - 1º semestre)"].tolist() == [-1, 2, 0]
    assert saida["Unid Grau (variação 2º - 1º semestre)"].tolist() == [-1.0, 1.5, 0.0]


def test_winsorizador_limita_extremos_e_preserva_binarias():
    X = np.column_stack([np.r_[np.arange(100), 10_000], np.r_[np.zeros(100), 1]])
    saida = Winsorizador(0.01, 0.99).fit(X).transform(X)
    assert saida[:, 0].max() < 10_000
    assert saida[:, 1].max() == 1


@pytest.mark.parametrize("nome", list(modelos_candidatos()))
def test_pipeline_de_cada_modelo_treina_e_preve(base, nome):
    X, y = base
    estimador, espaco = modelos_candidatos()[nome]
    pipe = montar_pipeline(estimador)
    cv = StratifiedKFold(3, shuffle=True, random_state=0)
    assert cross_val_score(pipe, X, y, cv=cv, scoring="roc_auc").mean() > 0.6
    busca = RandomizedSearchCV(pipe, espaco, n_iter=2, cv=cv, scoring="f1", random_state=0).fit(X, y)
    proba = busca.best_estimator_.predict_proba(X)[:, 1]
    assert proba.shape == (len(X),) and ((proba >= 0) & (proba <= 1)).all()


def test_pipeline_aceita_categoria_nova_na_previsao(base):
    X, y = base
    pipe = montar_pipeline(modelos_candidatos()["Regressão Logística"][0]).fit(X, y)
    novo = X.head(3).copy()
    novo["turno"] = "categoria_inedita"
    assert len(pipe.predict_proba(novo)) == 3


def test_previsao_com_colunas_ausentes_e_virgula_decimal(base):
    from src.predict import prever

    X, y = base
    pipe = montar_pipeline(modelos_candidatos()["Regressão Logística"][0]).fit(X, y)
    meta = {
        "limiar": 0.5,
        "features": [
            {"nome": "idade", "tipo": "numerica"},
            {"nome": "Unidades (enrolled)", "tipo": "numerica"},
            {"nome": "Unidades (approved)", "tipo": "numerica"},
            {"nome": "turno", "tipo": "categorica"},
            {"nome": "curso", "tipo": "categorica"},
        ],
    }
    lote = pd.DataFrame({"idade": ["21,5", "30"], "Unidades (enrolled)": ["6", "5"]})  # faltam colunas
    saida = prever(pipe, meta, lote)
    assert len(saida) == 2 and saida["probabilidade_evasao"].between(0, 1).all()


def test_limiar_padrao():
    assert 0 < config.THRESHOLD < 1
