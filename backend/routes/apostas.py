# C:\projetos_flutter\projeto-bilhetes\backend\routes\apostas.py

# --- Correção para resolver ModuleNotFoundError: No module named 'aposta' ---
# Esta seção adiciona o diretório pai ('backend') ao caminho de busca do Python
import sys
import os

# Obtém o caminho absoluto deste arquivo (routes\apostas.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Obtém o caminho do diretório pai (que é 'backend')
parent_dir = os.path.dirname(current_dir)

# Adiciona o diretório pai ao início do sys.path se ele ainda não estiver lá
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Agora podemos importar diretamente do arquivo 'aposta.py' que está no diretório 'backend'
# Como estamos adicionando o diretório 'backend' ao sys.path, o Python encontrará 'aposta.py'
# como um módulo.
from models.aposta import db, Modalidade, BilhetePredefinido, Premiacao, Aposta
# --- Fim da correção ---

from flask import Blueprint, jsonify, request
from datetime import datetime

apostas_bp = Blueprint('apostas', __name__)

# ... (restante do seu código original para as rotas) ...
# Mantenha todas as suas funções @apostas_bp.route(...) exatamente como estavam
# para não perder nenhuma funcionalidade.

@apostas_bp.route('/modalidades', methods=['GET'])
def get_modalidades():
    """Retorna todas as modalidades ativas"""
    try:
        modalidades = Modalidade.query.filter_by(ativo=True).all()
        return jsonify([modalidade.to_dict() for modalidade in modalidades])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/modalidades/<int:modalidade_id>/bilhetes', methods=['GET'])
def get_bilhetes_modalidade(modalidade_id):
    """Retorna os bilhetes pré-definidos de uma modalidade"""
    try:
        bilhetes = BilhetePredefinido.query.filter_by(
            modalidade_id=modalidade_id, 
            ativo=True
        ).all()
        return jsonify([bilhete.to_dict() for bilhete in bilhetes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/modalidades/<int:modalidade_id>/premiacoes', methods=['GET'])
def get_premiacoes_modalidade(modalidade_id):
    """Retorna as premiações de uma modalidade"""
    try:
        premiacoes = Premiacao.query.filter_by(modalidade_id=modalidade_id).all()
        return jsonify([premiacao.to_dict() for premiacao in premiacoes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/apostas', methods=['POST'])
def criar_aposta():
    """Cria uma nova aposta"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        modalidade_id = data.get('modalidade_id')
        bilhetes_selecionados = data.get('bilhetes_selecionados')
        valor_total = data.get('valor_total')
        
        if not all([modalidade_id, bilhetes_selecionados, valor_total]):
            return jsonify({'error': 'Dados obrigatórios faltando'}), 400
        
        # Verificar se a modalidade existe
        modalidade = Modalidade.query.get(modalidade_id)
        if not modalidade:
            return jsonify({'error': 'Modalidade não encontrada'}), 404
        
        # Criar a aposta
        aposta = Aposta(
            modalidade_id=modalidade_id,
            valor_total=valor_total
        )
        aposta.set_bilhetes_selecionados(bilhetes_selecionados)
        
        db.session.add(aposta)
        db.session.commit()
        
        return jsonify(aposta.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/apostas/<int:aposta_id>', methods=['GET'])
def get_aposta(aposta_id):
    """Retorna os detalhes de uma aposta específica"""
    try:
        aposta = Aposta.query.get(aposta_id)
        if not aposta:
            return jsonify({'error': 'Aposta não encontrada'}), 404
        
        return jsonify(aposta.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/apostas/<int:aposta_id>/comprovante/whatsapp', methods=['POST'])
def enviar_comprovante_whatsapp(aposta_id):
    """Simula o envio do comprovante via WhatsApp"""
    try:
        aposta = Aposta.query.get(aposta_id)
        if not aposta:
            return jsonify({'error': 'Aposta não encontrada'}), 404
        
        # Aqui seria implementada a integração com WhatsApp
        # Por enquanto, apenas retornamos sucesso
        return jsonify({
            'message': 'Comprovante enviado via WhatsApp com sucesso',
            'aposta_id': aposta_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/apostas/<int:aposta_id>/comprovante/imprimir', methods=['POST'])
def imprimir_comprovante(aposta_id):
    """Simula a impressão do comprovante"""
    try:
        aposta = Aposta.query.get(aposta_id)
        if not aposta:
            return jsonify({'error': 'Aposta não encontrada'}), 404
        
        # Aqui seria implementada a integração com impressora
        # Por enquanto, apenas retornamos sucesso
        return jsonify({
            'message': 'Comprovante enviado para impressão com sucesso',
            'aposta_id': aposta_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apostas_bp.route('/seed-data', methods=['POST'])
def seed_data():
    """Popula o banco de dados com dados iniciais"""
    try:
        # Limpar dados existentes
        db.session.query(Aposta).delete()
        db.session.query(Premiacao).delete()
        db.session.query(BilhetePredefinido).delete()
        db.session.query(Modalidade).delete()
        
        # Criar modalidades
        modalidades = [
            Modalidade(nome='2 pra 500', descricao='Escolha 2 números e concorra a R$ 500', cor='bg-blue-500'),
            Modalidade(nome='3 pra 1000', descricao='Escolha 3 números e concorra a R$ 1.000', cor='bg-green-500'),
            Modalidade(nome='5 pra 5000', descricao='Escolha 5 números e concorra a R$ 5.000', cor='bg-purple-500'),
            Modalidade(nome='Mega Sorte', descricao='Escolha 6 números e concorra a R$ 10.000', cor='bg-red-500')
        ]
        
        for modalidade in modalidades:
            db.session.add(modalidade)
        
        db.session.commit()
        
        # Criar bilhetes pré-definidos para a modalidade "2 pra 500"
        modalidade_2_pra_500 = Modalidade.query.filter_by(nome='2 pra 500').first()
        
        bilhetes_data = [
            [12, 34], [7, 21], [45, 18], [33, 9],
            [28, 41], [16, 52], [3, 37], [49, 25]
        ]
        
        for numeros in bilhetes_data:
            bilhete = BilhetePredefinido(
                modalidade_id=modalidade_2_pra_500.id,
                preco=5.00
            )
            bilhete.set_numeros(numeros)
            db.session.add(bilhete)
        
        # Criar premiações para a modalidade "2 pra 500"
        premiacoes_data = [
            ('1º Prêmio', 500.00),
            ('2º Prêmio', 100.00),
            ('3º Prêmio', 50.00)
        ]
        
        for posicao, valor in premiacoes_data: # Corrigido: estava 'premiacoes_' no seu código original
            premiacao = Premiacao(
                modalidade_id=modalidade_2_pra_500.id,
                posicao=posicao,
                valor=valor
            )
            db.session.add(premiacao)
        
        db.session.commit()
        
        return jsonify({'message': 'Dados iniciais criados com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
