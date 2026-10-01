# ADR-011 – Correção de notas que perderam o separador decimal

- **Status:** Aceito
- **Contexto:** Nas colunas `UnidadesCurriculares1SemestreGrau` e `UnidadesCurriculares2SemestreGrau` (escala 0–20), cerca de 40% dos valores estavam corrompidos: o separador decimal foi perdido, de modo que 13,875 aparece como `13875`, 13,30625 como `1330625` e 13,4285714 como `1.34285714285714e16` (1.790 e 1.675 valores, respectivamente). Treinar com esses valores tornaria as colunas inúteis e distorceria a padronização.
- **Decisão:** Em `src/data.py`, detectar colunas em que a maioria dos valores está em 0–20 mas existem valores acima de 200 e dividir cada valor acima de 20 por 10 até caber na escala. Colunas com escala própria (como a nota de admissão, 0–200) não são afetadas. A quantidade de valores corrigidos é registrada em `reports/eda_resumo.md`.
- **Validação da regra:** após a correção, as notas ficam entre 9,8 e 18,9 (média ≈ 12,7); nota maior que zero coincide exatamente com ter ao menos uma unidade aprovada, sem exceções; e os valores que já estavam corretos permanecem inalterados.
- **Alternativas consideradas:** descartar as colunas (perde informação relevante); descartar as linhas (perderia 40% da base); apenas limitar outliers (transformaria valores válidos em um teto sem sentido).
- **Consequências:** As notas voltam a ter significado e podem ser usadas pelo modelo. A correção deve ser mencionada como um tratamento de qualidade de dados; se a origem da base puder ser corrigida, a regra se torna desnecessária e inofensiva.
