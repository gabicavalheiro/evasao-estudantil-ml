"""Aplicação Streamlit para previsão de evasão estudantil.

Execução local:  streamlit run app/app.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import sklearn
import streamlit as st

from src import config
from src.features import _formatar
from src.predict import carregar, prever

st.set_page_config(page_title="Previsão de evasão estudantil", page_icon="🎓", layout="wide")


@st.cache_resource(show_spinner="Carregando modelo...")
def obter_modelo():
    return carregar()


@st.cache_data
def obter_exemplos():
    if config.EXAMPLES_PATH.exists():
        return pd.read_csv(config.EXAMPLES_PATH)
    return None


def chave(nome):
    return f"campo::{nome}"


def valor_padrao(f):
    if f["tipo"] == "numerica":
        v = f["mediana"]
        return int(round(v)) if f["inteiro"] else float(v)
    return f["padrao"]


def aplicar_exemplo(features, exemplos):
    escolha = st.session_state.get("exemplo")
    if escolha is None or escolha == "Preencher manualmente":
        for f in features:
            st.session_state[chave(f["nome"])] = valor_padrao(f)
        return
    linha = exemplos.iloc[int(escolha.split(" ")[1]) - 1]
    for f in features:
        bruto = linha.get(f["nome"])
        if f["tipo"] == "numerica":
            if pd.isna(bruto):
                valor = valor_padrao(f)
            else:
                valor = min(max(float(bruto), f["minimo"]), f["maximo"])
                valor = int(round(valor)) if f["inteiro"] else float(valor)
        else:
            texto = _formatar(bruto)
            valor = texto if isinstance(texto, str) and texto in f["opcoes"] else valor_padrao(f)
        st.session_state[chave(f["nome"])] = valor


def campo(f):
    k = chave(f["nome"])
    if k not in st.session_state:
        st.session_state[k] = valor_padrao(f)
    if f["tipo"] == "categorica":
        return st.selectbox(f["nome"], f["opcoes"], key=k)
    amplitude = f["maximo"] - f["minimo"]
    if f["inteiro"]:
        return st.number_input(f["nome"], min_value=int(f["minimo"]), max_value=int(f["maximo"]), step=1, key=k)
    passo = 0.01 if amplitude <= 1 else 0.1 if amplitude <= 30 else 1.0
    return st.number_input(
        f["nome"], min_value=float(f["minimo"]), max_value=float(f["maximo"]), step=passo, format="%.2f", key=k
    )


def mostrar_resultado(prob, pred, limiar):
    c1, c2 = st.columns([1, 2])
    c1.metric("Probabilidade de evasão", f"{prob:.1%}")
    c1.progress(min(max(prob, 0.0), 1.0))
    if pred == 1:
        c2.error(f"**Previsão: risco de evasão** (probabilidade acima do limiar de {limiar:.0%})")
    else:
        c2.success(f"**Previsão: baixo risco de evasão** (probabilidade abaixo do limiar de {limiar:.0%})")


# ---------------------------------------------------------------------------
try:
    modelo, meta = obter_modelo()
except FileNotFoundError:
    st.error("Modelo ainda não treinado. Execute `python -m src.train` e reinicie o app.")
    st.stop()

features = meta["features"]
exemplos = obter_exemplos()
teste = meta["metricas"]["teste"]

st.title("🎓 Previsão de evasão estudantil")
st.caption("Informe os dados do aluno para estimar a probabilidade de evasão. Ferramenta de apoio à análise, não substitui a avaliação da instituição.")

if meta.get("versao_sklearn") != sklearn.__version__:
    st.warning(
        f"O modelo foi treinado com scikit-learn {meta.get('versao_sklearn')} e o ambiente usa {sklearn.__version__}. "
        "Se houver erro ao prever, treine novamente com as versões do requirements.txt."
    )

with st.sidebar:
    st.header("Modelo")
    st.write(f"**{meta['modelo']}**")
    st.caption(f"Treinado em {meta['treinado_em'][:10]} com {meta['tamanho_treino']} alunos")
    st.metric("F1 (teste)", f"{teste['f1']:.3f}")
    st.metric("Recall (teste)", f"{teste['recall']:.3f}")
    st.metric("ROC-AUC (teste)", f"{teste['roc_auc']:.3f}")
    st.write(f"Diagnóstico de ajuste: **{meta['diagnostico']['status']}**")

aba_individual, aba_lote, aba_modelo = st.tabs(["Previsão individual", "Previsão em lote", "Sobre o modelo"])

# ------------------------------------------------------- previsão individual
with aba_individual:
    if exemplos is not None and len(exemplos):
        opcoes = ["Preencher manualmente"] + [
            f"Exemplo {i + 1} (resultado real: {'evadiu' if r['real'] == 1 else 'não evadiu'})"
            for i, r in exemplos.iterrows()
        ]
        st.selectbox(
            "Carregar um aluno do conjunto de teste",
            opcoes,
            key="exemplo",
            on_change=aplicar_exemplo,
            args=(features, exemplos),
        )

    with st.form("formulario"):
        colunas = st.columns(3)
        for i, f in enumerate(features):
            with colunas[i % 3]:
                campo(f)
        enviar = st.form_submit_button("Prever", type="primary")

    if enviar:
        entrada = pd.DataFrame([{f["nome"]: st.session_state[chave(f["nome"])] for f in features}])
        saida = prever(modelo, meta, entrada).iloc[0]
        mostrar_resultado(float(saida["probabilidade_evasao"]), int(saida["previsao"]), meta["limiar"])

# ------------------------------------------------------------------- em lote
with aba_lote:
    st.write("Envie um arquivo CSV ou Excel com uma linha por aluno. As colunas devem ter os mesmos nomes usados no treino.")
    if exemplos is not None:
        st.download_button(
            "Baixar arquivo de exemplo", exemplos.to_csv(index=False).encode("utf-8"), "exemplos.csv", "text/csv"
        )
    arquivo = st.file_uploader("Arquivo", type=["csv", "xlsx", "xls"])
    if arquivo is not None:
        if arquivo.name.lower().endswith((".xlsx", ".xls")):
            lote = pd.read_excel(arquivo)
        else:
            lote = pd.read_csv(arquivo, sep=None, engine="python")
        lote.columns = [str(c).strip() for c in lote.columns]
        faltando = [f["nome"] for f in features if f["nome"] not in lote.columns]
        if faltando:
            st.warning(f"Colunas ausentes (serão tratadas como vazias): {', '.join(faltando)}")
        resultado = pd.concat([lote, prever(modelo, meta, lote)], axis=1)
        st.metric("Alunos com risco de evasão", f"{int(resultado['previsao'].sum())} de {len(resultado)}")
        st.dataframe(resultado, width="stretch")
        st.download_button(
            "Baixar resultado", resultado.to_csv(index=False).encode("utf-8"), "previsoes.csv", "text/csv"
        )

# ---------------------------------------------------------- sobre o modelo
with aba_modelo:
    st.subheader("Desempenho")
    m = meta["metricas"]
    tabela = pd.DataFrame(
        {
            "Treino (dobras)": m["treino_cv"],
            "Validação cruzada": m["validacao_cv"],
            "Teste": m["teste"],
        }
    ).T[["f1", "recall", "precisao", "roc_auc", "acuracia"]]
    tabela.columns = ["F1", "Recall", "Precisão", "ROC-AUC", "Acurácia"]
    st.dataframe(tabela.round(3), width="stretch")
    st.subheader("Overfitting e underfitting")
    st.write(f"**{meta['diagnostico']['status'].capitalize()}.** {meta['diagnostico']['texto']}")

    imagens = {
        "06_curva_aprendizado.png": "Curva de aprendizado",
        "04_matriz_confusao.png": "Matriz de confusão (teste)",
        "05_curva_roc.png": "Curva ROC (teste)",
        "07_importancia_variaveis.png": "Importância das variáveis",
        "03_comparacao_modelos.png": "Comparação dos modelos",
    }
    existentes = [(config.FIGURES_DIR / nome, legenda) for nome, legenda in imagens.items() if (config.FIGURES_DIR / nome).exists()]
    colunas = st.columns(2)
    for i, (caminho, legenda) in enumerate(existentes):
        with colunas[i % 2]:
            st.image(str(caminho), caption=legenda, width="stretch")
