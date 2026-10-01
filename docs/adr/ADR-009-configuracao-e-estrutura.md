# ADR-009 – Configuração centralizada e estrutura do repositório

- **Status:** Aceito
- **Contexto:** Nome do alvo, valores de evasão e colunas a descartar dependem da base. Além disso, a avaliação considera a documentação dos passos e das conclusões.
- **Decisão:** Concentrar parâmetros em `src/config.py`, com sobrescrita por variáveis de ambiente, e separar o código por responsabilidade (dados, features, modelagem, relatórios, treino, previsão, app). Documentação em `README.md` (execução e funcionamento), `docs/adr/`, `docs/glossario.md` e `docs/roteiro.md`.
- **Alternativas consideradas:** notebook único (difícil de testar e de reutilizar no app); valores fixos no código (obrigam editar vários arquivos a cada mudança de base).
- **Consequências:** Trocar de base exige apenas ajustar a configuração. Há testes automatizados para as partes que não dependem da base. A execução do treino é um único comando, o que facilita a reprodução por quem for avaliar o projeto.
