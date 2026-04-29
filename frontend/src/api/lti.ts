import type { LtiSessionContext } from '@/types/lti'

export async function fetchLtiSessionContext(tool: LtiSessionContext['tool']): Promise<LtiSessionContext> {
  const response = await fetch(`/lti/api/session?tool=${encodeURIComponent(tool)}`, {
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    const fallbackMessage = response.status === 401 ? 'This LTI launch session is missing or expired.' : 'Unable to load this LTI tool.'
    try {
      const payload = (await response.json()) as { error?: { message?: string } }
      throw new Error(payload.error?.message ?? fallbackMessage)
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error(fallbackMessage, { cause: error })
    }
  }

  return response.json() as Promise<LtiSessionContext>
}
