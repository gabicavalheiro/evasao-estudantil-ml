"""Treinamento completo: EDA, separação, validação cruzada, ajuste e relatórios.

Uso:
    python -m src.train            # execução completa
    python -m src.train --rapido   # busca de hiperparâmetros reduzida
"""
import argparse
import json
import sys
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
    learning_curve,
    train_test_split,
)

from . import config, reporting
from .data import carregar_base
from .features import colunas_categoricas, colunas_numericas
from .modeling import modelos_candidatos, montar_pipeline

METRICAS_CV = {"f1": "f1", "recall": "recall", "precision": "precision", "roc_auc": "roc_auc", "accuracy": "accuracy"}


def _json_seguro(valor):
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating,)):
        return float(valor)
    return valor


def descrever_features(pipeline, X):
    """Esquema das colunas de entrada usado pelo app (tipos, faixas e opções)."""
    preparado = pipeline.named_steps["derivadas"]._preparar(X)
    itens = []
    for col in preparado.columns:
        serie = preparado[col]
        if col in colunas_numericas(preparado):
            valores = serie.dropna()
            inteiro = bool(len(valores) and np.all(np.equal(np.mod(valores, 1), 0)))
            itens.append(
                {
                    "nome": col,
                    "tipo": "numerica",
                    "minimo": float(valores.min()),
                    "maximo": float(valores.max()),
                    "mediana": float(valores.median()),
                    "inteiro": inteiro,
                }
            )
        else:
            frequencias = serie.dropna().value_counts()
            itens.append(
                {
                    "nome": col,
                    "tipo": "categorica",
                    "opcoes": [str(v) for v in frequencias.index[:100]],
                    "padrao": str(frequencias.index[0]),
                }
            )
    return itens


def selecionar_exemplos(modelo, X_teste, y_teste):
    proba = modelo.predict_proba(X_teste)[:, 1]
    pred = (proba >= config.THRESHOLD).astype(int)
    tabela = X_teste.copy()
    tabela["real"] = y_teste.values
    tabela["probabilidade_modelo"] = np.round(proba, 4)
    grupos = [
        tabela[(pred == 1) & (y_teste.values == 1)].head(4),
        tabela[(pred == 0) & (y_teste.values == 0)].head(4),
        tabela[(pred == 0) & (y_teste.values == 1)].head(1),
        tabela[(pred == 1) & (y_teste.values == 0)].head(1),
    ]
    return pd.concat(grupos)


