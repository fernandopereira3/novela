from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, send_file
import pandas as pd
import os
import re
import datetime
import io
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

app = Flask(__name__, instance_relative_config=True)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/cpppac'
app.config['SECRET_KEY'] = os.urandom(32)

try:
    # Inicializa o PyMongo corretamente
    mongo = PyMongo(app)
    db = mongo.db
    mongo.db.command('ping')
    print("Conectado ao MongoDB com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    exit(1)

class PesquisaForm(FlaskForm):
    matricula = StringField('Matrícula')
    nome = StringField('Nome')
    garrafas = StringField('Garrafas')
    homens = StringField('Homens')
    mulheres = StringField('Mulheres')
    criancas = StringField('Crianças')
    pesquisar = SubmitField('PESQUISAR')

# Inicializa um DataFrame vazio para armazenar sentenciados selecionados
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
    
    if sort_by in df_lista_sentenciados.columns:
        df_sorted = df_lista_sentenciados.sort_values(by=sort_by)
    else:
        df_sorted = df_lista_sentenciados
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    data = [df_sorted.columns.tolist()] + df_sorted.values.tolist()
    
    table = Table(data)
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    table.setStyle(style)

    elements.append(table)
    
    doc.build(elements)
    
    buffer.seek(0)
    
    current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'lista_sentenciados_{current_date}.pdf',
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
    tabela_html = df_lista_sentenciados.to_html(index=False)

    return render_template('lista.html', tabela=tabela_html)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)