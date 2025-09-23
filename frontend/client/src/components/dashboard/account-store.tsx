import { type Account } from "@shared/schema";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";
import { SiX, SiReddit, SiQuora } from "react-icons/si";

interface AccountStoreProps {
  accounts: Account[];
  isLoading: boolean;
}

const platformConfig = {
  twitter: {
    name: "X (Twitter) Accounts",
    icon: SiX,
    color: "text-gray-900",
  },
  reddit: {
    name: "Reddit Accounts",
    icon: SiReddit,
    color: "text-orange-500",
  },
  quora: {
    name: "Quora Accounts",
    icon: SiQuora,
    color: "text-red-600",
  },
};

export default function AccountStore({ accounts, isLoading }: AccountStoreProps) {

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4" data-testid="account-store-title">
        Connect Social Accounts
      </h2>
      <p className="text-gray-600 text-sm mb-6">
        Connect your social media accounts or buy premium aged accounts externally
      </p>
      
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {['twitter', 'reddit', 'quora'].map((platform) => {
            const config = platformConfig[platform as keyof typeof platformConfig];
            if (!config) return null;
            const IconComponent = config.icon;

            return (
              <div 
                key={platform} 
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                data-testid={`platform-connect-${platform}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <IconComponent className={`text-lg ${config.color}`} />
                    <span className="font-medium">{config.name}</span>
                  </div>
                  <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Connect your {platform} account or buy premium aged accounts
                </p>
                <Button
                  onClick={() => window.open('https://gumroad.com/l/social-accounts', '_blank')}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-md transition-all duration-200"
                  data-testid={`button-connect-${platform}`}
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Buy Premium Accounts
                </Button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
