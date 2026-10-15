"""Interpreta uma frase em português e sugere campos de uma tarefa.

Este módulo é de propósito "puro": não importa Flask nem o banco, para
que possa ser testado isoladamente com pytest. Ele só *sugere* valores —
quem valida e grava continua sendo a rota de tarefas (Fase 3).
"""

import re
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

import dateparser

# Fuso do usuário: prazos são interpretados e devolvidos nele.
FUSO = ZoneInfo("America/Manaus")

# dateparser em português, sempre olhando para o futuro, e já no fuso certo.
_CONFIG_DADOS = {
    "PREFER_DATES_FROM": "future",
    "TIMEZONE": "America/Manaus",
    "RETURN_AS_TIMEZONE_AWARE": True,
}

# Palavras que mudam a prioridade (comparamos já sem acento e minúsculas).
_PRIORIDADE_ALTA = {"urgente", "urgencia", "alta", "critica", "critico",
                    "prioritaria", "prioritario"}
_PRIORIDADE_BAIXA = {"baixa", "leve", "pouca", "pouco"}
_PRIORIDADE_MEDIA = {"media", "normal", "padrao"}

# Palavras que encaixam antes do nome do responsável ("para o Bruno").
_GATILHOS_RESPONSAVEL = {"para", "pra", "pro", "com", "responsavel", "pelo",
                         "pela", "pelos", "pelas", "do", "da", "dos", "das",
                         "o", "a", "os", "as", "em", "no", "na", "ao"}

# Preposições usadas antes de um prazo ("até sexta", "para amanhã").
_PREPOSICOES = r"até|ate|antes de|pra|para|em|no|na|do|dia"

# Trechos de ordem de serviço que não devem virar título.
_PADRAO_TAREFA = re.compile(
    r"\b(?:criar|crie|cria|criamos|montar|monte|adicionar|adicione|"
    r"adiciona|nova|novo|anotar)\s+(?:uma|o|a)?\s*tarefa\s*(?:de|para|:)?"
    r"|\b(?:lembrar de|lembrar-me de|me lembra de|lembre de|lembrar)\b",
    re.I,
)

# Trechos de prioridade escritos por extenso (a prioridade já foi capturada).
_PADRAO_PRIORIDADE_TEXTO = re.compile(
    r"\bprioridade\s+(?:alta|m[ée]dia|baixa|normal)\b"
    r"|\b(?:urgente|urg[êe]ncia)\b",
    re.I,
)

# Nomes de dias e meses, úteis tanto para achar quanto para limpar.
_DIAS = r"(?:segunda|ter[çc]a|quarta|quinta|sexta|s[áa]bado|domingo)(?:-\s?feira)?"
_MESES = (r"(?:janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|"
          r"setembro|outubro|novembro|dezembro)")

# O que o dateparser aceita: partes nomeadas (dia da semana, "20 de março"...)
_NUCLEO = (
    r"depois de amanh[ãa]|amanh[ãa]|hoje|" + _DIAS + r"|" + _MESES +
    r"|\d{1,2}\s*de\s*" + _MESES + r"|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?"
)
_NUCLEO_NOMEADO = r"(?:" + _NUCLEO + r")"
# Acrescenta o número solto ("até 20" só faz sentido com preposição).
_NUCLEO_COM_NUMERO = r"(?:" + _NUCLEO + r"|\d{1,2})"

# Usados para limpar o título depois de identificar os pedaços.
_RE_DATA = re.compile(r"\b(?:" + _NUCLEO + r"|dia\s+\d{1,2})\b", re.I)
_RE_PREPOSICAO_DATA = re.compile(
    r"\b(?:" + _PREPOSICOES + r")\s+\b(?=" + _NUCLEO_COM_NUMERO + r")", re.I,
)
_RE_PREPOSICAO_NUMERO = re.compile(
    r"\b(?:" + _PREPOSICOES + r")\s+(?:dia\s+)?\d{1,2}"
    r"(?!\s*de\s*" + _MESES + r")\b",
    re.I,
)

# Conjunções/preposições que podem sobrar nas pontas do título.
_BORDAS = r"(?:com|para|pra|pro|até|ate|em|de|da|do|no|na|ao|e)"

