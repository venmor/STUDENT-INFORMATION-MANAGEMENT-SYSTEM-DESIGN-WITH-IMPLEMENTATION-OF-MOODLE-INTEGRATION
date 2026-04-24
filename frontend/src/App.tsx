import { BrowserRouter } from 'react-router-dom'

import { AppProviders } from '@/app/app-providers'
import { AppRoutes } from '@/app/app-routes'

export default function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AppProviders>
  )
}
