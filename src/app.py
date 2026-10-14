import os
import unicodedata
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
from flask import Flask, render_template, redirect, request, flash, url_for, abort
from flask_login import (login_user, logout_user, LoginManager,
                         current_user, login_required)
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv
from database.models import (db, Usuario, Contato, Tarefa,
                             PRIORIDADES, STATUS_VALIDOS)

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 280, "pool_pre_ping": True}

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar esta página"
login_manager.login_message_category = "erro"

serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="redefinir-senha")
VALIDADE_TOKEN = 3600  
FUSO = ZoneInfo("America/Manaus")


@login_manager.user_loader
def carregar_usuario(id_user):
    return db.session.get(Usuario, int(id_user))


with app.app_context():
    db.create_all()


def mostrar_erros(erros):
    for erro in erros:
        flash(erro, "erro")


def normalizar(valor):
    """'Média' -> 'MEDIA', 'a-fazer' -> 'A_FAZER'"""
    valor = unicodedata.normalize("NFKD", valor or "")
    valor = "".join(c for c in valor if not unicodedata.combining(c))
    return valor.strip().upper().replace("-", "_").replace(" ", "_")


def validar_senha_nova(senha, confirmar):
    erros = []
    if len(senha) < 8:
        erros.append("Digite uma senha com mais de 7 caracteres")
    if senha != confirmar:
        erros.append("As senhas precisam ser iguais.")
    return erros


def ler_dados_tarefa():
    """Lê e valida o formulário de tarefa. Devolve (dados, erros)."""
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    prioridade = normalizar(request.form.get("prioridade", ""))
    status = normalizar(request.form.get("status", ""))
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

    if id_contato is not None:
        contato = db.session.get(Contato, id_contato)
        if contato is None or contato.id_user != current_user.id_user:
            erros.append("Responsável inválido.")

    dados = dict(titulo=titulo, descricao=descricao, prioridade=prioridade,
                 status=status, id_contato=id_contato, data_final=data_final)
    return dados, erros


def buscar_tarefa_do_usuario(id_tarefa):
    tarefa = db.session.get(Tarefa, id_tarefa) if id_tarefa else None
    if tarefa is None or tarefa.id_user != current_user.id_user:
        return None
    return tarefa


def criar_contato():
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
        ja_existe = Contato.query.filter_by(id_user=current_user.id_user,
                                            email=email).first()
        if ja_existe:
            erros.append("Você já tem um contato com esse email.")
        else:
            db.session.add(Contato(id_user=current_user.id_user, nome=nome,
                                   email=email, telefone=telefone))
            db.session.commit()
            flash("Contato adicionado!", "sucesso")
    return erros


def criar_tarefa():
    dados, erros = ler_dados_tarefa()
    agora = datetime.now(timezone.utc)
    hoje = datetime.now(FUSO).date()

    if dados["data_final"] and dados["data_final"].date() < hoje:
        erros.append("O prazo não pode ser anterior a hoje.")

    if not erros:
        db.session.add(Tarefa(id_user=current_user.id_user,
                              data_inicio=agora, **dados))
        db.session.commit()
        flash("Tarefa criada!", "sucesso")
    return erros


def excluir_tarefa():
    tarefa = buscar_tarefa_do_usuario(request.form.get("id_tarefa", type=int))
    if tarefa is None:
        return ["Tarefa não encontrada."]
    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa excluída.", "sucesso")
    return []




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

        mostrar_erros(erros)

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
        erros += validar_senha_nova(senha, confirmar_senha)

        if not erros:
            if Usuario.query.filter_by(email=email).first():
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

        mostrar_erros(erros)

    return render_template("cadastro.html")




@app.route("/redefinirSenha", methods=["GET", "POST"])
def redefinir_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        usuario = Usuario.query.filter_by(email=email).first() if email else None

        if usuario:
         
            token = serializer.dumps({"id": usuario.id_user,
                                      "h": usuario.senha_hash[-10:]})
            link = url_for("nova_senha", token=token, _external=True)
            
            app.logger.warning("LINK DE REDEFINICAO (%s): %s", email, link)

      
        flash("Se esse email estiver cadastrado, enviamos um link para redefinir a senha.",
              "sucesso")
        return redirect(url_for("redefinir_senha"))

    return render_template("redefinir_senha.html")


