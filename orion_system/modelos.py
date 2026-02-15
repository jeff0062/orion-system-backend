from datetime import date
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(15), nullable=False, unique=True)
    data_nascimento = db.Column(db.Date, nullable=False)
        
    def __repr__(self):
        return f"Usuario(id={self.id_usuario}, nome='{self.nome}', email='{self.email}')"


class CategoriaProduto(db.Model):
    __tablename__ = 'categoria_produto'
    
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria = db.Column(db.String(20), nullable=False)
    
    fk_id_usuario = db.Column(
    db.Integer,
    db.ForeignKey('usuario.id_usuario'),
    nullable=False
    )
    
    usuario = db.relationship('Usuario', backref='categorias')    
    produtos = db.relationship('Produtos', backref='categoria_produto', lazy=True)
    
    def __repr__(self):
        return f"CategoriaProduto(id={self.id_categoria}, categoria='{self.categoria}')"


class Produtos(db.Model):
    __tablename__ = 'produtos'
    
    id_produto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(30), nullable=False)
    descricao = db.Column(db.String(60))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    
    fk_id_usuario = db.Column(
    db.Integer,
    db.ForeignKey('usuario.id_usuario'),
    nullable=False
    )    

    usuario = db.relationship('Usuario', backref='produtos')
    
    fk_categoria_produto = db.Column(
        db.Integer,
        db.ForeignKey('categoria_produto.id_categoria')
    )


class EstoqueUsuario(db.Model):
    __tablename__ = 'estoque_usuario'
    
    id_estoque = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    fk_id_produto = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id_produto'),
        nullable=False
    )
    
    fk_id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id_usuario'),
        nullable=False
    )
    
    quantidade = db.Column(db.Integer, nullable=False)

    usuario = db.relationship(
        'Usuario',
        backref=db.backref('estoques', lazy=True),
        foreign_keys=[fk_id_usuario]
    )

    produto = db.relationship(
        'Produtos',
        backref=db.backref('estoques', lazy=True),
        foreign_keys=[fk_id_produto]
    )
   
    def __repr__(self):
        return (
            f"EstoqueUsuario(id={self.id_estoque}, usuario={self.fk_id_usuario}, "
            f"produto={self.fk_id_produto}, quantidade={self.quantidade})"
        )


class Movimentacao(db.Model):
    __tablename__ = 'movimentacao'
    
    id_movimentacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantidade = db.Column(db.Integer, nullable=False)
    data_e_hora = db.Column(db.DateTime, nullable=False)
    
    fk_id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id_usuario'),
        nullable=False
    )
    
    fk_id_produto = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id_produto'),
        nullable=False
    )
    
    usuario = db.relationship('Usuario', backref='movimentacoes', lazy=True)
    produto = db.relationship('Produtos', backref='movimentacoes', lazy=True)
    
    def __repr__(self):
        return (
            f"Movimentacao(id={self.id_movimentacao}, usuario={self.fk_id_usuario}, "
            f"produto={self.fk_id_produto}, quantidade={self.quantidade}, "
            f"data={self.data_e_hora})"
        )
