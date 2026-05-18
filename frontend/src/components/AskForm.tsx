import { useState, type KeyboardEvent } from "react";
import { ChevronDown, Search, Settings2 } from "lucide-react";

import type { AskLimit } from "../types/api";

interface AskFormProps {
  question: string;
  limit: AskLimit;
  isLoading: boolean;
  errorMessage?: string;
  compact?: boolean;
  onQuestionChange: (value: string) => void;
  onLimitChange: (value: AskLimit) => void;
  onSubmit: () => void;
}

export function AskForm({
  question,
  limit,
  isLoading,
  errorMessage,
  compact = false,
  onQuestionChange,
  onLimitChange,
  onSubmit,
}: AskFormProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="surface-card w-full rounded-[28px] p-4 shadow-glow sm:p-5">
      <div className="flex flex-col gap-4">
        <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-3">
          <textarea
            value={question}
            rows={compact ? 4 : 5}
            placeholder="Например: Найди документ на детскую одежду и объясни, почему он подходит"
            className="min-h-[132px] w-full resize-none border-none bg-transparent px-2 py-3 text-base leading-7 text-slate-100 outline-none placeholder:text-slate-500"
            onChange={(event) => onQuestionChange(event.target.value)}
            onKeyDown={handleKeyDown}
          />

          <div className="mt-4 flex flex-col gap-3 border-t border-white/10 pt-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Search className="h-4 w-4 text-accent" />
              <span>Отправка запроса по Ctrl/Cmd + Enter</span>
            </div>

            <button
              type="button"
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:bg-slate-500"
              disabled={isLoading}
              onClick={onSubmit}
            >
              <Search className="h-4 w-4" />
              Найти и объяснить
            </button>
          </div>
        </div>

        <div className="rounded-[24px] border border-white/10 bg-white/[0.03]">
          <button
            type="button"
            className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm text-slate-200 transition hover:bg-white/[0.03] sm:px-5"
            onClick={() => setIsSettingsOpen((current) => !current)}
          >
            <span className="inline-flex items-center gap-2 font-medium">
              <Settings2 className="h-4 w-4 text-accent" />
              Расширенные настройки
            </span>
            <ChevronDown
              className={`h-4 w-4 text-slate-400 transition ${isSettingsOpen ? "rotate-180" : ""}`}
            />
          </button>

          {isSettingsOpen ? (
            <div className="border-t border-white/10 px-4 py-4 sm:px-5">
              <label className="flex flex-col gap-2 text-sm text-slate-300">
                <span>Количество источников</span>
                <select
                  value={limit}
                  className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent"
                  onChange={(event) => onLimitChange(Number(event.target.value) as AskLimit)}
                >
                  <option value={3}>3</option>
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                </select>
              </label>
            </div>
          ) : null}
        </div>

        {errorMessage ? <p className="px-1 text-sm text-rose-300">{errorMessage}</p> : null}
      </div>
    </div>
  );
}
