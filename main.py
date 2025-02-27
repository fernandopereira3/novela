from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
import pandas as pd
import os
import re
import datetime
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

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

# Initialize an empty DataFrame to store selected sentenciados
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
            query['matricula'] = re.compile(f".*{matricula}.*", re.IGNORECASE)
        if nome:
            query['nome'] = {"$regex": nome, "$options": "i"}

        resultados = list(sentenciados.find(query))

        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])

    return render_template('pesquisa.html', form=form, sentenciados=resultados)

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
    global df_lista_sentenciados  # Access the global DataFrame

    # Convert DataFrame to HTML table
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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=80)