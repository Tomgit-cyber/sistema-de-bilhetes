from flask import Blueprint, request, jsonify, session
from src.models.database import db
from src.models.user import User

user_bp = Blueprint('user', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@user_bp.route('/perfil', methods=['GET'])
def get_perfil():
    """Retorna o perfil do usuário logado"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/perfil', methods=['PUT'])
def update_perfil():
    """Atualiza o perfil do usuário logado"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Atualiza campos permitidos
        if 'nome' in data:
            user.nome = data['nome']
        
        if 'telefone' in data:
            user.telefone = data['telefone']
        
        # Verifica se o email foi alterado e se já existe
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email já está em uso'}), 400
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/alterar-senha', methods=['PUT'])
def alterar_senha():
    """Altera a senha do usuário logado"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ('senha_atual', 'nova_senha')):
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        
        # Verifica a senha atual
        if not user.check_password(data['senha_atual']):
            return jsonify({'error': 'Senha atual incorreta'}), 400
        
        # Atualiza a senha
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(data['nova_senha'])
        
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/saldo', methods=['GET'])
def get_saldo():
    """Retorna o saldo atual do usuário"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        return jsonify({'saldo': user.saldo}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/adicionar-saldo', methods=['POST'])
def adicionar_saldo():
    """Adiciona saldo à conta do usuário (simulação de pagamento)"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        
        if not data or 'valor' not in data:
            return jsonify({'error': 'Valor é obrigatório'}), 400
        
        valor = data['valor']
        
        if not isinstance(valor, (int, float)) or valor <= 0:
            return jsonify({'error': 'Valor deve ser positivo'}), 400
        
        # Adiciona o saldo
        user.adicionar_saldo(valor)
        
        return jsonify({
            'message': 'Saldo adicionado com sucesso',
            'saldo_atual': user.saldo
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/historico-transacoes', methods=['GET'])
def historico_transacoes():
    """Retorna o histórico de transações do usuário (apostas)"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Pega parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Busca as apostas do usuário (que são as transações)
        from src.models.aposta import Aposta
        apostas_query = Aposta.query.filter_by(user_id=user.id).order_by(Aposta.data_aposta.desc())
        apostas_paginadas = apostas_query.paginate(page=page, per_page=per_page, error_out=False)
        
        transacoes = []
        for aposta in apostas_paginadas.items:
            transacao = {
                'id': aposta.id,
                'tipo': 'aposta',
                'valor': -aposta.valor_aposta,  # Negativo porque é débito
                'descricao': f'Aposta no número {aposta.numero_escolhido}',
                'data': aposta.data_aposta.isoformat(),
                'status': aposta.status,
                'sorteio_data': aposta.sorteio.data_sorteio.isoformat()
            }
            
            # Se a aposta foi ganhadora, adiciona o prêmio como transação separada
            if aposta.status == 'ganhadora':
                apostas_ganhadoras = aposta.sorteio.get_apostas_ganhadoras()
                if apostas_ganhadoras:
                    premio = aposta.sorteio.premio_total / len(apostas_ganhadoras)
                    transacao['premio'] = premio
            
            transacoes.append(transacao)
        
        return jsonify({
            'transacoes': transacoes,
            'total': apostas_paginadas.total,
            'pages': apostas_paginadas.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

