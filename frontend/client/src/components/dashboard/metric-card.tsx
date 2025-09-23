import { cn } from "@/lib/utils";
import { Reply, Target, MousePointer, Users } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change: string;
  changeLabel: string;
  icon: "reply" | "bullseye" | "mouse-pointer" | "users";
  emoji: string;
  color: "emerald" | "blue" | "amber" | "purple";
}

const iconMap = {
  reply: Reply,
  bullseye: Target,
  "mouse-pointer": MousePointer,
  users: Users,
};

const colorMap = {
  emerald: {
    bg: "bg-emerald-100",
    text: "text-emerald-600",
    change: "text-emerald-600",
  },
  blue: {
    bg: "bg-blue-100",
    text: "text-blue-600",
    change: "text-blue-600",
  },
  amber: {
    bg: "bg-amber-100",
    text: "text-amber-600",
    change: "text-amber-600",
  },
  purple: {
    bg: "bg-purple-100",
    text: "text-purple-600",
    change: "text-purple-600",
  },
};

export default function MetricCard({
  title,
  value,
  change,
  changeLabel,
  icon,
  emoji,
  color,
}: MetricCardProps) {
  const IconComponent = iconMap[icon];
  const colors = colorMap[color];

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className={cn("w-12 h-12 rounded-lg flex items-center justify-center", colors.bg)}>
          <IconComponent className={cn("text-xl", colors.text)} size={20} />
        </div>
        <span className="text-2xl">{emoji}</span>
      </div>
      <h3 
        className="text-2xl font-bold text-gray-900" 
        data-testid={`metric-${title.toLowerCase().replace(/\s+/g, "-")}`}
      >
        {value}
      </h3>
      <p className="text-gray-600">{title}</p>
      <div className="flex items-center mt-2">
        <span className={cn("text-sm font-medium", colors.change)}>{change}</span>
        <span className="text-gray-500 text-sm ml-1">{changeLabel}</span>
      </div>
    </div>
  );
}
