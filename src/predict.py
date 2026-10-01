"""Carregamento do modelo salvo e previsão."""
import json

import joblib
import numpy as np
import pandas as pd

from . import config


def carregar():
    """Retorna (modelo, metadata). Levanta FileNotFoundError se ainda não foi treinado."""
    if not config.MODEL_PATH.exists() or not config.METADATA_PATH.exists():
        raise FileNotFoundError("Modelo não encontrado. Execute `python -m src.train` antes.")
    modelo = joblib.load(config.MODEL_PATH)
    metadata = json.loads(config.METADATA_PATH.read_text(encoding="utf-8"))
    return modelo, metadata


def prever(modelo, metadata, df):
    """Recebe um DataFrame com as colunas de entrada e devolve probabilidade e classe."""
    nomes = [f["nome"] for f in metadata["features"]]
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for nome in nomes:
        if nome not in df.columns:
            df[nome] = np.nan
    X = df[nomes].copy()
    for f in metadata["features"]:
        if f["tipo"] == "numerica":
            texto = X[f["nome"]].astype("string").str.strip().str.replace(",", ".", regex=False)
            X[f["nome"]] = pd.to_numeric(texto, errors="coerce").astype(float)
    proba = modelo.predict_proba(X)[:, 1]
    saida = pd.DataFrame({"probabilidade_evasao": proba, "previsao": (proba >= metadata["limiar"]).astype(int)}, index=df.index)
    return saida
