from flask import (
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for,
    send_file,
    session,
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


@app.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    form = PesquisaForm()
    tabela_html = ''  # Tabela vazia inicialmente

    if form.validate_on_submit():
        matricula = form.matricula.data.strip()
        nome = form.nome.data.strip()
        query = {}

        if matricula:
            query['matricula'] = {
                '$regex': f'^\\s*{re.escape(matricula)}\\s*',
                '$options': 'i',
            }
        if nome:
            query['nome'] = {'$regex': nome, '$options': 'i'}

        # Só gera tabela quando há pesquisa
        tabela_html = construir_tabela(query=query, incluir_acoes=True)

    return render_template('pesquisa.html', form=form, tabela_html=tabela_html)


@app.route('/sentenciado_detalhes/<matricula>', methods=['GET'])
def sentenciado_detalhes(matricula):
    try:
        sentenciados_collection = db.sentenciados

        # Buscar o sentenciado
        sentenciado = sentenciados_collection.find_one(
            {'matricula': matricula}
        )

        if not sentenciado:
            return jsonify({'erro': 'Sentenciado não encontrado'}), 404

        # Converter ObjectId para string se existir
        if '_id' in sentenciado:
            sentenciado['_id'] = str(sentenciado['_id'])

        # Garantir que matricula seja string
        sentenciado['matricula'] = str(sentenciado['matricula'])

        # Retornar dados usando json_util para lidar com tipos MongoDB
        return (
            json_util.dumps(sentenciado),
            200,
            {'Content-Type': 'application/json'},
        )

    except Exception as e:
        print(f'Erro na rota sentenciado_detalhes: {str(e)}')  # Debug
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500


@app.route('/entrada_saida', methods=['GET', 'POST'])
def entrada_saida():
    form = PesquisaForm()
    sentenciados = db.sentenciados
    resultados = ''

    # Adicionar o resumo aqui
    resumo = resumo_visitas()

    if form.validate_on_submit():
        matricula = form.matricula.data.strip()
        nome = form.nome.data.strip()
        query = {}

        if matricula:
            query['matricula'] = {
                '$regex': f'^\\s*{re.escape(matricula)}\\s*',
                '$options': 'i',
            }
        if nome:
            query['nome'] = {'$regex': nome, '$options': 'i'}

        resultados = construir_tabela(query=query, incluir_acoes=True)

    return render_template(
        'entrada_saida.html', form=form, resultados=resultados, resumo=resumo
    )


# ADICIONA VISITA AO BANCO DE DADOS
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

        try:
            resultado = db.sentenciados.update_one(
                {'matricula': matricula},
                {
                    '$push': {
                        'visitas': datetime.datetime.now(),
                    },
                    '$set': {
                        'marcadores': [garrafas, homens, mulheres, criancas]
                    },
                },
            )

        except Exception as e:
            print(f'Erro ao atualizar documento: {str(e)}')
            return jsonify(
                {'status': 'error', 'message': f'Erro ao atualizar: {str(e)}'}
            )

        # Preparar a resposta
        response = {'status': 'success', 'message': 'Adicionado com sucesso'}
        if setor_trabalho:
            response['tem_trabalho'] = True
            response['setor'] = setor_trabalho

        return jsonify(response)

    else:
        print(f'Sentenciado não encontrado para matrícula: {matricula}')
        return jsonify(
            {'status': 'error', 'message': 'Matrícula não encontrada'}
        )


# LISTA DE VISITAS
@app.route('/lista', methods=['GET'])
def visualizar_lista():
    # Definir o início e fim do dia de hoje
    hoje_inicio = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    hoje_fim = datetime.datetime.now().replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    resumo = resumo_visitas()

    # Buscar apenas documentos que têm visitas de hoje E ordenar por nome
    documentos = list(
        db.sentenciados.find(
            {
                'visitas': {
                    '$elemMatch': {'$gte': hoje_inicio, '$lte': hoje_fim}
                }
            },
            {'_id': 0},
        ).sort('nome', 1)
    )  # 1 = ordem crescente (A-Z)

    # Processar documentos
    for doc in documentos:
        # Filtrar apenas as visitas de hoje
        visitas_hoje = [
            v for v in doc.get('visitas', []) if hoje_inicio <= v <= hoje_fim
        ]

        # Pegar a última visita de hoje
        if visitas_hoje:
            doc['data_visita'] = visitas_hoje[-1].strftime('%d/%m/%Y %H:%M')
        else:
            doc['data_visita'] = ''

        # Separar marcadores
        marcadores = doc.get('marcadores', [0, 0, 0, 0])
        doc['garrafas'] = marcadores[0] if len(marcadores) > 0 else 0
        doc['homens'] = marcadores[1] if len(marcadores) > 1 else 0
        doc['mulheres'] = marcadores[2] if len(marcadores) > 2 else 0
        doc['criancas'] = marcadores[3] if len(marcadores) > 3 else 0

    return render_template('lista.html', documentos=documentos, resumo=resumo)


@app.route('/api/lista_dados', methods=['GET'])
def api_lista_dados():
    # Definir o início e fim do dia de hoje
    hoje_inicio = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    hoje_fim = datetime.datetime.now().replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    # Buscar apenas documentos que têm visitas de hoje E ordenar por nome
    documentos = list(
        db.sentenciados.find(
            {
                'visitas': {
                    '$elemMatch': {'$gte': hoje_inicio, '$lte': hoje_fim}
                }
            },
            {'_id': 0},
        ).sort('nome', 1)
    )

    # Processar documentos
    for doc in documentos:
        # Filtrar apenas as visitas de hoje
        visitas_hoje = [
            v for v in doc.get('visitas', []) if hoje_inicio <= v <= hoje_fim
        ]

        # Pegar a última visita de hoje
        if visitas_hoje:
            doc['data_visita'] = visitas_hoje[-1].strftime('%d/%m/%Y %H:%M')
        else:
            doc['data_visita'] = ''

        # Separar marcadores
        marcadores = doc.get('marcadores', [0, 0, 0, 0])
        doc['garrafas'] = marcadores[0] if len(marcadores) > 0 else 0
        doc['homens'] = marcadores[1] if len(marcadores) > 1 else 0
        doc['mulheres'] = marcadores[2] if len(marcadores) > 2 else 0
        doc['criancas'] = marcadores[3] if len(marcadores) > 3 else 0

    return jsonify({'status': 'success', 'documentos': documentos})


@app.route('/editar_marcadores/<matricula>', methods=['PUT'])
def editar_marcadores(matricula):
    try:
        data = request.get_json()
        garrafas = int(data.get('garrafas', 0))
        homens = int(data.get('homens', 0))
        mulheres = int(data.get('mulheres', 0))
        criancas = int(data.get('criancas', 0))

        # Atualizar os marcadores no banco
        resultado = db.sentenciados.update_one(
            {'matricula': matricula},
            {'$set': {'marcadores': [garrafas, homens, mulheres, criancas]}},
        )

        if resultado.modified_count > 0:
            return jsonify(
                {
                    'status': 'success',
                    'message': 'Marcadores atualizados com sucesso',
                    'data': {
                        'matricula': matricula,
                        'garrafas': garrafas,
                        'homens': homens,
                        'mulheres': mulheres,
                        'criancas': criancas,
                    },
                }
            )
        else:
            return jsonify(
                {
                    'status': 'error',
                    'message': 'Matrícula não encontrada ou nenhuma alteração feita',
                }
            )

    except Exception as e:
        return jsonify(
            {
                'status': 'error',
                'message': f'Erro ao editar marcadores: {str(e)}',
            }
        )


# REMOVER NOME VISITA
@app.route('/remover_visita_hoje/<matricula>', methods=['DELETE'])
def remover_visita_hoje(matricula):
    try:
        # Definir hoje
        hoje_inicio = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        hoje_fim = datetime.datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        # Remover apenas as visitas de hoje
        resultado = db.sentenciados.update_one(
            {'matricula': matricula},
            {'$pull': {'visitas': {'$gte': hoje_inicio, '$lte': hoje_fim}}},
        )

        if resultado.modified_count > 0:
            return jsonify(
                {
                    'status': 'success',
                    'message': 'Visita de hoje removida com sucesso',
                }
            )
        else:
            return jsonify(
                {
                    'status': 'error',
                    'message': 'Nenhuma visita de hoje encontrada para esta matrícula',
                }
            )

    except Exception as e:
        return jsonify(
            {'status': 'error', 'message': f'Erro ao remover visita: {str(e)}'}
        )


# LIMPAR MATRICULA COMPLETA SISTEMA DE ADMIN
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


# BAIXA LISTA ROTA DOWNLOADS
@app.route('/download', methods=['GET'])
def download_pdf():
    # Definir o início e fim do dia de hoje
    hoje_inicio = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    hoje_fim = datetime.datetime.now().replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    # Buscar apenas documentos que têm visitas de hoje E ordenar por nome
    documentos = list(
        db.sentenciados.find(
            {
                'visitas': {
                    '$elemMatch': {'$gte': hoje_inicio, '$lte': hoje_fim}
                }
            },
            {'_id': 0},
        ).sort('nome', 1)
    )  # 1 = ordem crescente (A-Z)

    # Processar documentos
    for doc in documentos:
        # Filtrar apenas as visitas de hoje
        visitas_hoje = [
            v for v in doc.get('visitas', []) if hoje_inicio <= v <= hoje_fim
        ]

        # Pegar a última visita de hoje
        if visitas_hoje:
            doc['data_visita'] = visitas_hoje[-1].strftime('%d/%m/%Y %H:%M')
        else:
            doc['data_visita'] = ''

        # Separar marcadores
        marcadores = doc.get('marcadores', [0, 0, 0, 0])
        doc['garrafas'] = marcadores[0] if len(marcadores) > 0 else 0
        doc['homens'] = marcadores[1] if len(marcadores) > 1 else 0
        doc['mulheres'] = marcadores[2] if len(marcadores) > 2 else 0
        doc['criancas'] = marcadores[3] if len(marcadores) > 3 else 0

    # Converter para DataFrame
    if not documentos:
        # DataFrame vazio se não houver visitas hoje
        df_data = pd.DataFrame(
            columns=[
                'matricula',
                'nome',
                'garrafas',
                'homens',
                'mulheres',
                'criancas',
                'pavilhao',
                'data_visita',
            ]
        )
    else:
        df_data = pd.DataFrame(documentos)
        # Reordenar colunas para o PDF
        df_data = df_data[
            [
                'matricula',
                'nome',
                'garrafas',
                'homens',
                'mulheres',
                'criancas',
                'pavilhao',
                'data_visita',
            ]
        ]

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

    # Adicionar título com a data
    styles = getSampleStyleSheet()
    titulo = Paragraph(
        f'<b>Lista de Visitantes - {datetime.datetime.now().strftime("%d/%m/%Y")}</b>',
        styles['Title'],
    )
    elements.append(titulo)
    elements.append(Paragraph('<br/>', styles['Normal']))

    # Calcular totais
    try:
        totals = {
            'garrafas': df_data['garrafas'].fillna(0).astype(int).sum(),
            'homens': df_data['homens'].fillna(0).astype(int).sum(),
            'mulheres': df_data['mulheres'].fillna(0).astype(int).sum(),
            'criancas': df_data['criancas'].fillna(0).astype(int).sum(),
        }
        total_visitantes = (
            totals['homens'] + totals['mulheres'] + totals['criancas']
        )
    except Exception as e:
        totals = {'garrafas': 0, 'homens': 0, 'mulheres': 0, 'criancas': 0}
        total_visitantes = 0

    elements.append(Paragraph('<br/>', styles['Normal']))

    # Criar tabela
    if not df_data.empty:
        # Cabeçalhos da tabela
        headers = [
            'Matrícula',
            'Nome',
            'Garrafas',
            'Homens',
            'Mulheres',
            'Crianças',
            'Pavilhão',
            'Hora da Visita',
        ]
        data = [headers] + df_data.values.tolist()

        # Ajustar larguras das colunas
        table_nomes = Table(data, colWidths=[60, 140, 40, 40, 40, 40, 50, 70])
    else:
        # Tabela vazia se não houver dados
        data = [
            [
                'Matrícula',
                'Nome',
                'Garrafas',
                'Homens',
                'Mulheres',
                'Crianças',
                'Pavilhão',
                'Hora da Visita',
            ],
            ['', 'Nenhuma visita registrada hoje', '', '', '', '', '', ''],
        ]
        table_nomes = Table(data, colWidths=[60, 140, 40, 40, 40, 40, 50, 70])

    # Estilo da tabela
    style = TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Centralizar números
            (
                'ALIGN',
                (0, 1),
                (1, -1),
                'LEFT',
            ),  # Alinhar matrícula e nome à esquerda
        ]
    )

    table_nomes.setStyle(style)
    elements.append(table_nomes)

    # Espaçamento e assinatura com usuário da sessão
    elements.append(Paragraph('<br/><br/><br/>', styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'lista_visitas_{datetime.datetime.now().strftime("%d-%m")}.pdf',
        mimetype='application/pdf',
    )


def construir_tabela(
    documentos=None,
    query=None,
    incluir_acoes=True,
    classe_css='table table-striped',
):
    try:
        # Se não foram passados documentos, buscar no banco
        if documentos is None:
            if query is None:
                # Query padrão - todos os documentos
                query = {}

            documentos = list(
                db.sentenciados.find(query, {'_id': 0}).sort('nome', 1)
            )

        if documentos:
            # Colunas básicas
            acoes_header = '<th>Ações</th>' if incluir_acoes else ''

            html = f"""
            <table class="{classe_css}" id="tabela-sentenciados">
                <thead>
                    <tr>
                        <th>Matrícula</th>
                        <th>Nome</th>
                        <th>Alojamento</th>
                        {acoes_header}
                    </tr>
                </thead>
                <tbody>
            """

            # Adicionar cada documento como uma linha
            for doc in documentos:
                matricula = doc.get('matricula', '')
                nome = doc.get('nome', '')
                alojamento = doc.get('pavilhao', '') or doc.get(
                    'alojamento', ''
                )

                # Coluna de ações (se solicitada)
                acoes_cell = ''
                if incluir_acoes:
                    acoes_cell = f"""
                        <td>
                            
                        </td>
                    """

                linha = f"""
                    <tr id="row-{matricula}">
                        <td>{matricula}</td>
                        <td>{nome}</td>
                        <td>{alojamento}</td>
                        {acoes_cell}
                    </tr>
                """
                html += linha

            # Fechar a tabela
            html += """
                </tbody>
            </table>
            """
            return html
        else:
            return (
                '<p class="alert alert-info">Nenhum resultado encontrado.</p>'
            )

    except Exception as e:
        print(f'Erro ao construir tabela: {e}')
        return (
            f"<p class='alert alert-danger'>Erro ao processar dados: {e}</p>"
        )


def resumo_visitas():
    try:
        # Definir o início e fim do dia de hoje
        hoje_inicio = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        hoje_fim = datetime.datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        # Usar agregação do MongoDB para melhor performance
        pipeline = [
            {
                '$match': {
                    'visitas': {
                        '$elemMatch': {'$gte': hoje_inicio, '$lte': hoje_fim}
                    }
                }
            },
            {'$project': {'matricula': 1, 'marcadores': 1}},
        ]

        documentos_hoje = list(db.sentenciados.aggregate(pipeline))

        # Calcular resumo
        total_matriculas = len(documentos_hoje)
        total_garrafas = 0
        total_homens = 0
        total_mulheres = 0
        total_criancas = 0

        for doc in documentos_hoje:
            marcadores = doc.get('marcadores', [0, 0, 0, 0])

            # Conversão otimizada
            if marcadores and len(marcadores) >= 4:
                try:
                    total_garrafas += int(marcadores[0] or 0)
                    total_homens += int(marcadores[1] or 0)
                    total_mulheres += int(marcadores[2] or 0)
                    total_criancas += int(marcadores[3] or 0)
                except (ValueError, TypeError):
                    continue

        return {
            'matriculas': total_matriculas,
            'garrafas': total_garrafas,
            'homens': total_homens,
            'mulheres': total_mulheres,
            'criancas': total_criancas,
            'total_visitantes': total_homens + total_mulheres + total_criancas,
            'data_atual': datetime.datetime.now().strftime('%d/%m/%Y'),
        }

    except Exception as e:
        print(f'Erro ao calcular resumo: {str(e)}')
        return {
            'matriculas': 0,
            'garrafas': 0,
            'homens': 0,
            'mulheres': 0,
            'criancas': 0,
            'total_visitantes': 0,
            'data_atual': datetime.datetime.now().strftime('%d/%m/%Y'),
        }


@app.route('/api/resumo', methods=['GET'])
def api_resumo():
    """Retorna o resumo atual das visitas em formato JSON"""
    resumo = resumo_visitas()
    return jsonify(resumo)


@app.route('/')
def index():
    # Verificar se o usuário está logado
    if 'user' not in session:
        return redirect(url_for('login'))

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

    # Usar a função para obter o resumo
    resumo = resumo_visitas()

    return render_template('index.html', totals=totals, resumo=resumo)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
