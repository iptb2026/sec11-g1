// Every date and time is shown in Philippine time, whatever time zone the
// phone or computer is set to. The API stores and sends UTC.
export const TIME_ZONE = 'Asia/Manila'

// The API sends UTC datetimes without a zone ("2026-10-25T03:37:44");
// mark them as UTC so they convert correctly.
export function parseApiDateTime (val) {
  const text = String(val)
  return new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(text) ? text : text + 'Z')
}

// The hour of the day (0-23) in Philippine time, e.g. for "Good morning".
export function manilaHour (date = new Date()) {
  return Number(new Intl.DateTimeFormat('en-US', { hour: 'numeric', hourCycle: 'h23', timeZone: TIME_ZONE }).format(date))
}
