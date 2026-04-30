type ErrorBannerProps = {
  message: string
  onDismiss: () => void
}

export const ErrorBanner = ({ message, onDismiss }: ErrorBannerProps) => (
  <div className="mx-auto flex w-full max-w-3xl items-start gap-3 rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-left text-sm text-rose-100 shadow-lg shadow-rose-950/20">
    <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-rose-400/20 text-xs font-semibold text-rose-100">
      !
    </div>
    <p className="min-w-0 flex-1 leading-6">{message}</p>
    <button
      type="button"
      onClick={onDismiss}
      className="rounded-full px-2 py-1 text-xs font-medium text-rose-100/80 transition hover:bg-rose-100/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-rose-200/50"
      aria-label="Dismiss error"
    >
      Dismiss
    </button>
  </div>
)
