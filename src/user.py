# Importar diretamente as instâncias app e db
try:
    from main import app, db
except ImportError:
    # Fallback para quando executado de fora do diretório src
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from main import app, db
from flask import render_template, redirect, url_for, request, session


## LOGIN ##
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower().replace(' ', '')

        user = db.usuarios.find_one({'username': username})
        if not user:
            # Usuário não existe - criar novo usuário
            db.usuarios.insert_one({'username': username})
            session['user'] = username
            return redirect(url_for('index'))

        # Usuário existe - fazer login
        session['user'] = username
        return redirect(url_for('index'))

    return render_template('login.html')


## LOGIN ##
