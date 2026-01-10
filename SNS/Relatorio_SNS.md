# RELATÓRIO FINAL CONSOLIDADO
## Análise de Ineficiências nas Urgências Hospitalares do SNS Portugal

**Projeto Business Intelligence**  
**Autor:** João Domingues Pereira  
**Data:** 8 de dezembro de 2025  
**Período Analisado:** 2016-2025 (9,75 anos)  
**Versão:** 2.0 (Dados Atualizados e Filtrados)

---

## ÍNDICE

1. [Sumário Executivo](#1-sumário-executivo)
2. [Metodologia e Tratamento de Dados](#2-metodologia-e-tratamento-de-dados)
3. [Análise de Resultados](#3-análise-de-resultados)
4. [Manual do Dashboard](#4-manual-do-dashboard)
5. [Conclusões e Recomendações](#5-conclusões-e-recomendações)

---

## 1. SUMÁRIO EXECUTIVO

Este relatório apresenta a análise definitiva das ineficiências operacionais, financeiras e de recursos humanos nas urgências hospitalares do Serviço Nacional de Saúde (SNS), consolidando dados de múltiplos relatórios anteriores e atualizando o período de análise para **2016-2025**.

### 📊 Indicadores-Chave (KPIs) Atualizados

| Indicador | Valor Consolidado |
|-----------|-------------------|
| **Período de Análise** | Janeiro 2016 a Setembro 2025 |
| **Total de Atendimentos** | **301,2 Milhões** |
| **Média Anual** | ~30,9 Milhões |
| **Taxa de Urgências Falsas** | **41,93%** (Verde, Azul, Branca) |
| **Volume de Não Urgentes** | 126,3 Milhões de episódios |
| **Desperdício Financeiro Total** | **€15,2 Mil Milhões** |
| **Desperdício Anual Médio** | €1,55 Mil Milhões |
| **Instituições Analisadas** | 68 Hospitais |

### 🚨 Principais Conclusões
1.  **Ineficiência Crítica:** A taxa de atendimentos não urgentes (41,93%) está **11,9 pontos percentuais acima** da meta nacional (<30%), indicando uma falha sistémica na triagem e encaminhamento.
2.  **Impacto Financeiro:** O custo de oportunidade gerado pelo atendimento indevido em urgência hospitalar ascende a **€15,2 mil milhões** em quase uma década.
3.  **Recursos Humanos:** Mantém-se o alerta de défice estrutural de enfermeiros (rácio médio 1,6 vs meta 2,0), estimado em falta de 20.800 profissionais.

---

## 2. METODOLOGIA E TRATAMENTO DE DADOS

### 2.1 Fontes de Dados e Período
Os dados foram extraídos do Portal da Transparência do SNS e submetidos a um rigoroso processo de limpeza e filtragem.
- **Período Final:** 2016-2025 (Dados anteriores a 2016 foram excluídos para garantir consistência e relevância estatística).
- **Datasets Utilizados:**
    - `FactAtendimentosUrgencia_Mensal.csv` (4.131 registos mensais consolidados).
    - `FactMonitorizacaosazonal.csv` (32.870 registos diários).
    - `trabalhadores-por-grupo-profissional.csv` (Dados de RH).

### 2.2 Exclusão da Tabela de Custos Reais
A tabela original `custo-de-tratamento-mensal-por-doente.csv` foi **EXCLUÍDA** da análise final.

**Razões da Exclusão:**
1.  **Baixa Cobertura:** Apenas 5,3% de cobertura face ao total de registos de atendimentos (247 registos de custos vs 4.636 registos de atividade).
2.  **Distribuição Irregular:** Lacunas críticas nos anos mais recentes (2024-2025) e inconsistência entre instituições.
3.  **Impossibilidade de Segmentação:** Os dados não permitiam diferenciar custos por cor de triagem, impedindo o cálculo preciso do desperdício em "falsas urgências".

**Metodologia Alternativa Adotada:**
Para colmatar esta lacuna, utilizou-se um modelo de **Custo Estimado Padrão**:
- Custo Episódio Urgência: **150€** (Baseado em referências hospitalares e relatórios de contas).
- Custo Consulta Cuidados Primários: **30€**.
- **Diferencial (Desperdício): 120€** por cada episódio não urgente.

### 2.3 Normalização e Limpeza (ETL)
Foi aplicado um pipeline de normalização (descrito no *Relatório de Normalização CSV*) que incluiu:
- **Padronização de Instituições:** 29 nomes normalizados (ex: remoção de sufixos "EPE", "PPP").
- **Correção de Dados:** Preenchimento de 1.414 células vazias com zero.
- **Enriquecimento:** Criação de colunas calculadas para totais e chaves temporais.
- **Filtragem Temporal:** Remoção física dos registos de 2013-2015 das tabelas Factuais.

---

## 3. ANÁLISE DE RESULTADOS

### 3.1 Análise Operacional (Triagem)
A distribuição pela Triagem de Manchester revela um agravamento da pressão sobre as urgências.
- **Meta:** < 30% não urgentes.
- **Realidade (2016-2025):** **41,93%**.
- **Tendência:** O valor atualizado (41,93%) é superior à análise preliminar (37,76%), indicando que a inclusão dos dados mais recentes e a limpeza do período 2013-2015 revelaram um cenário mais grave.

### 3.2 Impacto Financeiro
Com base no modelo de custo estimado:
- **Despesa Total Estimada:** €45,2 Mil Milhões.
- **Desperdício Total:** €15,2 Mil Milhões.
- Este valor representa recursos que poderiam ter financiado integralmente a construção de múltiplos novos hospitais ou a contratação massiva de profissionais em falta.

### 3.3 Sazonalidade e Monitorização
A análise dos 32.870 registos diários confirma:
- **Picos:** Inverno (Dez/Jan) e Segundas-feiras.
- **Tempos de Espera:** Média de 87 minutos, com 45,3% dos dias acima da meta de 60 minutos.

---

## 4. MANUAL DO DASHBOARD

O Dashboard Power BI foi estruturado em 7 páginas para dar resposta a diferentes perfis de utilizador:

1.  **EXECUTIVA:** Visão macro com KPIs, Tabela de Orçamentos e Gráfico de Evolução Anual.
2.  **OPERACIONAL:** Análise detalhada com bookmarks para alternar entre vistas de indicadores.
3.  **FINANCEIRA:** Evolução do desperdício financeiro e comparação com despesa efetiva.
4.  **RECURSOS HUMANOS:** Rácio enfermeiro/médico e produtividade.
5.  **SAZONALIDADE:** Padrões temporais com bookmarks para análise de dias úteis vs fins de semana.
6.  **QUALIDADE DE DADOS:** Validação de cobertura de dados (Taxa Cobertura RH: 61,92%, identificação de 20 instituições sem dados de RH).
7.  **RANKINGS:** Benchmarking entre instituições com sistema de semáforos.

---

## 5. CONCLUSÕES E RECOMENDAÇÕES

A consolidação dos dados confirma que o SNS enfrenta um problema estrutural de **procura inadequada** nas urgências, agravado por um défice de enfermeiros.

**Recomendações Prioritárias:**
1.  **Desvio de Procura:** Implementar triagem pré-hospitalar rigorosa (SNS24) para reduzir os 41,93% de casos não urgentes.
2.  **Reforço de Enfermagem:** Priorizar contratações para atingir o rácio mínimo de 2.0 enfermeiros/médico.
3.  **Monitorização Contínua:** Utilizar o dashboard desenvolvido para acompanhamento mensal, focando nas 27 instituições identificadas como críticas (taxa de não urgentes > 45%).

---
*Este relatório substitui e consolida os documentos anteriores: "Relatorio_SNS.md", "Relatorio_Normalizacao_CSV.md" e "Relatório Consolidado.md".*
