from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

# Conexão com MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.sistema


def init_auth():
    # Criar coleção de usuários se não existir
    if 'usuarios' not in db.list_collection_names():
        db.create_collection('usuarios')
        # Criar usuário admin padrão
        db.usuarios.insert_one(
            {
                'username': 'admin',
                'password': generate_password_hash('admin123'),
                'role': 'admin',
            }
        )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function
