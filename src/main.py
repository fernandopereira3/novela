import os
import sys
from flask import Flask


# Adiciona o diretório pai ao path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Adiciona o diretório atual (src) ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from Data.conexao import conexao
db = conexao()

app = Flask(__name__, instance_relative_config=True)


secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key

# Importar módulos para registrar as rotas
from rotas import *
from  rotas_saida import *
from jumbo import *
from trabalho import *
from user import *
from functions import *
from debug import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
