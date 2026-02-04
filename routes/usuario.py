from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
from modelos import db, Usuario
from datetime import datetime
from .auth import login_required
 
usuarios_bp = Blueprint ('usuarios',__name__)

@usuarios_bp.route('/api/usuarios', methods=['POST'])
def adicionar_usuario():
    dados = request.json
    
    if not dados:
        return jsonify({
            'success':False,    
            'message':'Dados não enviados',
            'data':None
        }), 400

    campos_obrigatorios = [
        'nome', 'email', 'senha', 'telefone', 'data_nascimento'
    ]

    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo]:
            return jsonify({
                'success': False,
                'message':f'Campo "{campo}" é obrigatório',
                'data':None
            }), 400

    usuario_existente = Usuario.query.filter_by(
        email=dados['email']
    ).first()

    if usuario_existente:
        return jsonify({
            'success':False,
            'message':'Email já cadastrado',
            'data':None
        }), 409

    novo_usuario = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        senha=generate_password_hash(dados['senha']),
        telefone=dados['telefone'],
        data_nascimento=datetime.strptime(
            dados['data_nascimento'], '%Y-%m-%d'
        ).date()
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({
        'success':True,
        'message': 'Usuário criado com sucesso',
        'data':None
    }), 201

@usuarios_bp.route('/api/usuarios/me', methods=['PUT'])
@login_required
def atualizar_usuario(id_usuario):
    dados = request.json
    
    if not dados:
        return jsonify({
            'success': False,    
            'message': 'O campo nao pode ficar vazio.',
            'data': None
        }), 400

    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({
            'success': False,
            'message':'Usuário não encontrado',
            'data':None        
        }), 404
    
    if usuario.id_usuario != session['usuario_id']:
        return jsonify({
            'success': False,    
            'message':'Acesso não autorizado',
            'data':None
        }), 403

    if 'email' in dados:
        email_existente = Usuario.query.filter(
            Usuario.email == dados['email'],
            Usuario.id_usuario != id_usuario
        ).first()

        if email_existente:
            return jsonify({
                'success': False,
                'message':'Email já cadastrado',
                'data': None
            }), 409

        usuario.email = dados['email']

    if 'telefone' in dados:
        telefone_existente = Usuario.query.filter(
            Usuario.telefone == dados['telefone'],
            Usuario.id_usuario != id_usuario
        ).first()

        if telefone_existente:
            return jsonify({
                'success': False,    
                'message':'Telefone já cadastrado',
                'data': None
            }), 409

        usuario.telefone = dados['telefone']

    if 'nome' in dados:
        usuario.nome = dados['nome']

    if 'senha' in dados:
        usuario.senha = generate_password_hash(dados['senha'])

    if 'data_nascimento' in dados:
        usuario.data_nascimento = datetime.strptime(
            dados['data_nascimento'], '%Y-%m-%d'
        ).date()

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Usuário atualizado com sucesso',
        'data': None
    }), 200

@usuarios_bp.route('/api/usuarios/me', methods=['GET'])
@login_required
def usuario_me():
    id_usuario = session.get('id_usuario')

    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({
            'success': False,
            'message':'Usuário não encontrado',
            'data': None
        }), 404

    return jsonify({
        'success': True,
        'message':'Usuario encontrado com sucesso',
        'data':{
            'id_usuario': usuario.id_usuario,
            'nome': usuario.nome,
            'email': usuario.email,
            'telefone': usuario.telefone,
            'data_nascimento': usuario.data_nascimento.strftime('%Y-%m-%d')
        }
        
    }), 200
    
    
