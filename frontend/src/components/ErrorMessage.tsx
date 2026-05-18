import { AlertCircle } from "lucide-react";

interface ErrorMessageProps {
  message: string;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="rounded-[24px] border border-rose-300/15 bg-rose-300/10 p-4 text-sm text-rose-100 backdrop-blur-xl">
      <div className="flex items-start gap-3">
        <AlertCircle className="mt-0.5 h-5 w-5 flex-none" />
        <p className="leading-6">{message}</p>
      </div>
    </div>
  );
}
