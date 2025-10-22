import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { useAuth } from "../contexts/AuthContext";
import PageLayout from "@/components/layout/page-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertCircle,
  Calendar,
  TrendingUp,
  Target,
  BarChart3,
  Clock,
} from "lucide-react";
import { SiReddit } from "react-icons/si";

const API_URL = "http://localhost:6070";

interface DashboardMetrics {
  totalLeads: number;
  leadsToday: number;
  leadsThisWeek: number;
  highQualityLeads: number;
  totalRepliesPosted: number;
  repliesToday: number;
  repliesThisWeek: number;
}

interface PlatformStat {
  platform: string;
  leads: number;
  businesses: number;
}

interface RecentActivity {
  id: string;
  business: string;
  title: string;
  platform: string;
  score: number;
  processed_at: string;
}

interface BusinessStat {
  id: number;
  name: string;
  totalLeads: number;
  leadsToday: number;
  leadsThisWeek: number;
  highQualityLeads: number;
}

interface ScraperStatus {
  is_active: boolean;
  last_scrape: string | null;
  recent_activity: boolean;
  status_message: string;
}

interface DashboardData {
  metrics: DashboardMetrics;
  platformStats: PlatformStat[];
  recentActivity: RecentActivity[];
  businessStats: BusinessStat[];
}

