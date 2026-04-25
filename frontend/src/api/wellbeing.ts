export function wellbeingFeatureUnavailable() {
  return Promise.reject(
    new Error('Wellbeing endpoints are not implemented in the current Step 2.4 backend contract.'),
  )
}
