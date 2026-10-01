# Roteiro detalhado

Complementa o `roteiro.md`. Aqui cada trecho do vídeo tem: **tempo**, **o que abrir na tela**, **o que clicar/executar** e **fala sugerida**. As falas são um ponto de partida: adapte com as suas palavras. Tudo que está entre `[colchetes]` deve ser trocado pelo valor real que sair dos arquivos em `reports/`.

Meta de duração: 8 a 9 minutos (a prova exige no mínimo 5). A fala sugerida soma cerca de 1.200 palavras, o que dá aproximadamente 8 minutos em ritmo normal.

---

## 1. Antes de gravar

### 1.1 Preparação técnica
- [ ] Treino final executado (`python -m src.train`) e relatórios conferidos.
- [ ] App publicado e aberto em uma aba do navegador (link real).
- [ ] Repositório do GitHub aberto em outra aba, no README.
- [ ] Editor (VS Code) com a pasta do projeto aberta e estas abas, na ordem: `src/data.py`, `src/features.py`, `src/modeling.py`, `src/train.py`.
- [ ] Imagens de `reports/figures/` abertas ou acessíveis pelo explorador de arquivos do editor.
- [ ] `models/exemplos.csv` salvo em local de fácil acesso para o envio em lote.
- [ ] Fonte do editor ampliada (zoom 150%) e notificações desligadas.
- [ ] Teste de áudio de 10 segundos.

### 1.2 Números reais da sua base (já preenchidos)
Resultado do treino completo com `StudentsPrepared.xlsx`. Se você treinar de novo com a mesma base e a mesma semente, os valores se repetem; se mudar qualquer configuração, reconfira em `reports/`.

| Item | Onde encontrar | Valor |
|---|---|---|
| Nº de alunos / variáveis | `reports/eda_resumo.md` | 4.424 linhas (4.423 após remover 1 duplicada) / 27 variáveis (22 numéricas e 5 categóricas) |
| Evasão | `reports/eda_resumo.md` | 32,1% (1.420 desistentes; 3.003 não evadiram) |
| Colunas descartadas / ausentes | `reports/eda_resumo.md` | nenhuma / nenhum |
| Correção de dados | `reports/eda_resumo.md` | 1.790 e 1.675 notas dos dois semestres com a vírgula decimal perdida, recuperadas (ADR-011) |
| Variáveis derivadas | código e ADR-002 | taxa de aprovação do 1º e do 2º semestre; variação 2º − 1º semestre em unidades aprovadas e em nota |
| F1 de validação (RL / RF / GB) | `reports/comparacao_modelos.csv` | 0,780 / 0,773 / 0,781 (desvio padrão ≈ 0,02: empate técnico) |
| F1 de treino (RL / RF / GB) | `reports/comparacao_modelos.csv` | 0,797 / 1,000 / 0,980 |
| Modelo escolhido | `reports/diagnostico.md` | Regressão Logística, `C` = 0,0746 (regularização forte) |
| F1 treino / validação / teste | `reports/diagnostico.md` | 0,793 / 0,785 / 0,815 |
| Recall, precisão, ROC-AUC, acurácia (teste) | `reports/diagnostico.md` | 0,838 / 0,793 / 0,936 / 0,878 |
| Veredito | `reports/diagnostico.md` | bom ajuste (sem overfitting nem underfitting) |
| Matriz de confusão (teste, 885 alunos) | `figures/04_matriz_confusao.png` | 539 acertos de "não evadiu", 62 falsos alarmes, 46 evadidos não identificados, 238 evadidos identificados |
| Variáveis mais importantes | `figures/07_importancia_variaveis.png` | unidades aprovadas no 2º semestre (muito acima das demais), unidades aprovadas no 1º, mensalidades em dia, unidades inscritas no 2º |

### 1.3 Pontos que valem destaque no vídeo (com os números acima)
- **Overfitting nos modelos de árvore:** Random Forest e Gradient Boosting chegam a F1 de treino de 1,00 e 0,98, contra 0,77 e 0,78 na validação. Isso é overfitting clássico e mostra que você sabe reconhecê-lo. O modelo final foi escolhido justamente por empatar com eles na validação sendo mais simples (ADR-006).
- **Curva de aprendizado:** treino e validação ficam praticamente coladas em torno de 0,79 desde os primeiros 20% dos dados. Interpretação: não há variância (overfitting) e mais dados não melhorariam; o limite está na informação das variáveis.
- **Teste acima da validação (0,815 contra 0,785):** diferença de 0,03, dentro do ruído de um teste de 885 alunos; não é sinal de problema.
- **Correção das notas:** é um bom exemplo de cuidado com a qualidade dos dados (ADR-011). Mostrar em `reports/eda_resumo.md`.
- **Definição do alvo:** "Matriculado" conta como não evadiu. Se perguntarem, a alternativa de excluí-los dá F1 ≈ 0,89, mas responde a outra pergunta e descarta 18% dos alunos (ADR-010).
- **Limitações a citar:** as variáveis do 2º semestre só existem depois de um ano de curso, então a previsão é tardia; alunos "Matriculado" podem evadir depois; correlação não é causa.

