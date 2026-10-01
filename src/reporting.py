"""Métricas, gráficos e textos dos relatórios."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from . import config

COR_A = "#1f5f8b"
COR_B = "#d9822b"


def metricas(y_true, y_pred, y_proba):
    return {
        "acuracia": float(accuracy_score(y_true, y_pred)),
        "precisao": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
    }


def _salvar(fig, nome):
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    caminho = config.FIGURES_DIR / nome
    fig.tight_layout()
    fig.savefig(caminho, dpi=140)
    plt.close(fig)
    return caminho


def grafico_classes(y):
    contagem = y.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5, 4))
    barras = ax.bar(["Não evadiu (0)", "Evadiu (1)"], [contagem.get(0, 0), contagem.get(1, 0)], color=[COR_A, COR_B])
    for b in barras:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{int(b.get_height())}", ha="center", va="bottom")
    ax.set_title("Distribuição da variável alvo")
    ax.set_ylabel("Alunos")
    return _salvar(fig, "01_distribuicao_classes.png")


def grafico_correlacao(X, y, top=15):
    numericas = X.select_dtypes(include="number")
    if numericas.shape[1] == 0:
        return None
    corr = numericas.corrwith(y).dropna().sort_values(key=np.abs, ascending=False).head(top)[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(corr.index, corr.values, color=[COR_B if v > 0 else COR_A for v in corr.values])
    ax.set_title("Correlação das variáveis numéricas com a evasão")
    ax.set_xlabel("Correlação (Pearson)")
    return _salvar(fig, "02_correlacao_com_evasao.png")


def grafico_comparacao(tabela):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(tabela))
    ax.bar(x - 0.18, tabela["f1_treino"], 0.36, label="Treino (dobras)", color=COR_A)
    ax.bar(x + 0.18, tabela["f1_validacao"], 0.36, yerr=tabela["f1_validacao_dp"], label="Validação (dobras)", color=COR_B)
    ax.set_xticks(x)
    ax.set_xticklabels(tabela["modelo"], rotation=10)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1")
    ax.set_title("Comparação dos modelos (validação cruzada)")
    ax.legend()
    return _salvar(fig, "03_comparacao_modelos.png")


def grafico_matriz(y_true, y_pred):
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ConfusionMatrixDisplay.from_predictions(
        y_true, y_pred, display_labels=["Não evadiu", "Evadiu"], cmap="Blues", ax=ax, colorbar=False
    )
    ax.set_title("Matriz de confusão (teste)")
    ax.set_xlabel("Previsto")
    ax.set_ylabel("Real")
    return _salvar(fig, "04_matriz_confusao.png")


def grafico_roc(modelo, X_teste, y_teste):
    fig, ax = plt.subplots(figsize=(5, 4.5))
    RocCurveDisplay.from_estimator(modelo, X_teste, y_teste, ax=ax, curve_kwargs={"color": COR_A})
    ax.plot([0, 1], [0, 1], "--", color="gray")
    ax.set_title("Curva ROC (teste)")
    return _salvar(fig, "05_curva_roc.png")


def grafico_curva_aprendizado(tamanhos, treino, validacao):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for valores, rotulo, cor in ((treino, "Treino", COR_A), (validacao, "Validação", COR_B)):
        media, dp = valores.mean(axis=1), valores.std(axis=1)
        ax.plot(tamanhos, media, "o-", label=rotulo, color=cor)
        ax.fill_between(tamanhos, media - dp, media + dp, alpha=0.15, color=cor)
    ax.set_xlabel("Tamanho do conjunto de treino")
    ax.set_ylabel("F1")
    ax.set_ylim(0, 1.05)
    ax.set_title("Curva de aprendizado")
    ax.legend()
    return _salvar(fig, "06_curva_aprendizado.png")


def grafico_importancia(nomes, medias, desvios, top=15):
    ordem = np.argsort(medias)[::-1][:top][::-1]
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.barh(np.array(nomes)[ordem], np.array(medias)[ordem], xerr=np.array(desvios)[ordem], color=COR_A)
    ax.set_title("Importância das variáveis (permutação, teste)")
    ax.set_xlabel("Queda no ROC-AUC ao embaralhar a variável")
    return _salvar(fig, "07_importancia_variaveis.png")


def diagnosticar(f1_treino, f1_val, f1_teste, auc_treino, auc_val):
    """Classifica o ajuste do modelo com critérios simples e explícitos."""
    gap = f1_treino - f1_val
    gap_auc = auc_treino - auc_val
    dif_teste = f1_val - f1_teste
    if f1_treino < config.LIMIAR_UNDERFIT_F1 and f1_val < config.LIMIAR_UNDERFIT_F1:
        status = "underfitting"
        texto = (
            f"O F1 é baixo tanto no treino ({f1_treino:.3f}) quanto na validação ({f1_val:.3f}), "
            f"abaixo de {config.LIMIAR_UNDERFIT_F1:.2f}. O modelo não está conseguindo capturar o padrão "
            "dos dados, o que caracteriza underfitting."
        )
    elif gap > config.LIMIAR_GAP_OVERFIT:
        status = "overfitting"
        texto = (
            f"O F1 no treino ({f1_treino:.3f}) é {gap:.3f} maior que na validação ({f1_val:.3f}), acima do "
            f"limite de {config.LIMIAR_GAP_OVERFIT:.2f}. O modelo aprende detalhes do treino que não "
            "generalizam, o que caracteriza overfitting."
        )
    elif gap > config.LIMIAR_GAP_LEVE:
        status = "overfitting leve"
        texto = (
            f"O F1 no treino ({f1_treino:.3f}) é {gap:.3f} maior que na validação ({f1_val:.3f}). "
            "Há um sinal leve de overfitting, dentro de uma faixa aceitável."
        )
    else:
        status = "bom ajuste"
        texto = (
            f"O F1 no treino ({f1_treino:.3f}) e na validação ({f1_val:.3f}) são próximos (diferença de "
            f"{gap:.3f}) e acima de {config.LIMIAR_UNDERFIT_F1:.2f}. Não há evidência de overfitting nem de underfitting."
        )
    texto += (
        f" No ROC-AUC, a diferença treino-validação é {gap_auc:.3f}. "
        f"O F1 no teste ({f1_teste:.3f}) difere {abs(dif_teste):.3f} da validação cruzada"
        + (", o que indica que a estimativa da validação se manteve em dados nunca vistos." if abs(dif_teste) <= 0.05 else ", diferença que merece atenção.")
    )
    return status, texto


def resumo_eda(X, y, info):
    ausentes = X.isna().sum()
    ausentes = ausentes[ausentes > 0].sort_values(ascending=False)
    linhas = [
        "# Resumo da base",
        "",
        f"- Arquivo: `{info['arquivo']}`",
        f"- Linhas originais: {info['linhas_originais']}; após limpeza: {info['linhas']} "
        f"({info['linhas_duplicadas_removidas']} duplicadas removidas)",
        f"- Features utilizadas: {info['colunas_features']}",
        f"- Coluna alvo: `{info['coluna_alvo']}`; valores encontrados: {info['valores_alvo']}; "
        f"tratados como evasão (1): {info['valores_positivos']}",
        f"- Evasão: {int(y.sum())} alunos ({y.mean():.1%}); não evasão: {int((y == 0).sum())} ({1 - y.mean():.1%})",
        f"- Variáveis numéricas: {X.select_dtypes(include='number').shape[1]}; "
        f"categóricas/texto: {X.select_dtypes(exclude='number').shape[1]}",
        "",
        "## Colunas descartadas",
    ]
    if info["colunas_descartadas"]:
        linhas += [f"- `{c}`: {motivo}" for c, motivo in info["colunas_descartadas"].items()]
    else:
        linhas.append("- nenhuma")
    correcoes = info.get("correcoes_escala_decimal") or {}
    linhas += ["", "## Correção de escala decimal"]
    if correcoes:
        linhas.append("Notas que perderam o separador decimal (ex.: 13875 em vez de 13,875) foram recuperadas na escala 0-20:")
        linhas += [f"- `{c}`: {n} valores corrigidos" for c, n in correcoes.items()]
    else:
        linhas.append("- nenhuma")
    if info.get("linhas_excluidas_por_alvo"):
        linhas += ["", f"## Linhas excluídas pelo alvo: {info['linhas_excluidas_por_alvo']}"]
    linhas += ["", "## Valores ausentes"]
    if len(ausentes):
        linhas += [f"- `{c}`: {int(n)} ({n / len(X):.1%})" for c, n in ausentes.items()]
    else:
        linhas.append("- nenhum")
    return "\n".join(linhas) + "\n"
