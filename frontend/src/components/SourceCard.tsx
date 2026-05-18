import { CircleCheck, FileText, Hash, Package, ShieldCheck } from "lucide-react";

import type { RagSource } from "../types/api";

interface SourceCardProps {
  source: RagSource;
}

function getDocumentTypeLabel(documentType: string) {
  if (documentType === "declaration") {
    return "Декларация";
  }

  if (documentType === "certificate") {
    return "Сертификат";
  }

  return documentType || "Не указано";
}

function fallbackValue(value: string | null) {
  return value?.trim() ? value : "Не указано";
}

export function SourceCard({ source }: SourceCardProps) {
  return (
    <article className="surface-card rounded-[24px] p-5 transition duration-200 hover:-translate-y-0.5 hover:border-white/15 hover:bg-white/[0.06]">
      <div className="mb-5 flex items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-100">
            <ShieldCheck className="h-3.5 w-3.5" />
            {getDocumentTypeLabel(source.document_type)}
          </div>
          <p className="text-xs text-slate-500">ID: {source.document_id}</p>
        </div>
        <FileText className="h-5 w-5 flex-none text-slate-500" />
      </div>

      <div className="space-y-4 text-sm text-slate-200">
        <div className="flex gap-3">
          <Hash className="mt-0.5 h-4 w-4 flex-none text-accent" />
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Номер документа</p>
            <p className="mt-1 break-words leading-6">{fallbackValue(source.document_number)}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <CircleCheck className="mt-0.5 h-4 w-4 flex-none text-accentSoft" />
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Статус</p>
            <p className="mt-1 break-words leading-6">{fallbackValue(source.status)}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <Package className="mt-0.5 h-4 w-4 flex-none text-emerald-300" />
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Продукция</p>
            <p className="mt-1 break-words leading-6">{fallbackValue(source.product_full_name)}</p>
          </div>
        </div>
      </div>
    </article>
  );
}
