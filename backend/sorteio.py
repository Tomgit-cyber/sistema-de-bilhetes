from .database import db
from datetime import datetime, date
import random

class Sorteio(db.Model):
    """Model para sorteios diários do sistema"""
    __tablename__ = 'sorteios'
    
    id = db.Column(db.Integer, primary_key=True)
    data_sorteio = db.Column(db.Date, nullable=False, unique=True)
    numero_sorteado = db.Column(db.Integer, nullable=True)  # Null até o sorteio acontecer
    total_arrecadado = db.Column(db.Float, default=0.0)
    premio_total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='aberto')  # aberto, sorteado, finalizado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_sorteio_realizado = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    apostas = db.relationship('Aposta', backref='sorteio', lazy=True)
    
    def __init__(self, data_sorteio=None):
        if data_sorteio is None:
            data_sorteio = date.today()
        self.data_sorteio = data_sorteio
    
    def realizar_sorteio(self):
        """Realiza o sorteio e define o número ganhador"""
        if self.status != 'aberto':
            return False
        
        # Sorteia um número de 1 a 500
        self.numero_sorteado = random.randint(1, 500)
        self.status = 'sorteado'
        self.data_sorteio_realizado = datetime.utcnow()
        
        # Calcula o prêmio (90% do total arrecadado)
        self.premio_total = self.total_arrecadado * 0.9
        
        db.session.commit()
        return True
    
    def adicionar_aposta(self, valor_aposta):
        """Adiciona valor de uma aposta ao total arrecadado"""
        self.total_arrecadado += valor_aposta
        db.session.commit()
    
    def get_apostas_ganhadoras(self):
        """Retorna as apostas ganhadoras deste sorteio"""
        if self.numero_sorteado is None:
            return []
        
        from .aposta import Aposta
        return Aposta.query.filter_by(
            sorteio_id=self.id,
            numero_escolhido=self.numero_sorteado
        ).all()
    
    def finalizar_sorteio(self):
        """Finaliza o sorteio e distribui os prêmios"""
        if self.status != 'sorteado':
            return False
        
        apostas_ganhadoras = self.get_apostas_ganhadoras()
        
        if apostas_ganhadoras:
            # Divide o prêmio entre os ganhadores
            premio_por_ganhador = self.premio_total / len(apostas_ganhadoras)
            
            for aposta in apostas_ganhadoras:
                aposta.status = 'ganhadora'
                # Adiciona o prêmio ao saldo do usuário
                aposta.usuario.adicionar_saldo(premio_por_ganhador)
        
        # Marca todas as outras apostas como perdedoras
        from .aposta import Aposta
        apostas_perdedoras = Aposta.query.filter(
            Aposta.sorteio_id == self.id,
            Aposta.numero_escolhido != self.numero_sorteado
        ).all()
        
        for aposta in apostas_perdedoras:
            aposta.status = 'perdedora'
        
        self.status = 'finalizado'
        db.session.commit()
        return True
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'data_sorteio': self.data_sorteio.isoformat(),
            'numero_sorteado': self.numero_sorteado,
            'total_arrecadado': self.total_arrecadado,
            'premio_total': self.premio_total,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat(),
            'data_sorteio_realizado': self.data_sorteio_realizado.isoformat() if self.data_sorteio_realizado else None,
            'total_apostas': len(self.apostas)
        }
    
    @staticmethod
    def get_sorteio_atual():
        """Retorna o sorteio do dia atual"""
        hoje = date.today()
        sorteio = Sorteio.query.filter_by(data_sorteio=hoje).first()
        
        if not sorteio:
            # Cria um novo sorteio para hoje
            sorteio = Sorteio(data_sorteio=hoje)
            db.session.add(sorteio)
            db.session.commit()
        
        return sorteio
    
    def __repr__(self):
        return f'<Sorteio {self.data_sorteio} - Status: {self.status}>'

