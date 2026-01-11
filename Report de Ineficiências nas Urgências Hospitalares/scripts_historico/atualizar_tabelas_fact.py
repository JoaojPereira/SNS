"""
Script para atualizar as tabelas Fact do modelo Star Schema
Criado em: 08/12/2025
Objetivo: Transformar dados fonte em tabelas factuais com chaves dimensionais
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

print("=" * 80)
print("ATUALIZAÇÃO DAS TABELAS FACT - MODELO STAR SCHEMA")
print("=" * 80)
print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

# ============================================================================
# CARREGAMENTO DAS TABELAS DIMENSÃO
# ============================================================================

print("📂 A carregar tabelas dimensão...")

# Carregar dimensões
dim_instituicao = pd.read_csv('DimInstituicao.csv', sep=';', encoding='utf-8-sig')
dim_regiao = pd.read_csv('DimRegiao.csv', sep=';', encoding='utf-8-sig')
dim_indicador = pd.read_csv('DimIndicador.csv', sep=';', encoding='utf-8-sig')

print(f"  ✓ DimInstituicao: {len(dim_instituicao)} registos")
print(f"  ✓ DimRegiao: {len(dim_regiao)} registos")
print(f"  ✓ DimIndicador: {len(dim_indicador)} registos")

# Criar dicionários de mapeamento
mapa_regioes = dict(zip(dim_regiao['RegiaoNome'], dim_regiao['RegiaoID']))
mapa_indicadores = {
    'Tempo médio de espera entre a triagem e a primeira observação médica (rede de urgência hospitalar)': 1,
    'Taxa de atendimentos com prioridade VERDE e AZUL na Rede de Urgência Hospitalar': 2,
    'Taxa de atendimentos com internamento na rede de urgência hospitalar': 3,
    'Número estimado de episódios de urgência': 4
}

# Criar dicionário de mapeamento (cache) para performance
mapeamento_cache = {}

# Função para mapear instituição normalizada para ID
def mapear_instituicao(nome_norm, dim_instituicao):
    """
    Mapeia nome normalizado para InstituicaoID usando correspondência inteligente
    """
    # Usar cache se já mapeado
    if nome_norm in mapeamento_cache:
        return mapeamento_cache[nome_norm]
    
    # Remover sufixos comuns
    nome_limpo = str(nome_norm).replace(', EPE', '').replace(', PPP', '').replace(', E.P.E.', '').strip()
    
    # Tentar match direto
    match_direto = dim_instituicao[dim_instituicao['InstituicaoNome'].str.contains(nome_limpo, case=False, na=False, regex=False)]
    if len(match_direto) > 0:
        resultado = match_direto.iloc[0]['InstituicaoID']
        mapeamento_cache[nome_norm] = resultado
        return resultado
    
    # Extrair palavras-chave principais
    palavras_chave = []
    
    # Detectar tipo de instituição
    if nome_limpo.startswith('ULS '):
        palavras_chave.append('Unidade Local de Saúde')
        resto = nome_limpo.replace('ULS ', '').strip()
    elif nome_limpo.startswith('CHU '):
        palavras_chave.append('Universitário')
        resto = nome_limpo.replace('CHU ', '').strip()
    elif nome_limpo.startswith('CH '):
        palavras_chave.append('Centro Hospitalar')
        resto = nome_limpo.replace('CH ', '').strip()
    elif 'Hospital' in nome_limpo:
        palavras_chave.append('Hospital')
        resto = nome_limpo.replace('Hospital ', '').replace('Hospital de ', '').strip()
    else:
        resto = nome_limpo
    
    # Adicionar resto como palavra-chave
    if resto:
        palavras_chave.append(resto)
    
    # Procurar por palavras-chave
    for palavra in palavras_chave:
        if palavra:
            match = dim_instituicao[dim_instituicao['InstituicaoNome'].str.contains(palavra, case=False, na=False, regex=False)]
            if len(match) == 1:
                resultado = match.iloc[0]['InstituicaoID']
                mapeamento_cache[nome_norm] = resultado
                return resultado
            elif len(match) > 1:
                # Se múltiplos matches, tentar com todas as palavras-chave
                for idx, row in match.iterrows():
                    if all(p.lower() in row['InstituicaoNome'].lower() for p in palavras_chave if p):
                        resultado = row['InstituicaoID']
                        mapeamento_cache[nome_norm] = resultado
                        return resultado
    
    mapeamento_cache[nome_norm] = None
    return None

# ============================================================================
# FUNÇÃO PARA GERAR TIMEKEY
# ============================================================================

def gerar_timekey(periodo):
    """Converte período YYYY-MM ou YYYY-MM-DD para YYYYMMDD"""
    try:
        if pd.isna(periodo):
            return None
        
        periodo_str = str(periodo).strip()
        
        # Formato YYYY-MM-DD (data completa)
        if len(periodo_str) == 10 and periodo_str.count('-') == 2:
            return int(periodo_str.replace('-', ''))
        
        # Formato YYYY-MM (mês)
        if len(periodo_str) == 7 and periodo_str.count('-') == 1:
            return int(periodo_str.replace('-', '') + '01')
        
        return None
    except:
        return None

# ============================================================================
# ATUALIZAÇÃO FACTATENDIIMENTOURGENCIA
# ============================================================================

print("\n" + "─" * 80)
print("📊 A processar FactAtendimentosUrgencia...")
print("─" * 80)

try:
    # Carregar dados fonte
    atendimentos = pd.read_csv('atendimentos-em-urgencia-triagem-manchester.csv', 
                               sep=';', encoding='utf-8-sig')
    
    trabalhadores = pd.read_csv('trabalhadores-por-grupo-profissional.csv', 
                                sep=';', encoding='utf-8-sig')
    
    print(f"  📥 Atendimentos: {len(atendimentos)} registos")
    print(f"  📥 Trabalhadores: {len(trabalhadores)} registos")
    
    # Filtrar apenas instituições hospitalares (remover ARS e outras)
    trabalhadores_filtrado = trabalhadores[~trabalhadores['Instituição'].str.contains('Administração Regional|Infarmed|Serviços Centrais|SPMS|ACSS', case=False, na=False)].copy()
    
    # Aplicar mapeamento de instituições em trabalhadores
    trabalhadores_filtrado['InstituicaoID'] = trabalhadores_filtrado['Instituição'].apply(
        lambda x: mapear_instituicao(x, dim_instituicao)
    )
    
    trabalhadores_filtrado = trabalhadores_filtrado[trabalhadores_filtrado['InstituicaoID'].notna()]
    
    # Agregar trabalhadores por período e InstituicaoID
    trab_agregado = trabalhadores_filtrado.groupby(['Período', 'InstituicaoID']).agg({
        'Médicos S/ Internos': 'sum',
        'Médicos Internos': 'sum',
        'Enfermeiros': 'sum'
    }).reset_index()
    
    trab_agregado.columns = ['Período', 'InstituicaoID', 'Médicos', 'MedicosInternos', 'Enfermeiros']
    
    # Mapear InstituicaoID em atendimentos
    atendimentos['InstituicaoID'] = atendimentos['Instituição'].apply(
        lambda x: mapear_instituicao(x, dim_instituicao)
    )
    
    # Remover registos sem mapeamento
    atendimentos = atendimentos[atendimentos['InstituicaoID'].notna()]
    
    # Filtrar apenas dados de 2016 em diante
    atendimentos['Ano'] = atendimentos['Período'].str[:4].astype(int)
    atendimentos = atendimentos[atendimentos['Ano'] >= 2016]
    atendimentos = atendimentos.drop('Ano', axis=1)
    
    # Merge atendimentos com trabalhadores usando InstituicaoID
    fact = atendimentos.merge(trab_agregado, 
                              on=['Período', 'InstituicaoID'], 
                              how='left')
    
    # Preencher valores NaN de trabalhadores com 0
    fact['Médicos'] = fact['Médicos'].fillna(0).astype(int)
    fact['MedicosInternos'] = fact['MedicosInternos'].fillna(0).astype(int)
    fact['Enfermeiros'] = fact['Enfermeiros'].fillna(0).astype(int)
    
    # Adicionar colunas de custos (zeradas - excluídas)
    fact['Despesa'] = 0.0
    fact['NumDoentes'] = 0
    fact['CustoMedio'] = 0.0
    
    # Mapear IDs das dimensões
    fact['RegiaoID'] = fact['Região'].map(mapa_regioes)
    fact['TimeKey'] = fact['Período'].apply(gerar_timekey)
    
    # Remover registos sem mapeamento (InstituicaoID já está mapeado acima)
    fact = fact.dropna(subset=['RegiaoID', 'TimeKey'])
    
    # Converter IDs para inteiro
    fact['RegiaoID'] = fact['RegiaoID'].astype(int)
    fact['InstituicaoID'] = fact['InstituicaoID'].astype(int)
    fact['TimeKey'] = fact['TimeKey'].astype(int)
    
    # Selecionar e ordenar colunas finais
    fact_final = fact[[
        'Período', 'TimeKey', 'RegiaoID', 'InstituicaoID',
        'Vermelha', 'Laranja', 'Amarela', 'Verde', 'Azul', 'Branca', 'SemTriagem', 'TotalAtendimentos',
        'Médicos', 'MedicosInternos', 'Enfermeiros',
        'Despesa', 'NumDoentes', 'CustoMedio'
    ]]
    
    # Renomear colunas para padrão Fact
    fact_final.columns = [
        'Período', 'TimeKey', 'RegiaoID', 'InstituicaoID',
        'Atendimentos_Vermelha', 'Atendimentos_Laranja', 'Atendimentos_Amarela', 
        'Atendimentos_Verde', 'Atendimentos_Azul', 'Atendimentos_Branca', 
        'Atendimentos_SemTriagem', 'TotalAtendimentos',
        'Médicos', 'MedicosInternos', 'Enfermeiros',
        'Despesa', 'NumDoentes', 'CustoMedio'
    ]
    
    # Criar backup
    if os.path.exists('FactAtendimentosUrgencia_Mensal.csv'):
        backup_name = f"FactAtendimentosUrgencia_Mensal.csv.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename('FactAtendimentosUrgencia_Mensal.csv', backup_name)
        print(f"  ✓ Backup criado: {backup_name}")
    
    # Salvar
    fact_final.to_csv('FactAtendimentosUrgencia_Mensal.csv', sep=';', index=False, encoding='utf-8-sig')
    
    print(f"  ✅ FactAtendimentosUrgencia_Mensal atualizada")
    print(f"     • Total de registos: {len(fact_final)}")
    print(f"     • Período: {fact_final['Período'].min()} até {fact_final['Período'].max()}")
    print(f"     • Instituições: {fact_final['InstituicaoID'].nunique()}")
    print(f"     • Total atendimentos: {fact_final['TotalAtendimentos'].sum():,.0f}")

except Exception as e:
    print(f"  ❌ ERRO ao processar FactAtendimentosUrgencia_Mensal: {e}")

# ============================================================================
# ATUALIZAÇÃO FACTMONITORIZACAOSAZONAL
# ============================================================================

print("\n" + "─" * 80)
print("📊 A processar FactMonitorizacaosazonal...")
print("─" * 80)

try:
    # Carregar dados fonte
    monitorizacao = pd.read_csv('monitorizacao-sazonal-csh.csv', 
                                sep=';', encoding='utf-8-sig')
    
    print(f"  📥 Monitorização: {len(monitorizacao)} registos")
    
    # Normalizar nomes de regiões
    mapa_regioes_monitorizacao = {
        'ARS Norte': 'Região de Saúde Norte',
        'ARS Centro': 'Região de Saúde do Centro',
        'ARS Lisboa e Vale do Tejo': 'Região de Saúde LVT',
        'ARS Alentejo': 'Região de Saúde do Alentejo',
        'ARS Algarve': 'Região de Saúde do Algarve'
    }
    
    # Aplicar mapeamento de regiões
    monitorizacao['Região'] = monitorizacao['Região/ARS'].map(mapa_regioes_monitorizacao)
    
    # Filtrar apenas registos com regiões válidas (excluir Portugal Continental)
    monitorizacao = monitorizacao[monitorizacao['Região'].notna()]
    
    # Filtrar apenas dados de 2016 em diante
    monitorizacao['Ano'] = monitorizacao['Período'].str[:4].astype(int)
    monitorizacao = monitorizacao[monitorizacao['Ano'] >= 2016]
    monitorizacao = monitorizacao.drop('Ano', axis=1)
    
    # Mapear indicadores
    monitorizacao['IndicadorID'] = monitorizacao['Indicador'].map(mapa_indicadores)
    
    # Mapear RegiaoID
    monitorizacao['RegiaoID'] = monitorizacao['Região'].map(mapa_regioes)
    
    # Gerar TimeKey
    monitorizacao['TimeKey'] = monitorizacao['Período'].apply(gerar_timekey)
    
    # Remover registos sem mapeamento
    monitorizacao = monitorizacao.dropna(subset=['RegiaoID', 'IndicadorID', 'TimeKey'])
    
    # Converter para inteiro
    monitorizacao['RegiaoID'] = monitorizacao['RegiaoID'].astype(int)
    monitorizacao['IndicadorID'] = monitorizacao['IndicadorID'].astype(int)
    monitorizacao['TimeKey'] = monitorizacao['TimeKey'].astype(int)
    
    # Arredondar valores para 2 casas decimais
    monitorizacao['Valor'] = monitorizacao['Valor'].round(2)
    
    # Selecionar colunas finais
    fact_monit = monitorizacao[['Período', 'TimeKey', 'RegiaoID', 'IndicadorID', 'Valor']]
    
    # Ordenar por data
    fact_monit = fact_monit.sort_values(['TimeKey', 'RegiaoID', 'IndicadorID'])
    
    # Criar backup
    if os.path.exists('FactMonitorizacaosazonal.csv'):
        backup_name = f"FactMonitorizacaosazonal.csv.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename('FactMonitorizacaosazonal.csv', backup_name)
        print(f"  ✓ Backup criado: {backup_name}")
    
    # Salvar
    fact_monit.to_csv('FactMonitorizacaosazonal.csv', sep=';', index=False, encoding='utf-8-sig')
    
    print(f"  ✅ FactMonitorizacaosazonal atualizada")
    print(f"     • Total de registos: {len(fact_monit)}")
    print(f"     • Período: {fact_monit['Período'].min()} até {fact_monit['Período'].max()}")
    print(f"     • Regiões: {fact_monit['RegiaoID'].nunique()}")
    print(f"     • Indicadores: {fact_monit['IndicadorID'].nunique()}")

except Exception as e:
    print(f"  ❌ ERRO ao processar FactMonitorizacaosazonal: {e}")

# ============================================================================
# RESUMO FINAL
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO DA ATUALIZAÇÃO")
print("=" * 80)
print("✅ FactAtendimentosUrgencia_Mensal: OK")
print("✅ FactMonitorizacaosazonal: OK")
print("\n" + "=" * 80)
print("✓ ATUALIZAÇÃO CONCLUÍDA")
print("=" * 80)
print("\nAs tabelas Fact estão prontas para uso no Power BI.")
print("Pode agora atualizar o modelo clicando em 'Atualizar' no Power BI Desktop.")
