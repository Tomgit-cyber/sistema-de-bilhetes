# C:\projetos_flutter\projeto-bilhetes\backend\models\user.py
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # <<< Nome da tabela definido como 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    saldo = db.Column(db.Float, default=2.0) # Saldo inicial conforme requisitos

    # >>> RELACIONAMENTO COM APOSTAS <<< 
    # Esta linha é crucial para o funcionamento da ForeignKey em Aposta
    apostas = db.relationship('Aposta', backref='usuario', lazy=True)

    def __init__(self, nome, email, password, telefone=None):
        self.nome = nome
        self.email = email
        self.set_password(password) # Hasheia a senha no momento da criação
        self.telefone = telefone

    def set_password(self, password):
        """Hasheia a senha e a armazena."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.password_hash, password)

    def adicionar_saldo(self, valor):
        """Adiciona saldo à conta do usuário."""
        if valor > 0:
            self.saldo += valor

    def to_dict(self):
        """Retorna uma representação em dicionário do usuário (para JSON)."""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'saldo': self.saldo
        }

    def __repr__(self):
        return f'<User {self.email}>'
