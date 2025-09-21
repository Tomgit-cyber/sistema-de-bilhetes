from database import db
from datetime import datetime, date
import random

class Sorteio(db.Model):
    __tablename__ = 'sorteios'

    id = db.Column(db.Integer, primary_key=True)
    data_sorteio = db.Column(db.Date, nullable=False, unique=True)
    numeros_sorteados = db.Column(db.String(20), nullable=True)  # "12,34" formato
    status = db.Column(db.String(50), default='aberto')  # 'aberto', 'sorteado', 'finalizado'
    total_arrecadado = db.Column(db.Float, default=0.0)
    premio_total = db.Column(db.Float, default=500.0)  # Prêmio fixo de R$ 500

    apostas = db.relationship('Aposta', backref='sorteio', lazy=True)

    def __init__(self, data_sorteio):
        self.data_sorteio = data_sorteio

    def to_dict(self):
        return {
            'id': self.id,
            'data_sorteio': self.data_sorteio.isoformat(),
            'numeros_sorteados': self.get_numeros_sorteados(),
            'status': self.status,
            'total_arrecadado': self.total_arrecadado,
            'premio_total': self.premio_total,
            'total_apostas': len(self.apostas)
        }

    def get_numeros_sorteados(self):
        """Retorna os números sorteados como lista"""
        if self.numeros_sorteados:
            return [int(x) for x in self.numeros_sorteados.split(',')]
        return []

    def set_numeros_sorteados(self, numeros_list):
        """Define os números sorteados a partir de uma lista"""
        if len(numeros_list) != 2:
            raise ValueError("Devem ser sorteados exatamente 2 números")
        self.numeros_sorteados = ','.join(map(str, sorted(numeros_list)))

    @classmethod
    def get_sorteio_atual(cls):
        """Retorna o sorteio do dia atual, criando se não existir"""
        hoje = date.today()
        sorteio = cls.query.filter_by(data_sorteio=hoje).first()
        if not sorteio:
            sorteio = cls(data_sorteio=hoje)
            db.session.add(sorteio)
            db.session.commit()
        return sorteio

    @classmethod
    def get_proximo_sorteio(cls):
        """Retorna o próximo sorteio (hoje se ainda não foi sorteado, senão amanhã)"""
        hoje = date.today()
        sorteio_hoje = cls.query.filter_by(data_sorteio=hoje).first()
        
        if not sorteio_hoje or sorteio_hoje.status == 'aberto':
            return cls.get_sorteio_atual()
        
        # Se já foi sorteado hoje, criar sorteio de amanhã
        from datetime import timedelta
        amanha = hoje + timedelta(days=1)
        sorteio_amanha = cls.query.filter_by(data_sorteio=amanha).first()
        if not sorteio_amanha:
            sorteio_amanha = cls(data_sorteio=amanha)
            db.session.add(sorteio_amanha)
            db.session.commit()
        return sorteio_amanha

    def realizar_sorteio(self):
        """Realiza o sorteio dos números"""
        if self.status == 'aberto':
            # Sorteia 2 números entre 1 e 60
            numeros = random.sample(range(1, 61), 2)
            self.set_numeros_sorteados(numeros)
            self.status = 'sorteado'
            db.session.commit()
            self.verificar_ganhadores()
            return True
        return False

    def verificar_ganhadores(self):
        """Verifica as apostas ganhadoras e atualiza status"""
        if self.status == 'sorteado' and self.numeros_sorteados:
            numeros_sorteados = self.get_numeros_sorteados()
            
            apostas_ganhadoras = []
            for aposta in self.apostas:
                numeros_aposta = aposta.get_numeros_escolhidos()
                if set(numeros_aposta) == set(numeros_sorteados):
                    aposta.status = 'ganhadora'
                    apostas_ganhadoras.append(aposta)
                else:
                    aposta.status = 'perdedora'
            
            # Se há ganhadores, divide o prêmio
            if apostas_ganhadoras:
                premio_por_ganhador = self.premio_total / len(apostas_ganhadoras)
                for aposta in apostas_ganhadoras:
                    aposta.user.adicionar_saldo(premio_por_ganhador)
            
            self.status = 'finalizado'
            db.session.commit()
            
            return len(apostas_ganhadoras)
        return 0

    def adicionar_aposta(self, aposta):
        """Adiciona uma aposta ao sorteio"""
        if self.status == 'aberto':
            self.apostas.append(aposta)
            self.total_arrecadado += aposta.valor_aposta
            db.session.commit()
            return True
        return False

    def get_estatisticas(self):
        """Retorna estatísticas do sorteio"""
        return {
            'total_apostas': len(self.apostas),
            'total_arrecadado': self.total_arrecadado,
            'premio_total': self.premio_total,
            'apostas_ganhadoras': len([a for a in self.apostas if a.status == 'ganhadora']),
            'status': self.status
        }

