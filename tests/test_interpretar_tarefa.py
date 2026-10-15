"""Testes da interpretação de frases para criação de tarefa por voz."""

from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from services.interpretar_tarefa import interpretar_tarefa, normalizar

FUSO = ZoneInfo("America/Manaus")
# Segunda-feira, 2 de março de 2026, às 10h — base previsível para os testes.
AGORA = datetime(2026, 3, 2, 10, 0, tzinfo=FUSO)


def contato(id_contato, nome):
    """Dublê simples do model Contato (só o que a função usa)."""
    return SimpleNamespace(id_contato=id_contato, nome=nome)


# ---------------------------------------------------------------------------
# Tabela de frases: (texto, contatos, esperado)
# ---------------------------------------------------------------------------
CASOS = [
    pytest.param(
        "Revisar o relatório para o Bruno até sexta, prioridade alta",
        [contato(7, "Bruno")],
        {"titulo": "Revisar o relatório", "data": "2026-03-06",
         "prioridade": "ALTA", "id_contato": 7},
        id="completo-com-responsavel-prazo-e-prioridade",
    ),
    pytest.param(
        "Preparar slides da apresentação para amanhã",
        [],
        {"titulo": "Preparar slides da apresentação", "data": "2026-03-03",
         "prioridade": "MEDIA", "id_contato": None},
        id="sem-responsavel-com-prazo",
    ),
    pytest.param(
        "Revisar o capítulo três",
        [],
        {"titulo": "Revisar o capítulo três", "data": None,
         "prioridade": "MEDIA", "id_contato": None},
        id="sem-prazo",
    ),
    pytest.param(
        "Ligar para o José hoje",
        [contato(2, "José")],
        {"titulo": "Ligar", "data": "2026-03-02",
         "prioridade": "MEDIA", "id_contato": 2},
        id="nome-com-acento",
    ),
    pytest.param(
        "Falar com Maria Silva hoje",
        [contato(4, "Maria"), contato(5, "Maria Silva")],
        {"titulo": "Falar com Maria Silva", "data": "2026-03-02",
         "prioridade": "MEDIA", "id_contato": None},
        id="nome-ambiguo",
    ),
    pytest.param(
        "Revisar o relatório para o Bruno até sexta",
        [contato(1, "Bruno Silva")],
        {"titulo": "Revisar o relatório", "data": "2026-03-06",
         "prioridade": "MEDIA", "id_contato": 1},
        id="apenas-primeiro-nome-do-contato",
    ),
    pytest.param(
        "lembrar de comprar material até dia 20",
        [],
        {"titulo": "comprar material", "data": "2026-03-20",
         "prioridade": "MEDIA", "id_contato": None},
        id="comando-lembrar-e-dia-do-mes",
    ),
    pytest.param(
        "criar tarefa de pagar a conta de luz amanhã",
        [],
        {"titulo": "pagar a conta de luz", "data": "2026-03-03",
         "prioridade": "MEDIA", "id_contato": None},
        id="comando-criar-tarefa",
    ),
]


@pytest.mark.parametrize("texto, contatos, esperado", CASOS)
def test_interpretar_campos_principais(texto, contatos, esperado):
    resultado = interpretar_tarefa(texto, contatos, agora=AGORA)

    assert resultado["titulo"] == esperado["titulo"]
    assert resultado["prioridade"] == esperado["prioridade"]
    assert resultado["id_contato"] == esperado["id_contato"]
    if esperado["data"] is None:
        assert resultado["data_final"] is None
    else:
        assert resultado["data_final"][:10] == esperado["data"]


@pytest.mark.parametrize(
    "texto, data",
    [
        ("Entregar o resumo amanhã", "2026-03-03"),
        ("Entregar o resumo na sexta", "2026-03-06"),
        ("Entregar o resumo dia 20", "2026-03-20"),
        ("Entregar o resumo em 20 de março", "2026-03-20"),
        ("Entregar o resumo hoje", "2026-03-02"),
    ],
)
def test_prazos(texto, data):
    resultado = interpretar_tarefa(texto, [], agora=AGORA)
    assert resultado["data_final"][:10] == data


def test_texto_vazio():
    resultado = interpretar_tarefa("   ", [], agora=AGORA)
    assert resultado["titulo"] == ""
    assert resultado["data_final"] is None
    assert resultado["id_contato"] is None
    assert resultado["avisos"]  # precisa avisar que não recebeu texto


def test_sem_prazo_avisa():
    resultado = interpretar_tarefa("Estudar para a prova", [], agora=AGORA)
    assert resultado["data_final"] is None
    assert any("prazo" in aviso.lower() for aviso in resultado["avisos"])


def test_nome_ambiguo_avisa():
    contatos = [contato(1, "Ana"), contato(2, "Ana Paula")]
    # "Ana Paula" casa com os dois contatos: melhor não escolher sozinho.
    resultado = interpretar_tarefa("Ligar para Ana Paula amanhã", contatos,
                                   agora=AGORA)
    assert resultado["id_contato"] is None
    assert any("mais de um" in aviso.lower() for aviso in resultado["avisos"])


@pytest.mark.parametrize(
    "texto, prioridade",
    [
        ("Corrigir a prova urgente", "ALTA"),
        ("Enviar convite prioridade alta", "ALTA"),
        ("Arquivar documentos prioridade baixa", "BAIXA"),
        ("Organizar a estante", "MEDIA"),
    ],
)
def test_prioridade(texto, prioridade):
    assert interpretar_tarefa(texto, [], agora=AGORA)["prioridade"] == prioridade


def test_estrutura_da_resposta():
    """A sugestão traz as chaves combinadas e o início = agora."""
    resultado = interpretar_tarefa("Revisar algo", [], agora=AGORA)
    assert set(resultado) == {
        "titulo", "descricao", "data_inicio", "data_final",
        "prioridade", "id_contato", "avisos",
    }
    assert resultado["descricao"] == ""
    assert resultado["data_inicio"] == AGORA.isoformat()
    assert isinstance(resultado["avisos"], list)


def test_nao_depende_do_banco():
    """Passar contatos como dicts simples não deve quebrar (usa getattr)."""
    resultado = interpretar_tarefa("Falar com Bruno amanhã", [], agora=AGORA)
    assert resultado["id_contato"] is None


def test_normalizar_remove_acento_e_caixa():
    assert normalizar("José") == "jose"
    assert normalizar("  À Vista ") == "a vista"
