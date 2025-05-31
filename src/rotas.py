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
import pandas as pd
import re
import datetime
import io
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from main import app, db, PesquisaForm
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from debug import *

df_lista_sentenciados = pd.DataFrame(
    columns=[
        'matricula',
        'nome',
        'garrafas',
        'homens',
        'mulheres',
        'criancas',
        'data_adicao',
    ]
)
## app.secret_key = ''

@app.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    form = PesquisaForm()
    sentenciados = db.sentenciados
    resultados = []

    if form.validate_on_submit():
        matricula = form.matricula.data.strip()
        nome = form.nome.data.strip()
        query = {}

        if matricula:
            query['matricula'] = {
                '$regex': f'^\\s*{re.escape(matricula)}\\s*$',
                '$options': 'i',
            }
        if nome:
            query['nome'] = {'$regex': nome, '$options': 'i'}

        resultados = list(sentenciados.find(query))
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])

    return render_template('pesquisa.html', form=form, sentenciados=resultados)

@app.route('/sentenciado_detalhes/<id>', methods=['GET'])
def sentenciado_detalhes(id):
    try:
        from bson import json_util, ObjectId
        from flask import jsonify, JsonResponse
        sentenciados = db.sentenciados
        if not ObjectId.is_valid(id):
            return JsonResponse({"erro": "ID inválido"}, status=400)
        
        sentenciado = sentenciados.find_one({"_id": ObjectId(id)})

        if not sentenciado:
            return JsonResponse({"erro": "Sentenciado não encontrado"}, status=404)

        sentenciado["_id"] = str(sentenciado["_id"])
        return JsonResponse(json.loads(json_util.dumps(sentenciado)), safe=False)

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)




@app.route('/entrada_saida', methods=['GET', 'POST'])
def entrada_saida():
    form = PesquisaForm()
    sentenciados = db.sentenciados
    resultados = []

    if form.validate_on_submit():
        matricula = form.matricula.data.strip()
        nome = form.nome.data.strip()
        query = {}

        if matricula:
            query['matricula'] = {
                '$regex': f'^\\s*{re.escape(matricula)}\\s*$',
                '$options': 'i',
            }
        if nome:
            query['nome'] = {'$regex': nome, '$options': 'i'}

        resultados = list(sentenciados.find(query))
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])

    return render_template('entrada_saida.html', form=form, sentenciados=resultados)


@app.route('/download', methods=['GET'])
def download_pdf():
    # Get data from MongoDB collection instead of global variable
    collection = db['lista_sentenciados']
    records = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB _id field
    
    # Convert MongoDB records to DataFrame
    if not records:
        # Return empty DataFrame with expected columns if no records
        df_data = pd.DataFrame(
            columns=['matricula', 'nome', 'pavilhao', 'garrafas', 'homens', 'mulheres', 'criancas', 'data_adicao']
        )
    else:
        df_data = pd.DataFrame(records)
    
    # Sort data if requested
    sort_by = request.args.get('sort', 'nome')
    df_sorted = (
        df_data.sort_values(by=sort_by)
        if sort_by in df_data.columns
        else df_data
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=15,
        rightMargin=15,
        topMargin=20,
        bottomMargin=20,
    )
    elements = []

    try:
        totals = {
            'garrafas': df_data['garrafas']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
            'homens': df_data['homens']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
            'mulheres': df_data['mulheres']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
            'criancas': df_data['criancas']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
        }
    except Exception as e:
        totals = {'garrafas': 0, 'homens': 0, 'mulheres': 0, 'criancas': 0}

    data = [df_sorted.columns.tolist()] + df_sorted.values.tolist()
    table_nomes = Table(data, colWidths=[70, 180, 35, 35, 35, 35, 90])

    style = TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            ('ALIGN', (2, 1), (-2, -1), 'CENTER'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]
    )

    table_nomes.setStyle(style)

    elements.append(table_nomes)
    elements.append(
        Paragraph('<br/><br/><br/>', getSampleStyleSheet()['Normal'])
    )
 
    elements.append(
        Paragraph(
            '<br/><br/><br/>_____________________________<br/>Assinatura do Responsável',
            getSampleStyleSheet()['Normal'],
        )
    )

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'lista_{datetime.datetime.now().strftime("%d-%m-%Y-%H-%M")}.pdf',
        mimetype='application/pdf',
    )



@app.route('/adicionar/<matricula>', methods=['POST'])
def adicionar_lista(matricula):
    global df_lista_sentenciados

    sentenciado = db.sentenciados.find_one({'matricula': matricula})
    if sentenciado:
        data = request.get_json()

        # Verificar se existe na coleção trab
        setor_trabalho = None
        try:
            trabalho = db.trab.find_one({'matricula': matricula})
            if not trabalho:
                # Tentar buscar pelo nome se não encontrou pela matrícula
                trabalho = db.trab.find_one({'nome': sentenciado['nome']})

            if trabalho:
                setor_trabalho = trabalho.get(
                    'setor', 'Setor não especificado'
                )
        except Exception as e:
            print(f'Erro ao verificar coleção trab: {str(e)}')

        # Continuar com a adição normal
        garrafas = data.get('garrafas', 0)
        homens = data.get('homens', 0)
        mulheres = data.get('mulheres', 0)
        criancas = data.get('criancas', 0)
        data_adicao = datetime.datetime.now().strftime('%d/%m/%Y as %H:%M')

        new_row = {
            'matricula': sentenciado['matricula'],
            'nome': sentenciado['nome'],
            'pavilhao': sentenciado['pavilhao'],
            'garrafas': garrafas,
            'homens': homens,
            'mulheres': mulheres,
            'criancas': criancas,
            'data_adicao': data_adicao,
        }

        df_lista_sentenciados = pd.concat(
            [df_lista_sentenciados, pd.DataFrame([new_row])], ignore_index=True
        )

        # Preparar a resposta
        response = {'status': 'success', 'message': 'Adicionado com sucesso'}
        if setor_trabalho:
            response['tem_trabalho'] = True
            response['setor'] = setor_trabalho

        return jsonify(response)
    return jsonify({'status': 'error', 'message': 'Matrícula não encontrada'})


