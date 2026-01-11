# Guia de Atualização de Dados - Power BI
## Como atualizar dados sem perder configurações

---

## Objetivo

Atualizar os dados do dashboard mantendo **100%** das configurações:
- ✅ Medidas DAX
- ✅ Visualizações
- ✅ Formatação condicional
- ✅ Relações entre tabelas
- ✅ Bookmarks
- ✅ Slicers
- ✅ Filtros

---

## Método 1: Atualização Automática (Recomendado)

### Passo 1: Executar o Script de Atualização

```powershell
cd "sns_dashboard\sns\scripts_history"
python atualizar_dados_sns.py
```

**O que o script faz:**
1. ✓ Descarrega dados mais recentes do portal SNS
2. ✓ Cria backup automático dos ficheiros antigos
3. ✓ Aplica mesma normalização (nomes de colunas idênticos)
4. ✓ Mantém estrutura 100% compatível com Power BI

### Passo 2: Atualizar no Power BI Desktop

1. Abrir o ficheiro `.pbix`
2. Clicar em **"Atualizar"** no ribbon superior
   
   ![Botão Atualizar](imagem: botão circular com seta)

3. Aguardar conclusão (5-10 segundos)
4. Dados atualizados, configurações mantidas

---

## Método 2: Atualização Manual

Se preferir descarregar manualmente do portal:

### Passo 1: Descarregar do Portal

1. Aceder: https://transparencia.sns.gov.pt/explore/?sort=modified
2. Procurar datasets:
   - `sns/csv/atendimentos_urgencia_triagem_manchester`
   - `sns/csv/trabalhadores_grupo_profissional`
   - `sns/csv/monitorizacao_sazonal_csh.csv`
3. Clicar em "Exportar" → "CSV" (com separador `;`)

### Passo 2: Normalizar com Script

```powershell
python normalizar_csv_completo.py
```

### Passo 3: Substituir Ficheiros

**IMPORTANTE:** Usar os mesmos nomes:
- `sns\csv\atendimentos_urgencia_triagem_manchester.csv`
- `sns\csv\trabalhadores_grupo_profissional.csv`
- `sns\csv\monitorizacao_sazonal_csh.csv`

### Passo 4: Atualizar no Power BI

Igual ao Método 1, Passo 2

---

## Resolução de Problemas

### Erro: "Não foi possível localizar a origem de dados"

**Causa:** Caminho do ficheiro mudou

**Solução:**
1. Power BI Desktop → **"Transformar dados"**
2. No Power Query Editor, clicar com botão direito na consulta
3. **"Origem Avançada"** ou **"Definições de Origem"**
4. Atualizar caminho para nova localização
5. **"Fechar e Aplicar"**

### Erro: "Nome da coluna não encontrado"

**Causa:** Estrutura do CSV mudou

**Solução:**
1. Verificar se usou o script de normalização
2. Confirmar que colunas têm nomes corretos:
   - `Vermelha`, `Laranja`, `Amarela`, `Verde`, `Azul`, `Branca`
   - NÃO usar nomes longos originais
3. Re-executar: `sns\scripts_history\normalizar_csv_completo.py`

### Erro: "Tipo de dados incompatível"

**Causa:** Valores vazios ou texto em colunas numéricas

**Solução:**
- Script de normalização já preenche vazios com `0`
- Se persistir, verificar encoding do ficheiro (deve ser UTF-8)

### Dados não aparecem atualizados

**Verificar:**
1. Ficheiro foi realmente substituído na pasta correta?
2. Power BI está a ler da localização correta?
   - Ver "Definições de Origem" em cada consulta
3. Cache: Fechar Power BI completamente e reabrir

---

## Cuidados Importantes

### NÃO FAZER:

1. **Mudar nomes de colunas manualmente**
   - Medidas DAX deixam de funcionar
   - Use sempre o script de normalização

2. **Mudar nome dos ficheiros CSV**
   - Power BI perde referência
   - Mantém nomes originais ou atualiza em "Definições de Origem"

3. **Adicionar/remover colunas sem ajustar DAX**
   - Pode causar erros em medidas calculadas

### FAZER:

1. **Sempre criar backup antes de atualizar**
   - Script já faz automaticamente
   - Ou manualmente: copiar `.pbix` e CSVs