# Onde procurar a data no texto: depois de preposição e depois solta.
_RE_DATA_APOS = re.compile(
    r"\b(?:" + _PREPOSICOES + r")\s+\b(?P<data>" + _NUCLEO_COM_NUMERO + r")\b",
    re.I,
)
_RE_DATA_SOLTA = re.compile(r"\b(?P<data>" + _NUCLEO_NOMEADO + r")\b", re.I)


def normalizar(valor):
    """'José' -> 'jose': remove acentos e deixa minúsculo."""
    valor = unicodedata.normalize("NFKD", valor or "")
    valor = "".join(c for c in valor if not unicodedata.combining(c))
    return valor.strip().lower()


def _parecido(palavra, outra):
    """Grau de semelhança de 0 a 1 entre duas palavras."""
    return SequenceMatcher(None, palavra, outra).ratio()


def _achar_nome(nome, palavras):
    """Procura o nome completo (por palavra inteira) nas palavras do texto.

    Devolve (início, fim) nas posições das palavras, ou None.
    Primeiro tenta igualdade exata (sem acento/maiúsculas); se não achar,
    tenta semelhança alta para tolerar pequenos erros de ditado.
    """
    alvo = normalizar(nome).split()
    if not alvo or not palavras:
        return None
    tamanho = len(alvo)

    for inicio in range(len(palavras) - tamanho + 1):
        if palavras[inicio:inicio + tamanho] == alvo:
            return inicio, inicio + tamanho

    corte = 0.85  # corte alto de propósito: melhor deixar de citar o nome
    for inicio in range(len(palavras) - tamanho + 1):
        janela = palavras[inicio:inicio + tamanho]
        nota = sum(_parecido(a, b) for a, b in zip(alvo, janela)) / tamanho
        if nota >= corte:
            return inicio, inicio + tamanho
    return None


def _achar_primeiro_nome(contatos, palavras):
    """Caso o nome completo não apareça, procura só o primeiro nome.

    É o que faz "para o Bruno" encontrar o contato "Bruno Silva".
    Se mais de um contato tiver o mesmo primeiro nome, os dois entram
    como candidatos e a chamada principal avisa sobre a ambiguidade.
    """
    achados = []
    for contato in contatos:
        nome = (getattr(contato, "nome", "") or "").split()
        if not nome:
            continue
        primeira = normalizar(nome[0])
        if not primeira:
            continue
        posicao = None
        for indice, palavra in enumerate(palavras):
            if palavra == primeira:
                posicao = (indice, indice + 1)
                break
        if posicao is None:
            for indice, palavra in enumerate(palavras):
                if _parecido(primeira, palavra) >= 0.85:
                    posicao = (indice, indice + 1)
                    break
        if posicao:
            achados.append((posicao[0], posicao[1], contato))
    return achados


def _remover_palavras(texto, posicoes, palavras):
    """Apaga do texto as palavras nas posições indicadas (preserva o resto)."""
    trechos = []
    ultimo_fim = 0
    for posicao, achado in enumerate(palavras):
        if posicao in posicoes:
            trechos.append(texto[ultimo_fim:achado.start()])
            ultimo_fim = achado.end()
    trechos.append(texto[ultimo_fim:])
    return "".join(trechos)


def _montar_titulo(texto, posicoes_removidas, palavras):
    """Monta o título retirando responsável, prazo, prioridade e ordens."""
    titulo = _remover_palavras(texto, posicoes_removidas, palavras)
    titulo = _PADRAO_TAREFA.sub(" ", titulo)
    titulo = _PADRAO_PRIORIDADE_TEXTO.sub(" ", titulo)
    titulo = _RE_PREPOSICAO_NUMERO.sub(" ", titulo)
    titulo = _RE_PREPOSICAO_DATA.sub(" ", titulo)
    titulo = _RE_DATA.sub(" ", titulo)
    titulo = re.sub(r"\s+", " ", titulo).strip()
    # tira preposições soltas que sobraram nas pontas ("... com")
    for _ in range(2):
        titulo = re.sub(r"^(?:" + _BORDAS + r")\s+", "", titulo, flags=re.I)
        titulo = re.sub(r"\s+(?:" + _BORDAS + r")$", "", titulo, flags=re.I)
    return titulo.strip(" \t\n,;:–-!?.")


