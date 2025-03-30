from flask import render_template, jsonify
import pandas as pd
from main import app


@app.route('/saida', methods=['POST'])
def criar_lista_saida():
    global df_lista_sentenciados
    global df_lista_saida
    
    df_lista_saida = df_lista_sentenciados.copy()

    if df_lista_saida.empty:
        return jsonify({'status': 'error', 'message': 'Lista vazia'})
    else:
        return jsonify({'status': 'success', 'message': 'Lista de saída criada com sucesso'})
    
@app.route('/lista-saida', methods=['GET'])
def lista_saida():
    global df_lista_saida
    try:
        totals = {
            'garrafas': df_lista_saida['garrafas'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'homens': df_lista_saida['homens'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'mulheres': df_lista_saida['mulheres'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'criancas': df_lista_saida['criancas'].replace('', pd.NA).fillna(0).astype(int).sum()
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        totals = {
            'garrafas': 0,
            'homens': 0,
            'mulheres': 0,
            'criancas': 0
        }

    tabela_saida = df_lista_saida.to_html(index=False)

    return render_template('saida.html', tabela=tabela_saida, totals=totals)