export function QuickExitButton() {
  return (
    <a
      href="https://www.example.edu"
      onClick={() => sessionStorage.clear()}
      className="fixed right-4 top-4 z-20 rounded bg-neutral-900 px-3 py-1.5 text-xs text-white"
    >
      Quick Exit
    </a>
  )
}