export default function Dashboard() {
  const [, setLocation] = useLocation();
  const { session, signOut } = useAuth();

  const getAuthHeaders = () => {
    if (!session?.access_token) {
      console.log('🔐 No session token - redirecting to home');
      setLocation('/');
      return undefined;
    }
    return {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    };
  };

  const handleAuthError = async (response: Response) => {
    if (response.status === 401) {
      console.log('🔐 Authentication failed - signing out and redirecting to home');
      await signOut();
      setLocation('/');
      return true;
    }
    return false;
  };

  const {
    data: dashboardData,
    isLoading,
    error,
  } = useQuery<DashboardData>({
    queryKey: ["/api/dashboard"],
    queryFn: async () => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/dashboard`, {
        headers,
      });

      // Check for auth errors first
      if (await handleAuthError(response)) {
        throw new Error("Authentication failed");
      }

      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      return response.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  const {
    data: scraperStatus,
    isLoading: scraperLoading,
  } = useQuery<ScraperStatus>({
    queryKey: ["/api/scraper/status"],
    queryFn: async () => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/scraper/status`, {
        headers,
      });

      // Check for auth errors first
      if (await handleAuthError(response)) {
        throw new Error("Authentication failed");
      }

      if (!response.ok) {
        throw new Error("Failed to fetch scraper status");
      }

      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    );

    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "reddit":
        return <SiReddit className="w-5 h-5 text-orange-600" />;
      default:
        return <BarChart3 className="w-5 h-5 text-gray-600" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-red-100 text-red-800 border-red-200";
    if (score >= 70) return "bg-orange-100 text-orange-800 border-orange-200";
    if (score >= 60) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    return "bg-blue-100 text-blue-800 border-blue-200";
  };

  const getProbabilityEmoji = (probability: number) => {
    if (probability >= 80) return "🔥";
    if (probability >= 70) return "⭐";
    if (probability >= 60) return "👍";
    if (probability >= 40) return "💡";
    return "📝";
  };

  if (error) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Error Loading Dashboard
            </h1>
            <p className="text-gray-600">
              Failed to load dashboard data. Please try again.
            </p>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
            <p className="text-gray-600">
              AI-powered lead generation & reply automation
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {scraperLoading ? (
              <div className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Checking status...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-lg border border-gray-200">
                <div className={`w-2 h-2 rounded-full ${
                  scraperStatus?.is_active 
                    ? 'bg-green-500 animate-pulse' 
                    : 'bg-red-500'
                }`}></div>
                <span className={`text-sm font-medium ${
                  scraperStatus?.is_active 
                    ? 'text-green-700' 
                    : 'text-red-700'
                }`}>
                  {scraperStatus?.status_message || 'Scraper offline'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Daily Leads */}
          <Card className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 bg-white/50 backdrop-blur-sm border-gray-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Daily Leads
              </CardTitle>
              <Calendar className="h-5 w-5 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  dashboardData?.metrics?.leadsToday || 0
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1 font-medium">
                New opportunities today
              </p>
            </CardContent>
          </Card>

          {/* Weekly Leads */}
          <Card className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 bg-white/50 backdrop-blur-sm border-gray-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Weekly Leads
              </CardTitle>
              <BarChart3 className="h-5 w-5 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  dashboardData?.metrics?.leadsThisWeek || 0
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1 font-medium">
                Last 7 days
              </p>
            </CardContent>
          </Card>

          {/* AI Replies Posted */}
          <Card className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 bg-white/50 backdrop-blur-sm border-gray-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                AI Replies Posted
              </CardTitle>
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  dashboardData?.metrics?.totalRepliesPosted || 0
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1 font-medium">
                Automated responses posted
              </p>
            </CardContent>
          </Card>

          {/* High Quality */}
          <Card className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 bg-white/50 backdrop-blur-sm border-gray-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                High Quality (80%+)
              </CardTitle>
              <Target className="h-5 w-5 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  dashboardData?.metrics?.highQualityLeads || 0
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1 font-medium">
                Premium opportunities
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-6">
            {/* Reply Activity Chart */}
            <Card className="bg-gradient-to-br from-gray-50 to-white">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-gray-900 flex items-center">
                  📈 Reply Activity
                  <Badge className="ml-2 bg-emerald-100 text-emerald-800">
                    Live
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-64 w-full" />
                ) : (
                  <div className="h-64 flex items-end justify-between space-x-2 p-4">
                    {/* Fake chart bars for now */}
                    {Array.from({ length: 7 }).map((_, i) => {
                      const height = Math.random() * 200 + 20;
                      const isToday = i === 6;
                      return (
                        <div
                          key={i}
                          className="flex flex-col items-center flex-1"
                        >
                          <div
                            className={`w-full rounded-t-lg transition-all duration-500 ${
                              isToday
                                ? "bg-gradient-to-t from-blue-500 to-blue-400"
                                : "bg-gradient-to-t from-gray-300 to-gray-200"
                            }`}
                            style={{ height: `${height}px` }}
                          />
                          <div className="text-xs text-gray-500 mt-2">
                            {
                              [
                                "Mon",
                                "Tue",
                                "Wed",
                                "Thu",
                                "Fri",
                                "Sat",
                                "Today",
                              ][i]
                            }
                          </div>
                          <div
                            className={`text-sm font-bold ${
                              isToday ? "text-blue-600" : "text-gray-600"
                            }`}
                          >
                            {Math.floor(height / 10)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Platform Performance */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-gray-900">
                  🚀 Platform Performance
                </CardTitle>
                <p className="text-sm text-gray-600">Lead generation across all platforms</p>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-80 w-full" />
                ) : dashboardData?.platformStats?.length === 0 ? (
                  <div className="text-center py-12">
                    <SiReddit className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg font-medium">No platform data available</p>
                    <p className="text-sm text-gray-400 mt-2">
                      Start by creating a business and adding keywords
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Chart Area */}
                    <div className="bg-white rounded-lg p-6 border border-gray-100">
                      <div className="h-64 relative">
                        <svg className="w-full h-full" viewBox="0 0 400 200">
                          {/* Grid lines */}
                          <defs>
                            <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
                              <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#f3f4f6" strokeWidth="1"/>
                            </pattern>
                          </defs>
                          <rect width="100%" height="100%" fill="url(#grid)" />
                          
                          {/* Y-axis labels */}
                          <g className="text-xs fill-gray-500">
                            <text x="15" y="25" textAnchor="end">100</text>
                            <text x="15" y="65" textAnchor="end">75</text>
                            <text x="15" y="105" textAnchor="end">50</text>
                            <text x="15" y="145" textAnchor="end">25</text>
                            <text x="15" y="185" textAnchor="end">0</text>
                          </g>
                          
                          {/* Chart bars */}
                          {dashboardData?.platformStats?.map((stat, index) => {
                            const maxLeads = Math.max(...(dashboardData?.platformStats?.map(s => s.leads) || [1]));
                            const barHeight = (stat.leads / maxLeads) * 140;
                            const barWidth = 60;
                            const x = 50 + (index * 100);
                            const y = 180 - barHeight;
                            
                            const colors = [
                              { fill: '#ff6b35', stroke: '#e55a2b' }, // Orange for Reddit
                              { fill: '#1da1f2', stroke: '#1a91da' }, // Blue for Twitter
                              { fill: '#0077b5', stroke: '#006ba1' }, // LinkedIn blue
                            ];
                            
                            return (
                              <g key={index}>
                                {/* Bar */}
                                <rect
                                  x={x}
                                  y={y}
                                  width={barWidth}
                                  height={barHeight}
                                  fill={colors[index]?.fill || '#6b7280'}
                                  stroke={colors[index]?.stroke || '#4b5563'}
                                  strokeWidth="2"
                                  rx="4"
                                  className="transition-all duration-300 hover:opacity-80"
                                />
                                
                                {/* Value label on top of bar */}
                                <text
                                  x={x + barWidth/2}
                                  y={y - 8}
                                  textAnchor="middle"
                                  className="text-sm font-bold fill-gray-700"
                                >
                                  {stat.leads}
                                </text>
                                
                                {/* Platform label */}
                                <text
                                  x={x + barWidth/2}
                                  y={195}
                                  textAnchor="middle"
                                  className="text-sm font-medium fill-gray-600 capitalize"
                                >
                                  {stat.platform}
                                </text>
                              </g>
                            );
                          })}
                        </svg>
                      </div>
                    </div>
                    
                    {/* Platform Stats Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {dashboardData?.platformStats?.map((stat, index) => {
                        const colors = [
                          { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-600', icon: 'text-orange-600' },
                          { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-600', icon: 'text-blue-600' },
                          { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-600', icon: 'text-indigo-600' },
                        ];
                        
                        return (
                          <div
                            key={index}
                            className={`p-4 rounded-lg border ${colors[index]?.bg || 'bg-gray-50'} ${colors[index]?.border || 'border-gray-200'}`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className={`${colors[index]?.icon || 'text-gray-600'}`}>
                                {getPlatformIcon(stat.platform)}
                              </div>
                              <Badge className={`${colors[index]?.bg || 'bg-gray-100'} ${colors[index]?.text || 'text-gray-600'} border-0`}>
                                Active
                              </Badge>
                            </div>
                            <h3 className="font-bold text-gray-900 capitalize text-lg">
                              {stat.platform}
                            </h3>
                            <div className="mt-2 space-y-1">
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Leads Found:</span>
                                <span className={`font-bold ${colors[index]?.text || 'text-gray-600'}`}>
                                  {stat.leads}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Businesses:</span>
                                <span className="font-medium text-gray-700">
                                  {stat.businesses}
                                </span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Connect Accounts */}
            <Card className="bg-white border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-gray-900 flex items-center">
                  🔗 Connect Accounts
                  <Badge className="ml-2 bg-green-100 text-green-800 border-green-200">
                    New
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center space-x-3">
                    <SiReddit className="w-6 h-6 text-orange-600" />
                    <div>
                      <div className="font-medium text-gray-900">Reddit</div>
                      <div className="text-xs text-gray-500">
                        Auto-reply to leads
                      </div>
                    </div>
                  </div>
                  <button 
                    onClick={() => setLocation("/accounts")}
                    className="px-3 py-1 bg-purple-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Connect
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 opacity-60">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-blue-500 rounded flex items-center justify-center text-white text-xs font-bold">
                      T
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Twitter</div>
                      <div className="text-xs text-gray-500">Coming soon</div>
                    </div>
                  </div>
                  <button className="px-3 py-1 bg-gray-300 text-gray-500 text-sm rounded-md cursor-not-allowed">
                    Soon
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 opacity-60">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-blue-700 rounded flex items-center justify-center text-white text-xs font-bold">
                      L
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">LinkedIn</div>
                      <div className="text-xs text-gray-500">Coming soon</div>
                    </div>
                  </div>
                  <button className="px-3 py-1 bg-gray-300 text-gray-500 text-sm rounded-md cursor-not-allowed">
                    Soon
                  </button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="bg-white/50 backdrop-blur-sm border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-gray-900">
                  ⚡ Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-3">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                ) : dashboardData?.recentActivity?.length === 0 ? (
                  <div className="text-center py-8">
                    <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">No recent activity</p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {dashboardData?.recentActivity?.map((activity) => (
                      <div
                        key={activity.id}
                        className="flex items-start space-x-3 p-3 bg-white/30 rounded-lg hover:bg-white/60 transition-colors border border-gray-100"
                      >
                        <div className="flex-shrink-0 mt-1">
                          {getPlatformIcon(activity.platform)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {activity.title}
                          </p>
                          <div className="flex items-center space-x-2 mt-1">
                            <div className="flex items-center text-xs font-medium">
                              <span className="mr-1">
                                {getProbabilityEmoji(activity.score)}
                              </span>
                              <span className="text-gray-900">{activity.score}%</span>
                            </div>
                            <span className="text-xs text-gray-500">
                              {activity.business}
                            </span>
                          </div>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatTimeAgo(activity.processed_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>


          </div>
        </div>
      </div>
    </PageLayout>
  );
}
