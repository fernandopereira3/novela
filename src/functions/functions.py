from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class PesquisaForm(FlaskForm):
    matricula = StringField('Matrícula')
    nome = StringField('Nome')
    garrafas = StringField('Garrafas')
    homens = StringField('Homens')
    mulheres = StringField('Mulheres')
    criancas = StringField('Crianças')
    pesquisar = SubmitField('PESQUISAR')