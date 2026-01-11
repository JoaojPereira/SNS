let
    // Parâmetros de data
    StartDate = #date(2016, 1, 1),
    EndDate = #date(2026, 12, 31),
    
    // Criar lista de datas
    DayCount = Duration.Days(Duration.From(EndDate - StartDate)) + 1,
    Source = List.Dates(StartDate, DayCount, #duration(1,0,0,0)),
    TableFromList = Table.FromList(Source, Splitter.SplitByNothing()),
    
    // Renomear e adicionar colunas essenciais
    ChangedType = Table.TransformColumnTypes(TableFromList,{{"Column1", type date}}),
    RenamedColumns = Table.RenameColumns(ChangedType,{{"Column1", "Data"}}),
    
    // TimeKey - Chave para relacionamentos
    AddTimeKey = Table.AddColumn(RenamedColumns, "TimeKey", each 
        Date.Year([Data]) * 10000 + Date.Month([Data]) * 100 + Date.Day([Data]), 
        Int64.Type),
    
    // Hierarquia temporal: Ano > Trimestre > Mês > Dia
    AddAno = Table.AddColumn(AddTimeKey, "Ano", each Date.Year([Data]), Int64.Type),
    AddTrimestre = Table.AddColumn(AddAno, "Trimestre", each "T" & Number.ToText(Date.QuarterOfYear([Data])), type text),
    AddMes = Table.AddColumn(AddTrimestre, "Mes", each Date.Month([Data]), Int64.Type),
    AddMesNome = Table.AddColumn(AddMes, "MesNome", each Date.ToText([Data], "MMMM", "pt-PT"), type text),
    AddDia = Table.AddColumn(AddMesNome, "Dia", each Date.Day([Data]), Int64.Type),
    AddDiaSemana = Table.AddColumn(AddDia, "DiaSemana", each Date.ToText([Data], "dddd", "pt-PT"), type text),
    
    // Adicionar Sazonalidade (baseado em hemisfério norte - Portugal)
    AddSazonalidade = Table.AddColumn(AddDiaSemana, "Sazonalidade", each 
        let mes = Date.Month([Data])
        in if mes = 12 or mes = 1 or mes = 2 then "Inverno"
           else if mes >= 3 and mes <= 5 then "Primavera"
           else if mes >= 6 and mes <= 8 then "Verão"
           else "Outono",
        type text),
    
    // Coluna auxiliar para ordenação de mês/trimestre
    AddAnoMes = Table.AddColumn(AddSazonalidade, "AnoMes", each 
        Text.From(Date.Year([Data])) & "-" & Text.PadStart(Text.From(Date.Month([Data])), 2, "0"), 
        type text),
    
    // É Fim de Semana (Sábado ou Domingo)
    AddFimDeSemana = Table.AddColumn(AddAnoMes, "É Fim de Semana", each 
        Date.DayOfWeek([Data], Day.Monday) >= 5, 
        type logical),
    
    // É Feriado (Feriados Nacionais de Portugal)
    AddFeriado = Table.AddColumn(AddFimDeSemana, "É Feriado", each 
        let 
            ano = Date.Year([Data]),
            mes = Date.Month([Data]),
            dia = Date.Day([Data]),
            
            // Calcular Páscoa (Algoritmo de Meeus/Jones/Butcher)
            a = Number.Mod(ano, 19),
            b = Number.IntegerDivide(ano, 100),
            c = Number.Mod(ano, 100),
            d = Number.IntegerDivide(b, 4),
            e = Number.Mod(b, 4),
            f = Number.IntegerDivide(b + 8, 25),
            g = Number.IntegerDivide(b - f + 1, 3),
            h = Number.Mod(19 * a + b - d - g + 15, 30),
            i = Number.IntegerDivide(c, 4),
            k = Number.Mod(c, 4),
            l = Number.Mod(32 + 2 * e + 2 * i - h - k, 7),
            m = Number.IntegerDivide(a + 11 * h + 22 * l, 451),
            mesPascoa = Number.IntegerDivide(h + l - 7 * m + 114, 31),
            diaPascoa = Number.Mod(h + l - 7 * m + 114, 31) + 1,
            dataPascoa = #date(ano, mesPascoa, diaPascoa),
            
            // Feriados móveis baseados na Páscoa
            carnaval = Date.AddDays(dataPascoa, -47),           // 47 dias antes da Páscoa
            sextaFeiraSanta = Date.AddDays(dataPascoa, -2),     // Sexta-feira Santa
            pascoa = dataPascoa,                                 // Domingo de Páscoa
            corpusChristi = Date.AddDays(dataPascoa, 60),       // 60 dias após Páscoa
            
            // Feriados fixos de Portugal
            feriadosFixos = {
                #date(ano, 1, 1),    // Ano Novo
                #date(ano, 4, 25),   // 25 de Abril (Revolução dos Cravos)
                #date(ano, 5, 1),    // Dia do Trabalhador
                #date(ano, 6, 10),   // Dia de Portugal
                #date(ano, 8, 15),   // Assunção de Nossa Senhora
                #date(ano, 10, 5),   // Implantação da República
                #date(ano, 11, 1),   // Todos os Santos
                #date(ano, 12, 1),   // Restauração da Independência
                #date(ano, 12, 8),   // Imaculada Conceição
                #date(ano, 12, 25)   // Natal
            },
            
            // Todos os feriados (fixos + móveis)
            todosFeriados = feriadosFixos & {carnaval, sextaFeiraSanta, pascoa, corpusChristi}
        in
            List.Contains(todosFeriados, [Data]),
        type logical),
    
    // Tipo de Dia (útil, fim de semana ou feriado)
    AddTipoDia = Table.AddColumn(AddFeriado, "Tipo de Dia", each 
        if [É Feriado] then "Feriado"
        else if [É Fim de Semana] then "Fim de Semana"
        else "Dia Útil",
        type text),
    
    // Ordenar por TimeKey
    SortedRows = Table.Sort(AddTipoDia,{{"TimeKey", Order.Ascending}})
in
    SortedRows
