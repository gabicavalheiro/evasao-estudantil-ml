# ADR-010 – Definição da variável alvo (tratamento de "Matriculado")

- **Status:** Aceito
- **Contexto:** A coluna `Target` da base tem três valores: Graduado (2.209), Desistente (1.421) e Matriculado (794). O problema pedido é binário (evadiu / não evadiu). Os alunos "Matriculado" ainda não têm desfecho final conhecido.
- **Decisão:** Evasão (classe 1) = `Desistente`; todos os demais (`Graduado` e `Matriculado`) = não evadiu (classe 0), resultando em 32,1% de evasão. A opção `EXCLUDE_VALUES=matriculado` em `config.py` permite remover os matriculados antes do treino.
- **Alternativas consideradas:** excluir os matriculados. Foi testada como análise de sensibilidade, com os mesmos modelos e a mesma validação: F1 de teste ≈ 0,89 e ROC-AUC ≈ 0,96 (contra 0,82 e 0,94). A melhora é esperada, porque a tarefa passa a ser separar quem desistiu de quem se formou, que é mais fácil.
- **Por que não foi adotada:** o uso real do modelo é estimar o risco de alunos que **ainda estão matriculados**, e esses são justamente os casos que a versão filtrada nunca viu; além disso, ela descarta 18% da base. A definição escolhida é mais exigente e mais fiel ao uso.
- **Consequências:** As métricas reportadas são as da definição mais difícil. Parte dos alunos rotulados como 0 pode evadir no futuro (ruído de rótulo), o que limita o desempenho máximo e deve ser citado como limitação.
