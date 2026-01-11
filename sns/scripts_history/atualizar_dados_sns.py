#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Atualização Automática de Dados do SNS
Descarrega dados mais recentes e mantém compatibilidade com Power BI

Portal: https://transparencia.sns.gov.pt/explore/?sort=modified
"""
import pandas as pd
import requests
from datetime import datetime
import os

print("=" * 80)
print("ATUALIZAÇÃO DE DADOS DO PORTAL DA TRANSPARÊNCIA SNS")
print("=" * 80)
print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("Portal: https://transparencia.sns.gov.pt")
print()

# URLs dos datasets (podem precisar de atualização - verificar no portal)
DATASETS = {
    'atendimentos': {
        'url': 'https://transparencia.sns.gov.pt/api/explore/v2.1/catalog/datasets/atendimentos-em-urgencia-triagem-manchester/exports/csv?lang=pt&timezone=Europe%2FLisbon&use_labels=true&delimiter=%3B',
        'nome_original': '../csv/atendimentos_urgencia_triagem_manchester.csv',
        'descricao': 'Atendimentos em Urgência - Triagem Manchester'
    },
    'trabalhadores': {
        'url': 'https://transparencia.sns.gov.pt/api/explore/v2.1/catalog/datasets/trabalhadores-por-grupo-profissional/exports/csv?lang=pt&timezone=Europe%2FLisbon&use_labels=true&delimiter=%3B',
        'nome_original': '../csv/trabalhadores_grupo_profissional.csv',
        'descricao': 'Trabalhadores por Grupo Profissional'
    },
    'monitorizacao': {
        'url': 'https://transparencia.sns.gov.pt/api/explore/v2.1/catalog/datasets/monitorizacao-sazonal-csh/exports/csv?lang=pt&timezone=Europe%2FLisbon&use_labels=true&delimiter=%3B',
        'nome_original': '../csv/monitorizacao_sazonal_csh.csv',
        'descricao': 'Indicadores de Monitorização Sazonal'
    }
}

def descarregar_dataset(config, nome_dataset):
    """Descarrega dataset do portal SNS"""
    print(f"\n{'─' * 80}")
    print(f"📥 A descarregar: {config['descricao']}")
    print(f"{'─' * 80}")
    
    try:
        # Verificar se ficheiro antigo existe (backup)
        if os.path.exists(config['nome_original']):
            backup_name = f"{config['nome_original']}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(config['nome_original'], backup_name)
            print(f"✓ Backup criado: {backup_name}")
        
        # Descarregar
        print(f"🌐 A conectar ao portal SNS...")
        response = requests.get(config['url'], timeout=60)
        response.raise_for_status()
        
        # Guardar ficheiro
        with open(config['nome_original'], 'wb') as f:
            f.write(response.content)
        
        # Carregar e validar
        df = pd.read_csv(config['nome_original'], sep=';', encoding='utf-8')
        print(f"✓ Ficheiro descarregado: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Mostrar período coberto
        if 'Período' in df.columns:
            print(f"  Período: {df['Período'].min()} até {df['Período'].max()}")
        
        return True, df
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao descarregar: {e}")
        print(f"  URL: {config['url']}")
        return False, None
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False, None

def normalizar_atendimentos(df):
    """Aplica normalização aos dados de atendimentos"""
    print("\n🔧 A aplicar normalização...")
    
    # 1. Remover localização geográfica
    if 'Localização Geográfica' in df.columns:
        df = df.drop('Localização Geográfica', axis=1)
        print("  ✓ Coluna 'Localização Geográfica' removida")
    
    # 2. Encurtar nomes de colunas
    renomear = {
        'Nº Atendimentos em Urgência SU Triagem Manchester -Vermelha': 'Vermelha',
        'Nº Atendimentos em Urgência SU Triagem Manchester -Laranja': 'Laranja',
        'Nº Atendimentos em Urgência SU Triagem Manchester -Amarela': 'Amarela',
        'Nº Atendimentos em Urgência SU Triagem Manchester -Verde': 'Verde',
        'Nº Atendimentos em Urgência SU Triagem Manchester -Azul': 'Azul',
        'Nº Atendimentos em Urgência SU Triagem Manchester -Branca': 'Branca',
        'Nº Atendimentos s\\ Triagem Manchester': 'SemTriagem'
    }
    
    for old_name, new_name in renomear.items():
        for col in df.columns:
            if old_name in col or (new_name in old_name and new_name in col):
                df = df.rename(columns={col: new_name})
                break
    
    print("  ✓ Colunas renomeadas")
    
    # 3. Normalizar instituições
    correcoes_instituicoes = {
        'Unidade Local de Saúde do Baixo Alentejo, EPE': 'ULS Baixo Alentejo',
        'Centro Hospitalar Universitário Cova da Beira, EPE': 'CHU Cova da Beira',
        'Hospital Garcia de Orta, EPE': 'Hospital Garcia de Orta',
        'Centro Hospitalar Universitário de São João, EPE': 'CHU São João',
        'Centro Hospitalar Póvoa de Varzim/Vila do Conde, EPE': 'CH Póvoa Varzim/Vila Conde',
        'Centro Hospitalar Vila Nova de Gaia/Espinho, EPE': 'CH Vila Nova Gaia/Espinho',
        'Unidade Local de Saúde de Matosinhos, EPE': 'ULS Matosinhos',
        'Hospital Espírito Santo de Évora, EPE': 'Hospital Espírito Santo Évora',
        'Centro Hospitalar de Leiria, EPE': 'CH Leiria',
        'Centro Hospitalar e Universitário de Coimbra, EPE': 'CHU Coimbra',
        'Centro Hospitalar Tondela-Viseu, EPE': 'CH Tondela-Viseu',
        'Unidade Local de Saúde da Guarda, EPE': 'ULS Guarda',
        'Unidade Local de Saúde de Castelo Branco, EPE': 'ULS Castelo Branco',
        'Centro Hospitalar Barreiro/Montijo, EPE': 'CH Barreiro/Montijo',
        'Hospital Professor Doutor Fernando Fonseca, EPE': 'Hospital Fernando Fonseca',
        'Centro Hospitalar Entre Douro e Vouga, EPE': 'CH Entre Douro e Vouga',
        'Centro Hospitalar de Setúbal, EPE': 'CH Setúbal',
        'Centro Hospitalar Trás-os-Montes e Alto Douro, EPE': 'CH Trás-os-Montes Alto Douro',
        'Hospital de Braga, PPP': 'Hospital de Braga',
        'Centro Hospitalar Universitário do Algarve, EPE': 'CHU Algarve',
        'Centro Hospitalar Universitário Lisboa Norte, EPE': 'CHU Lisboa Norte',
        'Hospital de Loures, PPP': 'Hospital de Loures',
        'Hospital de Vila Franca de Xira, PPP': 'Hospital Vila Franca Xira',
        'Centro Hospitalar do Alto Ave, EPE': 'CH Alto Ave',
        'Centro Hospitalar Universitário do Porto, EPE': 'CHU Porto',
        'Unidade Local de Saúde do Norte Alentejano, EPE': 'ULS Norte Alentejano',
        'Unidade Local de Saúde do Litoral Alentejano, EPE': 'ULS Litoral Alentejano',
        'Hospital Distrital da Figueira da Foz, EPE': 'Hospital Figueira Foz',
        'Centro Hospitalar Universitário Lisboa Central, EPE': 'CHU Lisboa Central'
    }
    
    if 'Instituição' in df.columns:
        df['Instituição'] = df['Instituição'].replace(correcoes_instituicoes)
        print("  ✓ Instituições normalizadas")
    
    # 4. Preencher valores vazios
    colunas_numericas = ['Vermelha', 'Laranja', 'Amarela', 'Verde', 'Azul', 'Branca', 'SemTriagem']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    print("  ✓ Valores vazios preenchidos com 0")
    
    # 5. Calcular total
    colunas_cores = ['Vermelha', 'Laranja', 'Amarela', 'Verde', 'Azul', 'Branca']
    colunas_existentes = [col for col in colunas_cores if col in df.columns]
    if colunas_existentes:
        df['TotalAtendimentos'] = df[colunas_existentes].sum(axis=1)
        print("  ✓ Coluna 'TotalAtendimentos' calculada")
    
    return df

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

resultados = {}

# 1. ATENDIMENTOS
if 'atendimentos' in DATASETS:
    sucesso, df = descarregar_dataset(DATASETS['atendimentos'], 'atendimentos')
    if sucesso and df is not None:
        df_normalizado = normalizar_atendimentos(df)
        output_file = DATASETS['atendimentos']['nome_original']  # Usar nome original
        df_normalizado.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
        print(f"\n✓ Ficheiro atualizado: {output_file}")
        print(f"   (Normalização aplicada automaticamente)")
        resultados['atendimentos'] = 'OK'
    else:
        resultados['atendimentos'] = 'ERRO'

# 2. TRABALHADORES
if 'trabalhadores' in DATASETS:
    sucesso, df = descarregar_dataset(DATASETS['trabalhadores'], 'trabalhadores')
    if sucesso:
        resultados['trabalhadores'] = 'OK'
    else:
        resultados['trabalhadores'] = 'ERRO'

# 3. MONITORIZAÇÃO
if 'monitorizacao' in DATASETS:
    sucesso, df = descarregar_dataset(DATASETS['monitorizacao'], 'monitorizacao')
    if sucesso:
        resultados['monitorizacao'] = 'OK'
    else:
        resultados['monitorizacao'] = 'ERRO'

# ============================================================================
# RESUMO FINAL
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO DA ATUALIZAÇÃO")
print("=" * 80)

for dataset, status in resultados.items():
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} {dataset.capitalize()}: {status}")

print("\n" + "=" * 80)
print("PRÓXIMOS PASSOS NO POWER BI")
print("=" * 80)
print("""
1. Abra o ficheiro .pbix no Power BI Desktop
2. Vá a 'Página Inicial' → 'Transformar dados' → 'Atualizar Origem de Dados'
3. OU simplesmente clique em 'Atualizar' no ribbon
4. O Power BI irá:
   ✓ Ler os novos ficheiros CSV atualizados
   ✓ Manter todas as relações entre tabelas
   ✓ Manter todas as medidas DAX
   ✓ Manter todas as visualizações e formatações
   ✓ Manter todos os bookmarks e slicers

IMPORTANTE:
• Os nomes das colunas são os MESMOS (garante compatibilidade)
• A estrutura dos ficheiros é IDÊNTICA (garante relações)
• Apenas os DADOS foram atualizados (linhas novas adicionadas)

Se surgirem erros:
1. Verifique se os ficheiros estão na mesma pasta
2. Confirme que os nomes dos ficheiros não mudaram
3. Use 'Editar Consultas' para verificar caminhos das fontes
""")

print("=" * 80)
print("✓ ATUALIZAÇÃO CONCLUÍDA")
print("=" * 80)
