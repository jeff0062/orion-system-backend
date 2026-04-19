from flask import Flask
from flask_cors import CORS

from modelos import db
from routes.index import index_bp
from routes.estoque import estoque_bp 
from routes.usuario import usuarios_bp
from routes.categoria import categoria_bp
from routes.auth import auth_bp

app = Flask (__name__)

app.secret_key = 'hebert'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  

CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/orion'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db.init_app(app)

app.register_blueprint(index_bp)
app.register_blueprint(estoque_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(categoria_bp)
app.register_blueprint(auth_bp)
    
@app.route('/rotas')
def listar_rotas():
    return '<br>'.join(str(r) for r in app.url_map.iter_rules())

if __name__ == '__main__':
    app.run(debug=True, port=5000,)    