# Report de Ineficiências nas Urgências Hospitalares - SNS Portugal

Este projeto analisa dados públicos do SNS português (**2016-2025**) para identificar padrões de ineficiência operacional, financeira e de recursos humanos nas urgências hospitalares.

**Período de Análise:** Janeiro 2016 - Setembro 2025 (9.75 anos de dados históricos)

---

## Fonte dos Dados

**Portal da Transparência do SNS**  
🔗 https://transparencia.sns.gov.pt/explore/?sort=modified

### Datasets utilizados (2016-2025):

1. **atendimentos-em-urgencia-triagem-manchester.csv** - Atendimentos por cor de triagem Manchester
2. **trabalhadores-por-grupo-profissional.csv** - Recursos humanos por categoria
3. **monitorizacao-sazonal-csh.csv** - Indicadores diários de desempenho

---

## Estrutura do Modelo de Dados (Star Schema)

### Modelo Simplificado (2 Factuais + 4 Dimensões)

```
                    DimCalendar [TimeKey]
                           |
            ┌──────────────┼──────────────┐
            |                             |
            ↓                             ↓
  FactAtendimentosUrgencia_Mensal  FactMonitorizacaoSazonal
  (4.131 linhas, 18 colunas)       (32.870 linhas, 5 colunas)
      |              |                    |
      ↓              ↓                    ↓
  DimRegiao     DimInstituicao       DimIndicador
```

### Relacionamentos (Star Schema)
```
DimCalendar (1) ----(*) FactAtendimentosUrgencia_Mensal
DimCalendar (1) ----(*) FactMonitorizacaoSazonal

DimInstituicao (1) ----(*) FactAtendimentosUrgencia_Mensal
DimRegiao (1) ----(*) FactAtendimentosUrgencia_Mensal
DimRegiao (1) ----(*) DimInstituicao

DimIndicador (1) ----(*) FactMonitorizacaoSazonal
```

### Tabelas Fact

#### 1. FactAtendimentosUrgencia_Mensal (18 colunas)
- **Chaves:** Período, TimeKey, RegiaoID, InstituicaoID (4 colunas)
- **Triagem Manchester:** 7 cores triagem + Total (8 colunas) - **FONTE PRINCIPAL**
- **RH:** Médicos, MedicosInternos, Enfermeiros (3 colunas)
- **Custos:** Despesa, NumDoentes, CustoMedio (3 colunas)
- **Cobertura:** 100% triagem Manchester | 61.9% RH | 0% custos (Estimativa aplicada: €150/episódio)

#### 2. FactMonitorizacaoSazonal (5 colunas)
- **Chaves:** Período, TimeKey, RegiaoID, IndicadorID
- **Métrica:** Valor
- **Granularidade:** Diária (2016-2025)

### Tabelas Dim

- **DimCalendar:** TimeKey, Data, Ano, Mês, Trimestre, Feriados PT, Sazonalidade
- **DimRegiao:** RegiaoID (1-5), Norte/Centro/LVT/Alentejo/Algarve
- **DimInstituicao:** InstituicaoID (1-75), Nome, Tipo (ULS/CH/Hospital/CHU), RegiaoID (68 instituições ativas em 2016-2025)
- **DimIndicador:** IndicadorID (1-4), Tempo Espera/Taxa Verde-Azul/Taxa Internamento/Nº Episódios

---

## Medidas DAX Disponíveis

Ver ficheiro completo: 
- `Medidas_DAX_Completas.dax` (todas as medidas: triagem Manchester, custos, RH, tempos de espera, rankings)

### ÍNDICE DE MEDIDAS DAX (`Medidas_DAX_Completas.dax`)

