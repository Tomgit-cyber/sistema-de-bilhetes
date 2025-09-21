# C:\projetos_flutter\projeto-bilhetes\backend\models\aposta.py
from datetime import datetime
import json

# Importa db do database.py
from database import db

class Modalidade(db.Model):
    __tablename__ = 'modalidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    cor = db.Column(db.String(50), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com apostas
    apostas = db.relationship('Aposta', backref='modalidade_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'cor': self.cor,
            'ativo': self.ativo
        }

class BilhetePredefinido(db.Model):
    __tablename__ = 'bilhetes_predefinidos'
    
    id = db.Column(db.Integer, primary_key=True)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id'), nullable=False)
    numeros = db.Column(db.Text, nullable=False)  # JSON string com os números
    preco = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com a modalidade
    modalidade = db.relationship('Modalidade', backref='bilhetes_predefinidos')
    
    def get_numeros(self):
        try:
            return json.loads(self.numeros)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_numeros(self, numeros_list):
        self.numeros = json.dumps(numeros_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'modalidade_id': self.modalidade_id,
            'numeros': self.get_numeros(),
            'preco': self.preco,
            'ativo': self.ativo
        }

class Premiacao(db.Model):
    __tablename__ = 'premiacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id'), nullable=False)
    posicao = db.Column(db.String(50), nullable=False)  # "1º Prêmio", "2º Prêmio", etc.
    valor = db.Column(db.Float, nullable=False)
    
    # Relacionamento com a modalidade
    modalidade = db.relationship('Modalidade', backref='premiacoes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'modalidade_id': self.modalidade_id,
            'posicao': self.posicao,
            'valor': self.valor
        }

class Aposta(db.Model):
    __tablename__ = 'apostas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # >>> CORREÇÃO CRUCIAL AQUI <<< 
    # Adicionando a coluna user_id com a ForeignKey correta.
    # O nome da tabela deve corresponder EXATAMENTE ao __tablename__ da classe User.
    # Se User.__tablename__ = 'users', entao use 'users.id'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id'), nullable=False)
    # Supondo que 'bilhetes_selecionados' seja uma lista de IDs de BilhetePredefinido ou numeros
    bilhetes_selecionados = db.Column(db.Text, nullable=False)  # JSON string
    valor_total = db.Column(db.Float, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='confirmada')

    def get_bilhetes_selecionados(self):
        """Retorna a lista de bilhetes (ou numeros) a partir do campo JSON."""
        try:
            return json.loads(self.bilhetes_selecionados)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_bilhetes_selecionados(self, bilhetes_list):
        """Armazena a lista de bilhetes (ou numeros) como uma string JSON."""
        self.bilhetes_selecionados = json.dumps(bilhetes_list)

    def to_dict(self):
        """Serializa o objeto Aposta para um dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'modalidade_id': self.modalidade_id,
            'bilhetes_selecionados': self.get_bilhetes_selecionados(),
            'valor_total': self.valor_total,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'status': self.status,
            # Inclui os objetos relacionados se existirem
            'modalidade': self.modalidade_ref.to_dict() if self.modalidade_ref else None,
            'usuario': self.usuario.to_dict() if hasattr(self, 'usuario') and self.usuario else None
        }

    def __repr__(self):
        return f'<Aposta {self.id} - User: {self.user_id} - Valor: {self.valor_total}>'
