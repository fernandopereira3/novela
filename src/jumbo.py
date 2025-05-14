from main import app, db, PesquisaForm
from rotas import pesquisa_matricula
import pandas as pd
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for,
    send_file,
)

df_jumbo = pd.DataFrame(columns=['matricula', 'nome', 'visita'])


@app.route('/jumbo', methods=['GET', 'POST'])
def jumbo():
    try:
        form = PesquisaForm()
        return render_template('jumbo.html', form=form)
    except Exception as e:
        print(f'Error rendering template: {e}')
        return str(e), 500
