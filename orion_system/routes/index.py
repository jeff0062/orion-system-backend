from flask import Blueprint, render_template

index_bp = Blueprint('index',__name__)


@index_bp.route('/')
def homepage ():
    return render_template('index.html')


@index_bp.route('/dashboard')
def dashboard():
    return render_template('stock_dashboard.html')

@index_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')
