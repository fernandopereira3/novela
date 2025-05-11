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
        tem_colecao = 'trab' in colecoes

        # Informações sobre o banco de dados
        db_info = {
            'database_name': db.name,
            'collections': colecoes,
            'trabalho_collection_exists': tem_colecao,
        }

        # Se a coleção existir, recupera seus dados e estatísticas
        if tem_colecao:
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
                    <div class="card-header bg-primary text-white">
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
            # Obtém os documentos com paginação
            documentos = list(db.trab.find({}).skip(skip).limit(limit))

            # Contagem total para informações de paginação
            total = db.trab.count_documents({})

            # Converte ObjectId para string
            json_data = json.loads(json_util.dumps(documentos))

            return jsonify(
                {
                    'status': 'success',
                    'total': total,
                    'limit': limit,
                    'skip': skip,
                    'data': json_data,
                }
            )
        else:
            return jsonify(
                {
                    'status': 'error',
                    'message': "Coleção 'trabalho' não encontrada",
                }
            )
    except Exception as e:
        print(f'Error in api_trabalho_raw: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/test_debug')
def test_debug():
    return render_template(
        'debug.html',
        debug_content='<div class="alert alert-success">Teste funcionando!</div>',
    )
