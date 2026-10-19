# Ajuri — Gerenciador de Tarefas

Aplicação web de gerenciamento de tarefas em grupo, feita com **Python e Flask**. O sistema permite cadastrar contatos, criar tarefas, atribuí-las a um contato responsável e acompanhar o andamento por status coloridos.

Projeto acadêmico desenvolvido em equipe, com versionamento no GitHub.

## Funcionalidades

- **Autenticação:** cadastro, login, logout e redefinição de senha por link com validade de 1 hora.
- **Tarefas:** criar, editar, iniciar, concluir e excluir. Cada tarefa tem título, descrição, prazo, prioridade, status e responsável.
- **Contatos:** cadastrar e listar contatos (nome, e-mail e telefone). Cada tarefa é atribuída a um contato.
- **Status com cores:** A fazer, Fazendo, Concluída e Atrasada, com a mesma cor em todas as telas.
- **Atraso automático:** uma tarefa é "Atrasada" quando o prazo venceu e ela não está concluída. Esse status é calculado na exibição (fuso de Manaus) e não é gravado no banco.
- **Busca e filtros:** busca por texto e filtro por status na tela principal.
- **Tarefa por voz:** a pessoa fala a tarefa em português e o sistema sugere título, prazo, prioridade e responsável. Os dados são conferidos antes de salvar. Depende do suporte a reconhecimento de voz do navegador.
- **Segurança:** senhas com hash, proteção contra CSRF e dados separados por usuário.
- **Interface:** layout responsivo, com tema claro e escuro.

## Telas e rotas

| Rota | Tela |
|---|---|
| `/login` | Entrar no sistema |
| `/cadastrarNovoUsuario` | Criar conta |
| `/RedefinirSenha` | Pedir link de redefinição de senha |
| `/novaSenha` | Definir a nova senha pelo link recebido |
| `/home` | Lista de tarefas, contatos e janelas de criação e exclusão |
| `/especificacoesTarefas` | Editar uma tarefa |
| `/listarcontatos` | Lista de contatos |

## Valores de status e prioridade

| Campo | Valores |
|---|---|
| Status | `A_FAZER`, `FAZENDO`, `CONCLUIDA` e `ATRASADA` (calculada pelo prazo) |
| Prioridade | `ALTA`, `MEDIA` e `BAIXA` |

## Fluxo da aplicação

<img width="680" height="930" alt="DIAGRAMA DE ATIVIDADES" src="https://github.com/user-attachments/assets/cd20d43e-3cd2-437d-a494-247c8d29bd3e" />

## Tecnologias

- Python e Flask
- SQLAlchemy
- PostgreSQL no Supabase
- HTML, CSS e JavaScript simples
- Vercel (deploy)
- GitHub e VS Code

## Pré-requisitos

- **Python 3.10 ou superior**
- **Git**
- Acesso ao banco de dados do projeto (as credenciais ficam no arquivo `.env`, veja a seção de configuração)

Confira a versão instalada:

| Sistema | Comando |
|---|---|
| Windows | `py --version` |
| Linux e macOS | `python3 --version` |

## Como rodar o projeto

Escolha o seu sistema operacional. Todos os comandos são executados no terminal, dentro da pasta do projeto.

### 1. Baixar o projeto

Igual em todos os sistemas:

```bash
git clone https://github.com/jmiguelSantos2025/Projeto_Ajuri.git
cd Projeto_Ajuri
```

### 2. Criar e ativar o ambiente virtual

O ambiente virtual isola as bibliotecas do projeto, para não misturar com as de outros projetos.

**Windows (PowerShell):**

```powershell
py -m venv venv
venv\Scripts\activate
```

Se aparecer o erro "a execução de scripts foi desabilitada neste sistema", rode o comando abaixo e ative de novo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
venv\Scripts\activate
```

**Windows (Prompt de Comando, cmd):**

```bat
py -m venv venv
venv\Scripts\activate.bat
```

**Linux e macOS (bash ou zsh):**

```bash
python3 -m venv venv
source venv/bin/activate
```

Em Ubuntu e Debian, se aparecer o erro `ensurepip is not available` ou `No module named venv`, instale o pacote que falta e repita o comando:

```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

