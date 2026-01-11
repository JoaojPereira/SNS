#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conversor simples Markdown para HTML sem dependências externas
"""

import sys
import re

def converter_md_para_html(ficheiro_md):
    """Converte Markdown para HTML usando regex simples"""
    
    with open(ficheiro_md, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Substituições básicas
    html = conteudo
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Horizontal rule
    html = re.sub(r'^---$', r'<hr />', html, flags=re.MULTILINE)
    
    # Lists
    linhas = html.split('\n')
    html_processado = []
    em_lista = False
    em_tabela = False
    
    for linha in linhas:
        # Tabelas
        if '|' in linha and linha.strip().startswith('|'):
            if not em_tabela:
                html_processado.append('<table>')
                em_tabela = True
            
            if linha.strip().replace('|', '').replace('-', '').strip() == '':
                continue  # Skip separator
            
            celulas = [c.strip() for c in linha.split('|')[1:-1]]
            if '---' not in linha:
                if len(html_processado) == 1 or '</tr>' in html_processado[-1]:
                    html_processado.append('<tr>')
                    for celula in celulas:
                        html_processado.append(f'<td>{celula}</td>')
                    html_processado.append('</tr>')
        else:
            if em_tabela:
                html_processado.append('</table>')
                em_tabela = False
            
            # Lists
            if linha.strip().startswith('- '):
                if not em_lista:
                    html_processado.append('<ul>')
                    em_lista = True
                html_processado.append(f'<li>{linha.strip()[2:]}</li>')
            else:
                if em_lista:
                    html_processado.append('</ul>')
                    em_lista = False
                
                # Checkboxes
                linha = linha.replace('- [ ]', '☐')
                linha = linha.replace('- [x]', '☑')
                
                # Paragraphs
                if linha.strip() and not linha.strip().startswith('<'):
                    html_processado.append(f'<p>{linha}</p>')
                else:
                    html_processado.append(linha)
    
    if em_lista:
        html_processado.append('</ul>')
    if em_tabela:
        html_processado.append('</table>')
    
    html = '\n'.join(html_processado)
    
    # Template HTML
    html_final = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roteiro de Apresentação - Análise SNS</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        h1 {{
            color: #003DA5;
            border-bottom: 4px solid #003DA5;
            padding-bottom: 15px;
            margin-bottom: 20px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #0052CC;
            border-bottom: 3px solid #0052CC;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 2em;
        }}
        
        h3 {{
            color: #003DA5;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-left: 5px solid #003DA5;
            padding-left: 15px;
        }}
        
        h4 {{
            color: #666;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        strong {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        ul {{
            margin-left: 30px;
            margin-bottom: 20px;
        }}
        
        li {{
            margin-bottom: 10px;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        td {{
            padding: 12px 15px;
            border: 1px solid #ddd;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tr:hover {{
            background: #e9ecef;
        }}
        
        .destaque {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
            
            h2 {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
{html}
    </div>
</body>
</html>"""
    
    # Salvar HTML
    ficheiro_html = ficheiro_md.replace('.md', '.html')
    with open(ficheiro_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    print(f"✅ Conversão concluída: {ficheiro_html}")
    return ficheiro_html

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python convert_to_html_simple.py <ficheiro.md>")
        sys.exit(1)
    
    ficheiro_md = sys.argv[1]
    converter_md_para_html(ficheiro_md)
