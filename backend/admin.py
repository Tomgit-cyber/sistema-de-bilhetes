from flask import Blueprint, request, jsonify, session
from src.models.database import db
from src.models.user import User
from src.models.sorteio import Sorteio
from src.services.scheduler import sorteio_scheduler
from datetime import date, datetime

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Verifica se o usuário é administrador (simplificado para demo)"""
    # Em uma implementação real, você teria um campo 'is_admin' no modelo User
    # Por enquanto, vamos usar uma verificação simples
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    # Para demo, vamos considerar que o primeiro usuário é admin
    if user and user.id == 1:
        return user
    return None

@admin_bp.route('/executar-sorteio', methods=['POST'])
def executar_sorteio_manual():
    """Executa um sorteio manualmente (apenas para admin)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Acesso negado - Apenas administradores'}), 403
        
        data = request.get_json()
        data_sorteio = None
        
        if data and 'data_sorteio' in data:
            try:
                data_sorteio = datetime.strptime(data['data_sorteio'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Executa o sorteio manual
        sucesso = sorteio_scheduler.executar_sorteio_manual(data_sorteio)
        
        if sucesso:
            return jsonify({'message': 'Sorteio executado com sucesso'}), 200
        else:
            return jsonify({'error': 'Erro ao executar sorteio'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/status-scheduler', methods=['GET'])
def status_scheduler():
    """Retorna o status do scheduler de sorteios"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Acesso negado - Apenas administradores'}), 403
        
        status = sorteio_scheduler.get_proximo_sorteio()
        
        return jsonify({
            'scheduler_status': status,
            'scheduler_running': sorteio_scheduler.scheduler.running
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parar-scheduler', methods=['POST'])
def parar_scheduler():
    """Para o scheduler de sorteios"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Acesso negado - Apenas administradores'}), 403
        
        sorteio_scheduler.parar_scheduler()
        
        return jsonify({'message': 'Scheduler parado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reiniciar-scheduler', methods=['POST'])
def reiniciar_scheduler():
    """Reinicia o scheduler de sorteios"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Acesso negado - Apenas administradores'}), 403
        
        sorteio_scheduler.reiniciar_scheduler()
        
        return jsonify({'message': 'Scheduler reiniciado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/estatisticas-admin', methods=['GET'])
def estatisticas_admin():
    """Retorna estatísticas detalhadas para administradores"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Acesso negado - Apenas administradores'}), 403
        
        # Estatísticas de usuários
        total_usuarios = User.query.count()
        usuarios_ativos = User.query.filter_by(ativo=True).count()
        
        # Estatísticas de sorteios
        total_sorteios = Sorteio.query.count()
        sorteios_finalizados = Sorteio.query.filter_by(status='finalizado').count()
        
        # Estatísticas financeiras
        from src.models.aposta import Aposta
        total_apostas = Aposta.query.count()
        total_arrecadado = db.session.query(db.func.sum(Sorteio.total_arrecadado)).scalar() or 0
        total_premiado = db.session.query(db.func.sum(Sorteio.premio_total)).scalar() or 0
        
        # Saldo total dos usuários
        saldo_total_usuarios = db.session.query(db.func.sum(User.saldo)).scalar() or 0
        
        return jsonify({
            'usuarios': {
                'total': total_usuarios,
                'ativos': usuarios_ativos,
                'saldo_total': saldo_total_usuarios
            },
            'sorteios': {
                'total': total_sorteios,
                'finalizados': sorteios_finalizados,
                'pendentes': total_sorteios - sorteios_finalizados
            },
            'financeiro': {
                'total_apostas': total_apostas,
                'total_arrecadado': total_arrecadado,
                'total_premiado': total_premiado,
                'lucro_casa': total_arrecadado - total_premiado,
                'margem_casa': ((total_arrecadado - total_premiado) / total_arrecadado * 100) if total_arrecadado > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Lista todos os usuários (apenas para admin)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Acesso negado - Apenas administradores'}), 403
        
        # Pega parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        usuarios_query = User.query.order_by(User.data_criacao.desc())
        usuarios_paginados = usuarios_query.paginate(page=page, per_page=per_page, error_out=False)
        
        usuarios_list = []
        for user in usuarios_paginados.items:
            user_dict = user.to_dict()
            # Remove informações sensíveis
            user_dict.pop('password_hash', None)
            usuarios_list.append(user_dict)
        
        return jsonify({
            'usuarios': usuarios_list,
            'total': usuarios_paginados.total,
            'pages': usuarios_paginados.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

