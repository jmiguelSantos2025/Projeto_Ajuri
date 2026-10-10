from datetime import date

from flask import Flask, render_template, redirect

app = Flask(__name__)

# ---------------------------------------------------------------
# Dados de exemplo, só para ver as telas funcionando.
# O João troca por dados reais do banco (usuario, contato, tarefa).
# ---------------------------------------------------------------
USUARIO = {"nome": "Marina Souza", "email": "marina.souza@universidade.br"}

CONTATOS = [
    {"id_contato": 1, "nome": "Ana Clara Lima", "email": "ana.lima@universidade.br", "telefone": "(11) 98742-1308"},
    {"id_contato": 2, "nome": "Rafael Nunes", "email": "rafael.nunes@universidade.br", "telefone": "(11) 99608-5421"},
    {"id_contato": 3, "nome": "Beatriz Martins", "email": "bia.martins@universidade.br", "telefone": "(19) 98830-7714"},
    {"id_contato": 4, "nome": "João Pedro Alves", "email": "joao.alves@universidade.br", "telefone": "(21) 99102-4436"},
]

TAREFAS = [
    {"id_tarefa": 1, "titulo": "Entregar relatório de Banco de Dados",
     "descricao": "Consolidar consultas, modelo lógico e resultados dos testes.",
     "data_final": date(2026, 10, 8), "prioridade": "ALTA", "status": "ATRASADA",
     "id_contato": 1, "contato": "Ana Clara"},
    {"id_tarefa": 2, "titulo": "Revisar diagrama de classes",
     "descricao": "Validar associações e multiplicidades com a equipe.",
     "data_final": date(2026, 10, 14), "prioridade": "MEDIA", "status": "FAZENDO",
     "id_contato": 2, "contato": "Rafael Nunes"},
    {"id_tarefa": 3, "titulo": "Marcar reunião com o orientador",
     "descricao": "Alinhar o escopo da etapa final e os critérios de avaliação.",
     "data_final": date(2026, 10, 17), "prioridade": "ALTA", "status": "A_FAZER",
     "id_contato": None, "contato": "Marina Souza"},
    {"id_tarefa": 4, "titulo": "Preparar roteiro da apresentação",
     "descricao": "Distribuir falas e revisar a duração de cada seção.",
     "data_final": date(2026, 10, 10), "prioridade": "MEDIA", "status": "CONCLUIDA",
     "id_contato": 3, "contato": "Beatriz Martins"},
    {"id_tarefa": 5, "titulo": "Testar fluxo de cadastro",
     "descricao": "Cobrir validações de e-mail e confirmação de senha.",
     "data_final": date(2026, 10, 20), "prioridade": "BAIXA", "status": "A_FAZER",
     "id_contato": 4, "contato": "João Pedro"},
    {"id_tarefa": 6, "titulo": "Documentar endpoints da API",
     "descricao": "Registrar parâmetros, respostas e códigos de erro do projeto.",
     "data_final": date(2026, 10, 22), "prioridade": "MEDIA", "status": "FAZENDO",
     "id_contato": 2, "contato": "Rafael Nunes"},
]


# ---------------------------------------------------------------
# Rotas temporárias: só mostram as telas.
# Os formulários (POST) ainda não salvam nada.
# ---------------------------------------------------------------
@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/cadastrarNovoUsuario", methods=["GET", "POST"])
def cadastrar_novo_usuario():
    return render_template("cadastro.html")


@app.route("/RedefinirSenha", methods=["GET", "POST"])
def redefinir_senha():
    return render_template("redefinir_senha.html")


@app.route("/Home", methods=["GET", "POST"])
def home():
    return render_template("home.html", usuario=USUARIO, contatos=CONTATOS, tarefas=TAREFAS)


@app.route("/especificacoesTarefas", methods=["GET", "POST"])
def especificacoes_tarefa():
    return render_template("especificacoes_tarefa.html", usuario=USUARIO,
                           contatos=CONTATOS, tarefa=TAREFAS[1])


@app.route("/listarcontatos", methods=["GET", "POST"])
def listar_contatos():
    return render_template("listar_contatos.html", usuario=USUARIO, contatos=CONTATOS)


if __name__ == "__main__":
    app.run(debug=True)