1. [Métricas Básicas de Atendimento](#1-métricas-básicas-de-atendimento)
2. [Identificação de Urgências Falsas](#2-identificação-de-urgências-falsas)
3. [Análise de Custos e Ineficiência Financeira](#3-análise-de-custos-e-ineficiência-financeira)
4. [Indicadores de Recursos Humanos](#4-indicadores-de-recursos-humanos)
5. [Análise de Tempo de Espera](#5-análise-de-tempo-de-espera)
6. [Análise Temporal e Sazonalidade](#6-análise-temporal-e-sazonalidade)
7. [Rankings e Benchmarking](#7-rankings-e-benchmarking)
8. [Score de Ineficiência Global](#8-score-de-ineficiência-global)
9. [Alertas Críticos e Indicadores](#9-alertas-críticos-e-indicadores)
10. [Medidas Auxiliares](#10-medidas-auxiliares)

---

### 1. Métricas Básicas de Atendimento

```dax
// Totais por cor de triagem
Total Atendimentos = SUM(FactAtendimentosUrgencia[TotalAtendimentos])
Atendimentos Vermelha = SUM(FactAtendimentosUrgencia[Atendimentos_Vermelha])
Atendimentos Laranja = SUM(FactAtendimentosUrgencia[Atendimentos_Laranja])
Atendimentos Amarela = SUM(FactAtendimentosUrgencia[Atendimentos_Amarela])
Atendimentos Verde = SUM(FactAtendimentosUrgencia[Atendimentos_Verde])
Atendimentos Azul = SUM(FactAtendimentosUrgencia[Atendimentos_Azul])
Atendimentos Branca = SUM(FactAtendimentosUrgencia[Atendimentos_Branca])
Atendimentos Sem Triagem = SUM(FactAtendimentosUrgencia[Atendimentos_SemTriagem])
```

### 2. Identificação de Urgências Falsas

```dax
// Falsas urgências = Verde + Azul + Branca
Urgências Falsas = 
    [Atendimentos Verde] + [Atendimentos Azul] + [Atendimentos Branca]

% Urgências Falsas = 
    DIVIDE([Urgências Falsas], [Total Atendimentos], 0)

// Custo estimado desperdiçado
Custo Desperdiçado Falsas Urgências = 
    VAR _PercentFalsas = [% Urgências Falsas]
    VAR _CustoTotal = [Despesa Total]
    RETURN _CustoTotal * _PercentFalsas

// Horas de profissionais desperdiçadas (estimativa: 30min por atendimento)
Horas Desperdiçadas = 
    [Urgências Falsas] * 0.5

// Status por instituição
Status Urgências Falsas = 
    SWITCH(
        TRUE(),
        [% Urgências Falsas] >= 0.60, "🔴 CRÍTICO",
        [% Urgências Falsas] >= 0.50, "🟠 ALERTA VERMELHO",
        [% Urgências Falsas] >= 0.40, "🟡 ATENÇÃO",
        [% Urgências Falsas] >= 0.30, "🔵 MONITORIZAR",
        "🟢 ADEQUADO"
    )
```

### 3. Análise de Custos e Ineficiência Financeira

```dax
Despesa Total = SUM(FactAtendimentosUrgencia[Despesa])

Custo Médio por Doente = 
    DIVIDE(
        SUM(FactAtendimentosUrgencia[Despesa]),
        SUM(FactAtendimentosUrgencia[NumDoentes]),
        0
    )

// NOVO: Custo Médio por Doente (Direto)
// Utiliza a média mensal já normalizada da coluna CustoMedio
Custo Médio por Doente (Direto) = 
    AVERAGE(FactAtendimentosUrgencia[CustoMedio])

Custo por Atendimento = 
    DIVIDE([Despesa Total], [Total Atendimentos], 0)

// Comparação com média nacional
Custo Médio Nacional = 
    CALCULATE(
        [Custo Médio por Doente],
        ALL(DimInstituicao),
        ALL(DimRegiao)
    )

Desvio Custo vs Nacional = 
    [Custo Médio por Doente] - [Custo Médio Nacional]

% Desvio Custo = 
    DIVIDE([Desvio Custo vs Nacional], [Custo Médio Nacional], 0)

% Desperdício Financeiro = 
    [% Urgências Falsas] * [% Desvio Custo]
```

### 4. Indicadores de Recursos Humanos

```dax
Total Médicos = SUM(FactAtendimentosUrgencia[Médicos])
Total Médicos Internos = SUM(FactAtendimentosUrgencia[MedicosInternos])
Total Enfermeiros = SUM(FactAtendimentosUrgencia[Enfermeiros])

Total Profissionais = 
    [Total Médicos] + [Total Médicos Internos] + [Total Enfermeiros]

Total Médicos Completo = 
    [Total Médicos] + [Total Médicos Internos]

// Rácios recomendados pela OMS/DGS
Rácio Enfermeiro/Médico = 
    DIVIDE([Total Enfermeiros], [Total Médicos], 0)

// Meta ideal: >= 2.0
Status Rácio Enfermeiro/Médico = 
    SWITCH(
        TRUE(),
        [Rácio Enfermeiro/Médico] < 1.5, "🔴 CRÍTICO",
        [Rácio Enfermeiro/Médico] < 2.0, "🟡 ABAIXO DA META",
        "🟢 ADEQUADO"
    )

// Produtividade
Atendimentos por Médico = 
    DIVIDE([Total Atendimentos], [Total Médicos], 0)

Atendimentos por Enfermeiro = 
    DIVIDE([Total Atendimentos], [Total Enfermeiros], 0)

Atendimentos por Profissional = 
    DIVIDE([Total Atendimentos], [Total Profissionais], 0)

// Défice estimado de enfermeiros para atingir rácio 2:1
Défice Enfermeiros Estimado = 
    VAR _RacioIdeal = 2
    VAR _EnfermeirosNecessarios = [Total Médicos] * _RacioIdeal
    VAR _EnfermeirosAtuais = [Total Enfermeiros]
    RETURN 
        IF(_EnfermeirosAtuais < _EnfermeirosNecessarios,
           _EnfermeirosNecessarios - _EnfermeirosAtuais,
           0
        )

// Custo por profissional
Custo por Profissional = 
    DIVIDE([Despesa Total], [Total Profissionais], 0)
```

### 5. Análise de Tempo de Espera

```dax
Tempo Espera Médio = 
    CALCULATE(
        AVERAGE(FactMonitorizacaoSazonal[Valor]),
        DimIndicador[IndicadorNome] = "Tempo Médio Espera Triagem-Observação"
    )

// Meta Manchester: Vermelho = imediato, Laranja = 10min, Amarelo = 60min
% Dias Acima Meta 60min = 
    VAR Total = 
        CALCULATE(
            COUNTROWS(FactMonitorizacaoSazonal),
            DimIndicador[IndicadorNome] = "Tempo Médio Espera Triagem-Observação"
        )
    VAR Acima60 = 
        CALCULATE(
            COUNTROWS(FactMonitorizacaoSazonal),
            FactMonitorizacaoSazonal[Valor] > 60,
            DimIndicador[IndicadorNome] = "Tempo Médio Espera Triagem-Observação"
        )
    RETURN DIVIDE(Acima60, Total, 0)

Status Tempo Espera = 
    SWITCH(
        TRUE(),
        [Tempo Espera Médio] > 120, "🔴 CRÍTICO",
        [Tempo Espera Médio] > 90, "🟠 ELEVADO",
        [Tempo Espera Médio] > 60, "🟡 ACIMA DA META",
        "🟢 ADEQUADO"
    )
```

### 6. Análise Temporal e Sazonalidade

```dax
// Comparações Year-over-Year (2016-2025)
Total Atendimentos Ano Anterior = 
    CALCULATE(
        [Total Atendimentos],
        SAMEPERIODLASTYEAR(DimCalendar[Data])
    )

Variação YoY Atendimentos = 
    [Total Atendimentos] - [Total Atendimentos Ano Anterior]

% Variação YoY = 
    DIVIDE([Variação YoY Atendimentos], [Total Atendimentos Ano Anterior], 0)

// Comparações Month-over-Month
Total Atendimentos Mês Anterior = 
    CALCULATE(
        [Total Atendimentos],
        DATEADD(DimCalendar[Data], -1, MONTH)
    )

% Variação MoM = 
    DIVIDE(
        [Total Atendimentos] - [Total Atendimentos Mês Anterior],
        [Total Atendimentos Mês Anterior],
        0
    )

// Média móvel 3 meses (suaviza sazonalidade)
Média Móvel 3 Meses = 
    CALCULATE(
        [Total Atendimentos],
        DATESINPERIOD(DimCalendar[Data], LASTDATE(DimCalendar[Data]), -3, MONTH)
    ) / 3

// Análise sazonal
Índice Sazonalidade = 
    VAR _MediaAnual = CALCULATE([Total Atendimentos], ALL(DimCalendar[Mes]))
    VAR _AtualMes = [Total Atendimentos]
    RETURN DIVIDE(_AtualMes, _MediaAnual, 1)

// Picos de inverno vs verão
Atendimentos Inverno = 
    CALCULATE(
        [Total Atendimentos],
        DimCalendar[Sazonalidade] = "Inverno"
    )

Atendimentos Verão = 
    CALCULATE(
        [Total Atendimentos],
        DimCalendar[Sazonalidade] = "Verão"
    )

% Variação Inverno vs Verão = 
    DIVIDE([Atendimentos Inverno] - [Atendimentos Verão], [Atendimentos Verão], 0)
```

---
**Nota sobre 2020-2021:**  
A queda significativa no número de atendimentos de urgência em 2020 e 2021 coincide com o início da pandemia de COVID-19. Durante este período, restrições de circulação,
receio da população em procurar hospitais e mudanças nos protocolos hospitalares resultaram numa redução das idas às urgências, especialmente por motivos não graves. 
Este fenómeno foi observado em Portugal e internacionalmente.

### 7. Rankings e Benchmarking

```dax
Ranking Score Ineficiência = 
    RANKX(
        ALL(DimInstituicao[InstituicaoNome]),
        [Score Ineficiência Global],
        ,
        DESC,
        DENSE
    )

Ranking Custo por Doente = 
    RANKX(
        ALL(DimInstituicao[InstituicaoNome]),
        [Custo Médio por Doente],
        ,
        DESC,
        DENSE
    )

Ranking Produtividade = 
    RANKX(
        ALL(DimInstituicao[InstituicaoNome]),
        [Atendimentos por Profissional],
        ,
        DESC,
        DENSE
    )

Top 10% Ineficientes = 
    IF([Ranking Score Ineficiência] <= COUNTROWS(ALL(DimInstituicao)) * 0.1, "SIM", "NÃO")

Top 20% Produtividade = 
    IF([Ranking Produtividade] <= COUNTROWS(ALL(DimInstituicao)) * 0.2, "SIM", "NÃO")
```

### 8. Score de Ineficiência Global

```dax
// Score de 0-100 (quanto maior, pior)

// Score de 0-100 (quanto maior, pior)
Score Ineficiência Global = 
    VAR Score_NaoUrgentes = [% Não Urgentes] * 40
    VAR Score_TempoEspera = MIN(DIVIDE([Tempo Espera Médio], 120, 0), 1) * 30
    VAR Score_Produtividade = IF([Registros com RH] > 0, (1 - MIN(DIVIDE([Atendimentos por Médico], 500, 0), 1)) * 15, 0)
    VAR Score_Custos = MIN(DIVIDE([Custo Desperdiçado com Não Urgentes], [Despesa Efetiva], 0), 1) * 15
    RETURN Score_NaoUrgentes + Score_TempoEspera + Score_Produtividade + Score_Custos

// Ponderação:
// - 40% Não Urgentes
// - 30% Tempo de Espera
// - 15% Produtividade
// - 15% Custo Desperdiçado

Status Score Global = 
    SWITCH(
        TRUE(),
        [Score Ineficiência Global] >= 70, "🔴 CRÍTICO",
        [Score Ineficiência Global] >= 50, "🟠 ALERTA",
        [Score Ineficiência Global] >= 30, "🟡 ATENÇÃO",
        "🟢 ADEQUADO"
    )
```

### 9. Alertas Críticos e Indicadores

```dax
🚨 Alerta Crítico = 
    VAR _Score = [Score Ineficiência Global]
    VAR _UrgenciasFalsas = [% Urgências Falsas]
    VAR _Desperdicio = ABS([% Desvio Custo])
    VAR _RacioRH = [Rácio Enfermeiro/Médico]
    VAR _TempoEspera = [Tempo Espera Médio]
    RETURN
        SWITCH(
            TRUE(),
            _Score > 70 && _UrgenciasFalsas > 0.5, "⛔ INTERVENÇÃO IMEDIATA - Colapso Sistémico",
            _UrgenciasFalsas > 0.5, "⚠️ CAMPANHA SENSIBILIZAÇÃO URGENTE",
            _Desperdicio > 0.35, "⚠️ AUDITORIA FINANCEIRA NECESSÁRIA",
            _RacioRH < 1.5, "⚠️ DÉFICE CRÍTICO DE ENFERMEIROS",
            _TempoEspera > 120, "⚠️ TEMPOS DE ESPERA PERIGOSOS",
            _Score > 50, "🔶 MONITORIZAÇÃO APERTADA",
            "✅ Sem Alertas Críticos"
        )

⚠️ Rácio Enfermeiro/Médico Abaixo de 2 = 
    IF([Rácio Enfermeiro/Médico] < 2, "SIM", "NÃO")

⚠️ Produtividade Baixa = 
    VAR _MediaNacional = CALCULATE([Atendimentos por Profissional], ALL(DimInstituicao))
    RETURN IF([Atendimentos por Profissional] < _MediaNacional * 0.8, "SIM", "NÃO")

⚠️ Custo Elevado = 
    IF([% Desvio Custo] > 0.2, "SIM", "NÃO")

// Contador de alertas ativos
Nº Alertas Ativos = 
    IF([⚠️ Rácio Enfermeiro/Médico Abaixo de 2] = "SIM", 1, 0) +
    IF([⚠️ Produtividade Baixa] = "SIM", 1, 0) +
    IF([⚠️ Custo Elevado] = "SIM", 1, 0) +
    IF([% Urgências Falsas] > 0.4, 1, 0) +
    IF([Tempo Espera Médio] > 90, 1, 0)
```

### 10. Medidas Auxiliares

```dax
Contagem Instituições = DISTINCTCOUNT(FactAtendimentosUrgencia[InstituicaoID])
Contagem Meses = DISTINCTCOUNT(FactAtendimentosUrgencia[TimeKey])

Tem Dados Custo = 
    IF(NOT(ISBLANK([Despesa Total])) && [Despesa Total] > 0, "SIM", "NÃO")

Tem Dados RH = 
    IF([Total Profissionais] > 0, "SIM", "NÃO")

Última Atualização = MAX(DimCalendar[Data])

% Cobertura Dados RH = 
    VAR _TotalLinhas = COUNTROWS(FactAtendimentosUrgencia)
    VAR _LinhasComRH = 
        CALCULATE(
            COUNTROWS(FactAtendimentosUrgencia),
            FactAtendimentosUrgencia[Médicos] > 0
        )
    RETURN DIVIDE(_LinhasComRH, _TotalLinhas, 0)

% Cobertura Dados Custos = 
    VAR _TotalLinhas = COUNTROWS(FactAtendimentosUrgencia)
    VAR _LinhasComCustos = 
        CALCULATE(
            COUNTROWS(FactAtendimentosUrgencia),
            FactAtendimentosUrgencia[Despesa] > 0
        )
    RETURN DIVIDE(_LinhasComCustos, _TotalLinhas, 0)
```

---

## Estrutura do Dashboard Implementado

### 1. Página Executiva 🎯
**Objetivo:** Visão macro para administração e decisores políticos.

### 2. Página Operacional ⚙️
**Objetivo:** Monitorização detalhada por instituição.

### 3. Página Financeira 💰
**Objetivo:** Análise do impacto financeiro e desperdício.

### 4. Página Recursos Humanos 👥
**Objetivo:** Análise de equipas e produtividade.

### 5. Página Sazonalidade 📅

### 6. Página Rankings 🏆
**Objetivo:** Benchmarking e Score Global.

### 7. Página Qualidade de Dados 📊
**Objetivo:** Transparência sobre completude e integridade dos dados.

---

## Formatação Condicional Recomendada

### Tabelas/Matrix

| Medida | 🟢 Verde | 🟡 Amarelo | 🟠 Laranja | 🔴 Vermelho |
|--------|----------|------------|------------|-------------|
| **Score Ineficiência Global** | < 30 | 30-50 | 50-70 | > 70 |
| **% Urgências Falsas** | < 30% | 30-40% | 40-50% | > 50% |
| **Custo vs Média Nacional** | < €100 | €100-200 | €200-300 | > €300 |
| **Rácio Enfermeiros/Médico** | ≥ 2.0 | 1.8-2.0 | 1.5-1.8 | < 1.5 |
| **Tempo Espera Médio** | < 60min | 60-90min | 90-120min | > 120min |
| **Produtividade vs Nacional** | > 110% | 90-110% | 80-90% | < 80% |

### Visual Cues

- 🔴 **Crítico**: Exige intervenção imediata
- 🟠 **Alerta**: Requer monitorização apertada
- 🟡 **Atenção**: Em vigilância
- 🔵 **Monitorizar**: Observar evolução
- 🟢 **Adequado**: Dentro dos parâmetros

---

## Guia de Implementação Rápida

### Passo 1: Importar Dados
```powerquery
// No Power BI Desktop: Get Data → Text/CSV
// Importar 4 ficheiros CSV:
// 1. FactAtendimentosUrgencia.csv
// 2. FactMonitorizacaoSazonal.csv
// 3. DimInstituicao.csv
// 4. DimRegiao.csv
// 5. DimIndicador.csv
// Encoding: UTF-8
// Delimiter: ;
```

### Passo 2: Criar DimCalendar
```dax
// Modeling → New Table → Colar código de DimCalendar.m
// Abrange 2016-2025 com feriados PT
```

### Passo 3: Criar Relacionamentos
```
Model View → arrastar e soltar:
- DimCalendar[TimeKey] → FactAtendimentosUrgencia[TimeKey]
- DimCalendar[TimeKey] → FactMonitorizacaoSazonal[TimeKey]
- DimRegiao[RegiaoID] → FactAtendimentosUrgencia[RegiaoID]
- DimInstituicao[InstituicaoID] → FactAtendimentosUrgencia[InstituicaoID]
- DimIndicador[IndicadorID] → FactMonitorizacaoSazonal[IndicadorID]
- DimRegiao[RegiaoID] → DimInstituicao[RegiaoID]
```

### Passo 4: Criar Tabela de Medidas
```dax
// Modeling → New Table
Medidas = { BLANK() }
```

### Passo 5: Adicionar Medidas DAX
```
1. Abrir Medidas_DAX_Completas.dax
2. Copiar cada medida
3. Modeling → New Measure
4. Colar código DAX
5. Agrupar em tabela "Medidas"
6. Aplicar formatação:
   - % → Percentage (1 decimal)
   - € → Currency (0 decimals)
   - # → Whole Number (com separador milhares)
```

### Passo 6: Criar Páginas de Dashboard
```
1. Criar 7 páginas:
   - Executivo
   - Operacional
   - Financeiro
   - RH
   - Temporal
   - Benchmarking
   - Qualidade de Dados

2. Adicionar visuais conforme sugerido acima
3. Inserir slicers (Ano, Região, Instituição)
4. Aplicar formatação condicional às tabelas
5. Sincronizar slicers entre páginas (View → Sync Slicers)
6. Configurar drill-through para páginas de detalhe
```

### Passo 7: Publicar
```
Home → Publish → Escolher workspace
Configurar refresh automático (Settings → Schedule refresh)
Configurar Row-Level Security se necessário
```

---

## ⚙️ Configurações Avançadas

### Row-Level Security (RLS)
```dax
// Para restringir acesso por região:
// Manage Roles → Create Role "Região_Norte"
[RegiaoNome] = "Região de Saúde Norte"
// Aplicar a utilizadores específicos após publicação
```

### Drill-through
```
// Criar página de detalhes "Instituição_Detalhes"
// Visual Actions → Drill through → Selecionar InstituicaoID
// Permite clicar numa instituição e ver análise completa
```

### Bookmarks
```
// View → Bookmarks → Add
// Criar bookmarks para diferentes vistas:
// - "Vista Críticos" (filtrado Score > 70)
// - "Vista Top Performers" (Top 20% produtividade)
// - "Vista Temporal 2020-2025" (últimos 5 anos)
```

### Performance Optimization
```
// Modeling → Manage Aggregations
// Criar agregações para FactMonitorizacaoSazonal (64k linhas)
// Query reduction: File → Options → Query reduction
// Desativar "Auto date/time"
```

---

## Limitações e Notas

- **Custos:** Média calculada de 150 euros por episódio de urgência.
Custo Real para o SNS (valor de referência)
O custo médio de referência no SNS para um episódio de urgência é de 112€. Este é o valor usado internamente pelo SNS para contabilizar os custos.
Contudo, a ULS de Santa Maria indicou que o valor médio real pode chegar aos 252€ quando há necessidade de exames ou procedimentos adicionais.
Resumo Rápido: Utente paga: 18€ a 40€ (taxa moderadora)
Custo SNS (padrão): 112€
Custo SNS (com exames): pode chegar a 252€+

Diferença: O SNS suporta a maior parte dos custos, cobrando apenas uma pequena taxa moderadora que visa regular o uso dos serviços de urgência.
  
- **RH:** 61.9% cobertura (2.558 de 4.131 linhas)
  - Usar filtro `[Tem Dados RH] = "SIM"` para análises de recursos humanos

- **Granularidade:**
  - Atendimentos: Mensal agregado
  - Monitorização: Diária (tempo espera, taxas)
  - Não permite análise intradiária (turnos, horários de pico)

- **Dados 2016-2025:**
  - Período completo de 10 anos
  - Permite análise de tendências de longo prazo
  - Identificação de impactos de políticas públicas
  - Comparação pré/pós pandemia COVID-19 (2020-2021)

---

## Ficheiros Principais

### Dados (Prontos para Importação)
- ✅ `FactAtendimentosUrgencia_Mensal.csv` (4.131 registos, 2016-2025)
- ✅ `FactMonitorizacaoSazonal.csv` (32.870 registos, 2016-2025)
- ✅ `DimRegiao.csv` (5 regiões)
- ✅ `DimInstituicao.csv` (75 instituições, 68 ativas)
- ✅ `DimIndicador.csv` (4 indicadores)

### Medidas e Documentação
- ✅ `Relatorio_SNS.md` - **Relatório SNS** (Substitui anteriores)
- ✅ `Medidas_DAX_Completas.dax` - 50+ medidas organizadas
- ✅ `Medidas_Profissionais.dax` - Análise específica de RH
- ✅ `DimCalendar.m` - Calendário com feriados PT (2016-2025)
- ✅ `README.md` - Este ficheiro

### Scripts Histórico (Arquivo)
- `scripts_historico/` - scripts Python de normalização executados

---

## Indicadores de Ineficiência

1. **Urgências Falsas**: % Verde/Azul/Branca
   - Meta: < 30%
   - Crítico: > 50%

2. **Tempos de Espera**: vs metas Manchester
   - Vermelho: Imediato
   - Laranja: 10min
   - Amarelo: 60min
   - Verde: 120min

3. **Custos**: Variação entre instituições similares
   - Meta: ±10% da média do grupo
   - Crítico: > 35% acima da média

4. **RH**: Rácio Enfermeiro/Médico
   - Meta OMS: ≥ 2.0
   - Crítico: < 1.5

---

## Suporte e Contacto

Para questões sobre:
- **Dados**: Portal Transparência SNS (transparencia.sns.gov.pt)
- **Implementação**: João Domingues Pereira
- **Normalizações**: Consultar scripts Python em `/scripts_historico/`

---

## Changelog

### v3.5 - Dezembro 2025 (Atualização Final)
- ✅ **Tabela renomeada:** `FactAtendimentosUrgencia.csv` → `FactAtendimentosUrgencia_Mensal.csv` (compatibilidade Power BI)
- ✅ **Filtro temporal rigoroso:** Apenas dados de 2016 em diante (removidos 2013-2015 fisicamente)
- ✅ **Dados atualizados:** 4.131 registos mensais (2016-01 a 2025-09), 68 instituições ativas
- ✅ **Monitorização atualizada:** 32.870 registos diários (até 17 Dez 2025)
- ✅ **Scripts consolidados:** 45 scripts reduzidos a 3 essenciais com documentação
- ✅ **Automação completa:** Pipeline de atualização automática com backups

### v3.4 - Dezembro 2025
- ✅ **Relatório Unificado:** Criação de `Relatorio_SNS.md` agregando toda a documentação.
- ✅ **Filtro Temporal Rigoroso:** Dados filtrados estritamente para 2016-2025 (excluindo 2013-2015).
- ✅ **Justificação de Custos:** Documentação explícita da exclusão da tabela de custos reais (cobertura 5.3%) em favor do modelo estimativo.
- ✅ **Atualização de Contagens:** FactAtendimentosUrgencia_Mensal (4.131 linhas) e FactMonitorizacaoSazonal (32.870 linhas).

### v3.3 - Novembro 2025
- ✅ **Modelo otimizado:** 23 → 18 colunas finais em FactAtendimentosUrgencia
- ✅ **Removida coluna UrgenciaGeral:** Baixa cobertura (34.9% global, 10% em 2024-2025)
- ✅ **Foco 100% em Triagem Manchester:** Fonte única e completa (100% cobertura)
- ✅ **TotalAtendimentos corrigido:** Era 0, agora soma correta das 7 cores (363,9M atendimentos 2016-2025)
- ✅ **Análise de queda confirmada:** Não há queda real - apenas cobertura reduzida de dados secundários
- ✅ **Dataset descartado:** atendimentos-por-tipo-de-urgencia-hospitalar.csv não acrescenta valor
- ✅ **Backups múltiplos:** 3 versões guardadas para rollback se necessário

### v3.2 - Novembro 2025
- ⚠️ **Tentativa de integração de tipos de urgência** (posteriormente descartada)
- ⚠️ **Identificado problema de cobertura**: Apenas 10% em 2024-2025

### v3.1 - Novembro 2025
- ⚠️ **Tentativa inicial** com múltiplos tipos de urgência (abandonada)

### v3.0 - Novembro 2025
- ✅ Análise expandida para 2016-2025 (10 anos de dados)
- ✅ 50+ medidas DAX completas com alertas automáticos
- ✅ Score Ineficiência Global implementado
- ✅ 6 dashboards sugeridos com visuais detalhados
- ✅ Formatação condicional completa
- ✅ Documentação expandida

### v2.0 - Novembro 2025
- ✅ Normalização de 76 instituições (694 alterações)
- ✅ Correção de mojibake (caracteres corrompidos)
- ✅ Preservação de acentuação portuguesa
- ✅ DimCalendar com feriados PT
- ✅ Relacionamentos star schema otimizados

### v1.0 - Setembro 2025
- Estrutura inicial do modelo
- Importação de dados SNS
- Medidas básicas de atendimento

---

## Licença e Termos de Uso

Dados públicos do **Portal da Transparência do SNS**.  
Uso permitido para fins de análise, auditoria e melhoria dos serviços de saúde.

---

**Última Atualização:** 20 de Dezembro de 2025  
**Versão:** V 3.5  
**Autor:** João Domingues Pereira - Projeto business intelligence SNS  
**Período de Dados:** 2016-2025 (9.75 anos)

## Nota sobre custos

A tabela original de custos (`custo-de-tratamento-mensal-por-doente.csv`) foi removida do relatório principal devido à baixa cobertura de dados, especialmente nos anos mais recentes, o que poderia levar a interpretações erradas.

A partir de agora, todas as análises financeiras usam uma estimativa fixa de **150 euros por episódio de urgência**, baseada nos preços de referência do SNS e considerando custos médios de recursos humanos, exames e tratamentos. Este valor não inclui internamento.

> **Transparência:** Esta abordagem garante maior robustez e evita distorções causadas por dados incompletos. Recomenda-se que qualquer análise financeira seja interpretada como uma estimativa média nacional.
