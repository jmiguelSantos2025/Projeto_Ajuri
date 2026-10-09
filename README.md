# Ajuri - Gerenciador de Tarefas

Aplicação web de gerenciamento de tarefas desenvolvida em grupo, em Python com Flask, como projeto acadêmico do curso de Sistemas de Informação (UEA).

O sistema permite cadastrar contatos, criar tarefas, atribuí-las a um contato e acompanhar o andamento de cada uma por status e cor.

## Principais funcionalidades

- Cadastro de usuário, login e redefinição de senha
- Lista de contatos
- Criação de tarefas com **descrição**, **prazo**, **prioridade**, **status** e **responsável** (um contato)
- Edição e exclusão de tarefas
- Tela com todas as tarefas e seus respectivos responsáveis
- Quatro status, cada um com uma cor diferente em todas as telas:
  - A fazer
  - Fazendo
  - Concluída
  - Atrasada (prazo vencido e tarefa ainda não concluída)

## Rotas

| Rota |
|---|
| `/login` |
| `/cadastrarNovoUsuario` |
| `/RedefinirSenha` |
| `/Home` |
| `/especificacoesTarefas` |
| `/listarcontatos` |

## Fluxo do sistema

![Diagrama de atividades]<img width="680" height="930" alt="DIAGRAMA DE ATIVIDADES" src="https://github.com/user-attachments/assets/cd20d43e-3cd2-437d-a494-247c8d29bd3e" />


## Tecnologias

- Python
- Flask
- SQLAlchemy
- Supabase + PostgreSQL
- GitHub (versionamento)
- Vercel (deploy)
- VS Code (IDE)

## Como executar o projeto

> Os comandos abaixo serão atualizados quando a estrutura inicial do Flask estiver pronta.

1. Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DA_PASTA
```

2. Crie e ative o ambiente virtual (Windows):

```bash
py -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
flask run
```

5. Abra no navegador: `http://127.0.0.1:5000`

## Organização do trabalho

Cada integrante ficou responsável por uma parte do projeto, conforme o cronograma da equipe.

| Integrante | Responsabilidades |
|---|---|
| João Miguel | Cronograma, divisão de atividades, repositório, requisitos, definição de stack, modelagem e configuração do banco (Supabase + SQLAlchemy), `models.py`, rotas e lógica do backend, deploy e testes |
| Gabriel | Diagrama de fluxo de telas, estrutura de pastas, telas `/home` e `/listarContatos` |
| Nicole | Diagrama de atividades, README, levantamento das telas, estrutura inicial do Flask, telas `/login`, `/especificacoesTarefa` e `/cadastrarNovoUsuario` |

## Cronograma

| Sprint | Período | Prioridade |
|---|---|---|
| 1 | 07/10/2026 a 08/10/2026 | Alta |
| 2 | 09/10/2026 a 10/10/2026 | Alta |
| 3 | 11/10/2026 a 13/10/2026 | Média |
| 4 | 14/10/2026 a 16/10/2026 | Média |
| 5 | 17/10/2026 a 19/10/2026 | Baixa |

## Fluxo de trabalho com branches

> A definir conforme as instruções do repositório.

## Equipe

- João Miguel (Back-End)
- Gabriel(Front-End)
- Nicole(Front-End)
