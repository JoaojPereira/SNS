# 📂 Scripts Essenciais

Esta pasta contém apenas os **3 scripts essenciais** para manutenção do projeto.

---

## ✅ Scripts Ativos

### 1️⃣ `atualizar_dados_sns.py` ⭐
**Função:** Download automático e normalização de dados do Portal da Transparência SNS

**O que faz:**
- Descarrega os 3 datasets principais do Portal SNS:
  - Atendimentos em Urgência (Triagem Manchester)
  - Trabalhadores por Grupo Profissional  
  - Monitorização Sazonal
- Aplica normalização automática aos dados
- Cria backups antes de sobrescrever
- Mantém nomes originais dos ficheiros (compatibilidade Power BI)

**Quando usar:**
- Mensalmente para atualizar com novos dados oficiais
- Quando o Portal SNS publicar novos dados

**Como executar:**
```powershell
python atualizar_dados_sns.py
```

---

### 2️⃣ `atualizar_tabelas_fact.py` ⭐
**Função:** Atualiza as tabelas Fact do modelo Star Schema

**O que faz:**
- Lê os CSVs atualizados
- Filtra apenas dados de 2016 em diante (remove 2013-2015)
- Mapeia instituições usando tabela DimInstituicao com cache de performance
- Gera TimeKeys para relacionamentos temporais
- Atualiza FactAtendimentosUrgencia_Mensal.csv (4.131 registos)
- Atualiza FactMonitorizacaosazonal.csv (32.870 registos)
- Cria backups automáticos antes de sobrescrever

**Quando usar:**
- Após executar `atualizar_dados_sns.py`
- Sempre que os CSVs fonte forem modificados

**Como executar:**
```powershell
python atualizar_tabelas_fact.py
```

---

### 3️⃣ `converter_md_to_html.py`
**Função:** Converte ficheiros Markdown para HTML com estilos

**O que faz:**
- Lê ficheiros .md
- Converte para HTML com CSS embutido
- Cria versão apresentável para navegador

**Quando usar:**
- Quando atualizar documentação .md
- Para gerar versões HTML de relatórios

**Como executar:**
```powershell
python converter_md_to_html.py
```

---

## 🗂️ Ficheiros de Suporte

### `ANALISE_SCRIPTS.md`
Documento de análise que identificou scripts redundantes e justifica a consolidação.

### `Medidas_Profissionais.dax`
Fórmulas DAX específicas para análise de recursos humanos (referência).

---

## 🎯 Workflow de Atualização Completa

```
1. python atualizar_dados_sns.py        → Descarrega dados novos
2. python atualizar_tabelas_fact.py     → Atualiza tabelas Fact
3. Abrir Power BI → Atualizar (F5)      → Visuais atualizados
```

---

## 📋 O Que Foi Eliminado?

**42 scripts** obsoletos foram removidos, incluindo:
- ✅ Scripts de normalização (integrados em atualizar_dados_sns.py)
- ✅ Scripts de limpeza (integrados)
- ✅ Scripts de correção pontual (já aplicadas)
- ✅ Scripts de análise exploratória (executados uma vez)
- ✅ Scripts de criação de dimensões (executados uma vez)
- ✅ Conversores específicos (consolidados num genérico)

**Resultado:** Manutenção 93% mais simples!

---

## 🔄 Dependências

Instalar antes de executar:
```powershell
pip install pandas requests openpyxl
```

Ou ativar o ambiente virtual:
```powershell
.venv\Scripts\Activate.ps1
```

---

## 📞 Suporte

Para adicionar novos scripts ou modificar os existentes, consulte a documentação principal no README.md da raiz do projeto.

---

**Última atualização:** 20/12/2025  
**Consolidação:** De 45 scripts para 3 essenciais ✅