def main(rapido=False):
    for pasta in (config.MODELS_DIR, config.REPORTS_DIR, config.FIGURES_DIR):
        pasta.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ 1. dados
    X, y, info = carregar_base()
    (config.REPORTS_DIR / "eda_resumo.md").write_text(reporting.resumo_eda(X, y, info), encoding="utf-8")
    reporting.grafico_classes(y)
    reporting.grafico_correlacao(X, y)

    # ----------------------------------------------------- 2. treino / teste
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=config.RANDOM_STATE
    )
    print(f"[split] treino = {len(X_treino)}, teste = {len(X_teste)}")
    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)

    # ------------------------------------- 3. comparação com validação cruzada
    candidatos = modelos_candidatos()
    linhas = []
    for nome, (estimador, _) in candidatos.items():
        print(f"[cv] {nome} ...")
        res = cross_validate(
            montar_pipeline(estimador), X_treino, y_treino, cv=cv, scoring=METRICAS_CV, return_train_score=True, n_jobs=-1
        )
        linhas.append(
            {
                "modelo": nome,
                "f1_treino": res["train_f1"].mean(),
                "f1_validacao": res["test_f1"].mean(),
                "f1_validacao_dp": res["test_f1"].std(),
                "recall_validacao": res["test_recall"].mean(),
                "precisao_validacao": res["test_precision"].mean(),
                "roc_auc_validacao": res["test_roc_auc"].mean(),
                "acuracia_validacao": res["test_accuracy"].mean(),
            }
        )
    comparacao = pd.DataFrame(linhas).round(4)
    comparacao.to_csv(config.REPORTS_DIR / "comparacao_modelos.csv", index=False)
    reporting.grafico_comparacao(comparacao)
    print(comparacao.to_string(index=False))

    topo = comparacao.sort_values("f1_validacao", ascending=False).iloc[0]
    limite = topo["f1_validacao"] - topo["f1_validacao_dp"]
    empatados = comparacao[comparacao["f1_validacao"] >= limite]["modelo"].tolist()
    melhor_nome = min(
        empatados,
        key=lambda n: config.ORDEM_SIMPLICIDADE.index(n) if n in config.ORDEM_SIMPLICIDADE else 99,
    )
    print(f"[cv] Maior F1 de validação: {topo['modelo']} ({topo['f1_validacao']:.4f}); "
          f"empatados a 1 desvio padrão: {empatados}")
    print(f"[cv] Modelo escolhido (regra de 1 desvio padrão, o mais simples entre os empatados): {melhor_nome}")

    # ------------------------------------ 4. ajuste de hiperparâmetros (melhor)
    estimador, espaco = candidatos[melhor_nome]
    n_iter = 5 if rapido else config.N_ITER_BUSCA
    busca = RandomizedSearchCV(
        montar_pipeline(estimador),
        espaco,
        n_iter=n_iter,
        scoring=METRICAS_CV,
        refit=config.SCORING_PRINCIPAL,
        cv=cv,
        return_train_score=True,
        n_jobs=-1,
        random_state=config.RANDOM_STATE,
    )
    print(f"[busca] {melhor_nome}: {n_iter} combinações x {config.CV_FOLDS} dobras ...")
    busca.fit(X_treino, y_treino)
    modelo = busca.best_estimator_
    i = busca.best_index_
    res = busca.cv_results_
    cv_metricas = {m: float(res[f"mean_test_{m}"][i]) for m in METRICAS_CV}
    cv_metricas_dp = {m: float(res[f"std_test_{m}"][i]) for m in METRICAS_CV}
    cv_treino = {m: float(res[f"mean_train_{m}"][i]) for m in METRICAS_CV}
    pd.DataFrame(res).sort_values("rank_test_f1").head(10).to_csv(
        config.REPORTS_DIR / "busca_hiperparametros_top10.csv", index=False
    )

    # ------------------------------------------------------ 5. avaliação final
    proba_treino = modelo.predict_proba(X_treino)[:, 1]
    proba_teste = modelo.predict_proba(X_teste)[:, 1]
    pred_treino = (proba_treino >= config.THRESHOLD).astype(int)
    pred_teste = (proba_teste >= config.THRESHOLD).astype(int)
    m_treino = reporting.metricas(y_treino, pred_treino, proba_treino)
    m_teste = reporting.metricas(y_teste, pred_teste, proba_teste)
    reporting.grafico_matriz(y_teste, pred_teste)
    reporting.grafico_roc(modelo, X_teste, y_teste)

    # -------------------------------------- 6. overfitting / underfitting
    tamanhos, lc_treino, lc_val = learning_curve(
        clone(modelo), X_treino, y_treino, cv=cv, scoring="f1", train_sizes=np.linspace(0.2, 1.0, 5), n_jobs=-1
    )[:3]
    reporting.grafico_curva_aprendizado(tamanhos, lc_treino, lc_val)
    status, texto = reporting.diagnosticar(
        cv_treino["f1"], cv_metricas["f1"], m_teste["f1"], cv_treino["roc_auc"], cv_metricas["roc_auc"]
    )
    print(f"[diagnóstico] {status}")

    # --------------------------------------- 7. importância das variáveis
    imp = permutation_importance(
        modelo, X_teste, y_teste, scoring="roc_auc", n_repeats=5, random_state=config.RANDOM_STATE, n_jobs=-1
    )
    reporting.grafico_importancia(list(X_teste.columns), imp.importances_mean, imp.importances_std)

    # ------------------------------------------------------ 8. relatórios
    def linha(nome, d):
        return f"| {nome} | {d['f1']:.3f} | {d['recall']:.3f} | {d['precisao']:.3f} | {d['roc_auc']:.3f} | {d['acuracia']:.3f} |"

    cv_fmt = {
        "f1": cv_metricas["f1"],
        "recall": cv_metricas["recall"],
        "precisao": cv_metricas["precision"],
        "roc_auc": cv_metricas["roc_auc"],
        "acuracia": cv_metricas["accuracy"],
    }
    cv_tr_fmt = {
        "f1": cv_treino["f1"],
        "recall": cv_treino["recall"],
        "precisao": cv_treino["precision"],
        "roc_auc": cv_treino["roc_auc"],
        "acuracia": cv_treino["accuracy"],
    }
    diag = [
        "# Diagnóstico de overfitting e underfitting",
        "",
        f"Modelo final: **{melhor_nome}** | hiperparâmetros: `{ {k.replace('modelo__', ''): _json_seguro(v) for k, v in busca.best_params_.items()} }`",
        "",
        "| Conjunto | F1 | Recall | Precisão | ROC-AUC | Acurácia |",
        "|---|---|---|---|---|---|",
        linha("Treino (média das dobras)", cv_tr_fmt),
        linha(f"Validação cruzada ({config.CV_FOLDS} dobras)", cv_fmt),
        linha("Treino completo (após refit)", m_treino),
        linha("Teste (dados nunca vistos)", m_teste),
        "",
        f"**Resultado: {status}.**",
        "",
        texto,
        "",
        "## Critérios usados",
        f"- Underfitting: F1 de treino e de validação abaixo de {config.LIMIAR_UNDERFIT_F1:.2f}.",
        f"- Overfitting: F1 de treino maior que o de validação em mais de {config.LIMIAR_GAP_OVERFIT:.2f}; "
        f"entre {config.LIMIAR_GAP_LEVE:.2f} e {config.LIMIAR_GAP_OVERFIT:.2f} é considerado leve.",
        "- Esses limites são heurísticos; a leitura deve ser feita junto da curva de aprendizado "
        "(`figures/06_curva_aprendizado.png`).",
    ]
    (config.REPORTS_DIR / "diagnostico.md").write_text("\n".join(diag) + "\n", encoding="utf-8")

    metadata = {
        "treinado_em": datetime.now().isoformat(timespec="seconds"),
        "versao_sklearn": sklearn.__version__,
        "coluna_alvo": info["coluna_alvo"],
        "valores_positivos": info["valores_positivos"],
        "modelo": melhor_nome,
        "hiperparametros": {k.replace("modelo__", ""): _json_seguro(v) for k, v in busca.best_params_.items()},
        "limiar": config.THRESHOLD,
        "diagnostico": {"status": status, "texto": texto},
        "metricas": {"treino_cv": cv_tr_fmt, "validacao_cv": cv_fmt, "validacao_cv_dp": cv_metricas_dp, "teste": m_teste},
        "tamanho_treino": int(len(X_treino)),
        "tamanho_teste": int(len(X_teste)),
        "features": descrever_features(modelo, X_treino),
    }
    (config.METADATA_PATH).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (config.REPORTS_DIR / "metricas.json").write_text(
        json.dumps(metadata["metricas"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    selecionar_exemplos(modelo, X_teste, y_teste).to_csv(config.EXAMPLES_PATH, index=False)

    joblib.dump(modelo, config.MODEL_PATH, compress=3)
    tamanho_mb = config.MODEL_PATH.stat().st_size / 1e6
    print(f"[modelo] salvo em {config.MODEL_PATH} ({tamanho_mb:.1f} MB)")
    if tamanho_mb > 50:
        print("[aviso] Modelo grande para o GitHub/Streamlit. Reduza n_estimators ou max_depth em modeling.py.")
    print(f"[teste] F1 = {m_teste['f1']:.3f} | recall = {m_teste['recall']:.3f} | ROC-AUC = {m_teste['roc_auc']:.3f}")
    print("[ok] Treinamento concluído. Veja a pasta reports/.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rapido", action="store_true", help="busca de hiperparâmetros reduzida")
    args = parser.parse_args()
    sys.exit(main(rapido=args.rapido))
