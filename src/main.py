from flask import Flask
import os
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__, instance_relative_config=True)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/cpppac')
app.config['SECRET_KEY'] = os.urandom(32)

# Inicializa o PyMongo corretamente
try:
    mongo = PyMongo(app)
    db = mongo.db
    mongo.db.command('ping')
    print(f'🔌Conectado ao MongoDB com sucesso!')
except Exception as e:
    print(f'Erro ao conectar ao MongoDB: {e}')
    exit(1)


class PesquisaForm(FlaskForm):
    matricula = StringField('Matrícula')
    nome = StringField('Nome')
    garrafas = StringField('Garrafas')
    homens = StringField('Homens')
    mulheres = StringField('Mulheres')
    criancas = StringField('Crianças')
    pesquisar = SubmitField('PESQUISAR')


# Importa os módulos após a criação do app e db para evitar importação circular
from rotas import *
from rotas_saida import *
from jumbo import *
from user import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
