from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


db = SQLAlchemy()

PRIORIDADES = ["baixa", "media", "alta"]
STATUS_VALIDOS = ["a_fazer", "fazendo", "concluida"]




class Usuario(db.Model, UserMixin):
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    contatos = db.relationship("Contato",back_populates="dono", cascade="all, delete-orphan")
    tarefas_listadas = db.relationship("Tarefa", back_populates="usuario_dono_tarefa", cascade="all, delete-orphan")

    def definir_senha(self,senha):
        self.senha_hash = generate_password_hash(senha)
    def verificar_senha(self,senha):
        return check_password_hash(self.senha_hash,senha)
    def get_id(self):
        return str(self.id_user)
class Contato(db.Model):
    id_contato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer,db.ForeignKey("usuario.id_user"), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    dono = db.relationship("Usuario", back_populates="contatos")
    tarefas = db.relationship("Tarefa", back_populates="responsavel")
    

class Tarefa(db.Model):
    id_tarefa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey("usuario.id_user"), nullable=False)
    id_contato = db.Column(db.Integer, db.ForeignKey("contato.id_contato"))
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    data_final = db.Column(db.DateTime(timezone=True), nullable=False)
    prioridade = db.Column(db.String(10), nullable=False, default="media")
    status = db.Column(db.String(15), nullable=False, default="a_fazer")
    responsavel = db.relationship("Contato", back_populates="tarefas")
    usuario_dono_tarefa = db.relationship("Usuario", back_populates="tarefas_listadas")