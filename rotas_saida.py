from flask import render_template, jsonify, request, flash, redirect, url_for
import pandas as pd
import datetime
import io
from main import app, db  # Make sure to import db from main
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from flask import send_file

# Create a global DataFrame to store the data
df_lista_saida = pd.DataFrame(columns=['matricula', 'nome', 'garrafas', 'homens', 'mulheres', 'criancas'])

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
    global df_lista_saida
    # Load data from MongoDB collection
    try:
        # Check if collection exists
        if 'lista_sentenciados' in db.list_collection_names():
            # Create DataFrame from the lista_sentenciados collection
            df_lista_saida = pd.DataFrame(list(db.lista_sentenciados.find({}, {'_id': 0})))
            
            # If DataFrame is empty, initialize with proper columns
            if df_lista_saida.empty:
                df_lista_saida = pd.DataFrame(columns=['matricula', 'nome', 'pavilhao', 'garrafas', 'homens', 'mulheres', 'criancas'])
        else:
            # If collection doesn't exist, create empty DataFrame
            df_lista_saida = pd.DataFrame(columns=['matricula', 'nome', 'pavilhao', 'garrafas', 'homens', 'mulheres', 'criancas'])
            flash('A coleção lista_sentenciados não existe no banco de dados.', 'warning')
    except Exception as e:
        print(f"Error loading data from MongoDB: {str(e)}")
        df_lista_saida = pd.DataFrame(columns=['matricula', 'nome', 'pavilhao', 'garrafas', 'homens', 'mulheres', 'criancas'])
        flash(f'Erro ao carregar dados: {str(e)}', 'danger')
    
    # Calculate totals - returns dictionary with 'garrafas', 'homens', 'mulheres', 'criancas' sums
    saida = get_total_counts(df_lista_saida)
    # Count total number of matriculas
    total_matriculas = len(df_lista_saida['matricula'].unique())    
    # Convert DataFrame to HTML table
    tabela_saida = df_lista_saida.to_html(index=False, classes='table table-striped table-bordered')
    
    return render_template('saida.html', tabela_saida=tabela_saida, saida=saida, total_matriculas=total_matriculas)


@app.route('/limpar_saida', methods=['POST'])
def limpar_saida():
    global df_lista_saida

    
    # Delete all documents from the collection
    db.lista_sentenciados.delete_many({})
    
    # Reset the DataFrame to empty with proper columns
    df_lista_saida = pd.DataFrame(columns=['matricula', 'nome', 'pavilhao', 'garrafas', 'homens', 'mulheres', 'criancas'])
    flash('Lista limpa com sucesso!', 'success')
    return redirect(url_for('lista_saida'))