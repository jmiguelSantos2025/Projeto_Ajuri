const themeToggle = document.querySelector("[data-theme-toggle]")
const updateThemeToggle = (theme) => {
  if (!themeToggle) return
  const dark = theme === "dark"
  themeToggle.textContent = dark ? "☀ Tema claro" : "☾ Tema escuro"
  themeToggle.setAttribute("aria-label", dark ? "Ativar modo claro" : "Ativar modo escuro")
  themeToggle.setAttribute("aria-pressed", String(dark))
}

const currentTheme =
  document.documentElement.dataset.theme === "dark" ? "dark" : "light"
document.documentElement.dataset.theme = currentTheme
updateThemeToggle(currentTheme)

themeToggle?.addEventListener("click", () => {
  const nextTheme =
    document.documentElement.dataset.theme === "dark" ? "light" : "dark"
  document.documentElement.dataset.theme = nextTheme
  updateThemeToggle(nextTheme)
  try {
    localStorage.setItem("ajuri-theme", nextTheme)
  } catch (error) {
    console.error("Não foi possível salvar a preferência de tema do Ajuri.", error)
  }
})

document.querySelectorAll("[data-password-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.passwordToggle)
    if (!input) return
    const showing = input.type === "text"
    input.type = showing ? "password" : "text"
    button.textContent = showing ? "Mostrar" : "Ocultar"
    button.setAttribute(
      "aria-label",
      showing ? "Mostrar senha" : "Ocultar senha",
    )
  })
})

document.querySelectorAll("[data-open-modal]").forEach((button) => {
  button.addEventListener("click", () => {
    const dialog = document.getElementById(button.dataset.openModal)
    // Guarda o id da tarefa no formulário da janela (usado para excluir)
    const campoId = dialog?.querySelector("[name=id_tarefa]")
    if (campoId && button.dataset.idTarefa) campoId.value = button.dataset.idTarefa
    dialog?.showModal()
  })
})

document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog")?.close())
})

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close()
  })
})

const rows = [...document.querySelectorAll(".task-row")]
const taskList = document.querySelector(".task-list")
const markTaskEntryComplete = (event) => {
  if (event.target instanceof Element && event.target.matches(".task-row")) {
    event.target.dataset.entered = "true"
  }
}
taskList?.querySelectorAll(".task-row").forEach((row) => {
  const entryAlreadyFinished = (row.getAnimations?.() || [])
    .some(
      (animation) =>
        animation.animationName === "task-enter" &&
        animation.playState === "finished",
    )
  if (entryAlreadyFinished) row.dataset.entered = "true"
})
taskList?.addEventListener("animationend", markTaskEntryComplete)
taskList?.addEventListener("animationcancel", markTaskEntryComplete)
const filters = [...document.querySelectorAll("[data-filter]")]
const search = document.querySelector("[data-task-search]")
const emptyState = document.querySelector("[data-empty-state]")
const applyTaskFilters = () => {
  const active =
    document.querySelector("[data-filter].is-active")?.dataset.filter || "todas"
  const term = (search?.value || "").trim().toLocaleLowerCase("pt-BR")
  let visible = 0
  rows.forEach((row) => {
    const statusMatches = active === "todas" || row.dataset.status === active
    const textMatches =
      !term || row.textContent.toLocaleLowerCase("pt-BR").includes(term)
    row.hidden = !(statusMatches && textMatches)
    if (!row.hidden) visible += 1
  })
  if (emptyState) emptyState.hidden = visible > 0
}
filters.forEach((filter) =>
  filter.addEventListener("click", () => {
    filters.forEach((item) => {
      item.classList.remove("is-active")
      item.setAttribute("aria-pressed", "false")
    })
    filter.classList.add("is-active")
    filter.setAttribute("aria-pressed", "true")
    applyTaskFilters()
  }),
)
search?.addEventListener("input", applyTaskFilters)

document.querySelector("[data-request-save]")?.addEventListener("click", () => {
  const confirmation = document.querySelector("[data-save-confirmation]")
  if (confirmation) {
    confirmation.hidden = false
    confirmation.scrollIntoView({ behavior: "smooth", block: "nearest" })
  }
})
document.querySelector("[data-cancel-save]")?.addEventListener("click", () => {
  const confirmation = document.querySelector("[data-save-confirmation]")
  if (confirmation) confirmation.hidden = true
})
// Token anti-CSRF das requisições feitas com fetch (rotas que só aceitam JSON)
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content

// Iniciar / Concluir tarefa: envia JSON para /tarefas/<id>/status e recarrega
// para a lista mostrar o novo status (inclusive "atrasada", calculado no servidor).
document.querySelectorAll("[data-status-tarefa]").forEach((botao) => {
  botao.addEventListener("click", async () => {
    const id = botao.dataset.statusTarefa
    const novoStatus = botao.dataset.novoStatus
    botao.disabled = true
    try {
      const resposta = await fetch(`/tarefas/${id}/status`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrfToken || "",
        },
        body: JSON.stringify({ status: novoStatus }),
      })
      if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`)
      window.location.reload()
    } catch (erro) {
      console.error("Não foi possível mudar o status da tarefa.", erro)
      botao.disabled = false
      alert("Não foi possível atualizar o status. Recarregue a página e tente de novo.")
    }
  })
})

document.querySelectorAll('form').forEach(function (form) {
  form.addEventListener('submit', function () {
    form.querySelectorAll('button[type="submit"]').forEach(function (botao) {
      botao.disabled = true;
    });
  });
});