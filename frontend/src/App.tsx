import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";

import { askQuestion, getHealth } from "./api/client";
import { AnswerBlock } from "./components/AnswerBlock";
import { AskForm } from "./components/AskForm";
import { ErrorMessage } from "./components/ErrorMessage";
import { HealthBadge } from "./components/HealthBadge";
import { LoadingThinking } from "./components/LoadingThinking";
import type { ApiClientError, AskLimit, AskResponse } from "./types/api";

function getAskErrorMessage(error: unknown): string {
  const apiError = error as ApiClientError | undefined;

  if (apiError?.kind === "network") {
    return "Не удалось подключиться к backend. Проверьте, что сервер запущен.";
  }

  return "Не удалось получить объяснение. Проверьте настройки backend и ключ GigaChat.";
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [limit, setLimit] = useState<AskLimit>(3);
  const [formError, setFormError] = useState("");
  const [activeQuestion, setActiveQuestion] = useState("");
  const [response, setResponse] = useState<AskResponse | null>(null);

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 15000,
  });

  const askMutation = useMutation({
    mutationFn: ({ nextQuestion, nextLimit }: { nextQuestion: string; nextLimit: AskLimit }) =>
      askQuestion(nextQuestion, nextLimit),
    onMutate: ({ nextQuestion }) => {
      setActiveQuestion(nextQuestion);
      setResponse(null);
    },
    onSuccess: (data) => {
      setResponse(data);
    },
  });

  const healthState =
    healthQuery.isPending
      ? ("loading" as const)
      : healthQuery.data?.status === "ok"
        ? ("online" as const)
        : ("offline" as const);

  const resultQuestion = response?.question ?? activeQuestion;
  const hasConversation = Boolean(resultQuestion || askMutation.isPending || askMutation.isError);

  const handleQuestionChange = (value: string) => {
    setQuestion(value);

    if (formError) {
      setFormError("");
    }

    if (askMutation.isError) {
      askMutation.reset();
    }
  };

  const handleSubmit = () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setFormError("Введите вопрос для поиска");
      return;
    }

    setFormError("");
    askMutation.mutate({
      nextQuestion: trimmedQuestion,
      nextLimit: limit,
    });
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-ink text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(110,231,242,0.12),transparent_28%),radial-gradient(circle_at_80%_20%,rgba(59,130,246,0.15),transparent_22%),radial-gradient(circle_at_bottom,rgba(139,92,246,0.12),transparent_32%)]" />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-white/10" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="flex justify-end">
          <HealthBadge status={healthState} />
        </header>

        <section
          className={`mx-auto flex w-full max-w-4xl flex-1 flex-col ${
            hasConversation ? "gap-8 pb-10 pt-8" : "items-center justify-center gap-10 py-12"
          }`}
        >
          <div className={hasConversation ? "space-y-4 text-center" : "space-y-6 text-center"}>
            <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 backdrop-blur-xl">
              <Sparkles className="h-4 w-4 text-accent" />
              AI-поиск по реестру Росаккредитации
            </div>
            <div className="space-y-3">
              <h1 className="font-display text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
                ReestrPro
              </h1>
              <p className="mx-auto max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
                Поиск сертификатов и деклараций соответствия с объяснением результата
              </p>
            </div>
          </div>

          <AskForm
            question={question}
            limit={limit}
            isLoading={askMutation.isPending}
            errorMessage={formError}
            compact={hasConversation}
            onQuestionChange={handleQuestionChange}
            onLimitChange={setLimit}
            onSubmit={handleSubmit}
          />

          {askMutation.isPending && resultQuestion ? (
            <div className="space-y-4">
              <AnswerBlock question={resultQuestion} answer="" sources={[]} isPending />
              <LoadingThinking />
            </div>
          ) : null}

          {!askMutation.isPending && askMutation.isError ? (
            <div className="space-y-4">
              {resultQuestion ? (
                <AnswerBlock question={resultQuestion} answer="" sources={[]} isError />
              ) : null}
              <ErrorMessage message={getAskErrorMessage(askMutation.error)} />
            </div>
          ) : null}

          {response ? (
            <AnswerBlock
              question={response.question}
              answer={response.answer}
              sources={response.sources}
            />
          ) : null}
        </section>
      </div>
    </main>
  );
}
