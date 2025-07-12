from flask import Flask
import os
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm



app = Flask(__name__, instance_relative_config=True)
#app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://db-novela:27017/cpppac')
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


if __name__ == '__main__':
    from rotas import *
    from rotas_saida import *
    from jumbo import *
    from user import *
    app.run(host='0.0.0.0', port=5000, debug=True)
