export function Footer() {
  const currentYear =
    new Date().getFullYear()

  return (
    <footer className="border-t bg-white px-6 py-4">
      <div className="flex flex-col items-center justify-between gap-2 text-sm text-slate-500 sm:flex-row">
        <p>
          © {currentYear} Enterprise AI
          Workspace
        </p>

        <p>
          Secure enterprise intelligence
          platform
        </p>
      </div>
    </footer>
  )
}