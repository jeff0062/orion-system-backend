-- =============================================================================
-- Schema: Orion System - Banco de Dados PostgreSQL ('orion')
-- Baseado nas definições de modelos.py com todos os relacionamentos preservados
-- =============================================================================

-- Remover tabelas existentes (ordem reversa de dependência)
DROP TABLE IF EXISTS movimentacao CASCADE;
DROP TABLE IF EXISTS estoque_usuario CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS categoria_produto CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

-- -----------------------------------------------------------------------------
-- Tabela: usuario
-- -----------------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nome VARCHAR(20) NOT NULL,
    email VARCHAR(30) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(15) NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL
);

-- -----------------------------------------------------------------------------
-- Tabela: categoria_produto
-- -----------------------------------------------------------------------------
CREATE TABLE categoria_produto (
    id_categoria SERIAL PRIMARY KEY,
    categoria VARCHAR(20) NOT NULL,
    fk_id_usuario INTEGER NOT NULL,
    CONSTRAINT fk_categoria_usuario
        FOREIGN KEY (fk_id_usuario) 
        REFERENCES usuario (id_usuario) 
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Tabela: produtos
-- -----------------------------------------------------------------------------
CREATE TABLE produtos (
    id_produto SERIAL PRIMARY KEY,
    nome VARCHAR(30) NOT NULL,
    descricao VARCHAR(60),
    preco NUMERIC(10, 2) NOT NULL,
    fk_id_usuario INTEGER NOT NULL,
    fk_categoria_produto INTEGER,
    CONSTRAINT fk_produto_usuario
        FOREIGN KEY (fk_id_usuario) 
        REFERENCES usuario (id_usuario) 
        ON DELETE CASCADE,
    CONSTRAINT fk_produto_categoria
        FOREIGN KEY (fk_categoria_produto) 
        REFERENCES categoria_produto (id_categoria) 
        ON DELETE SET NULL
);

-- -----------------------------------------------------------------------------
-- Tabela: estoque_usuario
-- -----------------------------------------------------------------------------
CREATE TABLE estoque_usuario (
    id_estoque SERIAL PRIMARY KEY,
    fk_id_produto INTEGER NOT NULL,
    fk_id_usuario INTEGER NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT fk_estoque_produto
        FOREIGN KEY (fk_id_produto) 
        REFERENCES produtos (id_produto) 
        ON DELETE CASCADE,
    CONSTRAINT fk_estoque_usuario
        FOREIGN KEY (fk_id_usuario) 
        REFERENCES usuario (id_usuario) 
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Tabela: movimentacao
-- -----------------------------------------------------------------------------
CREATE TABLE movimentacao (
    id_movimentacao SERIAL PRIMARY KEY,
    quantidade INTEGER NOT NULL,
    data_e_hora TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fk_id_usuario INTEGER NOT NULL,
    fk_id_produto INTEGER NOT NULL,
    CONSTRAINT fk_movimentacao_usuario
        FOREIGN KEY (fk_id_usuario) 
        REFERENCES usuario (id_usuario) 
        ON DELETE CASCADE,
    CONSTRAINT fk_movimentacao_produto
        FOREIGN KEY (fk_id_produto) 
        REFERENCES produtos (id_produto) 
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Índices para otimização de consultas e junções frequentes
-- -----------------------------------------------------------------------------
CREATE INDEX idx_categoria_usuario ON categoria_produto (fk_id_usuario);
CREATE INDEX idx_produtos_usuario ON produtos (fk_id_usuario);
CREATE INDEX idx_produtos_categoria ON produtos (fk_categoria_produto);
CREATE INDEX idx_estoque_usuario ON estoque_usuario (fk_id_usuario);
CREATE INDEX idx_estoque_produto ON estoque_usuario (fk_id_produto);
CREATE INDEX idx_movimentacao_usuario ON movimentacao (fk_id_usuario);
CREATE INDEX idx_movimentacao_produto ON movimentacao (fk_id_produto);
