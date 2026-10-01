# Roteiro: o que fazer e o que mostrar

Este documento tem duas partes: **A) passo a passo de execução** (do zero até a entrega) e **B) roteiro de gravação do vídeo** (o que mostrar na tela e o que falar). Os números do vídeo vêm dos arquivos em `reports/` depois que o treino rodar; nada aqui depende de um resultado específico.

---

## Entregáveis e resumo da prova

| # | Entregável | Como este projeto atende |
|---|---|---|
| 1 | Repositório GitHub com documentação dos passos e conclusões | Este projeto: `README.md`, `docs/`, `reports/` |
| 2 | Aplicação deployada no Streamlit | `app/app.py` publicado no Streamlit Community Cloud |
| 3 | Vídeo de no mínimo 5 minutos | Parte B deste roteiro |
| 4 | Arquivo `.txt` com os 3 links | `entrega.txt` |

O que a prova pede, em uma frase: construir uma pipeline que preveja a evasão de alunos (classificação binária), com feature engineering para dados numéricos e categóricos, separação treino/teste, validação cruzada, análise de overfitting/underfitting, deploy em Streamlit, repositório documentado e vídeo de pelo menos 5 minutos.

| Requisito da prova | Onde está no projeto |
|---|---|
| Feature engineering (numéricos e categóricos) | `src/features.py`, `src/modeling.py`; ADR-002 |
| Separação treino/teste | `src/train.py` (passo 2); ADR-003 |
| Modelo binário com validação cruzada | `src/train.py` (passos 3 e 4); ADR-004, ADR-006 |
| Análise de overfitting/underfitting | `reports/diagnostico.md`, `reports/figures/06_curva_aprendizado.png`; ADR-007 |
| Deploy no Streamlit | `app/app.py`; ADR-008 |
| Repositório com documentação | `README.md`, `docs/` |
| Vídeo ≥ 5 min | Parte B |

---

## Parte A – O que fazer, em ordem

### 1. Preparar o ambiente (5 min)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Colocar a base em `data/` (2 min)
Copie o arquivo "Base Sub Fase 3" para a pasta `data/`. Abra a base uma vez (Excel ou `head`) e anote: nome da coluna que indica a evasão, os valores que ela assume e colunas que sejam identificadores ou que "entreguem" o resultado (por exemplo, data de saída, situação final da matrícula).

### 3. Primeiro treino (5 a 15 min, conforme o tamanho da base)
```bash
python -m src.train --rapido
```
Confira no terminal:
- `Coluna alvo identificada` mostra a coluna certa?
- `Colunas descartadas` faz sentido? Nenhuma coluna importante foi removida?
- A proporção de evasão está coerente com a base?

Se algo estiver errado, ajuste por variáveis de ambiente (tabela no README), por exemplo:
```bash
TARGET_COLUMN=Situacao POSITIVE_VALUES=evadido DROP_COLUMNS=matricula,data_saida CATEGORICAL_COLUMNS=curso python -m src.train --rapido
```
Atenção a colunas que revelam o resultado (vazamento): se o desempenho vier "perfeito demais" (F1 ou ROC-AUC acima de 0,98), investigue `reports/figures/07_importancia_variaveis.png`; provavelmente uma coluna está entregando a resposta e deve entrar em `DROP_COLUMNS`.

### 4. Treino final (10 a 30 min)
```bash
python -m src.train
```
(mesmos ajustes de variáveis de ambiente do passo anterior). Depois, abra e leia, nesta ordem:

1. `reports/eda_resumo.md`: tamanho, balanceamento, ausentes, colunas descartadas.
2. `reports/comparacao_modelos.csv`: qual modelo ganhou e com quanto.
3. `reports/diagnostico.md`: tabela treino × validação × teste e o veredito sobre overfitting/underfitting.
4. `reports/figures/`: os 7 gráficos.

Tome nota dos números que vai citar no vídeo (F1, recall, ROC-AUC no teste; F1 de treino e de validação).

