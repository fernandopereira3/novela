import pandas as pd
from main import app, db
from flask import jsonify, request
import json
from bson import json_util
from trabalho import *
from rotas import *


@app.route('/debug', methods=['GET'])
def debug_trabalho():
    """Rota de debug para visualizar detalhes do DataFrame df_trabalho"""
    try:
        # Tentativa de acessar df_trabalho do escopo global
        from rotas import df_lista_sentenciados

        # [código existente para coletar informações]

        # Gerar HTML para o template em vez de retornar JSON
        html_output = f"""
        <div class="container debug-container">
            <h2>Debug DataFrame df_lista_sentenciados</h2>
            <div class="card">
                <div class="card-header bg-info text-white">
                    Informações Básicas
                </div>
                <div class="card-body">
                    <p><strong>Dimensões:</strong> {df_lista_sentenciados.shape[0]} linhas x {df_lista_sentenciados.shape[1]} colunas</p>
                    <p><strong>Colunas:</strong> {', '.join(df_lista_sentenciados.columns)}</p>
                    <p><strong>Tipos de dados:</strong></p>
                    <ul>
                        {''.join([f'<li>{col}: {dtype}</li>' for col, dtype in df_lista_sentenciados.dtypes.items()])}
                    </ul>
                </div>
            </div>
            
            <h3 class="mt-4">Conteúdo do DataFrame</h3>
            <div class="table-responsive">
                {df_lista_sentenciados.to_html(classes='table table-striped table-sm', index=True)}
            </div>
        </div>
        """

        return render_template('debug.html', debug_content=html_output)

    except Exception as e:
        error_html = f"""
        <div class="alert alert-danger">
            <h4>Erro ao acessar DataFrame</h4>
            <p>{str(e)}</p>
        </div>
        """
        return render_template('debug.html', debug_content=error_html)


@app.route('/debug/trabalho/db', methods=['GET'])
def debug_trabalho_db():
    """Rota de debug para visualizar dados diretamente do banco de dados"""
    try:
        # Verifica se a coleção existe
        colecoes = db.list_collection_names()
        trab = 'trab' in colecoes

        # Informações sobre o banco de dados
        db_info = {
            'database_name': db.name,
            'collections': colecoes,
            'trabalho_collection_exists': trab,
        }

        # Se a coleção existir, recupera seus dados e estatísticas
        if trab:
            # Conta documentos
            count = db.trab.count_documents({})

            # Obtém amostra de documentos (limita a 100 para evitar sobrecarga)
            documentos = list(db.trab.find({}).limit(150))

            # Pega o primeiro documento para analisar a estrutura (se houver)
            primeiro_doc = db.trab.find_one({})
            estrutura = {}

            if primeiro_doc:
                for campo, valor in primeiro_doc.items():
                    if campo != '_id':  # Ignora o campo _id do MongoDB
                        estrutura[campo] = type(valor).__name__

            # Converte dados do MongoDB para DataFrame para análise
            df_temp = pd.DataFrame(documentos)
            if '_id' in df_temp.columns:
                df_temp = df_temp.drop(columns=['_id'])

            # Saída para o console
            print('\n===== DEBUG MONGODB TRABALHO =====')
            print(f'Banco de dados: {db.name}')
            print(f'Coleções: {colecoes}')
            print(f"Documentos na coleção 'trabalho': {count}")
            print('\nEstrutura do documento:')
            for campo, tipo in estrutura.items():
                print(f'  - {campo}: {tipo}')
            print('\nPrimeiros 5 documentos:')
            if not df_temp.empty:
                print(df_temp.head())
            print('============================\n')

            # HTML para visualização
            html_output = f"""
            <div class="container debug-container">
                <h2>Debug MongoDB - Coleção 'trabalho'</h2>
                
                <div class="card mb-4">
                    <div class="card-body bg-primary text-white">
                        Informações do Banco de Dados
                    </div>
                    <div class="card-body">
                        <p><strong>Banco de dados:</strong> {db.name}</p>
                        <p><strong>Coleções disponíveis:</strong> {', '.join(colecoes)}</p>
                        <p><strong>Total de documentos na coleção 'trabalho':</strong> {count}</p>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header bg-info text-white">
                        Estrutura dos Documentos
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Campo</th>
                                    <th>Tipo</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([f'<tr><td>{campo}</td><td>{tipo}</td></tr>' for campo, tipo in estrutura.items()])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <h3>Amostra de Dados (até 150 documentos)</h3>
                <div class="table-responsive">
                    {df_temp.to_html(classes='table table-striped table-sm', index=False) if not df_temp.empty else '<p>Não há dados na coleção.</p>'}
                </div>
                
                <div class="mt-4">
                    <h3>Estatísticas Numéricas (se disponível)</h3>
                    {df_temp.describe().to_html(classes='table table-bordered') if not df_temp.empty and df_temp.select_dtypes(include=['number']).shape[1] > 0 else '<p>Não há dados numéricos para análise estatística.</p>'}
                </div>
            </div>
            """

            return render_template('debug.html', debug_content=html_output)

        else:
            # Se a coleção não existir
            html_output = f"""
            <div class="container debug-container">
                <div class="alert alert-warning">
                    <h4>Coleção 'trabalho' não encontrada no banco de dados</h4>
                    <p>Banco de dados: {db.name}</p>
                    <p>Coleções disponíveis: {', '.join(colecoes) if colecoes else 'Nenhuma'}</p>
                </div>
            </div>
            """
            return render_template('debug.html', debug_content=html_output)

    except Exception as e:
        # Em caso de erro
        error_html = f"""
        <div class="container">
            <div class="alert alert-danger">
                <h4>Erro ao acessar o banco de dados</h4>
                <p>{str(e)}</p>
            </div>
        </div>
        """
        return render_template('debug.html', debug_content=error_html)


