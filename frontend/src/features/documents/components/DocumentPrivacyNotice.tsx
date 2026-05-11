import { ShieldCheckIcon } from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Card, CardTitle } from '@/components/ui/Card'

export function DocumentPrivacyNotice({ studentUploadEnabled = false }: { studentUploadEnabled?: boolean }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
      <Alert title="Document privacy" icon={<ShieldCheckIcon className="h-5 w-5" />}>
        Documents are access-controlled and audit logged. File downloads use the protected API and do not expose raw
        storage paths.
      </Alert>
      <Card className="p-4">
        <CardTitle>Current Scope</CardTitle>
        <p className="mt-2 text-sm leading-6 text-neutral-600">
          This module manages student-linked institutional documents. It does not implement admissions intake, OCR, AI
          document analysis, e-signatures, permanent deletion, or external cloud storage. Step 3.5G Admissions remains
          optional/future.
        </p>
        <p className="mt-2 text-sm text-neutral-600">
          {studentUploadEnabled
            ? 'Students may upload supporting files for review.'
            : 'Admins manage upload and review workflows from the repository.'}
        </p>
      </Card>
    </div>
  )
}