def _interpretar_data(texto, agora):
    """Devolve o prazo em ISO (fuso do usuário) ou None se não achar.

    O dateparser não entende frases inteiras ("até sexta" falha), então
    primeiro destacamos só o trecho de data e mandamos ele para ele.
    """
    config = {**_CONFIG_DADOS, "RELATIVE_BASE": agora}
    candidatos = [m.group("data") for m in _RE_DATA_APOS.finditer(texto)]
    candidatos += [m.group("data") for m in _RE_DATA_SOLTA.finditer(texto)]

    for candidato in candidatos:
        try:
            momento = dateparser.parse(candidato, languages=["pt"],
                                       settings=config)
        except (ValueError, OverflowError):
            continue
        if momento:
            return momento.isoformat()
    return None


def interpretar_tarefa(texto, contatos, agora=None):
    """Sugere os campos de uma tarefa a partir de uma frase.

    Args:
        texto: o que a pessoa falou/escreveu (até 500 caracteres).
        contatos: objetos com `.nome` e `.id_contato` (os do usuário logado).
        agora: momento de referência para datas relativas ("amanhã").

    Returns:
        dict com titulo, descricao, data_inicio, data_final (ISO),
        prioridade, id_contato e avisos. Nada é gravado.
    """
    agora = agora or datetime.now(FUSO)
    if agora.tzinfo is None:  # entrada sem fuso: assume UTC
        agora = agora.replace(tzinfo=timezone.utc)

    avisos = []
    sugestao = {
        "titulo": "",
        "descricao": "",
        "data_inicio": agora.isoformat(),
        "data_final": None,
        "prioridade": "MEDIA",
        "id_contato": None,
        "avisos": avisos,
    }

    texto = (texto or "").strip()
    if not texto:
        avisos.append("Não recebi nenhum texto para interpretar.")
        return sugestao

    achados = list(re.finditer(r"\w+", texto))
    palavras = [normalizar(achado.group(0)) for achado in achados]

    # --- Responsável: compara só com os contatos recebidos ----------------
    candidatos = []
    for contato in contatos:
        nome = getattr(contato, "nome", None)
        if not nome:
            continue
        trecho = _achar_nome(nome, palavras)
        if trecho:
            candidatos.append((trecho[0], trecho[1], contato))

    if not candidatos:
        candidatos = _achar_primeiro_nome(contatos, palavras)

    posicoes_removidas = set()
    if len(candidatos) == 1:
        inicio, fim, contato = candidatos[0]
        sugestao["id_contato"] = getattr(contato, "id_contato", None)
        posicoes_removidas.update(range(inicio, fim))
        # remove também "para o" / "com a" logo antes do nome
        anterior = inicio - 1
        while anterior >= 0 and palavras[anterior] in _GATILHOS_RESPONSAVEL:
            posicoes_removidas.add(anterior)
            anterior -= 1
    elif len(candidatos) > 1:
        nomes = ", ".join(c.nome for _, _, c in candidatos)
        avisos.append(
            "Mais de um contato parece corresponder ao texto ({}); "
            "escolha o responsável manualmente.".format(nomes)
        )

    # --- Prioridade --------------------------------------------------------
    if set(palavras) & _PRIORIDADE_ALTA:
        sugestao["prioridade"] = "ALTA"
    elif set(palavras) & _PRIORIDADE_BAIXA:
        sugestao["prioridade"] = "BAIXA"
    else:
        sugestao["prioridade"] = "MEDIA"

    # --- Prazo -------------------------------------------------------------
    sugestao["data_final"] = _interpretar_data(texto, agora)
    if sugestao["data_final"] is None:
        avisos.append("Não identifiquei o prazo; preencha a data manualmente.")

    # --- Título ------------------------------------------------------------
    sugestao["titulo"] = _montar_titulo(texto, posicoes_removidas, achados)
    if not sugestao["titulo"]:
        avisos.append("Não consegui identificar o título; escreva-o manualmente.")

    return sugestao
