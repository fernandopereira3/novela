from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, send_file
import pandas as pd
import re
import datetime
import io
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from main import app, db, PesquisaForm

df_lista_sentenciados = pd.DataFrame(columns=['matricula', 'nome', 'garrafas', 'homens', 'mulheres', 'criancas', 'data_adicao'])
@app.route('/lista', methods=['GET', 'POST'])
def pesquisa_matricula():
    form = PesquisaForm()
    sentenciados = db.sentenciados
    resultados = []

    if form.validate_on_submit():
        matricula = form.matricula.data.strip()
        nome = form.nome.data.strip()
        query = {}

        if matricula:
            query['matricula'] = {"$regex": f"^\\s*{re.escape(matricula)}\\s*$", "$options": "i"}
        if nome:
            query['nome'] = {"$regex": nome, "$options": "i"}

        resultados = list(sentenciados.find(query))
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])

    return render_template('pesquisa.html', form=form, sentenciados=resultados)



@app.route('/download', methods=['GET'])
def download_pdf():
    global df_lista_sentenciados
    
    sort_by = request.args.get('sort', 'nome')
    df_sorted = df_lista_sentenciados.sort_values(by=sort_by) if sort_by in df_lista_sentenciados.columns else df_lista_sentenciados
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=15, rightMargin=15, topMargin=20, bottomMargin=20)
    elements = []
    
    try:
        totals = {
            'garrafas': df_lista_sentenciados['garrafas'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'homens': df_lista_sentenciados['homens'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'mulheres': df_lista_sentenciados['mulheres'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'criancas': df_lista_sentenciados['criancas'].replace('', pd.NA).fillna(0).astype(int).sum()
        }
    except Exception as e:
        totals = {'garrafas': 0, 'homens': 0, 'mulheres': 0, 'criancas': 0}

    data = [df_sorted.columns.tolist()] + df_sorted.values.tolist()
    table_nomes = Table(data, colWidths=[70, 180, 35, 35, 35, 35, 90])
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('WORDWRAP', (0, 0), (-1, -1), True),
        ('ALIGN', (2, 1), (-2, -1), 'CENTER'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])
    
    table_nomes.setStyle(style)

    summary_data = [
        ['Resumo', 'Total'],
        ['Garrafas', str(totals['garrafas'])],
        ['Homens', str(totals['homens'])],
        ['Mulheres', str(totals['mulheres'])],
        ['Crianças', str(totals['criancas'])]
    ]
    
    summary_table = Table(summary_data, colWidths=[60, 60])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    elements.append(table_nomes)
    elements.append(Paragraph("<br/><br/><br/>", getSampleStyleSheet()['Normal']))
    elements.append(summary_table)
    elements.append(Paragraph("<br/><br/><br/>_____________________________<br/>Assinatura do Responsável", getSampleStyleSheet()['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'lista_{datetime.datetime.now().strftime("%d-%m-%Y-%H-%M")}.pdf',
        mimetype='application/pdf'
    )


@app.route('/adicionar/<matricula>', methods=['POST'])
def adicionar_lista(matricula):
    global df_lista_sentenciados

    sentenciado = db.sentenciados.find_one({'matricula': matricula})
    if sentenciado:
        data = request.get_json()

        garrafas = data.get('garrafas', 0)
        homens = data.get('homens', 0)
        mulheres = data.get('mulheres', 0)
        criancas = data.get('criancas', 0)
        data_adicao = datetime.datetime.now().strftime("%d/%m/%Y as %H:%M")

        new_row = {
            'matricula': sentenciado['matricula'],
            'nome': sentenciado['nome'],
            'pavilhao': sentenciado['pavilhao'],
            'garrafas': garrafas,
            'homens': homens,
            'mulheres': mulheres,
            'criancas': criancas,
            'data_adicao': data_adicao
        }

        df_lista_sentenciados = pd.concat([df_lista_sentenciados, pd.DataFrame([new_row])], ignore_index=True)

        return jsonify({'status': 'success', 'message': 'Adicionado com sucesso'})
    return jsonify({'status': 'error', 'message': 'Matrícula não encontrada'})



@app.route('/lista-selecionados', methods=['GET'])
def visualizar_lista():
    global df_lista_sentenciados
    try:
        # Replace empty strings with NaN, then fill NaN with 0 before converting to int
        totals = {
            'garrafas': df_lista_sentenciados['garrafas'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'homens': df_lista_sentenciados['homens'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'mulheres': df_lista_sentenciados['mulheres'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'criancas': df_lista_sentenciados['criancas'].replace('', pd.NA).fillna(0).astype(int).sum()
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        totals = {
            'garrafas': 0,
            'homens': 0,
            'mulheres': 0,
            'criancas': 0
        }

    tabela_html = df_lista_sentenciados.to_html(index=False)

    return render_template('lista.html', tabela=tabela_html, totals=totals)


@app.route('/remover/<matricula>', methods=['DELETE'])
def remover_lista(matricula):
    global df_lista_sentenciados
    
    df_lista_sentenciados = df_lista_sentenciados[df_lista_sentenciados['matricula'] != matricula]

    if df_lista_sentenciados.empty:
        return jsonify({'status': 'error', 'message': 'Matrícula não encontrada'})
    else:
        return jsonify({'status': 'success', 'message': 'Matrícula removida com sucesso'})

@app.route('/limpar_lista', methods=['POST'])
def limpar_lista():
    global df_lista_sentenciados

    df_lista_sentenciados = pd.DataFrame(columns=df_lista_sentenciados.columns)
    flash('Lista limpa com sucesso!', 'success')
    return redirect(url_for('pesquisa_matricula'))

@app.route('/clear', methods=['GET'])
def clean_matricula_complete():
    count = 0
    for doc in db.sentenciados.find():
        if 'matricula' in doc and isinstance(doc['matricula'], str):
            original = doc['matricula']
            
            clean_matricula = original.replace(' ', '').replace('.', '').replace('-', '')
            
            if len(clean_matricula) > 0:
                clean_matricula = clean_matricula[:-1]
            
            if clean_matricula != original:
                db.sentenciados.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'matricula': clean_matricula}}
                )
                count += 1
    
    return f"Cleaned {count} matricula records by removing spaces, periods, hyphens, and the last digit"

@app.route('/')
def index():
    return render_template('index.html')
