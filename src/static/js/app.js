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