---|---|---|
| Nº de alunos / nº de variáveis | `reports/eda_resumo.md` | [  ] / [  ] |
| % de evasão | `reports/eda_resumo.md` | [  ]% |
| Colunas descartadas | `reports/eda_resumo.md` | [  ] |
| Variáveis derivadas criadas | `reports/diagnostico.md` / código | [  ] |
| Modelo vencedor | `reports/comparacao_modelos.csv` | [  ] |
| F1 de validação dos 3 modelos | `reports/comparacao_modelos.csv` | [  ] / [  ] / [  ] |
| Hiperparâmetros escolhidos | `reports/diagnostico.md` | [  ] |
| F1 treino / validação / teste | `reports/diagnostico.md` | [  ] / [  ] / [  ] |
| Recall e precisão no teste | `reports/diagnostico.md` | [  ] / [  ] |
| ROC-AUC no teste | `reports/diagnostico.md` | [  ] |
| Veredito do diagnóstico | `reports/diagnostico.md` | [  ] |
| 3 variáveis mais importantes | `reports/figures/07_importancia_variaveis.png` | [  ] |
| Falsos negativos / falsos positivos | `reports/figures/04_matriz_confusao.png` | [  ] / [  ] |

---

## 2. Roteiro de gravação

### Bloco 1 | Abertura (0:00 – 0:45)
**Tela:** README do repositório no GitHub.
**Ação:** deixar a página parada, rolando só até a seção "Estrutura" no final do bloco.

**Fala:**
> Olá, meu nome é [nome] e este é o projeto da prova substitutiva da Fase 3 de Machine Learning Engineering. O problema que escolhi resolver é a evasão de estudantes: dado o desempenho acadêmico de um aluno, o modelo estima se ele tem risco de evadir. Isso é útil porque permite à instituição agir antes da saída, priorizando quem mais precisa de acompanhamento.
>
> Neste vídeo vou mostrar a base de dados, o tratamento das variáveis, a separação entre treino e teste, a validação cruzada, a análise de overfitting e underfitting, e por fim a aplicação publicada no Streamlit.

---

### Bloco 2 | A base de dados (0:45 – 1:45)
**Tela:** `reports/eda_resumo.md`, depois `figures/01_distribuicao_classes.png` e `figures/02_correlacao_com_evasao.png`.
**Ação:** destacar com o cursor as linhas de tamanho, proporção de evasão e colunas descartadas.

**Fala:**
> A base tem [N] alunos e [M] variáveis, entre numéricas, como [exemplos], e categóricas, como [exemplos]. A variável alvo é [nome da coluna], e a evasão representa [X]% dos casos. [Se desbalanceada: Isso é um desbalanceamento, e por isso escolhi o F1 como métrica principal em vez da acurácia, além de usar peso de classe nos modelos.]
>
> Antes de modelar, removi uma linha duplicada e verifiquei que não há valores ausentes nem colunas inúteis. Um ponto importante: cerca de 40% das notas dos dois semestres estavam corrompidas, com a vírgula decimal perdida, por exemplo 13,875 aparecendo como 13875. Como a escala é de 0 a 20, consegui recuperar os valores, e confirmei que a regra é consistente: nota maior que zero coincide exatamente com ter alguma unidade aprovada.
>
> Neste gráfico de correlação, vemos que [duas ou três variáveis] têm a relação mais forte com a evasão, o que faz sentido porque [explicação curta em linguagem de negócio].

---

### Bloco 3 | Feature engineering (1:45 – 3:30)
**Tela:** `src/modeling.py`, função `montar_preprocessamento`; depois `src/features.py`.
**Ação:** rolar devagar pelo código, destacando cada bloco enquanto fala.

