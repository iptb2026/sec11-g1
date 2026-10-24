import { defineBoot } from '#q-app'

// On phones every table row is shown as a card with the column name next to
// each value (see "Phones" in css/app.css). CSS can't read the header row, so
// this copies each header's text onto the cells below it as data-label,
// for every q-table, whenever tables render or change.

// Header text without the sort arrow icon (a q-icon's text is its icon name).
function headerText (th) {
  return [...th.childNodes]
    .filter((node) => node.nodeType === Node.TEXT_NODE)
    .map((node) => node.textContent)
    .join('')
    .trim()
}

function labelTables () {
  document.querySelectorAll('table.q-table').forEach((table) => {
    const labels = [...table.querySelectorAll('thead th')].map(headerText)
    table.querySelectorAll('tbody tr').forEach((tr) => {
      [...tr.children].forEach((td, i) => {
        const label = labels[i] || ''
        if (td.dataset.label !== label) td.dataset.label = label
      })
    })
  })
}

export default defineBoot(() => {
  let queued = false
  new MutationObserver(() => {
    if (queued) return
    queued = true
    requestAnimationFrame(() => {
      queued = false
      labelTables()
    })
  }).observe(document.body, { childList: true, subtree: true })
})
