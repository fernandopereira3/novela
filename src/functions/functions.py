from flask_wtf import FlaskForm
import datetime
from wtforms import StringField, SubmitField
from db.connection import connection
db = connection()


class PesquisaForm(FlaskForm):
    matricula = StringField('Matrícula')
    nome = StringField('Nome')
    garrafas = StringField('Garrafas')
    homens = StringField('Homens')
    mulheres = StringField('Mulheres')
    criancas = StringField('Crianças')
    pesquisar = SubmitField('PESQUISAR')



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