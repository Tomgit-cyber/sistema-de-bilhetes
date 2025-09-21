# C:\projetos_flutter\projeto-bilhetes\backend\main.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager

# Importações corrigidas com base na estrutura de pastas
# database.py está na mesma pasta que main.py
from database import db

# user.py está na mesma pasta que main.py
from user import User

# apostas.py está na subpasta 'routes', então importamos o módulo
from routes import apostas

# sorteios.py está na mesma pasta que main.py
import sorteios

# admin.py está na subpasta 'routes', então importamos o módulo
from routes import admin

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui' # Substitua por uma chave segura
# Usar um caminho absoluto ou relativo mais robusto para o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'bilhetes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configura CORS para permitir requisições do frontend React
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Inicializa o LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Substitua 'login' pela função de view de login real se for diferente

@login_manager.user_loader
def load_user(user_id):
    # Assumindo que User.query.get é o método correto do SQLAlchemy
    return User.query.get(int(user_id))

# Inicializa o banco de dados com o app
db.init_app(app)

# Registra os blueprints das rotas
# Certifique-se de que os blueprints se chamam 'apostas_bp', 'sorteios_bp', 'admin_bp'
# e que foram criados nos respectivos arquivos (.py)
# Acessamos o blueprint através do módulo importado
app.register_blueprint(apostas.apostas_bp, url_prefix='/api/apostas')
app.register_blueprint(sorteios.sorteios_bp, url_prefix='/api/sorteios')
app.register_blueprint(admin.admin_bp, url_prefix='/api/admin')

# Servir os arquivos estáticos do frontend (React)
# Esta parte pode precisar de ajuste dependendo de como o frontend é servido
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Verifica se o arquivo solicitado existe no diretório 'frontend/build'
    # (assumindo que o React foi compilado para essa pasta)
    # Ajuste o caminho relativo conforme a estrutura real do seu projeto
    frontend_folder = os.path.join(app.root_path, '..', 'frontend', 'build')
    if path != "" and os.path.exists(os.path.join(frontend_folder, path)):
        return send_from_directory(frontend_folder, path)
    else:
        # Se não for um arquivo específico, serve o index.html (para SPA)
        index_path = os.path.join(frontend_folder, 'index.html')
        if os.path.exists(index_path):
             return send_from_directory(frontend_folder, 'index.html')
        else:
             # Se index.html não for encontrado, retorne um erro ou uma página padrão
             return "Frontend build not found. Please run 'npm run build' in the frontend directory.", 404

# Cria as tabelas do banco de dados (se não existirem)
# Esta função é chamada imediatamente após a inicialização do app
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Inicia o servidor Flask em modo debug na porta 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
