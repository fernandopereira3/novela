from main import app, db
from flask import render_template, redirect, url_for, request, session, flash
from werkzeug.security import check_password_hash

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
