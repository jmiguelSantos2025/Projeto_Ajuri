import os
from datetime import datetime, time, timezone
from flask import Flask, render_template, redirect, request, flash, url_for, abort
from flask_login import (login_user, logout_user, LoginManager,
                         current_user, login_required)
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from database.models import (db, Usuario, Contato, Tarefa,
                             PRIORIDADES, STATUS_VALIDOS)

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
login_manager.login_message_category = "erro"


@login_manager.user_loader
def carregar_usuario(id_user):
    return db.session.get(Usuario, int(id_user))


with app.app_context():
    db.create_all()


# ---------- funções auxiliares ----------

def criar_contato():
    """Cria um contato do usuário logado a partir do formulário. Devolve a lista de erros."""
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    telefone = request.form.get("telefone", "").strip()
    erros = []

    if not nome:
        erros.append("Informe o nome do contato.")
    if "@" not in email:
        erros.append("Digite um email valido para o contato.")
    if not telefone:
        erros.append("Informe o telefone do contato.")

    if not erros:
        contato = Contato(id_user=current_user.id_user, nome=nome,
                          email=email, telefone=telefone)
        db.session.add(contato)
        db.session.commit()
        flash("Contato adicionado!", "sucesso")
    return erros


def criar_tarefa():
    """Cria uma tarefa do usuário logado a partir do formulário. Devolve a lista de erros."""
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    prioridade = request.form.get("prioridade", "")
    status = request.form.get("status", "")
    id_contato = request.form.get("id_contato", type=int)
    erros = []

    if not titulo:
        erros.append("Informe o título da tarefa.")
    if prioridade not in PRIORIDADES:
        erros.append("Prioridade inválida.")
    if status not in STATUS_VALIDOS:
        erros.append("Status inválido.")

    data_final = None
    try:
        dia = datetime.strptime(request.form.get("data_final", ""), "%Y-%m-%d").date()
        data_final = datetime.combine(dia, time(12, 0), tzinfo=timezone.utc)
    except ValueError:
        erros.append("Prazo inválido.")

    agora = datetime.now(timezone.utc)
    if data_final and data_final.date() < agora.date():
        erros.append("O prazo não pode ser anterior a hoje.")

    if id_contato is not None:
        contato = db.session.get(Contato, id_contato)
        if contato is None or contato.id_user != current_user.id_user:
            erros.append("Responsável inválido.")

    if not erros:
        tarefa = Tarefa(id_user=current_user.id_user, id_contato=id_contato,
                        titulo=titulo, descricao=descricao,
                        data_inicio=agora, data_final=data_final,
                        prioridade=prioridade, status=status)
        db.session.add(tarefa)
        db.session.commit()
        flash("Tarefa criada!", "sucesso")
    return erros


def excluir_tarefa():
    id_tarefa = request.form.get("id_tarefa", type=int)
    tarefa = db.session.get(Tarefa, id_tarefa) if id_tarefa else None

    if tarefa is None or tarefa.id_user != current_user.id_user:
        return ["Tarefa não encontrada."]

    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa excluída.", "sucesso")
    return []


# ---------- rotas ----------

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        erros = []
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email:
            erros.append("Digite seu email")
        if not senha:
            erros.append("Digite sua senha")

        if not erros:
            usuario = Usuario.query.filter_by(email=email).first()

            if usuario is None or not usuario.verificar_senha(senha):
                erros.append("Email ou senha invalidos")
            else:
                login_user(usuario)

                proximo = request.args.get("next", "")
                if proximo.startswith("/") and not proximo.startswith(("//", "/\\")):
                    return redirect(proximo)
                return redirect(url_for("home"))

        for erro in erros:
            flash(erro, "erro")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/cadastrarNovoUsuario", methods=["GET", "POST"])
def cadastrar_novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        erros = []

        if not nome:
            erros.append("Informe seu nome.")
        if "@" not in email:
            erros.append("Digite um email valido")
        if len(senha) < 8:
            erros.append("Digite uma senha com mais de 7 caracteres")
        if senha != confirmar_senha:
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
                    flash("Conta criada com sucesso!", "sucesso")
                    return redirect(url_for("login"))

        for erro in erros:
            flash(erro, "erro")

    return render_template("cadastro.html")


@app.route("/redefinirSenha", methods=["GET", "POST"])
def redefinir_senha():
    return render_template("redefinir_senha.html")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        acao = request.form.get("acao", "")

        if acao == "nova_tarefa":
            erros = criar_tarefa()
        elif acao == "excluir_tarefa":
            erros = excluir_tarefa()
        elif acao == "novo_contato":
            erros = criar_contato()
        else:
            erros = ["Ação inválida."]

        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("home"))

    return render_template("home.html", usuario=current_user,
                           contatos=current_user.contatos,
                           tarefas=current_user.tarefas_listadas)


@app.route("/listarcontatos", methods=["GET", "POST"])
@login_required
def listar_contatos():
    if request.method == "POST":
        if request.form.get("acao", "") == "novo_contato":
            erros = criar_contato()
        else:
            erros = ["Ação inválida."]

        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("listar_contatos"))

    return render_template("listar_contatos.html", usuario=current_user,
                           contatos=current_user.contatos)


@app.route("/especificacoesTarefas")
@login_required
def especificacoes_tarefa():
    id_tarefa = request.args.get("id", type=int)
    tarefa = db.session.get(Tarefa, id_tarefa) if id_tarefa else None

    if tarefa is None or tarefa.id_user != current_user.id_user:
        abort(404)

    return render_template("especificacoes_tarefa.html", usuario=current_user,
                           contatos=current_user.contatos, tarefa=tarefa)


if __name__ == "__main__":
    app.run(debug=True)