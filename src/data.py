"""Leitura da base, identificação do alvo e limpeza inicial."""
import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

CANDIDATOS_ALVO = ["evas", "evad", "dropout", "abandon", "desist", "churn", "target", "status", "situa"]
COLUNAS_ID = {"id", "matricula", "matrícula", "ra", "id_aluno", "aluno_id", "student_id", "cpf"}


def localizar_base():
    if config.DATA_PATH:
        caminho = config.DATA_PATH
        return caminho
    candidatos = []
    for ext in ("*.csv", "*.xlsx", "*.xls"):
        candidatos += sorted(config.DATA_DIR.glob(ext))
    if not candidatos:
        raise FileNotFoundError(
            f"Nenhuma base encontrada em {config.DATA_DIR}. Coloque o arquivo "
            "(.csv, .xlsx ou .xls) na pasta data/ ou defina DATA_PATH."
        )
    return str(candidatos[0])


def ler_tabela(caminho):
    caminho = str(caminho)
    if caminho.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(caminho)
    for codificacao in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(caminho, sep=None, engine="python", encoding=codificacao)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível ler {caminho}")


def _converter_numericas_em_texto(df):
    """Colunas de texto que na verdade são números (inclusive com vírgula decimal)."""
    for col in df.select_dtypes(exclude="number").columns:
        serie = df[col]
        if serie.dtype == bool:
            continue
        texto = serie.astype("string").str.strip().str.replace(",", ".", regex=False)
        convertido = pd.to_numeric(texto, errors="coerce")
        nao_nulos = serie.notna().sum()
        if nao_nulos and convertido.notna().sum() / nao_nulos >= 0.95:
            df[col] = convertido
    return df


def corrigir_escala_notas(X, info):
    """Recupera notas (escala 0-20) que perderam o separador decimal.

    Em algumas bases, valores como 13,875 aparecem como 13875 ou
    1.34285714285714e16. Uma coluna é considerada afetada quando a maior parte
    dos valores está entre 0 e 20, mas existem valores acima de 200 (a
    escala própria de colunas como a nota de admissão, 0-200, não é afetada).
    Cada valor acima de 20 é dividido por 10 até caber na escala.
    """
    correcoes = {}
    for col in X.select_dtypes(include="number").columns:
        s = X[col].astype(float)
        if (s <= 20).mean() >= 0.5 and (s > 200).any():
            acima = s > 20
            v = s.copy()
            for _ in range(40):
                mascara = v > 20
                if not mascara.any():
                    break
                v[mascara] = v[mascara] / 10
            X[col] = v
            correcoes[col] = int(acima.sum())
    info["correcoes_escala_decimal"] = correcoes
    if correcoes:
        print(f"[dados] Escala decimal corrigida (valores ajustados por coluna): {correcoes}")
    return X


def identificar_alvo(df):
    if config.TARGET_COLUMN:
        if config.TARGET_COLUMN not in df.columns:
            raise KeyError(f"Coluna alvo '{config.TARGET_COLUMN}' não existe. Colunas: {list(df.columns)}")
        return config.TARGET_COLUMN
    for trecho in CANDIDATOS_ALVO:
        for col in df.columns:
            if trecho in col.lower():
                print(f"[dados] Coluna alvo identificada automaticamente: '{col}'")
                return col
    raise KeyError(
        "Não consegui identificar a coluna alvo. Defina TARGET_COLUMN. "
        f"Colunas: {list(df.columns)}"
    )


def codificar_alvo(serie):
    """Transforma a coluna alvo em 0/1 (1 = evadiu)."""
    normalizada = serie.astype("string").str.strip().str.lower()
    # valores numéricos como 1.0 viram "1"
    normalizada = normalizada.str.replace(r"^(\d+)\.0+$", r"\1", regex=True)
    valores = sorted(normalizada.dropna().unique())
    positivos = [v for v in valores if v in config.POSITIVE_VALUES]
    if not positivos:
        raise ValueError(
            f"Nenhum valor da coluna alvo corresponde a evasão. Valores encontrados: {valores}. "
            "Defina POSITIVE_VALUES (ex.: POSITIVE_VALUES=dropout)."
        )
    y = normalizada.isin(positivos).astype(int)
    y[normalizada.isna()] = -1
    return y, positivos, valores


def carregar_base():
    """Retorna X (features), y (0/1) e um dicionário com informações da carga."""
    caminho = localizar_base()
    print(f"[dados] Lendo {caminho}")
    df = ler_tabela(caminho)
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    info = {"arquivo": Path(str(caminho)).name, "linhas_originais": int(len(df)), "colunas_originais": int(df.shape[1])}

    alvo = identificar_alvo(df)
    info["coluna_alvo"] = alvo

    df = df[df[alvo].notna()].copy()
    if config.EXCLUDE_VALUES:
        rotulos = df[alvo].astype("string").str.strip().str.lower()
        excluir = rotulos.isin(config.EXCLUDE_VALUES)
        info["linhas_excluidas_por_alvo"] = int(excluir.sum())
        df = df[~excluir].copy()
        print(f"[dados] {int(excluir.sum())} linhas com alvo {config.EXCLUDE_VALUES} excluídas")
    duplicadas = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    info["linhas_duplicadas_removidas"] = duplicadas

    y, positivos, valores = codificar_alvo(df[alvo])
    info["valores_alvo"] = valores
    info["valores_positivos"] = positivos
    X = df.drop(columns=[alvo])

    descartadas = {}
    for col in config.DROP_COLUMNS:
        if col in X.columns:
            descartadas[col] = "definida em DROP_COLUMNS"
    for col in X.columns:
        if col in descartadas:
            continue
        if col.lower() in COLUNAS_ID:
            descartadas[col] = "identificador"
        elif X[col].isna().all():
            descartadas[col] = "todos os valores ausentes"
        elif X[col].nunique(dropna=True) <= 1:
            descartadas[col] = "valor constante"
        elif (not pd.api.types.is_float_dtype(X[col])) and X[col].nunique() == len(X) and len(X) > 50:
            descartadas[col] = "valor único por linha (provável identificador)"
    X = X.drop(columns=list(descartadas))

    X = _converter_numericas_em_texto(X)
    X = corrigir_escala_notas(X, info)

    for col in X.select_dtypes(exclude="number").columns:
        if X[col].nunique() > config.HIGH_CARDINALITY_MAX:
            descartadas[col] = f"mais de {config.HIGH_CARDINALITY_MAX} categorias distintas"
    X = X.drop(columns=[c for c in descartadas if c in X.columns])

    info["colunas_descartadas"] = descartadas
    info["linhas"] = int(len(X))
    info["colunas_features"] = int(X.shape[1])
    info["proporcao_evasao"] = float(y.mean())
    print(f"[dados] {len(X)} linhas, {X.shape[1]} features, evasão = {y.mean():.1%}")
    if descartadas:
        print(f"[dados] Colunas descartadas: {descartadas}")
    return X, y, info
