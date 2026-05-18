import { Sparkles } from "lucide-react";

export function LoadingThinking() {
  return (
    <div className="surface-card rounded-[28px] p-5 shadow-glow sm:p-6">
      <div className="flex items-center gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/10 text-cyan-100">
          <Sparkles className="h-5 w-5 animate-pulse" />
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-100">Сервис анализирует документы...</p>
          <div className="thinking-dots flex items-center gap-1">
            <span />
            <span />
            <span />
          </div>
        </div>
      </div>
    </div>
  );
}
