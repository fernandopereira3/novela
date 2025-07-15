try:
    from main import app
except ImportError:
    # Fallback para quando executado de fora do diretório src
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from main import app
###################################################################
from functions.functions import PesquisaForm
import pandas as pd
from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
    make_response,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import datetime
from Data.conexao import conexao
db = conexao()


# Create DataFrame for daily visits with proper datetime type
df_visitas = pd.DataFrame(
    columns=['matricula', 'nome', 'visitante', 'parentesco', 'data_visita']
)
df_visitas['data_visita'] = pd.to_datetime(df_visitas['data_visita'])


@app.route('/jumbo', methods=['GET', 'POST'])
def jumbo():
    try:
        global df_visitas
        form = PesquisaForm()

        if request.method == 'POST':
            if 'limpar_lista' in request.form:
                df_visitas = pd.DataFrame(
                    columns=[
                        'matricula',
                        'nome',
                        'visitante',
                        'parentesco',
                        'data_visita',
                    ]
                )
                flash('Lista diária limpa com sucesso', 'success')
                return redirect(url_for('jumbo'))

        today = datetime.datetime.now().date()
        if not df_visitas.empty:
            df_visitas = df_visitas[
                pd.to_datetime(df_visitas['data_visita']).dt.date == today
            ]

        if request.method == 'POST':
            if 'pesquisar' in request.form:
                matricula = request.form.get('matricula')
                sentenciado = db.sentenciados.find_one(
                    {'matricula': matricula}
                )
                if sentenciado:
                    # Normalizar nome do sentenciado em maiúsculas
                    nome_normalizado = (
                        sentenciado.get('nome', '').upper().strip()
                    )
                    form.nome.data = nome_normalizado
                    form.matricula.data = sentenciado.get('matricula')

            elif 'adicionar' in request.form:
                matricula = request.form.get('matricula')
                visitante = request.form.get('visita')
                nome = request.form.get('nome')
                parentesco = request.form.get('parentesco')

                if not all([matricula, visitante, nome, parentesco]):
                    flash('Todos os campos devem ser preenchidos', 'error')
                    return redirect(url_for('jumbo'))

                # NORMALIZAÇÃO DOS NOMES EM MAIÚSCULAS
                nome_normalizado = nome.upper().strip()
                visitante_normalizado = visitante.upper().strip()
                parentesco_normalizado = parentesco.upper().strip()

                existing_mongo = db.visita.find_one(
                    {
                        'matricula': matricula,
                        'visitante': visitante_normalizado,
                    }
                )

                nova_visita = {
                    'matricula': matricula,
                    'nome': nome_normalizado,  # Nome normalizado
                    'visitante': visitante_normalizado,  # Visitante normalizado
                    'parentesco': parentesco_normalizado,  # Parentesco normalizado
                    'data_visita': pd.Timestamp.now(),
                }

                df_visitas = pd.concat(
                    [df_visitas, pd.DataFrame([nova_visita])],
                    ignore_index=True,
                )

                if existing_mongo:
                    flash('Visita já existe no Banco de dados', 'info')
                else:
                    db.visita.insert_one(nova_visita)
                    flash(
                        'Visita registrada com sucesso no histórico permanente',
                        'success',
                    )

            elif 'remover' in request.form:
                index = int(request.form.get('index'))
                df_visitas = df_visitas.drop(index).reset_index(drop=True)
                flash(f'Visita removida da lista de {today}', 'info')

        return render_template(
            'jumbo.html', form=form, visitas=df_visitas.to_dict('records')
        )
    except Exception as e:
        print(f'Error: {e}')
        return str(e), 500


@app.route('/download_visitas_pdf')
def download_visitas_pdf():
    try:
        hoje = datetime.datetime.now().strftime('%d-%m-%Y')
        global df_visitas

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Create table data from DataFrame
        elements = []
        table_data = [['Matrícula', 'Nome', 'Visitante', 'Parentesco']]

        for _, row in df_visitas.iterrows():
            table_data.append(
                [
                    row['matricula'],
                    row['nome'],  # Já estará em maiúsculas
                    row['visitante'],  # Já estará em maiúsculas
                    row['parentesco'],  # Já estará em maiúsculas
                ]
            )

        # Create table
        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(table)

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=lista_visitas_{hoje}.pdf'
        )

        return response

    except Exception as e:
        print(f'Error generating PDF: {e}')
        flash('Erro ao gerar PDF. Por favor, verifique os logs.', 'error')
        return redirect(url_for('jumbo'))
