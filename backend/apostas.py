from flask import Blueprint, request, jsonify, session
from src.models.database import db
from src.models.user import User
from src.models.aposta import Aposta
from src.models.sorteio import Sorteio
from datetime import date

apostas_bp = Blueprint('apostas', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@apostas_bp.route('/fazer-aposta', methods=['POST'])
def fazer_aposta():
    """Realiza uma nova aposta"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        
        if not data or 'numero' not in data:
            return jsonify({'error': 'Número da aposta é obrigatório'}), 400
        
        numero = data['numero']
        
        # Validação do número
        if not isinstance(numero, int) or numero < 1 or numero > 500:
            return jsonify({'error': 'Número deve estar entre 1 e 500'}), 400
        
        # Verifica se o usuário tem saldo suficiente
        valor_aposta = 2.0
        if user.saldo < valor_aposta:
            return jsonify({'error': 'Saldo insuficiente'}), 400
        
        # Pega o sorteio atual
        sorteio = Sorteio.get_sorteio_atual()
        
        if sorteio.status != 'aberto':
            return jsonify({'error': 'Sorteio não está aberto para apostas'}), 400
        
        # Verifica se o usuário já apostou neste número hoje
        aposta_existente = Aposta.query.filter_by(
            user_id=user.id,
            sorteio_id=sorteio.id,
            numero_escolhido=numero
        ).first()
        
        if aposta_existente:
            return jsonify({'error': 'Você já apostou neste número hoje'}), 400
        
        # Debita o saldo do usuário
        if not user.debitar_saldo(valor_aposta):
            return jsonify({'error': 'Erro ao debitar saldo'}), 500
        
        # Cria a aposta
        aposta = Aposta(
            user_id=user.id,
            sorteio_id=sorteio.id,
            numero_escolhido=numero,
            valor_aposta=valor_aposta
        )
        
        db.session.add(aposta)
        
        # Adiciona o valor ao total arrecadado do sorteio
        sorteio.adicionar_aposta(valor_aposta)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Aposta realizada com sucesso',
            'aposta': aposta.to_dict(),
            'saldo_restante': user.saldo
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/minhas-apostas', methods=['GET'])
def minhas_apostas():
    """Retorna as apostas do usuário logado"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Pega parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Busca as apostas do usuário
        apostas_query = Aposta.query.filter_by(user_id=user.id).order_by(Aposta.data_aposta.desc())
        apostas_paginadas = apostas_query.paginate(page=page, per_page=per_page, error_out=False)
        
        apostas_list = []
        for aposta in apostas_paginadas.items:
            aposta_dict = aposta.to_dict()
            aposta_dict['sorteio'] = aposta.sorteio.to_dict()
            apostas_list.append(aposta_dict)
        
        return jsonify({
            'apostas': apostas_list,
            'total': apostas_paginadas.total,
            'pages': apostas_paginadas.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/apostas-hoje', methods=['GET'])
def apostas_hoje():
    """Retorna as apostas do usuário para o sorteio de hoje"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Pega o sorteio de hoje
        sorteio = Sorteio.get_sorteio_atual()
        
        # Busca as apostas do usuário para hoje
        apostas = Aposta.query.filter_by(
            user_id=user.id,
            sorteio_id=sorteio.id
        ).order_by(Aposta.numero_escolhido).all()
        
        apostas_list = [aposta.to_dict() for aposta in apostas]
        
        return jsonify({
            'apostas': apostas_list,
            'sorteio': sorteio.to_dict(),
            'total_apostas': len(apostas_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/numeros-disponiveis', methods=['GET'])
def numeros_disponiveis():
    """Retorna os números disponíveis para aposta (que o usuário ainda não apostou hoje)"""
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Pega o sorteio de hoje
        sorteio = Sorteio.get_sorteio_atual()
        
        if sorteio.status != 'aberto':
            return jsonify({
                'numeros_disponiveis': [],
                'message': 'Sorteio não está aberto para apostas'
            }), 200
        
        # Busca os números que o usuário já apostou hoje
        apostas_hoje = Aposta.query.filter_by(
            user_id=user.id,
            sorteio_id=sorteio.id
        ).all()
        
        numeros_apostados = [aposta.numero_escolhido for aposta in apostas_hoje]
        
        # Gera lista de números disponíveis (1 a 500, exceto os já apostados)
        numeros_disponiveis = [num for num in range(1, 501) if num not in numeros_apostados]
        
        return jsonify({
            'numeros_disponiveis': numeros_disponiveis,
            'numeros_apostados': numeros_apostados,
            'total_disponiveis': len(numeros_disponiveis)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