@app.route("/novaSenha/<token>", methods=["GET", "POST"])
def nova_senha(token):
    try:
        dados = serializer.loads(token, max_age=VALIDADE_TOKEN)
    except (BadSignature, SignatureExpired):
        flash("Link inválido ou expirado. Peça um novo.", "erro")
        return redirect(url_for("redefinir_senha"))

    usuario = db.session.get(Usuario, dados["id"])
    if usuario is None or usuario.senha_hash[-10:] != dados["h"]:
        flash("Este link já foi usado ou é inválido. Peça um novo.", "erro")
        return redirect(url_for("redefinir_senha"))

    if request.method == "POST":
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        erros = validar_senha_nova(senha, confirmar)

        if not erros:
            usuario.definir_senha(senha)
            db.session.commit()
            flash("Senha alterada! Faça login.", "sucesso")
            return redirect(url_for("login"))
        mostrar_erros(erros)

    return render_template("nova_senha.html")




@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        print(">>> POST /home:", dict(request.form), flush=True)
       
        acao = request.form.get("acao", "")

        if acao == "nova_tarefa":
            erros = criar_tarefa()
        elif acao == "excluir_tarefa":
            erros = excluir_tarefa()
        elif acao == "novo_contato":
            erros = criar_contato()
        else:
            erros = ["Ação inválida."]
        print(">>> ERROS:", erros, flush=True)
        mostrar_erros(erros)
        return redirect(url_for("home"))

    tarefas = (Tarefa.query
               .options(selectinload(Tarefa.responsavel))
               .filter_by(id_user=current_user.id_user)
               .order_by(Tarefa.data_final)
               .all())
    contatos = Contato.query.filter_by(id_user=current_user.id_user).all()
    return render_template("home.html", usuario=current_user,
                           contatos=contatos, tarefas=tarefas)
@app.route("/tarefas/<int:id_tarefa>/status", methods=["POST"])
@login_required
def mudar_status(id_tarefa):
    tarefa = buscar_tarefa_do_usuario(id_tarefa)
    novo_status = normalizar(request.form.get("status", ""))

    if tarefa is None:
        flash("Tarefa não encontrada.", "erro")
    elif novo_status not in STATUS_VALIDOS:
        flash("Status inválido.", "erro")
    else:
        tarefa.status = novo_status
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/listarcontatos", methods=["GET", "POST"])
@login_required
def listar_contatos():
    if request.method == "POST":
        if request.form.get("acao", "") == "novo_contato":
            erros = criar_contato()
        else:
            erros = ["Ação inválida."]
        mostrar_erros(erros)
        return redirect(url_for("listar_contatos"))

    return render_template("listar_contatos.html", usuario=current_user,
                           contatos=current_user.contatos)


@app.route("/especificacoesTarefas", methods=["GET", "POST"])
@login_required
def especificacoes_tarefa():
    id_tarefa = request.args.get("id", type=int)
    tarefa = buscar_tarefa_do_usuario(id_tarefa)
    if tarefa is None:
        abort(404)

    if request.method == "POST":
        dados, erros = ler_dados_tarefa()

        if dados["data_final"] and dados["data_final"].date() < tarefa.data_inicio.date():
            erros.append("O prazo não pode ser anterior ao início da tarefa.")

        if not erros:
            for campo, valor in dados.items():
                setattr(tarefa, campo, valor)
            db.session.commit()
            flash("Tarefa atualizada!", "sucesso")
            return redirect(url_for("home"))

        mostrar_erros(erros)

    return render_template("especificacoes_tarefa.html", usuario=current_user,
                           contatos=current_user.contatos, tarefa=tarefa)


if __name__ == "__main__":
    app.run(debug=True)