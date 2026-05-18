import type { ReactNode } from "react";
import { Bot, UserRound } from "lucide-react";

import type { RagSource } from "../types/api";
import { SourceCard } from "./SourceCard";

interface AnswerBlockProps {
  question: string;
  answer: string;
  sources: RagSource[];
  isPending?: boolean;
  isError?: boolean;
}

function ChatMessage({
  title,
  icon,
  children,
}: {
  title: string;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <article className="surface-card rounded-[28px] p-5 shadow-glow sm:p-6">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] text-slate-100">
          {icon}
        </div>
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">{title}</h2>
      </div>
      <div className="text-sm leading-7 text-slate-100 sm:text-[15px]">{children}</div>
    </article>
  );
}

export function AnswerBlock({
  question,
  answer,
  sources,
  isPending = false,
  isError = false,
}: AnswerBlockProps) {
  return (
    <div className="space-y-4">
      <ChatMessage
        title="Вы"
        icon={<UserRound className="h-5 w-5 text-accent" />}
      >
        <p className="whitespace-pre-wrap">{question}</p>
      </ChatMessage>

      <ChatMessage
        title="ReestrPro"
        icon={<Bot className="h-5 w-5 text-accent" />}
      >
        {isPending ? (
          <p className="text-slate-400">Сервис готовит ответ...</p>
        ) : isError ? (
          <p className="text-slate-400">Ответ не был сформирован.</p>
        ) : (
          <p className="whitespace-pre-wrap">{answer}</p>
        )}
      </ChatMessage>

      {!isPending && !isError ? (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">
              Использованные документы
            </h3>
            <span className="text-xs text-slate-500">{sources.length} шт.</span>
          </div>

          {sources.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {sources.map((source) => (
                <SourceCard
                  key={`${source.document_id}-${source.document_number ?? "empty"}`}
                  source={source}
                />
              ))}
            </div>
          ) : (
            <div className="surface-card rounded-[24px] p-5 text-sm text-slate-400">
              Backend не вернул список использованных документов.
            </div>
          )}
        </section>
      ) : null}
    </div>
  );
}
