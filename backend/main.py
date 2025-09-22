import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.database import db, init_db
from src.models.user import User
from src.models.aposta import Aposta
from src.models.sorteio import Sorteio

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configuração CORS para permitir requisições do frontend
CORS(app, origins=['*'], supports_credentials=True)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados
init_db(app)

# Importa e registra as rotas
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.apostas import apostas_bp
from src.routes.sorteios import sorteios_bp
from src.routes.admin import admin_bp

# Importa e inicializa o scheduler
from src.services.scheduler import sorteio_scheduler

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(apostas_bp, url_prefix='/api/apostas')
app.register_blueprint(sorteios_bp, url_prefix='/api/sorteios')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Inicializa o scheduler de sorteios
sorteio_scheduler.init_app(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
