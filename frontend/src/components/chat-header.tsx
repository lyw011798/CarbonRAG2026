export const ChatHeader = () => (
  <header className="border-b border-white/10 bg-slate-950/80 px-5 py-4 backdrop-blur md:px-8">
    <div className="mx-auto flex max-w-5xl flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div className="icon shrink-0">
        <img
          src="icon.png"
          alt="CarbonRAG Logo"
          className="h-16 w-16 object-contain md:h-20 md:w-20"
        />
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300/80">
          CarbonRAG
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white md:text-3xl">
          Taiwan Carbon Marketing AI Chat
        </h1>
      </div>
      <p className="max-w-xl text-sm leading-6 text-slate-300">
        Ask the knowledge base through a clean chat interface.
      </p>
    </div>
  </header>
);