**Fala:**
> Todo o tratamento está dentro de uma única pipeline do scikit-learn. Isso é importante por um motivo: se eu tratasse os dados antes de separar treino e validação, informações da validação vazariam para o treino e as métricas ficariam otimistas. Com a pipeline, cada transformação é aprendida só com os dados de treino de cada dobra.
>
> Para as variáveis numéricas, faço três passos. Primeiro, a imputação dos ausentes pela mediana, que é menos sensível a valores extremos que a média. Segundo, a limitação de outliers entre os percentis 1 e 99, para que valores muito fora do padrão não distorçam o modelo sem que eu precise apagar linhas. Terceiro, a padronização, que coloca as variáveis na mesma escala, o que ajuda especialmente a regressão logística.
>
> Para as categóricas, imputo pela moda e aplico One-Hot Encoding, que transforma cada categoria em uma coluna de zero e um. Escolhi One-Hot porque as categorias não têm ordem, e um número inteiro sugeriria uma ordem que não existe. Categorias raras, com menos de cinco ocorrências, são agrupadas, e categorias inéditas na hora da previsão não quebram o app.
>
> Também criei variáveis derivadas, a taxa de aprovação de cada semestre, que divide as unidades aprovadas pelas inscritas, e a variação do 1º para o 2º semestre em unidades aprovadas e em nota. Como a base não tem valores ausentes, não foi preciso criar a contagem de ausentes. A taxa de aprovação é mais informativa que os dois números separados porque normaliza o desempenho pela carga de cada aluno.

---

### Bloco 4 | Separação treino e teste (3:30 – 4:15)
**Tela:** `src/train.py`, trecho do `train_test_split`.

**Fala:**
> Separei a base em 80% para treino e 20% para teste, de forma estratificada, ou seja, mantendo a mesma proporção de evasão nos dois conjuntos, e com semente fixa para o resultado ser reproduzível. O conjunto de teste fica guardado e só é usado uma vez, no final, para medir o desempenho em dados que o modelo nunca viu. Nenhuma escolha de modelo ou de hiperparâmetro foi feita olhando para ele.

---

### Bloco 5 | Modelagem e validação cruzada (4:15 – 5:30)
**Tela:** `reports/comparacao_modelos.csv` (ou `figures/03_comparacao_modelos.png`), depois `reports/busca_hiperparametros_top10.csv`.

**Fala:**
> Comparei três modelos: uma regressão logística, como referência simples e interpretável, uma Random Forest e um Gradient Boosting, que são modelos de árvores com mais capacidade. Todos foram avaliados com validação cruzada estratificada de 5 dobras, sobre o conjunto de treino.
>
> O F1 médio de validação foi [X] para a regressão logística, [Y] para a Random Forest e [Z] para o Gradient Boosting. O melhor foi o [modelo], com desvio padrão de [dp] entre as dobras, o que indica [estabilidade / instabilidade].
>
> Em seguida, ajustei os hiperparâmetros desse modelo com busca aleatória, usando as mesmas dobras. Os parâmetros escolhidos foram [citar], e vários deles são de regularização, como [profundidade máxima / mínimo de amostras por folha / parâmetro C], que ajudam a controlar o overfitting.

---

### Bloco 6 | Resultados e overfitting/underfitting (5:30 – 7:00)
**Tela:** `reports/diagnostico.md`, `figures/06_curva_aprendizado.png`, `figures/04_matriz_confusao.png`, `figures/05_curva_roc.png`, `figures/07_importancia_variaveis.png`.
**Ação:** nesta ordem. Começar pela tabela do diagnóstico e ficar nela por pelo menos 30 segundos, porque é o ponto central da prova.

**Fala (tabela do diagnóstico):**
> Esta tabela compara o desempenho em três situações: treino, validação cruzada e teste. O F1 no treino foi [A], na validação [B] e no teste [C].

**Fala, se o veredito for bom ajuste:**
> A diferença entre treino e validação é de apenas [A−B], e o teste ficou muito próximo da validação. Isso mostra que o modelo não decorou os dados de treino, ou seja, não há overfitting relevante, e também que não é simples demais, porque o desempenho é consistente e [adequado]. A curva de aprendizado confirma: as curvas de treino e validação [se aproximam / estabilizam] conforme aumentamos os dados.

**Fala, se o veredito for overfitting:**
> O F1 de treino é [A], bem acima do de validação, [B], uma diferença de [A−B]. Isso caracteriza overfitting: o modelo aprende detalhes do treino que não se repetem em dados novos. Para reduzi-lo, usei regularização, limitando [profundidade / folhas / C], e o ajuste de hiperparâmetros por validação cruzada. A curva de aprendizado mostra que [ainda existe um espaço entre as curvas, e que mais dados ajudariam].

**Fala, se o veredito for underfitting:**
> O F1 é baixo tanto no treino, [A], quanto na validação, [B], e os dois são próximos. Isso indica underfitting, ou limite da informação disponível: o modelo não consegue capturar mais padrão com as variáveis atuais. Como o teste, [C], ficou alinhado com a validação, o resultado é consistente, mas o caminho para melhorar é incluir novas variáveis, e não aumentar a complexidade do modelo.

