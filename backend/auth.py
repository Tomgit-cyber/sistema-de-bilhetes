from flask import Blueprint, request, jsonify, session
from src.models.database import db
from src.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data or not all(k in data for k in ('nome', 'email', 'telefone', 'password')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verifica se o email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Cria o novo usuário
        user = User(
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            password=data['password']
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Salva o usuário na sessão
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Faz login do usuário"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('email', 'password')):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        if not user.ativo:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Salva o usuário na sessão
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Faz logout do usuário"""
    session.pop('user_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Retorna os dados do usuário logado"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

