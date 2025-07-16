from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/cpppac'

def conexao():
    try:
        mongo = PyMongo(app)
        db = mongo.db
        mongo.db.command('ping')
        print(f"Conexão bem-sucedida ao MongoDB!")
        return db
        
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None

   