### 5. Revisar o diagnóstico (5 min)
O veredito em `diagnostico.md` segue regras simples (ADR-007). Confirme com a curva de aprendizado:
- Curvas de treino e validação se aproximando → sem overfitting.
- Treino muito acima da validação → overfitting (citar a estratégia: regularização, limitar profundidade).
- Ambas baixas e próximas → underfitting ou limite dos dados.
A conclusão que você falar no vídeo precisa bater com o que os gráficos mostram.

### 6. Testar o app localmente (5 min)
```bash
streamlit run app/app.py
```
Teste: carregar um exemplo do conjunto de teste, clicar em Prever, enviar `models/exemplos.csv` na aba de lote, ver a aba "Sobre o modelo". Se aparecer erro de versão, reinstale com `pip install -r requirements.txt` e rode o treino de novo.

Opcional: `pip install pytest && pytest -q`.

### 7. Publicar no GitHub (10 min)
```bash
git init
git add .
git commit -m "Pipeline de previsão de evasão estudantil"
git branch -M main
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```
Confira no GitHub que `models/model.joblib`, `models/metadata.json`, `models/exemplos.csv` e `reports/` foram enviados (o app precisa deles). O repositório deve estar **público**. Se a base não puder ser pública, remova o arquivo de `data/` antes do commit e registre no README onde obtê-lo.

### 8. Deploy no Streamlit Community Cloud (10 min)
1. Entrar em share.streamlit.io com a conta do GitHub.
2. New app → escolher o repositório, branch `main`, arquivo principal `app/app.py`.
3. Advanced settings → Python 3.11 ou superior.
4. Deploy. Quando abrir, testar em aba anônima e com um exemplo do conjunto de teste.

### 9. Gravar e publicar o vídeo (45 a 60 min, contando ensaio)
Seguir a Parte B. Publicar no YouTube (pode ser "não listado") ou no Drive com acesso liberado por link. Abrir o link em aba anônima para confirmar que funciona.

### 10. Montar a entrega
Preencher `entrega.txt` com os três links e enviar o arquivo.

### Checklist final
- [ ] `python -m src.train` rodou sem erros e gerou `models/` e `reports/`
- [ ] Diagnóstico lido e conferido com a curva de aprendizado
- [ ] App funciona localmente
- [ ] Repositório público com modelo, relatórios e documentação
- [ ] App publicado e testado em aba anônima
- [ ] Vídeo com mais de 5 minutos e link acessível
- [ ] `entrega.txt` com os três links corretos

---

## Parte B – Roteiro do vídeo (alvo: 8 a 9 minutos; mínimo: 5)

Dica geral: grave a tela com duas janelas prontas (repositório/editor e app). Fale com as suas palavras; os tópicos abaixo são o que precisa ser dito, não um texto para ler. Confirme a duração final antes de enviar.

### 0:00 – 0:45 | Abertura e problema
**Na tela:** página inicial do repositório (README).
- Apresentar-se, dizer a disciplina e o tema.
- Problema: prever se um aluno vai evadir; por que isso importa (agir antes da saída, priorizar acompanhamento).
- Roteiro do vídeo: dados → features → treino/teste → validação cruzada → análise → app.

### 0:45 – 1:45 | A base de dados
**Na tela:** `reports/eda_resumo.md` e `reports/figures/01_distribuicao_classes.png`, `02_correlacao_com_evasao.png`.
- Quantos alunos, quantas variáveis, tipos (numéricas e categóricas).
- Proporção de evasão e o que isso implica (desbalanceamento → uso de F1 e `class_weight`; ADR-005).
- Colunas descartadas e por quê.
- Um ou dois achados da correlação.

### 1:45 – 3:30 | Feature engineering
**Na tela:** `src/features.py` e `src/modeling.py` (função `montar_preprocessamento`).
- Numéricas: imputação pela mediana, limitação de outliers (1%–99%), padronização.
- Categóricas: imputação pela moda, One-Hot, categorias raras agrupadas, categorias novas toleradas.
- Variáveis criadas: taxa de aprovação, contagem de ausentes (se houver).
- Ponto-chave: tudo dentro de uma `Pipeline`, reajustada a cada dobra da validação cruzada, para evitar vazamento de dados (ADR-001, ADR-002).