@app.route('/api/trabalho/stats', methods=['GET'])
def api_trabalho_stats():
    """Rota que fornece estatísticas sobre a coleção trabalho"""
    try:
        if 'trabalho' in db.list_collection_names():
            # Obtém todos os documentos
            df_temp = pd.DataFrame(list(db.trab.find({}, {'_id': 0})))

            if not df_temp.empty:
                # Calcular estatísticas básicas
                stats = {
                    'count': len(df_temp),
                    'columns': df_temp.columns.tolist(),
                    'null_counts': df_temp.isnull().sum().to_dict(),
                }

                # Adicionar estatísticas numéricas se houver colunas numéricas
                num_cols = df_temp.select_dtypes(
                    include=['number']
                ).columns.tolist()
                if num_cols:
                    stats['numeric_stats'] = json.loads(
                        df_temp[num_cols].describe().to_json()
                    )

                # Contar valores únicos para colunas categóricas (limitado a 20 valores únicos)
                for col in df_temp.columns:
                    if df_temp[col].nunique() < 20:
                        stats[f'{col}_value_counts'] = (
                            df_temp[col].value_counts().to_dict()
                        )

                return jsonify({'status': 'success', 'statistics': stats})
            else:
                return jsonify(
                    {'status': 'success', 'message': 'Coleção vazia'}
                )
        else:
            return jsonify(
                {
                    'status': 'error',
                    'message': "Coleção 'trabalho' não encontrada",
                }
            )
    except Exception as e:
        print(f'Error in api_trabalho_stats: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/trabalho/raw', methods=['GET'])
