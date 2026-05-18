import { Activity, LoaderCircle, WifiOff } from "lucide-react";

interface HealthBadgeProps {
  status: "loading" | "online" | "offline";
}

const statusMap = {
  loading: {
    label: "Проверка backend",
    icon: <LoaderCircle className="h-4 w-4 animate-spin" />,
    className: "border-amber-300/20 bg-amber-300/10 text-amber-100",
  },
  online: {
    label: "Backend доступен",
    icon: <Activity className="h-4 w-4" />,
    className: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  },
  offline: {
    label: "Backend недоступен",
    icon: <WifiOff className="h-4 w-4" />,
    className: "border-rose-300/20 bg-rose-300/10 text-rose-100",
  },
};

export function HealthBadge({ status }: HealthBadgeProps) {
  const current = statusMap[status];

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-medium backdrop-blur-xl ${current.className}`}
    >
      {current.icon}
      <span>{current.label}</span>
    </div>
  );
}
