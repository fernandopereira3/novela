from flask import render_template, jsonify
import pandas as pd
from main import app

def get_total_counts(df):
    try:
        return {
            'garrafas': df['garrafas'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'homens': df['homens'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'mulheres': df['mulheres'].replace('', pd.NA).fillna(0).astype(int).sum(),
            'criancas': df['criancas'].replace('', pd.NA).fillna(0).astype(int).sum()
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'garrafas': 0,
            'homens': 0,
            'mulheres': 0,
            'criancas': 0
        }

@app.route('/saida', methods=['GET'])
def lista_saida():
    df_lista_saida = 0
    res_saida = get_total_counts(df_lista_saida)
    tabela_saida = df_lista_saida.to_html(index=False)
    return render_template('saida.html', tabela_saida=tabela_saida, res_saida=res_saida)