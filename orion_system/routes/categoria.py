from flask import Blueprint, jsonify, request
from modelos import db, CategoriaProduto, Produtos
from .auth import login_required, get_usuario_logado
from sqlalchemy import func

categoria_bp = Blueprint('categoria', __name__)

@categoria_bp.route('/api/categorias', methods=['POST'])
@login_required
def adicionar_categoria():
    usuario = get_usuario_logado()
    dados = request.get_json()

    if not dados or not dados.get('categoria'):
        return jsonify({
            'success': False,
            'message': 'Campo categoria é obrigatório',
            'data': None
        }), 400

    nome_categoria = dados['categoria'].strip()

    if not nome_categoria:
        return jsonify({
            'success': False,
            'message': 'Nome da categoria inválido',
            'data': None
        }), 400


    categoria_existente = CategoriaProduto.query.filter_by(
        categoria=nome_categoria,
        fk_id_usuario=usuario.id_usuario
    ).first()

    if categoria_existente:
        return jsonify({
            'success': False,
            'message': 'Categoria já existe para este usuário',
            'data': None
        }), 409

    nova_categoria = CategoriaProduto(
        categoria=nome_categoria,
        fk_id_usuario=usuario.id_usuario
    )

    db.session.add(nova_categoria)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Categoria criada com sucesso',
        'data': {
            'id_categoria': nova_categoria.id_categoria,
            'categoria': nova_categoria.categoria
        }
    }), 201

@categoria_bp.route('/api/categorias/<int:id_categoria>', methods=['PUT'])
@login_required
def atualizar_categoria(id_categoria):
    usuario = get_usuario_logado()
    dados = request.get_json()

    if not dados or not dados.get('categoria'):
        return jsonify({
            'success': False,
            'message': 'Campo categoria é obrigatório',
            'data': None
        }), 400

    nome_categoria = dados['categoria'].strip()

    if not nome_categoria:
        return jsonify({
            'success': False,
            'message': 'Nome da categoria inválido',
            'data': None
        }), 400

    categoria = CategoriaProduto.query.filter_by(
        id_categoria=id_categoria,
        fk_id_usuario=usuario.id_usuario
    ).first()

    if not categoria:
        return jsonify({
            'success': False,
            'message': 'Categoria não encontrada',
            'data': None
        }), 404

    categoria_duplicada = CategoriaProduto.query.filter_by(
        categoria=nome_categoria,
        fk_id_usuario=usuario.id_usuario
    ).first()

    if categoria_duplicada and categoria_duplicada.id_categoria != id_categoria:
        return jsonify({
            'success': False,
            'message': 'Já existe uma categoria com esse nome',
            'data': None
        }), 409

    categoria.categoria = nome_categoria
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Categoria atualizada com sucesso',
        'data': {
            'id_categoria': categoria.id_categoria,
            'categoria': categoria.categoria
        }
    }), 200

@categoria_bp.route('/api/categorias/<int:id_categoria>', methods=['DELETE'])
@login_required
def deletar_categoria(id_categoria):
    usuario = get_usuario_logado()   

    categoria = CategoriaProduto.query.filter_by(
        id_categoria=id_categoria,
        fk_id_usuario=usuario.id_usuario
    ).first()

    if not categoria:
        return jsonify({
            'success': False,
            'message': 'Categoria não encontrada',
            'data': None
        }), 404

    produtos_vinculados = Produtos.query.filter_by(
    fk_categoria_produto=categoria.id_categoria,
    fk_id_usuario=usuario.id_usuario
    ).first()

    if produtos_vinculados:
        return jsonify({
            'success': False,
            'message': 'Categoria possui produtos vinculados',
            'data': None
        }), 409

    db.session.delete(categoria)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Categoria removida com sucesso',
        'data': None
    }), 200

@categoria_bp.route('/api/categorias', methods=['GET'])
@login_required
def listar_categorias():
    usuario = get_usuario_logado()

    categorias = CategoriaProduto.query.filter_by(
        fk_id_usuario=usuario.id_usuario
    ).order_by(CategoriaProduto.categoria.asc()).all()

    return jsonify({
        'success': True,
        'message': 'Categorias listadas com sucesso',
        'data': [
            {
                'id_categoria': categoria.id_categoria,
                'categoria': categoria.categoria
            }
            for categoria in categorias
        ]
    }), 200


@categoria_bp.route('/api/categorias/resumo', methods=['GET'])
@login_required
def resumo_categorias():
    usuario = get_usuario_logado()

    resumo = (
        db.session.query(
            CategoriaProduto.id_categoria,
            CategoriaProduto.categoria,
            func.count(Produtos.id_produto).label('total_produtos')
        )
        .outerjoin(
            Produtos,
            (Produtos.fk_categoria_produto == CategoriaProduto.id_categoria) &
            (Produtos.fk_id_usuario == usuario.id_usuario)
        )
        .filter(CategoriaProduto.fk_id_usuario == usuario.id_usuario)
        .group_by(CategoriaProduto.id_categoria, CategoriaProduto.categoria)
        .order_by(CategoriaProduto.categoria.asc())
        .all()
    )

    return jsonify({
        'success': True,
        'message': 'Resumo de categorias gerado com sucesso',
        'data': [
            {
                'id_categoria': item.id_categoria,
                'categoria': item.categoria,
                'total_produtos': item.total_produtos
            }
            for item in resumo
        ]
    }), 200