### 3:30 – 4:15 | Separação treino/teste
**Na tela:** `src/train.py`, trecho do `train_test_split`.
- 80/20, estratificado, semente fixa; duplicadas removidas antes (ADR-003).
- O teste só é usado na avaliação final.

### 4:15 – 5:30 | Modelagem e validação cruzada
**Na tela:** `reports/comparacao_modelos.csv` e `reports/figures/03_comparacao_modelos.png`; depois `reports/busca_hiperparametros_top10.csv`.
- Três modelos comparados e por quê (referência linear, floresta, boosting; ADR-006).
- Validação cruzada estratificada de 5 dobras; citar F1 médio e desvio padrão do melhor (ADR-004).
- Ajuste de hiperparâmetros com `RandomizedSearchCV`; citar os parâmetros escolhidos.

### 5:30 – 7:00 | Resultados e overfitting/underfitting
**Na tela:** `reports/diagnostico.md`, `04_matriz_confusao.png`, `05_curva_roc.png`, `06_curva_aprendizado.png`, `07_importancia_variaveis.png`.
- Métricas no teste (F1, recall, precisão, ROC-AUC) e leitura da matriz de confusão (quantos evadidos foram identificados; quantos falsos alarmes).
- **Diagnóstico (ponto central da prova):** mostrar a tabela treino × validação × teste; dizer o veredito (bom ajuste, overfitting ou underfitting) **com os números** e apoiar na curva de aprendizado.
- Se houve overfitting: o que foi feito (regularização, limitação de profundidade, busca de hiperparâmetros). Se não houve: justificar pela proximidade entre treino, validação e teste.
- Variáveis mais importantes e o que isso sugere para a instituição.
- Limitações: dados de uma instituição, limiar de 0,5 ajustável (ADR-005), correlação não é causa.

### 7:00 – 8:30 | Demonstração da aplicação
**Na tela:** app publicado no Streamlit (link real, não localhost).
1. Mostrar o endereço no navegador.
2. Aba **Previsão individual**: carregar um exemplo de aluno que evadiu e prever; depois um que não evadiu; comentar as probabilidades. Se houver um exemplo que o modelo errou, mostrar e comentar (transparência sobre limites).
3. Alterar manualmente um ou dois campos (por exemplo, unidades aprovadas) e mostrar a probabilidade mudando.
4. Aba **Previsão em lote**: enviar `exemplos.csv` e mostrar a tabela de resultados.
5. Aba **Sobre o modelo**: métricas e gráficos.
6. Citar brevemente como o deploy foi feito: repositório no GitHub → Streamlit Cloud → `app/app.py` (ADR-008).

### 8:30 – 9:00 | Encerramento
**Na tela:** repositório (README e pasta `docs/adr`).
- Resumo: o que foi feito e a conclusão principal.
- Próximos passos: mais dados e variáveis (frequência, dados socioeconômicos), monitoramento do modelo, calibração do limiar conforme a capacidade de atendimento.
- Onde achar o código e a documentação.

---

## Perguntas que podem surgir (e onde está a resposta)

| Pergunta | Resposta curta |
|---|---|
| Por que F1 e não acurácia? | Classes desbalanceadas; acurácia esconde falhas na classe minoritária (ADR-005) |
| Como evitou vazamento de dados? | Pré-processamento dentro da pipeline, ajustado só no treino de cada dobra (ADR-001) |
| Por que esse modelo? | Venceu a comparação por validação cruzada e foi ajustado com busca de hiperparâmetros (ADR-006) |
| Como sabe que não houve overfitting? | Treino, validação e teste próximos; curva de aprendizado; critérios do ADR-007 |
| O teste influenciou alguma escolha? | Não; foi usado uma vez, ao final (ADR-003) |
| O que muda se mudar o limiar? | Menor limiar aumenta o recall e os falsos positivos; maior faz o inverso |
| Por que treinou só com 80%? | Para que as métricas valham para o modelo publicado (ADR-008) |
