from flask import Blueprint, request, jsonify, session
from database import db
from user import User
from models.aposta import Aposta
from sorteio import Sorteio
from datetime import date, datetime, timedelta

sorteios_bp = Blueprint('sorteios', __name__)

@sorteios_bp.route('/atual', methods=['GET'])
def sorteio_atual():
    """Retorna informações do sorteio atual"""
    try:
        sorteio = Sorteio.get_sorteio_atual()
        
        return jsonify({
            'sorteio': sorteio.to_dict(),
            'estatisticas': sorteio.get_estatisticas()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sorteios_bp.route('/proximo', methods=['GET'])
def proximo_sorteio():
    """Retorna informações do próximo sorteio"""
    try:
        sorteio = Sorteio.get_proximo_sorteio()
        
        return jsonify({
            'sorteio': sorteio.to_dict(),
            'estatisticas': sorteio.get_estatisticas()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sorteios_bp.route('/historico', methods=['GET'])
def historico_sorteios():
    """Retorna o histórico de sorteios"""
    try:
        # Pega parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Busca sorteios finalizados
        sorteios_query = Sorteio.query.filter(
            Sorteio.status.in_(['sorteado', 'finalizado'])
        ).order_by(Sorteio.data_sorteio.desc())
        
        sorteios_paginados = sorteios_query.paginate(page=page, per_page=per_page, error_out=False)
        
        sorteios_list = []
        for sorteio in sorteios_paginados.items:
            sorteio_dict = sorteio.to_dict()
            
            # Adiciona informações dos ganhadores
            apostas_ganhadoras = [a for a in sorteio.apostas if a.status == 'ganhadora']
            sorteio_dict['total_ganhadores'] = len(apostas_ganhadoras)
            
            if apostas_ganhadoras:
                sorteio_dict['premio_por_ganhador'] = sorteio.premio_total / len(apostas_ganhadoras)
            else:
                sorteio_dict['premio_por_ganhador'] = 0
            
            sorteios_list.append(sorteio_dict)
        
        return jsonify({
            'sorteios': sorteios_list,
            'total': sorteios_paginados.total,
            'pages': sorteios_paginados.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sorteios_bp.route('/resultado/<int:sorteio_id>', methods=['GET'])
def resultado_sorteio(sorteio_id):
    """Retorna o resultado detalhado de um sorteio específico"""
    try:
        sorteio = Sorteio.query.get(sorteio_id)
        
        if not sorteio:
            return jsonify({'error': 'Sorteio não encontrado'}), 404
        
        if sorteio.status == 'aberto':
            return jsonify({'error': 'Sorteio ainda não foi realizado'}), 400
        
        sorteio_dict = sorteio.to_dict()
        
        # Adiciona informações dos ganhadores
        apostas_ganhadoras = [a for a in sorteio.apostas if a.status == 'ganhadora']
        ganhadores = []
        
        for aposta in apostas_ganhadoras:
            ganhadores.append({
                'usuario_nome': aposta.user.nome,
                'numeros_escolhidos': aposta.get_numeros_escolhidos(),
                'data_aposta': aposta.data_criacao.isoformat(),
                'premio_recebido': sorteio.premio_total / len(apostas_ganhadoras) if apostas_ganhadoras else 0
            })
        
        sorteio_dict['ganhadores'] = ganhadores
        sorteio_dict['total_ganhadores'] = len(ganhadores)
        
        return jsonify({'resultado': sorteio_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sorteios_bp.route('/realizar/<int:sorteio_id>', methods=['POST'])
def realizar_sorteio(sorteio_id):
    """Realiza um sorteio (apenas para admins)"""
    try:
        # Verificar se o usuário é admin
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores'}), 403
        
        sorteio = Sorteio.query.get(sorteio_id)
        if not sorteio:
            return jsonify({'error': 'Sorteio não encontrado'}), 404
        
        if sorteio.status != 'aberto':
            return jsonify({'error': 'Sorteio já foi realizado'}), 400
        
        # Realizar o sorteio
        if sorteio.realizar_sorteio():
            return jsonify({
                'message': 'Sorteio realizado com sucesso',
                'resultado': sorteio.to_dict(),
                'ganhadores': sorteio.verificar_ganhadores()
            }), 200
        else:
            return jsonify({'error': 'Erro ao realizar sorteio'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sorteios_bp.route('/estatisticas', methods=['GET'])
def estatisticas():
    """Retorna estatísticas gerais dos sorteios"""
    try:
        # Estatísticas gerais
        total_sorteios = Sorteio.query.filter(Sorteio.status != 'aberto').count()
        total_apostas = Aposta.query.count()
        total_arrecadado = db.session.query(db.func.sum(Sorteio.total_arrecadado)).scalar() or 0
        total_premiado = db.session.query(db.func.sum(Sorteio.premio_total)).scalar() or 0
        
        # Combinações mais sorteadas (últimos 30 sorteios)
        sorteios_recentes = Sorteio.query.filter(
            Sorteio.numeros_sorteados.isnot(None)
        ).order_by(Sorteio.data_sorteio.desc()).limit(30).all()
        
        combinacoes_sorteadas = {}
        for sorteio in sorteios_recentes:
            numeros = tuple(sorted(sorteio.get_numeros_sorteados()))
            combinacoes_sorteadas[numeros] = combinacoes_sorteadas.get(numeros, 0) + 1
        
        # Números individuais mais sorteados
        numeros_individuais = {}
        for sorteio in sorteios_recentes:
            for numero in sorteio.get_numeros_sorteados():
                numeros_individuais[numero] = numeros_individuais.get(numero, 0) + 1
        
        return jsonify({
            'estatisticas_gerais': {
                'total_sorteios': total_sorteios,
                'total_apostas': total_apostas,
                'total_arrecadado': total_arrecadado,
                'total_premiado': total_premiado,
                'taxa_premio': (total_premiado / total_arrecadado * 100) if total_arrecadado > 0 else 0
            },
            'combinacoes_mais_sorteadas': sorted(
                [{'numeros': list(nums), 'vezes': vezes} for nums, vezes in combinacoes_sorteadas.items()],
                key=lambda x: x['vezes'],
                reverse=True
            )[:10],
            'numeros_mais_sorteados': sorted(
                [{'numero': num, 'vezes': vezes} for num, vezes in numeros_individuais.items()],
                key=lambda x: x['vezes'],
                reverse=True
            )[:20]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

