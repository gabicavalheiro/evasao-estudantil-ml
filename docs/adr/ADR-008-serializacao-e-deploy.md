# ADR-008 – Serialização do modelo e deploy no Streamlit

- **Status:** Aceito
- **Contexto:** O modelo precisa ser consumido por uma aplicação web pública, gratuita e ligada ao repositório do GitHub.
- **Decisão:** Salvar a pipeline completa com `joblib` (compressão ativada), junto de `metadata.json` com o esquema das colunas de entrada, e publicar o app no Streamlit Community Cloud. O formulário é montado a partir do `metadata.json`, e o modelo final é treinado apenas com o conjunto de treino, para que as métricas reportadas correspondam exatamente ao modelo publicado.
- **Alternativas consideradas:** treinar novamente com toda a base antes de salvar (mais dados, porém as métricas deixam de valer para o modelo publicado); API separada com FastAPI (mais infraestrutura do que o necessário).
- **Consequências:** Deploy simples, com atualização a cada push. O arquivo do modelo depende da versão do scikit-learn, então as versões estão fixadas em `requirements.txt` e o app exibe um aviso se detectar diferença. O modelo precisa ser pequeno para respeitar os limites do plano gratuito.
