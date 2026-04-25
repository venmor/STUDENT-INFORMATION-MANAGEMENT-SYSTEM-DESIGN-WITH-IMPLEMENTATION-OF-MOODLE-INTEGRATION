export function aiFeatureUnavailable() {
  return Promise.reject(
    new Error('AI endpoints are not implemented in the current Step 2.4 backend contract.'),
  )
}
