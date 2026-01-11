# 📋 ANÁLISE DE SCRIPTS - CONSOLIDAÇÃO

## ✅ SCRIPTS ESSENCIAIS (Manter)

### 1. Atualização Automática
- **atualizar_dados_sns.py** ⭐ - Download e normalização automática do Portal SNS
- **atualizar_tabelas_fact.py** ⭐ - Atualiza tabelas Fact com novos dados

### 2. Conversores (Manter apenas 1)
- **converter_md_to_html.py** - Converte Markdown para HTML (genérico)
- ❌ converter_readme.py - REDUNDANTE (específico)
- ❌ converter_relatorio.py - REDUNDANTE (específico)
- ❌ converter_tecnico.py - REDUNDANTE (específico)

---

## ❌ SCRIPTS OBSOLETOS/REDUNDANTES (Eliminar)

### Normalização e Limpeza (Já integrados em atualizar_dados_sns.py)
1. normalizar_csv_completo.py - Função integrada
2. limpar_csv_atendimentos.py - Função integrada
3. limpar_csv_trabalhadores.py - Função integrada
4. limpar_csv_monitorizacao.py - Função integrada
5. preencher_celulas_vazias.py - Função integrada
6. corrigir_valores_vazios.py - Função integrada
7. remover_decimais.py - Função integrada

### Filtros e Remoções (Já integrados)
8. filtrar_periodo_2016_2025.py - Obsoleto (dados já filtrados)
9. remover_urgenciageral.py - Função integrada
10. remover_admin_regional.py - Função integrada
11. remover_instituicoes_especializadas.py - Função integrada
12. remover_instituicoes_nao_hospitalares.py - Função integrada
13. remover_portugal_continental.py - Função integrada

### Padronização (Já integrados)
14. padronizar_nomes_instituicoes.py - Função integrada
15. padronizar_todos_nomes.py - Função integrada
16. alterar_ppp_para_epe.py - Função integrada
17. encurtar_nomes_colunas.py - Função integrada
18. encurtar_indicadores.py - Função integrada
19. simplificar_urgencias.py - Função integrada

### IDs e TimeKeys (Já integrados em atualizar_tabelas_fact.py)
20. adicionar_ids_factual.py - Função integrada
21. adicionar_ids_monitorizacao.py - Função integrada
22. adicionar_timekey.py - Função integrada

### Criação de Tabelas (Já integrados)
23. criar_dimensoes.py - Executado uma vez, obsoleto
24. criar_factual_consolidada.py - Função integrada
25. modelo_2_factuais.py - Obsoleto (modelo já criado)

### Correções Pontuais (Já aplicadas)
26. corrigir_total_atendimentos.py - Correção já aplicada
27. correcoes_finais_powerbi.py - Correções já aplicadas
28. normalizar_datas_2016.py - Normalização já aplicada

### Análises Exploratórias (Uma vez só)
29. analisar_2024_vs_2025.py - Análise pontual
30. analise_periodos.py - Análise pontual
31. analise_completa_instituicoes.py - Análise pontual
32. comparar_instituicoes.py - Análise pontual
33. comparar_todas_instituicoes.py - Análise pontual
34. arquitetura_modelo_dados.py - Documentação gerada

### Diagnósticos (Já resolvidos)
35. diagnostico_erros_powerbi.py - Problemas resolvidos
36. diagnostico_join.py - Problemas resolvidos
37. verificacao_powerbi.py - Problemas resolvidos

### Geradores Específicos (Obsoletos)
38. gerar_monitorizacao_por_instituicao.py - Obsoleto
39. gerar_valores_mensais.py - Obsoleto

---

## 📊 RESUMO

**Total:** 45 scripts
**Manter:** 3 scripts essenciais
**Eliminar:** 42 scripts obsoletos/redundantes

### Scripts a Manter:
1. ✅ atualizar_dados_sns.py
2. ✅ atualizar_tabelas_fact.py
3. ✅ converter_md_to_html.py (ou substituto simples)

---

## 🎯 BENEFÍCIOS DA CONSOLIDAÇÃO

- ✅ Manutenção simplificada
- ✅ Menos confusão
- ✅ Funcionamento automatizado
- ✅ Código centralizado
- ✅ Fácil atualização futura
