from flask import Blueprint, request, jsonify, session
from src.models.database import db
from src.models.user import User
from src.models.aposta import Aposta
from src.models.sorteio import Sorteio
from datetime import date, datetime, timedelta

sorteios_bp = Blueprint('sorteios', __name__)

@sorteios_bp.route('/sorteio-atual', methods=['GET'])
def sorteio_atual():
    """Retorna informações do sorteio atual"""
    try:
        sorteio = Sorteio.get_sorteio_atual()
        
        # Conta total de apostas
        total_apostas = len(sorteio.apostas)
        
        # Conta apostas por número (para estatísticas)
        apostas_por_numero = {}
        for aposta in sorteio.apostas:
            num = aposta.numero_escolhido
            apostas_por_numero[num] = apostas_por_numero.get(num, 0) + 1
        
        sorteio_dict = sorteio.to_dict()
        sorteio_dict['apostas_por_numero'] = apostas_por_numero
        sorteio_dict['numeros_mais_apostados'] = sorted(
            apostas_por_numero.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]  # Top 10 números mais apostados
        
        return jsonify({
            'sorteio': sorteio_dict,
            'total_apostas': total_apostas
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
            apostas_ganhadoras = sorteio.get_apostas_ganhadoras()
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
        apostas_ganhadoras = sorteio.get_apostas_ganhadoras()
        ganhadores = []
        
        for aposta in apostas_ganhadoras:
            ganhadores.append({
                'usuario_nome': aposta.usuario.nome,
                'numero_escolhido': aposta.numero_escolhido,
                'data_aposta': aposta.data_aposta.isoformat(),
                'premio_recebido': sorteio.premio_total / len(apostas_ganhadoras) if apostas_ganhadoras else 0
            })
        
        sorteio_dict['ganhadores'] = ganhadores
        sorteio_dict['total_ganhadores'] = len(ganhadores)
        
        return jsonify({'resultado': sorteio_dict}), 200
        
    except Exception as e:
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
        
        # Números mais sorteados
        numeros_sorteados = db.session.query(
            Sorteio.numero_sorteado,
            db.func.count(Sorteio.numero_sorteado).label('vezes')
        ).filter(
            Sorteio.numero_sorteado.isnot(None)
        ).group_by(
            Sorteio.numero_sorteado
        ).order_by(
            db.func.count(Sorteio.numero_sorteado).desc()
        ).limit(10).all()
        
        # Números mais apostados (histórico)
        numeros_apostados = db.session.query(
            Aposta.numero_escolhido,
            db.func.count(Aposta.numero_escolhido).label('vezes')
        ).group_by(
            Aposta.numero_escolhido
        ).order_by(
            db.func.count(Aposta.numero_escolhido).desc()
        ).limit(10).all()
        
        return jsonify({
            'estatisticas_gerais': {
                'total_sorteios': total_sorteios,
                'total_apostas': total_apostas,
                'total_arrecadado': total_arrecadado,
                'total_premiado': total_premiado,
                'taxa_premio': (total_premiado / total_arrecadado * 100) if total_arrecadado > 0 else 0
            },
            'numeros_mais_sorteados': [
                {'numero': num, 'vezes': vezes} for num, vezes in numeros_sorteados
            ],
            'numeros_mais_apostados': [
                {'numero': num, 'vezes': vezes} for num, vezes in numeros_apostados
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

