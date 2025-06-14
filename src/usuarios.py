from flask import request, jsonify, render_template, redirect, url_for, flash
from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash
from main import app
from modelos import User, UserSchema, UserPublic
from sqlite import get_session


def criar_usuario():
    session = get_session()
    try:
        # Verifica se é uma requisição JSON (API) ou form (HTML)
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password')
            }
        
        if not data:
            if request.is_json:
                return jsonify({'error': 'Dados são obrigatórios'}), 400
            else:
                flash('Dados são obrigatórios', 'error')
                return redirect(url_for('criar_usuario_form'))
        
        # Valida campos obrigatórios
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                error_msg = f'Campo {field} é obrigatório'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('criar_usuario_form'))
        
        # Verifica se email ou username já existem
        existing_user = session.scalar(
            select(User).where(
                (User.email == data['email']) | (User.username == data['username'])
            )
        )
        
        if existing_user:
            error_msg = 'Email ou Nome de usuário já existe'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return redirect(url_for('criar_usuario_form'))
        
        # Cria o usuário com senha hasheada
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Retorna resposta baseada no tipo de requisição
        if request.is_json:
            return jsonify({
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }), 201
        else:
            flash(f'Usuário {new_user.username} criado com sucesso!', 'success')
            return redirect(url_for('criar_usuario_form'))
    
    except Exception as e:
        session.rollback()
        error_msg = f'Erro interno do servidor: {str(e)}'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('criar_usuario_form'))
    
    finally:
        session.close()