Quando o ambiente estiver ativo, o terminal mostra `(venv)` no começo da linha.

### 3. Instalar as dependências

Com o `(venv)` ativo, o comando é o mesmo em todos os sistemas:

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

As credenciais do banco e a chave secreta do Flask **não vão para o GitHub**. Crie um arquivo chamado `.env` na raiz do projeto, com os valores combinados com o grupo (peça ao João).

**Windows:**

```powershell
New-Item .env -ItemType File
```

**Linux e macOS:**

```bash
touch .env
```

Abra o arquivo no VS Code e preencha. O exemplo abaixo mostra o formato; use os **mesmos nomes de variáveis que o código lê** (veja em `src/`):

```
# Exemplo de formato. Ajuste os nomes e valores conforme o projeto.
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
SECRET_KEY=uma-chave-secreta-longa
```

> Nunca envie o `.env` para o GitHub. Ele já deve estar no `.gitignore`.

### 5. Executar a aplicação

**Windows:**

```powershell
py src/app.py
```

**Linux e macOS:**

```bash
python3 src/app.py
```

Abra no navegador: <http://127.0.0.1:5000/login>

Para parar o servidor, use `Ctrl + C` no terminal.

### 6. Desativar o ambiente virtual

Igual em todos os sistemas:

```bash
deactivate
```

## Como rodar os testes

Com o ambiente virtual ativo:

**Windows:**

```powershell
py -m pytest -q
```

**Linux e macOS:**

```bash
python3 -m pytest -q
```

Os testes automáticos cobrem a interpretação da tarefa por voz. As demais telas devem ser conferidas manualmente no navegador.

## Problemas comuns

| Problema | O que fazer |
|---|---|
| `python3: command not found` (Linux/macOS) | Instale o Python 3 pelo gerenciador de pacotes do sistema (por exemplo, `sudo apt install python3`). |
| `py` não é reconhecido (Windows) | Reinstale o Python em python.org marcando a opção **Add Python to PATH**. |
| `ModuleNotFoundError` | O ambiente virtual não está ativo ou as dependências não foram instaladas. Ative o `venv` e rode `pip install -r requirements.txt`. |
| Erro ao conectar no banco | Confira o `.env` e a conexão com a internet. |
| `Address already in use` (porta 5000 ocupada) | Feche o outro programa que usa a porta 5000 ou reinicie o terminal. |
| O visual não atualizou | Aperte `Ctrl + F5` no navegador para limpar o cache. |
| A tarefa por voz não funciona | Use um navegador com suporte a reconhecimento de voz e permita o uso do microfone. |
| Redefinição de senha: não chegou e-mail | O sistema gera o link de redefinição, mas não envia e-mail. Veja a observação abaixo. |

> **Observação:** a redefinição de senha gera um link com validade de 1 hora, que fica registrado no log do servidor. O envio por e-mail ainda não está implementado.

## Estrutura do projeto

```
Projeto_Ajuri/
├── docs/                 # diagramas, levantamento das telas e imagens de referência
├── src/
│   ├── app.py            # aplicação Flask e rotas
│   ├── templates/        # páginas HTML (Jinja)
│   └── static/           # CSS e JavaScript
├── requirements.txt      # bibliotecas do projeto
└── README.md
```

## Divisão de responsabilidades

Baseada no cronograma do grupo (planejamento AJURI).

| Integrante | Responsabilidades |
|---|---|
| **João Miguel** | Repositório, requisitos, definição das tecnologias, modelagem do banco, rotas e lógica do backend, tarefa por voz, testes e deploy |
| **Gabriel** | Diagrama de fluxo de telas, estrutura de pastas, telas `/Home` e `/listarcontatos` |
| **Nicole** | Diagrama de atividades, README, levantamento das telas, estrutura inicial do Flask, telas de login, cadastro, redefinição de senha e especificações da tarefa |

## Equipe

- João Miguel (Back-End e BD)
- Gabriel (Front-end)
- Nicole (Front-end)
