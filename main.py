from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import re
import datetime
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import logging

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
    pesquisar = SubmitField('PESQUISAR')
    
class apagar(FlaskForm):
    apagar = SubmitField('APAGAR LISTA')

@app.route('/lista', methods=['GET',  'POST'])
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
            query['nome'] = {"$regex": nome,  "$options": "i"}
        resultados = list(sentenciados.find(query))
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])

    return render_template('pesquisa.html', form=form, sentenciados=resultados)

@app.route('/adicionar/<matricula>', methods=['POST'])
def adicionar_lista(matricula):
    logging.debug(f"Tentando adicionar matrícula: {matricula}")
    try:
        sentenciado = db.sentenciados.find_one({'matricula': matricula})
        if sentenciado:
            lista_selecionados = db.lista_selecionados
            lista_selecionados.insert_one({
                'nome': sentenciado['nome'],
                'matricula': sentenciado['matricula'],
                'garrafas': input("Informe o número de garrafas: "),
                'homens': input("Informe o número de homens: "),
                'mulheres': input("Informe o número de mulheres: "),
                'criancas': input("Informe o número de crianças: "),
                'data_adicao': datetime.datetime.now()
            })
            
            logging.debug("Sentenciado adicionado à lista com sucesso.")
            return jsonify({'status': 'success', 'message': 'Adicionado com sucesso'})
        else:
            logging.warning(f"Matrícula não encontrada: {matricula}")
            return jsonify({'status': 'error', 'message': 'Matrícula não encontrada'})
    except Exception as e:
        logging.error(f"Erro ao adicionar matrícula: {matricula}. Erro: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/lista-selecionados', methods=['GET'])
def visualizar_lista():
    lista_selecionados = db.lista_selecionados.find()
    return render_template('lista.html', lista=lista_selecionados)

@app.route('/remover/<matricula>', methods=['DELETE'])
def remover_lista(matricula):
    resultado = db.lista_selecionados.delete_one({'matricula': matricula})
    if resultado.deleted_count > 0:
        return jsonify({'status': 'success', 'message': 'Matrícula removida com sucesso'})
    else:
        return jsonify({'status': 'error', 'message': 'Matrícula não encontrada'})

@app.route('/del-lista', methods=['DELETE'])
def completa():
    form = apagar()
    resultado = db.lista_selecionados.delete_many({})
    if resultado.deleted_count > 0:
        return jsonify({'status': 'success', 'message': 'Todos os sentenciados foram removidos com sucesso'})
    else:
        return jsonify({'status': 'error', 'message': 'Nenhum sentenciado encontrado para remover'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=80)