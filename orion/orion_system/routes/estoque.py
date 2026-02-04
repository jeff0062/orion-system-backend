from flask import Blueprint, jsonify, request
from modelos import db, EstoqueUsuario, Produtos, CategoriaProduto
from .auth import login_required, get_usuario_logado

estoque_bp = Blueprint('estoque', __name__)

@estoque_bp.route('/api/estoque', methods=['GET'])
@login_required
def listar_estoque():
    usuario = get_usuario_logado()
    
    itens = EstoqueUsuario.query.filter_by(
        fk_id_usuario=usuario.id_usuario
    ).all()
    
    resultado = []

    for item in itens:
        produto = item.produto
        categoria = CategoriaProduto.query.get(produto.fk_categoria_produto)

        resultado.append({
            'id_estoque': item.id_estoque,
            'nome': produto.nome,
            'categoria': produto.categoria_produto.categoria if produto.categoria_produto else None,
            'quantidade': item.quantidade,
            'preco': float(produto.preco),            
        })

    return jsonify({
        'success': True,
        'message':'Estoque listado com sucesso',
        'data': resultado
    }), 200

@estoque_bp.route('/api/estoque/<int:id_estoque>', methods=['DELETE'])
@login_required
def delete_item(id_estoque):
    usuario = get_usuario_logado()

    item = EstoqueUsuario.query.filter_by(
        id_estoque=id_estoque,
        fk_id_usuario=usuario.id_usuario
    ).first()

    if not item:
        return jsonify({
            'success': False,
            'message': 'item não encontrado',
            'data': None
        }), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({
            'success':True,
            'message':'Item removido com sucesso',
            'data':None
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            'success':False,
            'message':'Erro ao remover item',
            'data':None
        }), 500

@estoque_bp.route('/api/estoque', methods=['POST'])
@login_required
def adicionar_item_estoque():
    usuario = get_usuario_logado()
    dados = request.json

    if not dados:
        return jsonify({
            'success':False,
            'message':'Dados da requisição não enviados',
            'data':None
        }), 400

    campos_obrigatorios = ['nome', 'preco', 'quantidade', 'id_categoria']
    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] in [None, '']:
            return jsonify({
                'success':False,
                'message': f'Campo "{campo}" é obrigatório',
                'data':None
            }), 400       
    
    if not dados['nome'].strip():
        return jsonify({
            'success':False,
            'message':'Nome do produto inválido',
            'data': None
        }), 400

    try:
        preco = float(dados['preco'])
        quantidade = int(dados['quantidade'])
    except (ValueError, TypeError):
        return jsonify({
            'success':False,
            'message':'Preço ou quantidade inválidos',
            'data': None
        }), 400

    if preco < 0 or quantidade < 0:
        return jsonify({
            'success':False,
            'message':'Preço ou quantidade inválidos',
            'data':None
        }), 400

    try:
        id_categoria = int(dados['id_categoria'])
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'message':'Categoria inválida',
            'data':None
        }), 400

    categoria = CategoriaProduto.query.filter_by(
        id_categoria=id_categoria,
        fk_id_usuario=usuario.id_usuario
    ).first()
    
    if not categoria:
        return jsonify({
            'success':False,    
            'message':'Categoria não encontrada',
            'data':None
        }), 404

    produto = Produtos.query.filter_by(
        nome=dados['nome'].strip(),
        fk_categoria_produto=dados['id_categoria'],
        fk_id_usuario=usuario.id_usuario
    ).first()
    
    if produto:
        return jsonify({
            'success': False,
            'message': 'Produto já existe nesta categoria',
            'data': None
        }), 409

    produto = Produtos(
        nome=dados['nome'],
        preco=preco,
        fk_categoria_produto=dados['id_categoria'],
        fk_id_usuario=usuario.id_usuario
    )
    db.session.add(produto)
    db.session.flush()

    estoque = EstoqueUsuario.query.filter_by(
        fk_id_usuario=usuario.id_usuario,
        fk_id_produto=produto.id_produto
    ).first()

    if estoque:
        estoque.quantidade += quantidade
    else:
        estoque = EstoqueUsuario(
            fk_id_usuario=usuario.id_usuario,
            fk_id_produto=produto.id_produto,
            quantidade=quantidade
        )
    db.session.add(estoque)
    db.session.commit()

    return jsonify({
        'success':True,
        'message': 'Produto adicionado ao estoque',
        'data':{
            'produto': {
                'nome': produto.nome,
                'categoria': categoria.categoria,
                'quantidade': estoque.quantidade,
                'preco': float(produto.preco)
            }    
        }
    }), 201

@estoque_bp.route('/api/estoque/<int:id_estoque>', methods=['PUT'])
@login_required
def atualizar_item_estoque(id_estoque):
    usuario = get_usuario_logado()
    dados = request.json
    
    if not dados:
        return jsonify({
            'success':False,    
            'message':'Dados da requisição não enviados',
            'data': None
        }), 400

    estoque = EstoqueUsuario.query.filter_by(
        id_estoque=id_estoque,
        fk_id_usuario=usuario.id_usuario
    ).first()

    if not estoque:
        return jsonify({
            'success':False,    
            'message':'Item de estoque não encontrado',
            'data':None
        }), 404

    produto = estoque.produto

    if 'quantidade' in dados:
        try:
            quantidade = int(dados['quantidade'])
        except (ValueError, TypeError):
            return jsonify({
                'success':False,    
                'message':'Quantidade inválida',
                'data':None
            }), 400

        if quantidade < 0:
            return jsonify({
                'success': False,
                'message':'Quantidade inválida',
                'data': None
            }), 400

        estoque.quantidade = quantidade


    if 'nome' in dados:
        if not isinstance(dados['nome'], str) or not dados['nome'].strip():
            return jsonify({
                'success':False,
                'message':'Nome inválido',
                'data':None
            }), 400

        produto.nome = dados['nome'].strip()

    if 'preco' in dados:
        try:
            preco = float(dados['preco'])
        except (ValueError, TypeError):
            return jsonify({
                'success':False,
                'message':'Preço inválido',
                'data':None
            }), 400
                
        if preco < 0:
            return jsonify({
                'success':False,
                'message':'Preço inválido',
                'data':None
            }), 400

        produto.preco = preco

    if 'id_categoria' in dados:
        try:
            id_categoria = int(dados['id_categoria'])
        except (ValueError, TypeError):
            return jsonify({
                'success':False,
                'message':'Categoria inválida',
                'data':None
            }), 400

        categoria = CategoriaProduto.query.filter_by(
            id_categoria=id_categoria,
            fk_id_usuario=usuario.id_usuario
        ).first()   

        if not categoria:
            return jsonify({
                'success':False,
                'message':'Categoria não encontrada',
                'data':None
            }), 404

        produto.id_categoria = id_categoria

    db.session.commit()
    
    categoria_atual = CategoriaProduto.query.get(produto.id_categoria)

    return jsonify({
        'success': True,
        'message': 'Item atualizado com sucesso',
        'data':{
            'produto': {
                'nome': produto.nome,
                'preco': float(produto.preco),
                'categoria': categoria_atual.categoria if categoria_atual else None,
                'quantidade': estoque.quantidade
            }   
        }
    }), 200