2. **Testar atualização num ficheiro de teste**
   - Fazer cópia do `.pbix` primeiro
   - Testar atualização na cópia
   - Se OK, aplicar no original

3. **Verificar datas após atualização**
   - Confirmar que período mais recente aparece
   - Verificar se há gaps temporais

---

## Vantagens da Atualização Automática

### Power BI mantém automaticamente:

| Elemento | Mantido? | Observações |
|----------|----------|-------------|
| Medidas DAX | ✅ 100% | Desde que nomes de colunas sejam iguais |
| Visualizações | ✅ 100% | Gráficos, tabelas, cards |
| Formatação condicional | ✅ 100% | Cores, ícones, regras |
| Relações | ✅ 100% | Entre fact e dimension tables |
| Bookmarks | ✅ 100% | Vistas guardadas |
| Slicers | ✅ 100% | Filtros interativos |
| Hierarquias | ✅ 100% | Drill-down |
| Parâmetros | ✅ 100% | What-if parameters |
| RLS (Row Level Security) | ✅ 100% | Se configurado |

---

## Agendamento Automático (Opcional)

### Para atualização periódica sem intervenção:

### Opção 1: Power BI Service (Cloud)

1. Publicar dashboard no Power BI Service
2. Configurar Gateway (se dados locais)
3. Agendar atualização automática:
   - Diária, semanal ou mensal
   - Notificações por email em caso de erro

### Opção 2: Task Scheduler (Windows)

1. Criar tarefa agendada:
   ```
   Ação: python atualizar_dados_sns.py
   Frequência: Mensal (dia 15 de cada mês)
   ```
2. Power BI atualiza automaticamente ao abrir

### Opção 3: Script PowerShell Agendado

```powershell
# Criar task mensal
$action = New-ScheduledTaskAction -Execute "python" -Argument "sns\scripts_history\atualizar_dados_sns.py" -WorkingDirectory "D:\Ambiente de trabalho\TransformacaoBi\sns_dashboard\sns\scripts_history"
$trigger = New-ScheduledTaskTrigger -Monthly -At 2am -DaysOfMonth 15
Register-ScheduledTask -TaskName "Atualizar Dados SNS" -Action $action -Trigger $trigger
```

---

## Checklist de Atualização

Antes de atualizar:
- [ ] Fazer backup do ficheiro `.pbix`
- [ ] Fazer backup dos CSVs atuais
- [ ] Verificar conectividade ao portal SNS

Durante atualização:
- [ ] Executar `sns\scripts_history\atualizar_dados_sns.py`
- [ ] Verificar mensagens de sucesso/erro
- [ ] Confirmar que ficheiros foram criados

Após atualização:
- [ ] Abrir Power BI Desktop
- [ ] Clicar em "Atualizar"
- [ ] Verificar período mais recente nos dados
- [ ] Testar slicers e filtros
- [ ] Verificar totais/médias fazem sentido
- [ ] Guardar ficheiro `.pbix`

---

## Dicas Profissionais

### 1. Documentar última atualização
Adicionar text box no dashboard:
```
Última atualização: [DATA]
Período coberto: Janeiro 2016 - Setembro 2025
```

### 2. Criar página de "Notas de Versão"
Documentar mudanças em cada atualização:
- Novos períodos adicionados
- Correções aplicadas
- Instituições adicionadas/removidas

### 3. Monitorizar qualidade dos dados
Criar medidas de validação:
```dax
Linhas Novas = 
VAR LinhasAnteriores = 6060
VAR LinhasAtuais = COUNTROWS(FactAtendimentosUrgencia)
RETURN LinhasAtuais - LinhasAnteriores
```

---

## Suporte

### Recursos:
- **Scripts:** Pasta `scripts_history` tem 42 scripts de referência
- **Documentação:** `ANALISE_SCRIPTS.md` explica cada script
- **Relatório:** `relatorio_sns.md` tem detalhes técnicos

### Contactos:
- Portal SNS: https://transparencia.sns.gov.pt
- Documentação Power BI: https://docs.microsoft.com/power-bi

---

**Última atualização deste guia:** 8 de dezembro de 2025  
**Compatível com:** Power BI Desktop (todas as versões 2023+)
**Autor:** João Domingues Pereira

