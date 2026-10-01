# Resumo da base

- Arquivo: `StudentsPrepared.xlsx`
- Linhas originais: 4424; após limpeza: 4423 (1 duplicadas removidas)
- Features utilizadas: 27
- Coluna alvo: `Target`; valores encontrados: ['desistente', 'graduado', 'matriculado']; tratados como evasão (1): ['desistente']
- Evasão: 1420 alunos (32.1%); não evasão: 3003 (67.9%)
- Variáveis numéricas: 22; categóricas/texto: 5

## Colunas descartadas
- nenhuma

## Correção de escala decimal
Notas que perderam o separador decimal (ex.: 13875 em vez de 13,875) foram recuperadas na escala 0-20:
- `UnidadesCurriculares1SemestreGrau`: 1790 valores corrigidos
- `UnidadesCurriculares2SemestreGrau`: 1675 valores corrigidos

## Valores ausentes
- nenhum
