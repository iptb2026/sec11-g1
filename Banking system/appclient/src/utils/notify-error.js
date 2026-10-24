// Turns an Axios error from the FastAPI backend into a readable message.
// `detail` is a string for 400/404 errors, but a list of
// { loc, msg, ... } objects for 422 validation errors.
export function errorMessage (err, fallback = 'Something went wrong') {
  const status = err?.response?.status
  const detail = err?.response?.data?.detail

  if (status === 403) {
    return "You don't have permission for this"
  }
  if (status === 405) {
    return "This can't be changed here"
  }

  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : null
        return field && field !== 'body' ? `${field}: ${d.msg}` : d.msg
      })
      .join(', ')
  }
  if (!err?.response) {
    return 'Could not reach the backend API'
  }
  return fallback
}
