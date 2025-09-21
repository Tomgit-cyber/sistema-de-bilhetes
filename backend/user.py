# C:\projetos_flutter\projeto-bilhetes\backend\user.py
# ou
# C:\projetos_flutter\projeto-bilhetes\backend\models\user.py
print(f"Carregando user.py de: {__file__}")

from database import db # Assumindo que database.py esta na mesma pasta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users' # Nome da tabela no banco de dados

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    saldo = db.Column(db.Float, default=2.0) # Saldo inicial conforme requisitos

    # Relacionamento com as apostas
    # 'Aposta' deve ser o nome da classe do modelo Aposta
    # 'usuario' sera um atributo em cada instancia de Aposta
    apostas = db.relationship('Aposta', backref='usuario', lazy=True)

    def __init__(self, nome, email, password, telefone=None):
        self.nome = nome
        self.email = email
        self.set_password(password) # Hasheia a senha
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
        """Retorna uma representação em dicionário do usuário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'saldo': self.saldo
        }

    def __repr__(self):
        return f'<User {self.email}>'
