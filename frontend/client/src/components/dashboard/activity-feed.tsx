import { type Reply } from "@shared/schema";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { SiX, SiReddit, SiQuora } from "react-icons/si";

interface ActivityFeedProps {
  replies: Reply[];
  isLoading: boolean;
}

const platformIcons = {
  twitter: { icon: SiX, color: "text-gray-900" },
  reddit: { icon: SiReddit, color: "text-orange-500" },
  quora: { icon: SiQuora, color: "text-red-600" },
};

const formatTimeAgo = (date: Date | string | null) => {
  if (!date) return "Unknown";
  
  const now = new Date();
  const dateObj = new Date(date); // This handles both Date objects and date strings
  const diffMs = now.getTime() - dateObj.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  
  if (diffMinutes < 60) {
    return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
  } else {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  }
};

export default function ActivityFeed({ replies, isLoading }: ActivityFeedProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6" data-testid="recent-replies-title">
        Recent AI Replies
      </h2>
      
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex space-x-3">
              <Skeleton className="w-6 h-6 rounded" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-16" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {replies.map((reply) => (
              <div 
                key={reply.id} 
                className="flex space-x-3"
                data-testid={`reply-${reply.id}`}
              >
                {(() => {
                  const config = platformIcons[reply.platform as keyof typeof platformIcons];
                  if (!config) return null;
                  const IconComponent = config.icon;
                  return <IconComponent className={`text-lg mt-1 ${config.color}`} />;
                })()}
                <div className="flex-1">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-sm text-gray-700">"{reply.content}"</p>
                  </div>
                  <div className="flex items-center space-x-2 mt-2 text-xs text-gray-500">
                    <span>{formatTimeAgo(reply.createdAt)}</span>
                    <span>•</span>
                    <span>{reply.upvotes} upvote{reply.upvotes !== 1 ? 's' : ''}</span>
                    <span>•</span>
                    <span>{reply.username}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-6">
            <Button 
              variant="ghost" 
              className="text-blue-600 hover:text-blue-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100 transition-all duration-200"
              data-testid="button-view-all-activity"
            >
              View all activity <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
