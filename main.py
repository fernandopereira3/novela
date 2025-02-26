from flask import Flask, render_template, jsonify
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
    sentenciado = db.sentenciados.find_one({'matricula': matricula})
    if sentenciado:
        lista_selecionados = db.lista_selecionados
        lista_selecionados.insert_one({
            'nome': sentenciado['nome'],
            'matricula': sentenciado['matricula'],
            'data_adicao': datetime.datetime.now()
        })
        # Criar DataFrame com os dados
        import pandas as pd
        df = pd.DataFrame({
            'nome': [sentenciado['nome']],
            'matricula': [sentenciado['matricula']],
            'data_adicao': datetime.datetime.now()
        })
        
        return jsonify({'status': 'success', 'message': 'Adicionado com sucesso', 'data': df.to_dict('records')})
    return jsonify({'status': 'error', 'message': 'Matrícula não encontrada'})
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


@app.route('/completa', methods=['GET'])
def completa():
    resultado = db.sentenciados.find()
    lista = list(resultado)
    return jsonify(lista)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=80)