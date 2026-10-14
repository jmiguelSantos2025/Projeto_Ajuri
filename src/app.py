from datetime import date
from flask import Flask, render_template, redirect, request ,flash,url_for
from flask_login import login_user, LoginManager, current_user, login_required
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from database.models import db, Usuario

## ler as variaveis de ambiente
load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar esta página"
login_manager.login_message_category =  "erro"

@login_manager.user_loader
def carregar_usuario(id_user):
    return db.session.get(Usuario, int(id_user))

with app.app_context():
    db.create_all()




@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        error = []
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email:
            error.append("Digite seu email")
        if not senha:
            error.append("Digite sua senha")

        if not error:
            usuario = Usuario.query.filter_by(email=email).first()

            if(usuario is None or not usuario.verificar_senha(senha)):
                error.append("Email ou senha invalidos")
            else:
                login_user(usuario)

                proximo = request.args.get("next","")
                if(proximo.startswith("/") and not proximo.startswith(("//", "/\\"))):
                    return redirect(proximo)
                return redirect(url_for("home"))

        for erros in error:
            flash("error: ", erros)


        

            
            
        
            

    return render_template("login.html")


@app.route("/cadastrarNovoUsuario", methods=["GET", "POST"])
def cadastrar_novo_usuario():
    if(request.method == "POST"):
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        erros = []

        if not nome:
            erros.append("Informe seu nome.")

        if "@" not in email:
            erros.append("Digite um email valido")
        if(len(senha) < 8):
            erros.append("Digite uma senha com mais de 7 caracteres")
        if(senha != confirmar_senha):
            erros.append("As senhas precisam ser iguais.")


        if not erros:
            existente = Usuario.query.filter_by(email=email).first()
            if existente:
                erros.append("Este email já está cadastrado")
            else:
                usuario = Usuario(nome=nome, email=email)
                usuario.definir_senha(senha)

                try:
                    db.session.add(usuario)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    erros.append("Este e-mail já está cadastrado.")
                else:
                    flash("Conta criada com sucesso!")
                    return redirect(url_for("login"))
        for erro in erros:
            flash("error: ", erro)




        

        
    return render_template("cadastro.html")


@app.route("/redefinirSenha", methods=["GET", "POST"])
def redefinir_senha():
    return render_template("redefinir_senha.html")


@app.route("/especificacoesTarefas", methods=["GET", "POST"])
def especificacoes_tarefa():
    return render_template("especificacoes_tarefa.html", usuario=USUARIO,
contatos=CONTATOS, tarefa=TAREFAS[1])


@app.route("/home")
@login_required()
def home():
    return render_template("home.html", usuario=USUARIO, contatos=CONTATOS, tarefas=TAREFAS)


@app.route("/listarcontatos", methods=["GET", "POST"])
def listar_contatos():
    return render_template("listar_contatos.html", usuario=USUARIO, contatos=CONTATOS)


if __name__ == "__main__":
    app.run(debug=True)
