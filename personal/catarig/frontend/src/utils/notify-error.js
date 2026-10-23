// Turns an Axios error from the FastAPI backend into a readable message.
// `detail` is a string for 400/404 errors, but a list of
// { loc, msg, ... } objects for 422 validation errors.
export function errorMessage (err, fallback = 'Something went wrong') {
  const detail = err?.response?.data?.detail

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
