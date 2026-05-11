import { TooltipProvider } from '@/components/ui/Tooltip'
import { AppRouter } from '@/router'

export default function App() {
  return (
    <TooltipProvider>
      <AppRouter />
    </TooltipProvider>
  )
}