@app.route('/lista', methods=['GET'])
def visualizar_lista():
    global df_lista_sentenciados

    try:
        entrada = {
            'matriculas': df_lista_sentenciados['matricula'].count(),
            'garrafas': df_lista_sentenciados['garrafas']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
            'homens': df_lista_sentenciados['homens']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
            'mulheres': df_lista_sentenciados['mulheres']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
            'criancas': df_lista_sentenciados['criancas']
            .replace('', pd.NA)
            .fillna(0)
            .astype(int)
            .sum(),
        }
    except Exception as e:
        print(f'Error: {str(e)}')
        totals = {'garrafas': 0, 'homens': 0, 'mulheres': 0, 'criancas': 0}

    tabela_entrada = df_lista_sentenciados.to_html(
        index=False, classes='table table-bordered'
    )

    return render_template(
        'lista.html', tabela_entrada=tabela_entrada, entrada=entrada
    )


@app.route('/remover/<matricula>', methods=['DELETE'])
def remover_lista(matricula):
    global df_lista_sentenciados

    df_lista_sentenciados = df_lista_sentenciados[
        df_lista_sentenciados['matricula'] != matricula
    ]

    if df_lista_sentenciados.empty:
        return jsonify(
            {'status': 'error', 'message': 'Matrícula não encontrada'}
        )
    else:
        return jsonify(
            {'status': 'success', 'message': 'Matrícula removida com sucesso'}
        )


@app.route('/limpar_lista', methods=['POST'])
def limpar_lista():
    global df_lista_sentenciados
    df_lista_sentenciados = pd.DataFrame(columns=df_lista_sentenciados.columns)
    flash('Lista limpa com sucesso!', 'success')
    return redirect(url_for('entrada_saida'))


@app.route('/clear', methods=['GET'])
def clean_matricula_complete():
    count = 0
    for doc in db.sentenciados.find():
        if 'matricula' in doc and isinstance(doc['matricula'], str):
            original = doc['matricula']

            clean_matricula = (
                original.replace(' ', '').replace('.', '').replace('-', '')
            )

            if len(clean_matricula) > 0:
                clean_matricula = clean_matricula[:-1]

            if clean_matricula != original:
                db.sentenciados.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'matricula': clean_matricula}},
                )
                count += 1

    return f'LIMPO ! FORAM REMOVIDOS ESPACOS, PONTOS E O DIGITO DE {count} MATRICULAS'


@app.route('/salvar-lista', methods=['POST'])
def salvar_lista_no_banco():
    global df_lista_sentenciados

    if df_lista_sentenciados.empty:
        return jsonify({'Nao ha dados para salvar'})

    try:
        # Criar nome da coleção com timestamp para evitar conflitos
        collection_name = f'lista_sentenciados'
        collection = db[collection_name]

        # Limpar dados existentes na coleção
        collection.delete_many({})

        # Converter DataFrame para lista de dicionários e salvar no MongoDB
        registros = df_lista_sentenciados.to_dict('records')

        # Inserir registros na coleção
        result = collection.insert_many(registros)

        # Verificar se inserção foi bem-sucedida
        if len(result.inserted_ids) == len(registros):
            return jsonify({f'Lista salva com sucesso'})
        else:
            return jsonify(
                {
                    f'Alguns registros nao foram salvos. {len(result.inserted_ids)} de {len(registros)} registros salvos.'
                }
            )

    except Exception as e:
        return jsonify({f'Erro ao salvar no banco de dados: {str(e)}'})


## LOGIN ##


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.usuarios.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))

        flash('Usuário ou senha inválidos')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


## LOGIN ##


@app.route('/')
def index():
    # Calculate totals for each pavilion from your data
    totals = {
        'aloj_1a': db.sentenciados.count_documents({'pavilhao': '1A'}),
        'aloj_1b': db.sentenciados.count_documents({'pavilhao': '1B'}),
        'aloj_2a': db.sentenciados.count_documents({'pavilhao': '2A'}),
        'aloj_2b': db.sentenciados.count_documents({'pavilhao': '2B'}),
        'aloj_3a': db.sentenciados.count_documents({'pavilhao': '3A'}),
        'aloj_3b': db.sentenciados.count_documents({'pavilhao': '3B'}),
        'aloj_4a': db.sentenciados.count_documents({'pavilhao': '4A'}),
        'aloj_4b': db.sentenciados.count_documents({'pavilhao': '4B'}),
        'total': db.sentenciados.count_documents({}),
    }

    resumo = {
        'matriculas': df_lista_sentenciados['matricula'].count(),
        'garrafas': df_lista_sentenciados['garrafas']
        .replace('', pd.NA)
        .fillna(0)
        .astype(int)
        .sum(),
        'homens': df_lista_sentenciados['homens']
        .replace('', pd.NA)
        .fillna(0)
        .astype(int)
        .sum(),
        'mulheres': df_lista_sentenciados['mulheres']
        .replace('', pd.NA)
        .fillna(0)
        .astype(int)
        .sum(),
        'criancas': df_lista_sentenciados['criancas']
        .replace('', pd.NA)
        .fillna(0)
        .astype(int)
        .sum(),
    }

    return render_template(
        'index.html', totals=totals, resumo=resumo, trabalho=trabalho
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
