"""Transformadores de feature engineering.

Tudo aqui é ajustado (fit) apenas com os dados de treino de cada dobra da
validação cruzada, porque faz parte do Pipeline do scikit-learn.
"""
import re

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


def _formatar(valor):
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, (float, np.floating)) and float(valor).is_integer():
        return str(int(valor))
    return str(valor).strip()


def como_categoria(serie):
    """Converte uma coluna para texto, mantendo ausentes como NaN."""
    return serie.map(_formatar).astype(object)


def colunas_numericas(X):
    return [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]


def colunas_categoricas(X):
    return [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]


class FeaturesDerivadas(BaseEstimator, TransformerMixin):
    """Ajusta tipos e cria variáveis derivadas.

    - força colunas categóricas (por ex. códigos inteiros) a virarem texto;
    - cria taxas de aprovação quando existem pares "(approved)"/"(enrolled)";
    - cria razões definidas em config.RATIOS;
    - cria a contagem de campos ausentes por aluno, se a base tiver ausentes.
    """

    def __init__(self, categoricas=None, numericas=None, razoes=None, contar_ausentes=True):
        self.categoricas = categoricas
        self.numericas = numericas
        self.razoes = razoes
        self.contar_ausentes = contar_ausentes

    def _preparar(self, X):
        X = pd.DataFrame(X).copy()
        for col in self.categoricas or []:
            if col in X.columns:
                X[col] = como_categoria(X[col])
        for col in self.numericas or []:
            if col in X.columns:
                X[col] = pd.to_numeric(X[col], errors="coerce")
        for col in X.columns:
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)
        return X

    def _descobrir_razoes(self, X):
        """Taxa de aprovação (aprovadas / inscritas) para pares de colunas equivalentes."""
        razoes = [tuple(r) for r in (self.razoes or [])]
        padroes = [
            (r"^(.*)\(approved\)\s*$", lambda g: g + "(enrolled)"),  # nomes em inglês
            (r"^(.*)Aprovado\s*$", lambda g: g + "Inscrito"),  # nomes em português
        ]
        for col in X.columns:
            for padrao, par_de in padroes:
                m = re.match(padrao, col, flags=re.IGNORECASE)
                if m:
                    par = par_de(m.group(1))
                    if par in X.columns:
                        razoes.append((col, par, f"{m.group(1).strip()} (taxa de aprovação)"))
        return [r for r in razoes if r[0] in X.columns and r[1] in X.columns]

    def _descobrir_variacoes(self, X):
        """Variação do 1º para o 2º semestre em colunas de aprovação e nota."""
        variacoes = []
        for col in X.columns:
            m = re.match(r"^(.*)1(?:st )?Sem(?:estre|\b)(.*)$", col, flags=re.IGNORECASE)
            if not m or not re.search(r"(aprovado|grau|approved|grade)\s*\)?$", col, flags=re.IGNORECASE):
                continue
            for cand in X.columns:
                if cand != col and re.sub(r"2", "1", cand, count=1) == col and "2" in cand:
                    nome = f"{m.group(1).strip()} {m.group(2).strip()} (variação 2º - 1º semestre)"
                    variacoes.append((cand, col, nome))
                    break
        return variacoes

    def fit(self, X, y=None):
        X = self._preparar(X)
        self.razoes_ = self._descobrir_razoes(X)
        self.variacoes_ = self._descobrir_variacoes(X)
        self.adicionar_ausentes_ = bool(self.contar_ausentes and X.isna().any().any())
        self.feature_names_in_ = np.array(X.columns, dtype=object)
        return self

    def transform(self, X):
        check_is_fitted(self, "razoes_")
        X = self._preparar(X)
        if self.adicionar_ausentes_:
            X["qtd_campos_ausentes"] = X.isna().sum(axis=1)
        for num, den, nome in self.razoes_:
            n = pd.to_numeric(X[num], errors="coerce").astype(float)
            d = pd.to_numeric(X[den], errors="coerce").astype(float)
            X[nome] = np.where(d > 0, n / d, np.nan)
        for seg, prim, nome in self.variacoes_:
            X[nome] = (
                pd.to_numeric(X[seg], errors="coerce").astype(float)
                - pd.to_numeric(X[prim], errors="coerce").astype(float)
            )
        return X


class Winsorizador(BaseEstimator, TransformerMixin):
    """Limita valores extremos aos percentis aprendidos no treino.

    Colunas binárias ou com poucos valores são preservadas para não apagar
    categorias raras.
    """

    def __init__(self, inferior=0.01, superior=0.99):
        self.inferior = inferior
        self.superior = superior

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.n_features_in_ = X.shape[1]
        self.baixo_ = np.nanquantile(X, self.inferior, axis=0)
        self.alto_ = np.nanquantile(X, self.superior, axis=0)
        for j in range(X.shape[1]):
            if len(np.unique(X[~np.isnan(X[:, j]), j])) <= 5:
                self.baixo_[j] = np.nanmin(X[:, j])
                self.alto_[j] = np.nanmax(X[:, j])
        return self

    def transform(self, X):
        check_is_fitted(self, "baixo_")
        return np.clip(np.asarray(X, dtype=float), self.baixo_, self.alto_)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features, dtype=object)
