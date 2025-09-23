import { type Campaign } from "@shared/schema";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { SiX, SiReddit, SiQuora } from "react-icons/si";

interface CampaignTableProps {
  campaigns: Campaign[];
  isLoading: boolean;
}

const platformIcons = {
  twitter: { icon: SiX, color: "text-gray-900" },
  reddit: { icon: SiReddit, color: "text-orange-500" },
  quora: { icon: SiQuora, color: "text-red-600" },
};

export default function CampaignTable({ campaigns, isLoading }: CampaignTableProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900" data-testid="active-campaigns-title">
          Active Campaigns
        </h2>
        <Button 
          className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-md transition-all duration-200"
          data-testid="button-new-campaign"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Campaign
        </Button>
      </div>
      
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {campaigns.map((campaign) => (
            <div 
              key={campaign.id} 
              className="border border-gray-200 rounded-lg p-4"
              data-testid={`campaign-${campaign.id}`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div 
                    className={`w-3 h-3 rounded-full ${
                      campaign.status === 'active' ? 'bg-emerald-500' : 'bg-amber-500'
                    }`}
                  />
                  <span className="font-medium text-gray-900">{campaign.name}</span>
                </div>
                <Badge 
                  variant={campaign.status === 'active' ? 'default' : 'secondary'}
                  className={
                    campaign.status === 'active' 
                      ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-100' 
                      : 'bg-amber-100 text-amber-800 hover:bg-amber-100'
                  }
                >
                  {campaign.status === 'active' ? 'Active' : 'Paused'}
                </Badge>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Keywords:</span>
                  <p className="font-medium">{campaign.keywords.join(", ")}</p>
                </div>
                <div>
                  <span className="text-gray-500">Platforms:</span>
                  <div className="flex space-x-2 mt-1">
                    {campaign.platforms.map((platform) => {
                      const config = platformIcons[platform as keyof typeof platformIcons];
                      if (!config) return null;
                      const IconComponent = config.icon;
                      return (
                        <IconComponent 
                          key={platform} 
                          className={`text-lg ${config.color}`}
                          title={platform}
                        />
                      );
                    })}
                  </div>
                </div>
                <div>
                  <span className="text-gray-500">Performance:</span>
                  <p className="font-medium">127 replies, 4.2% CTR</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
