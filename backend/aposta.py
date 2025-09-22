from .database import db
from datetime import datetime

class Aposta(db.Model):
    """Model para apostas do sistema"""
    __tablename__ = 'apostas'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sorteio_id = db.Column(db.Integer, db.ForeignKey('sorteios.id'), nullable=False)
    numero_escolhido = db.Column(db.Integer, nullable=False)
    valor_aposta = db.Column(db.Float, nullable=False, default=2.0)
    data_aposta = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='ativa')  # ativa, ganhadora, perdedora
    
    def __init__(self, user_id, sorteio_id, numero_escolhido, valor_aposta=2.0):
        self.user_id = user_id
        self.sorteio_id = sorteio_id
        self.numero_escolhido = numero_escolhido
        self.valor_aposta = valor_aposta
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sorteio_id': self.sorteio_id,
            'numero_escolhido': self.numero_escolhido,
            'valor_aposta': self.valor_aposta,
            'data_aposta': self.data_aposta.isoformat(),
            'status': self.status
        }
    
    def __repr__(self):
        return f'<Aposta {self.id} - Número {self.numero_escolhido}>'

