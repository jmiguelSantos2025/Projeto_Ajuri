// Criação de tarefa por voz.
//
// Usa a Web Speech API do navegador para transcrever uma frase em pt-BR,
// envia o texto para /api/tarefas/interpretar e preenche o formulário
// "Nova tarefa". Nada é salvo aqui: o envio passa pelas validações do
// formulário normal, que a pessoa confere antes de salvar.
//
// Observação: a transcrição é feita pelo navegador e pode passar pelos
// servidores dele (por exemplo, do Google/Microsoft).

const formulario = document.querySelector("#task-modal form")

if (formulario) {
  const tokenCsrf = document.querySelector('meta[name="csrf-token"]')?.content
  const Reconhecimento =
    window.SpeechRecognition || window.webkitSpeechRecognition

  // --- Monta a interface de voz reaproveitando as classes existentes -----
  const areaVoz = document.createElement("div")
  areaVoz.className = "field field--wide"
  areaVoz.innerHTML = `
    <span class="field-label">Preencher por voz</span>
    <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center">
      <button class="btn btn--secondary" type="button" data-voz-botao
              aria-label="Gravar áudio e preencher a tarefa por voz"
              aria-pressed="false">Falar tarefa</button>
      <button class="btn btn--secondary" type="button" data-voz-interpretar hidden>
        Interpretar texto
      </button>
    </div>
    <input class="input" data-voz-transcricao aria-label="Texto reconhecido pela voz"
           placeholder="O que você falou aparece aqui para você corrigir">
    <p class="field-hint" data-voz-status role="status" aria-live="polite">
      A transcrição é feita pelo navegador e pode passar pelos servidores dele.
    </p>
  `
  const grade = formulario.querySelector(".form-grid")
  formulario.insertBefore(areaVoz, grade || formulario.firstChild)

  const botaoVoz = areaVoz.querySelector("[data-voz-botao]")
  const botaoInterpretar = areaVoz.querySelector("[data-voz-interpretar]")
  const entradaTexto = areaVoz.querySelector("[data-voz-transcricao]")
  const status = areaVoz.querySelector("[data-voz-status]")

  const campo = (id) => formulario.querySelector(`#${id}`)

  // Aviso (verde/vermelho) no topo do formulário, usando o estilo de notice.
  const aviso = document.createElement("div")
  aviso.hidden = true
  formulario.insertBefore(aviso, areaVoz)

  function mostrarStatus(texto) {
    status.textContent = texto
  }

  function mostrarAvisos(textos, tipo) {
    aviso.hidden = false
    aviso.className = `notice notice--${tipo === "sucesso" ? "success" : "error"}`
    aviso.setAttribute("role", tipo === "sucesso" ? "status" : "alert")
    aviso.textContent = ""
    textos.forEach((texto) => {
      const linha = document.createElement("p")
      linha.textContent = texto
      aviso.appendChild(linha)
    })
  }

  // --- Estados do botão: parado (3 visíveis), ouvindo e processando ------
  function definirEstado(estado) {
    botaoVoz.classList.remove("btn--danger")
    botaoVoz.disabled = false
    botaoVoz.removeAttribute("aria-busy")
    if (estado === "ouvindo") {
      botaoVoz.textContent = "Ouvindo… (clique para parar)"
      botaoVoz.classList.add("btn--danger")
      botaoVoz.setAttribute("aria-label", "Parar de gravar áudio")
      botaoVoz.setAttribute("aria-pressed", "true")
    } else if (estado === "processando") {
      botaoVoz.textContent = "Processando…"
      botaoVoz.disabled = true
      botaoVoz.setAttribute("aria-busy", "true")
      botaoVoz.setAttribute("aria-label", "Interpretando o que você falou")
      botaoVoz.setAttribute("aria-pressed", "false")
    } else {
      botaoVoz.textContent = "Falar tarefa"
      botaoVoz.setAttribute("aria-label", "Gravar áudio e preencher a tarefa por voz")
      botaoVoz.setAttribute("aria-pressed", "false")
    }
  }

  // --- Preenche os campos e marca os que vieram da voz -------------------
  function preencher(sugestao) {
    const preenchidos = []
    const faltando = []

    const marcar = (elemento) => {
      elemento.dataset.preenchidoPorVoz = "true"
      // Destaque simples, sem mexer no CSS: contorno na cor de foco.
      elemento.style.outline = "2px solid var(--color-focus)"
      elemento.style.outlineOffset = "2px"
    }

    const titulo = campo("titulo")
    if (sugestao.titulo) {
      titulo.value = sugestao.titulo
      marcar(titulo)
      preenchidos.push("Título")
    } else {
      faltando.push("Título")
    }

    const descricao = campo("descricao")
    if (sugestao.descricao) {
      descricao.value = sugestao.descricao
      marcar(descricao)
      preenchidos.push("Descrição")
    }

    const prazo = campo("data_final")
    if (sugestao.data_final) {
      prazo.value = sugestao.data_final.slice(0, 10) // ISO -> YYYY-MM-DD
      marcar(prazo)
      preenchidos.push("Prazo")
    } else {
      faltando.push("Prazo")
    }

    const prioridade = campo("prioridade")
    if (prioridade && sugestao.prioridade) {
      prioridade.value = sugestao.prioridade
      marcar(prioridade)
      preenchidos.push("Prioridade")
    }

    const contato = campo("id_contato")
    if (contato) {
      if (sugestao.id_contato !== null && sugestao.id_contato !== undefined) {
        contato.value = String(sugestao.id_contato)
        marcar(contato)
        preenchidos.push("Responsável")
      } else {
        contato.value = "" // sem responsável é válido
      }
    }

    const resumo = preenchidos.length
      ? `Preenchidos por voz: ${preenchidos.join(", ")}.`
      : "Nada foi preenchido automaticamente."
    const pendencia = faltando.length
      ? ` Falta preencher: ${faltando.join(", ")}.`
      : ""
    mostrarAvisos([resumo + pendencia], "sucesso")

    if (sugestao.avisos && sugestao.avisos.length) {
      sugestao.avisos.forEach((texto) => {
        const extra = document.createElement("p")
        extra.textContent = `Atenção: ${texto}`
        aviso.appendChild(extra)
      })
    }

    // Leva o cursor ao primeiro campo que ficou faltando.
    const primeiroVazio = (faltando.includes("Título") && titulo) ||
      (faltando.includes("Prazo") && prazo)
    if (primeiroVazio) primeiroVazio.focus()
  }

  // Ao editar um campo marcado, tira o destaque (já não é mais "da voz").
  formulario.addEventListener("input", (evento) => {
    const elemento = evento.target
    if (elemento instanceof HTMLElement && elemento.dataset.preenchidoPorVoz) {
      delete elemento.dataset.preenchidoPorVoz
      elemento.style.outline = ""
      elemento.style.outlineOffset = ""
    }
  })

  // --- Envia o texto para o backend --------------------------------------
  async function interpretar() {
    const texto = entradaTexto.value.trim()
    if (!texto) {
      mostrarStatus("Fale ou digite algo antes de interpretar.")
      return
    }
    definirEstado("processando")
    mostrarStatus("Interpretando o texto…")
    try {
      const resposta = await fetch("/api/tarefas/interpretar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": tokenCsrf || "",
        },
        body: JSON.stringify({ texto }),
      })
      const corpo = await resposta.json().catch(() => ({}))
      if (!resposta.ok) {
        throw new Error(corpo.erro || `Erro ${resposta.status}`)
      }
      preencher(corpo)
      mostrarStatus("Pronto! Confira os campos e salve a tarefa.")
    } catch (erro) {
      console.error("Falha ao interpretar a tarefa por voz.", erro)
      mostrarStatus(`Não foi possível interpretar: ${erro.message}`)
    } finally {
      definirEstado("parado")
    }
  }

  botaoInterpretar.addEventListener("click", interpretar)

  // --- Reconhecimento de voz ---------------------------------------------
  if (!Reconhecimento) {
    mostrarStatus(
      "Seu navegador não suporta ditado por voz. Preencha o formulário normalmente.",
    )
    botaoVoz.disabled = true
  } else {
    const reconhecimento = new Reconhecimento()
    reconhecimento.lang = "pt-BR"
    reconhecimento.interimResults = true
    reconhecimento.continuous = false // uma frase por vez
    reconhecimento.maxAlternatives = 1

    let falhou = false

    reconhecimento.onstart = () => {
      falhou = false
      entradaTexto.value = ""
      definirEstado("ouvindo")
      mostrarStatus("Ouvindo… fale a tarefa em uma frase.")
    }

    reconhecimento.onresult = (evento) => {
      let texto = ""
      for (let i = 0; i < evento.results.length; i += 1) {
        texto += evento.results[i][0].transcript
      }
      entradaTexto.value = texto
      botaoInterpretar.hidden = false
    }

    reconhecimento.onerror = (evento) => {
      falhou = true
      const mensagens = {
        "not-allowed": "Permita o acesso ao microfone no navegador para usar a voz.",
        "service-not-allowed": "O ditado por voz não está disponível neste navegador.",
        "no-speech": "Não ouvi nada. Tente de novo.",
        "audio-capture": "Não encontrei um microfone no seu dispositivo.",
        network: "Houve uma falha de rede no reconhecimento de voz.",
      }
      mostrarStatus(mensagens[evento.error] || "Não consegui ouvir. Tente de novo.")
    }

    reconhecimento.onend = () => {
      // Se terminou sozinho e temos texto, já interpreta.
      if (!falhou && entradaTexto.value.trim()) {
        interpretar()
      } else {
        definirEstado("parado")
      }
    }

    botaoVoz.addEventListener("click", () => {
      if (botaoVoz.getAttribute("aria-pressed") === "true") {
        reconhecimento.stop() // já está ouvindo: o clique serve para parar
      } else {
        try {
          reconhecimento.start()
        } catch (erro) {
          // start() reclama se já estiver ouvindo; nesse caso, ignora.
          console.error("Não foi possível iniciar o reconhecimento.", erro)
        }
      }
    })
  }
}
