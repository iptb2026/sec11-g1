// Suggests a unique-looking reference number for a new transaction, e.g.
// newReference('DEP') -> "DEP-20261024-153012-482". Staff can still change it;
// the backend rejects duplicates.
export function newReference (prefix) {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const date = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`
  const time = `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
  const random = String(Math.floor(Math.random() * 1000)).padStart(3, '0')
  return `${prefix}-${date}-${time}-${random}`
}
