from flask import Blueprint, request, jsonify, session
from modelos import Usuario
from sqlalchemy import or_
from werkzeug.security import check_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def get_usuario_logado():
    id_usuario = session.get('id_usuario')
    if not id_usuario:
        return None
    return Usuario.query.get(id_usuario)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'id_usuario' not in session:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado',
                'data': None
        }), 401

        return func(*args, **kwargs)
    return wrapper


@auth_bp.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()

    if not dados:
        return jsonify({
            "success": False,
            "message": "Dados inválidos",
            "data": None
        }), 400

    identificador = dados.get('identificador')
    senha = dados.get('senha')

    if not identificador or not senha:
        return jsonify({
            'success': False,
            'message': 'Necessário preencher todos os campos',
            'data': None
        }), 400

    usuario = Usuario.query.filter(
        or_(
            Usuario.email == identificador,
            Usuario.telefone == identificador
        )
    ).first()

    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({
            'success': False,
            'message': 'Usuário ou senha inválidos',
            'data': None
        }), 401

    session.clear()
    session['id_usuario'] = usuario.id_usuario
    session['nome'] = usuario.nome

    return jsonify({
        'success': True,
        'message': 'Login realizado com sucesso',
        'data': {
            'id_usuario': usuario.id_usuario,
            'nome': usuario.nome
        },
    }), 200

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso',
        'data': None                   
    }), 200

