import { type PlatformStats } from "@shared/schema";
import { cn } from "@/lib/utils";
import { SiX, SiReddit, SiQuora } from "react-icons/si";

interface PlatformCardProps {
  platform: PlatformStats;
}

const platformConfig = {
  twitter: {
    name: "X (Twitter)",
    icon: SiX,
    gradient: "from-gray-900/5 to-blue-50",
    border: "border-gray-900/20",
    color: "text-gray-900",
  },
  reddit: {
    name: "Reddit",
    icon: SiReddit,
    gradient: "from-orange-500/5 to-orange-50",
    border: "border-orange-500/20",
    color: "text-orange-500",
  },
  quora: {
    name: "Quora",
    icon: SiQuora,
    gradient: "from-red-600/5 to-red-50",
    border: "border-red-600/20",
    color: "text-red-600",
  },
};

export default function PlatformCard({ platform }: PlatformCardProps) {
  const config = platformConfig[platform.platform as keyof typeof platformConfig];
  
  if (!config) return null;

  return (
    <div 
      className={cn(
        "border-2 rounded-lg p-4 bg-gradient-to-br",
        config.border,
        config.gradient
      )}
      data-testid={`platform-card-${platform.platform}`}
    >
      <div className="flex items-center justify-between mb-3">
        <config.icon className={`text-2xl ${config.color}`} />
        <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full text-xs font-medium">
          {platform.isActive ? "Active" : "Inactive"}
        </span>
      </div>
      <h3 className="font-semibold text-gray-900 mb-1">{config.name}</h3>
      <p className="text-sm text-gray-600 mb-2">
        {platform.repliesPosted} {platform.platform === 'reddit' ? 'comments' : platform.platform === 'quora' ? 'answers' : 'replies'} posted
      </p>
      <div className="flex items-center text-sm">
        <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div>
        <span className="text-gray-600">
          {platform.accountsConnected} account{platform.accountsConnected !== 1 ? 's' : ''} connected
        </span>
      </div>
    </div>
  );
}