def api_trabalho_raw():
    """Rota que retorna os dados brutos da coleção trabalho"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        skip = request.args.get('skip', default=0, type=int)

        if 'trab' in db.list_collection_names():
            documentos = list(db.trab.find({}).skip(skip).limit(limit))

            total = db.trab.count_documents({})

            json_data = json.loads(json_util.dumps(documentos))
            return jsonify(
                {
                    'status': 'success',
                    'pagination': {
                        'total_records': total,
                        'records_per_page': limit,
                        'current_offset': skip,
                        'current_page': skip // limit + 1,
                        'total_pages': -(-total // limit),
                    },
                    'data': json_data,
                }
            ), {'indent': 2}
        else:
            return jsonify(
                {
                    'status': 'error',
                    'message': "Coleção 'trabalho' não encontrada",
                }
            ), {'indent': 2}

    except Exception as e:
        print(f'Error in api_trabalho_raw: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/test_debug')
def test_debug():
    return render_template(
        'debug.html',
        debug_content='<div class="alert alert-success">Teste funcionando!</div>',
    )


@app.route('/normalizar_banco', methods=['GET', 'POST'])
def normalizar_banco():
    """Rota simplificada para normalizar todos os nomes do banco de dados em maiúsculas"""

    if request.method == 'GET':
        # Retornar página simples de confirmação
        return render_template(
            'debug.html',
            debug_content="""
            <div class="alert alert-warning">
                <h4><i class="fas fa-exclamation-triangle"></i> Normalizar Banco de Dados</h4>
                <p>Esta ação irá converter todos os nomes para MAIÚSCULAS.</p>
                <form method="POST">
                    <button type="submit" class="btn btn-warning">
                        <i class="fas fa-check"></i> Confirmar Normalização
                    </button>
                    <a href="/debug" class="btn btn-secondary">Cancelar</a>
                </form>
            </div>
        """,
        )

    try:
        total_atualizados = 0
        erros = []

        # 1. NORMALIZAR SENTENCIADOS
        print('Normalizando sentenciados...')
        for doc in db.sentenciados.find():
            try:
                updates = {}

                # Nome
                if 'nome' in doc and doc['nome']:
                    nome_novo = doc['nome'].upper().strip()
                    if doc['nome'] != nome_novo:
                        updates['nome'] = nome_novo

                # Outros campos texto
                for campo in ['procedencia', 'artigo', 'observacoes']:
                    if (
                        campo in doc
                        and doc[campo]
                        and isinstance(doc[campo], str)
                    ):
                        valor_novo = doc[campo].upper().strip()
                        if doc[campo] != valor_novo:
                            updates[campo] = valor_novo

                if updates:
                    db.sentenciados.update_one(
                        {'_id': doc['_id']}, {'$set': updates}
                    )
                    total_atualizados += 1

            except Exception as e:
                erros.append(
                    f'Sentenciado {doc.get("matricula", "N/A")}: {str(e)}'
                )

        # 2. NORMALIZAR VISITAS
        print('Normalizando visitas...')
        if 'visita' in db.list_collection_names():
            for doc in db.visita.find():
                try:
                    updates = {}

                    for campo in ['nome', 'visitante', 'parentesco']:
                        if campo in doc and doc[campo]:
                            valor_novo = doc[campo].upper().strip()
                            if doc[campo] != valor_novo:
                                updates[campo] = valor_novo

                    if updates:
                        db.visita.update_one(
                            {'_id': doc['_id']}, {'$set': updates}
                        )
                        total_atualizados += 1

                except Exception as e:
                    erros.append(
                        f'Visita {doc.get("matricula", "N/A")}: {str(e)}'
                    )

        # 3. NORMALIZAR TRABALHO
        print('Normalizando trabalho...')
        if 'trab' in db.list_collection_names():
            for doc in db.trab.find():
                try:
                    updates = {}

                    for campo in ['nome', 'setor', 'funcao']:
                        if (
                            campo in doc
                            and doc[campo]
                            and isinstance(doc[campo], str)
                        ):
                            valor_novo = doc[campo].upper().strip()
                            if doc[campo] != valor_novo:
                                updates[campo] = valor_novo

                    if updates:
                        db.trab.update_one(
                            {'_id': doc['_id']}, {'$set': updates}
                        )
                        total_atualizados += 1

                except Exception as e:
                    erros.append(
                        f'Trabalho {doc.get("matricula", "N/A")}: {str(e)}'
                    )

        # RESULTADO SIMPLES
        resultado_html = f"""
        <div class="alert alert-success">
            <h4><i class="fas fa-check-circle"></i> Normalização Concluída!</h4>
            <p><strong>Total de registros atualizados:</strong> {
            total_atualizados
        }</p>
            {
            f'<p><strong>Erros encontrados:</strong> {len(erros)}</p>'
            if erros
            else ''
        }
        </div>
        
        {
            f'''
        <div class="alert alert-warning">
            <h5>Erros:</h5>
            <ul>
                {''.join([f'<li>{erro}</li>' for erro in erros[:10]])}
                {f'<li>... e mais {len(erros) - 10} erros</li>' if len(erros) > 10 else ''}
            </ul>
        </div>
        '''
            if erros
            else ''
        }
        
        <div class="mt-3">
            <a href="/debug" class="btn btn-primary">
                <i class="fas fa-arrow-left"></i> Voltar ao Debug
            </a>
            <a href="/" class="btn btn-success">
                <i class="fas fa-home"></i> Página Inicial
            </a>
        </div>
        """

        return render_template('debug.html', debug_content=resultado_html)

    except Exception as e:
        erro_html = f"""
        <div class="alert alert-danger">
            <h4><i class="fas fa-exclamation-circle"></i> Erro na Normalização</h4>
            <p><strong>Erro:</strong> {str(e)}</p>
            <div class="mt-3">
                <a href="/debug" class="btn btn-primary">Voltar ao Debug</a>
            </div>
        </div>
        """
        return render_template('debug.html', debug_content=erro_html)


@app.route('/api/normalizar_preview', methods=['GET'])
def preview_normalizacao():
    """Preview simplificado da normalização"""
    try:
        contadores = {'sentenciados': 0, 'visitas': 0, 'trabalho': 0}

        # Contar sentenciados que precisam normalização
        for doc in db.sentenciados.find().limit(100):
            if (
                'nome' in doc
                and doc['nome']
                and doc['nome'] != doc['nome'].upper().strip()
            ):
                contadores['sentenciados'] += 1

        # Contar visitas que precisam normalização
        if 'visita' in db.list_collection_names():
            for doc in db.visita.find().limit(100):
                for campo in ['nome', 'visitante', 'parentesco']:
                    if (
                        campo in doc
                        and doc[campo]
                        and doc[campo] != doc[campo].upper().strip()
                    ):
                        contadores['visitas'] += 1
                        break

        # Contar trabalho que precisa normalização
        if 'trab' in db.list_collection_names():
            for doc in db.trab.find().limit(100):
                for campo in ['nome', 'setor']:
                    if (
                        campo in doc
                        and doc[campo]
                        and isinstance(doc[campo], str)
                        and doc[campo] != doc[campo].upper().strip()
                    ):
                        contadores['trabalho'] += 1
                        break

        return jsonify({'status': 'success', 'preview': contadores})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
