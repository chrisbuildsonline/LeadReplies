import { useQuery } from "@tanstack/react-query";
import Sidebar from "@/components/layout/sidebar";
import MetricCard from "@/components/dashboard/metric-card";
import PlatformCard from "@/components/dashboard/platform-card";
import CampaignTable from "@/components/dashboard/campaign-table";
import AccountStore from "@/components/dashboard/account-store";
import ActivityFeed from "@/components/dashboard/activity-feed";
import PerformanceChart from "@/components/dashboard/performance-chart";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle } from "lucide-react";
import { 
  type Metrics, 
  type PlatformStats, 
  type Campaign, 
  type Reply, 
  type Account, 
  type DailyStats 
} from "@shared/schema";

interface DashboardData {
  metrics: Metrics;
  platformStats: PlatformStats[];
  campaigns: Campaign[];
  replies: Reply[];
  accounts: Account[];
  dailyStats: DailyStats;
}

export default function Dashboard() {
  const { data: dashboardData, isLoading, error } = useQuery<DashboardData>({
    queryKey: ["/api/dashboard"],
  });

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Dashboard</h1>
          <p className="text-gray-600">Failed to load dashboard data. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="p-8 bg-[#ffffff]">
          
          {/* Key Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-32" />
              ))
            ) : (
              <>
                <MetricCard
                  title="AI Replies Posted"
                  value={dashboardData?.metrics?.totalReplies || 0}
                  change="+12%"
                  changeLabel="vs last week"
                  icon="reply"
                  emoji="📈"
                  color="emerald"
                />
                <MetricCard
                  title="Products Promoted"
                  value={dashboardData?.metrics?.productsPromoted || 0}
                  change="+8%"
                  changeLabel="vs last week"
                  icon="bullseye"
                  emoji="🎯"
                  color="blue"
                />
                <MetricCard
                  title="Click-through Rate"
                  value={`${dashboardData?.metrics?.clickThroughRate || 0}%`}
                  change="+0.3%"
                  changeLabel="vs last week"
                  icon="mouse-pointer"
                  emoji="⚡"
                  color="amber"
                />
                <MetricCard
                  title="Engagement Rate"
                  value={`${dashboardData?.metrics?.engagementRate || 0}%`}
                  change="+5%"
                  changeLabel="vs last week"
                  icon="users"
                  emoji="🔥"
                  color="purple"
                />
              </>
            )}
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-8">
              {/* Platform Performance */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6" data-testid="platform-performance-title">
                  Platform Performance
                </h2>
                {isLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <Skeleton key={i} className="h-24" />
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {dashboardData?.platformStats?.map((stat) => (
                      <PlatformCard key={stat.id} platform={stat} />
                    ))}
                  </div>
                )}
              </div>

              {/* Performance Chart */}
              <PerformanceChart isLoading={isLoading} />

              {/* Active Campaigns */}
              <CampaignTable campaigns={dashboardData?.campaigns || []} isLoading={isLoading} />
            </div>

            {/* Right Column */}
            <div className="space-y-8">
              {/* Account Store */}
              <AccountStore accounts={dashboardData?.accounts || []} isLoading={isLoading} />

              {/* Recent Activity */}
              <ActivityFeed replies={dashboardData?.replies || []} isLoading={isLoading} />

              {/* Quick Stats */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4" data-testid="today-performance-title">
                  Today's Performance
                </h2>
                {isLoading ? (
                  <div className="space-y-4">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <Skeleton key={i} className="h-6" />
                    ))}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Replies sent</span>
                      <span className="font-semibold text-gray-900" data-testid="replies-sent-today">
                        {dashboardData?.dailyStats?.repliesPosted || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Clicks generated</span>
                      <span className="font-semibold text-gray-900" data-testid="clicks-generated-today">
                        {dashboardData?.dailyStats?.clicksGenerated || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Engagement rate</span>
                      <span className="font-semibold text-emerald-600" data-testid="engagement-rate-today">
                        {dashboardData?.dailyStats?.engagementRate || 0}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Keywords tracked</span>
                      <span className="font-semibold text-gray-900" data-testid="keywords-tracked-today">
                        {dashboardData?.dailyStats?.keywordsTracked || 0}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
