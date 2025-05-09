from flask import render_template, flash
from main import *


# Armazenamento em cache simples
_cached_table_html = None
_last_updated = 0

def construir_tabela_html(force_refresh=False):
    global _cached_table_html, _last_updated
    import time
    
    # Usar cache se disponível e não forçar atualização
    current_time = time.time()
    if not force_refresh and _cached_table_html and (current_time - _last_updated < 900):
        return _cached_table_html
       # Atualizar cache
        _cached_table_html = html
        _last_updated = current_time
        return html

# Função para construir a tabela HTML
def construir_tabela_html():
    try:
        # Verificar se a coleção 'trab' existe
        if 'trab' in db.list_collection_names():
            # Buscar documentos diretamente do MongoDB
            documentos = list(db.trab.find({}, {'_id': 0}))
            
            if documentos:
                # Iniciar a tabela com cabeçalhos
                html = """
                 <table class="table table-striped" id="tabela-trabalho">
                  <thead>
                    <tr>
                      <th>Matrícula</th>
                      <th>Nome</th>
                      <th>Setor</th>
                    </tr>
                  </thead>
                  <tbody>
                """
                
                # Adicionar cada documento como uma linha
                for doc in documentos:
                    matricula = doc.get('matricula', '')
                    nome = doc.get('nome', '')
                    setor = doc.get('setor', '')
                    
                    linha = f"""
                    <tr>
                      <td>{matricula}</td>
                      <td>{nome}</td>
                      <td>{setor}</td>
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
                return "<p>Esta função esta desativada, o banco de dados não foi sincronizado com o SIA. Favor verificar! </p>"
        else:
            return "<p>Coleção de trabalho não encontrada</p>"
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return f"<p class='alert alert-danger'>Erro ao processar dados: {e}</p>"

# Context processor para disponibilizar a tabela em todos os templates
@app.context_processor
def inject_tabela_trabalho():
    return {'tab_trabalho': construir_tabela_html()}

# Rota padrão apenas para visualização
@app.route('/trabalho', methods=['GET'])
def trabalho():
    # Não precisa mais passar a tabela explicitamente
    # O context processor já a disponibiliza
    return render_template('index.html')

def conf_trabalho(matricula):
    """Verifica se uma matrícula existe na coleção 'trab'"""
    try:
        # Verificar diretamente no MongoDB
        resultado = db.trab.find_one({'matricula': str(matricula)})
        return resultado is not None
    except Exception as e:
        print(f"Erro ao verificar matrícula: {e}")
        return False

@app.route('/api/trabalho', methods=['GET'])
def api_trabalho():
    """API para obter os dados em formato JSON"""
    try:
        if 'trab' in db.list_collection_names():
            documentos = list(db.trab.find({}, {'_id': 0}))
            return {
                "status": "success",
                "data": documentos,
                "count": len(documentos)
            }
        else:
            return {
                "status": "warning",
                "message": "Coleção não encontrada",
                "data": [],
                "count": 0
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500