**Fala (demais gráficos):**
> No teste, o modelo tem recall de [R], ou seja, identifica [R]% dos alunos que de fato evadiram, com precisão de [P]. A matriz de confusão mostra [FN] evadidos que o modelo deixou passar e [FP] alertas falsos. O ROC-AUC de [AUC] indica boa capacidade de separar as duas classes.
>
> As variáveis mais importantes foram [1, 2 e 3], o que sugere que [interpretação de negócio]. Vale lembrar que isso mostra associação e não causa, e que o limiar de decisão de 0,5 pode ser reduzido se a instituição preferir capturar mais alunos em risco, aceitando mais alertas falsos.

---

### Bloco 7 | Demonstração do app (7:00 – 8:30)
**Tela:** aba do navegador com o app publicado. Mostrar o endereço (URL) no início.

**Passo a passo:**
1. Aba **Previsão individual**. No seletor "Carregar um aluno do conjunto de teste", escolher um exemplo cujo resultado real foi **evadiu** e clicar em **Prever**.
2. Escolher um exemplo de **não evadiu** e prever de novo.
3. Alterar manualmente um campo relevante (por exemplo, unidades aprovadas) e prever, mostrando a mudança na probabilidade.
4. Aba **Previsão em lote**: enviar `exemplos.csv` e mostrar a tabela e o contador de alunos em risco.
5. Aba **Sobre o modelo**: passar pelas métricas e pela curva de aprendizado.

**Fala:**
> Esta é a aplicação publicada no Streamlit, com este endereço público. Na aba de previsão individual, posso preencher os dados de um aluno ou carregar um exemplo real do conjunto de teste. Aqui carreguei um aluno que de fato evadiu: o modelo estimou [X]% de probabilidade e classificou como risco de evasão, acertando.
>
> Agora um aluno que não evadiu: a probabilidade foi de [Y]%, classificado como baixo risco. Se eu mudo este campo, [campo], de [valor] para [valor], a probabilidade passa para [Z]%, o que mostra como o modelo reage às variáveis.
>
> Na aba de lote, posso enviar uma planilha com vários alunos e receber todas as previsões, que também posso baixar. E na aba "Sobre o modelo" ficam as métricas e os gráficos que mostrei.
>
> O deploy foi feito conectando este repositório do GitHub ao Streamlit Community Cloud, apontando para o arquivo `app/app.py`, e a aplicação carrega o modelo salvo com o joblib.

---

### Bloco 8 | Encerramento (8:30 – 9:00)
**Tela:** README e pasta `docs/adr` no GitHub.

**Fala:**
> Em resumo, construí uma pipeline completa: tratamento de variáveis numéricas e categóricas, separação estratificada, validação cruzada, ajuste de hiperparâmetros e análise de ajuste, que concluiu [veredito]. O modelo final, o [modelo], alcançou F1 de [C] e ROC-AUC de [AUC] no teste.
>
> Como próximos passos, incluiria novas variáveis, como [frequência / dados socioeconômicos], acompanharia o modelo ao longo do tempo e calibraria o limiar conforme a capacidade de atendimento da instituição. Todo o código e as decisões de arquitetura estão no repositório, no README e na pasta de ADRs. Obrigado por assistir.

---

## 3. Depois de gravar

- [ ] Assistir o vídeo inteiro e conferir que passa de 5 minutos.
- [ ] Conferir se o áudio está claro e se nenhuma informação pessoal ou senha apareceu na tela.
- [ ] Publicar (YouTube "não listado" ou Drive com acesso por link) e abrir o link em aba anônima.
- [ ] Preencher `entrega.txt` com os três links e conferir cada um.

---

## 4. Plano B se algo falhar durante a gravação

| Problema | O que fazer |
|---|---|
| App do Streamlit "dormindo" | Abrir o link alguns minutos antes e clicar em "Wake up" se aparecer; só então gravar |
| Erro de versão ao carregar o modelo | Reinstalar com `pip install -r requirements.txt`, treinar de novo e subir os arquivos de `models/` atualizados |
| Veredito diferente do esperado | Usar a fala do veredito real; a prova pede a justificativa, não um resultado específico |
| F1 ou ROC-AUC acima de 0,98 | Provável vazamento: conferir `figures/07_importancia_variaveis.png`, colocar a coluna suspeita em `DROP_COLUMNS` e treinar de novo antes de gravar |
| Passou do tempo | Encurtar o bloco 3 e o bloco 7, mantendo o bloco 6 completo |
| Ficou abaixo de 5 minutos | Aprofundar blocos 3 e 6 (explicar uma variável derivada e a curva de aprendizado) |
