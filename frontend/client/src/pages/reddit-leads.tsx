import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import PageLayout from "@/components/layout/page-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, ExternalLink, Play, RefreshCw, TrendingUp, Users, Zap } from "lucide-react";
import { SiReddit } from "react-icons/si";

interface RedditLead {
  id: string;
  reddit_id: string;
  title: string;
  content: string;
  url: string;
  author: string;
  subreddit: string;
  ai_probability: number;
  ai_analysis: string;
  keywords_matched: string[];
  upvotes: number;
  created_date: string;
  processed_at: string;
}

interface RedditLeadsResponse {
  leads: RedditLead[];
  total: number;
}

interface ScrapingStatus {
  active: boolean;
  last_scrape: string | null;
  total_leads: number;
}

export default function RedditLeads() {
  const [selectedFilter, setSelectedFilter] = useState<"all" | "high" | "medium">("high");
  const queryClient = useQueryClient();

  // Fetch leads based on filter
  const getMinProbability = () => {
    switch (selectedFilter) {
      case "high": return 70;
      case "medium": return 40;
      case "all": return 0;
      default: return 70;
    }
  };

  const { data: leadsData, isLoading: leadsLoading, error: leadsError } = useQuery<RedditLeadsResponse>({
    queryKey: [`/api/reddit/leads`, selectedFilter],
    queryFn: async () => {
      const response = await fetch(`/api/reddit/leads?limit=100&min_probability=${getMinProbability()}`);
      if (!response.ok) throw new Error('Failed to fetch leads');
      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: scrapingStatus, isLoading: statusLoading } = useQuery<ScrapingStatus>({
    queryKey: ['/api/reddit/scraping/status'],
    queryFn: async () => {
      const response = await fetch('/api/reddit/scraping/status');
      if (!response.ok) throw new Error('Failed to fetch status');
      return response.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Run scraping mutation
  const runScrapingMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/reddit/scraping/run-once', {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to run scraping');
      return response.json();
    },
    onSuccess: () => {
      // Refresh leads and status after successful scraping
      queryClient.invalidateQueries({ queryKey: ['/api/reddit/leads'] });
      queryClient.invalidateQueries({ queryKey: ['/api/reddit/scraping/status'] });
    },
  });

  const getProbabilityColor = (probability: number) => {
    if (probability >= 80) return "bg-red-100 text-red-800 border-red-200";
    if (probability >= 70) return "bg-orange-100 text-orange-800 border-orange-200";
    if (probability >= 60) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    if (probability >= 40) return "bg-blue-100 text-blue-800 border-blue-200";
    return "bg-gray-100 text-gray-800 border-gray-200";
  };

  const getProbabilityEmoji = (probability: number) => {
    if (probability >= 80) return "🔥";
    if (probability >= 70) return "⭐";
    if (probability >= 60) return "👍";
    if (probability >= 40) return "💡";
    return "📝";
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  if (leadsError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Reddit Leads</h1>
          <p className="text-gray-600">Failed to load Reddit leads data. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <PageLayout>
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Reddit Leads</h1>
              <p className="text-gray-600">AI-powered lead discovery from Reddit conversations</p>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => runScrapingMutation.mutate()}
                disabled={runScrapingMutation.isPending}
                className="bg-orange-600 hover:bg-orange-700"
              >
                {runScrapingMutation.isPending ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                Run Scraping
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <SiReddit className="w-6 h-6 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Leads</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {statusLoading ? <Skeleton className="h-8 w-16" /> : scrapingStatus?.total_leads || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">High Quality</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {leadsLoading ? <Skeleton className="h-8 w-16" /> : 
                       selectedFilter === "high" ? leadsData?.total || 0 : "N/A"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Subreddits</p>
                    <p className="text-2xl font-bold text-gray-900">27</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Zap className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Last Scrape</p>
                    <p className="text-sm font-bold text-gray-900">
                      {statusLoading ? <Skeleton className="h-4 w-20" /> : 
                       scrapingStatus?.last_scrape ? formatTimeAgo(scrapingStatus.last_scrape) : "Never"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filter Tabs */}
          <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
            {[
              { key: "high", label: "High Quality (70%+)", count: leadsData?.total || 0 },
              { key: "medium", label: "Medium Quality (40%+)", count: 0 },
              { key: "all", label: "All Leads", count: 0 }
            ].map((filter) => (
              <button
                key={filter.key}
                onClick={() => setSelectedFilter(filter.key as any)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedFilter === filter.key
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {/* Leads Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {leadsLoading ? (
              Array.from({ length: 12 }).map((_, i) => (
                <Card key={i} className="h-80">
                  <CardContent className="p-4">
                    <Skeleton className="h-4 w-16 mb-2" />
                    <Skeleton className="h-5 w-full mb-3" />
                    <Skeleton className="h-4 w-full mb-2" />
                    <Skeleton className="h-4 w-3/4 mb-4" />
                    <Skeleton className="h-20 w-full mb-3" />
                    <Skeleton className="h-8 w-full" />
                  </CardContent>
                </Card>
              ))
            ) : leadsData?.leads.length === 0 ? (
              <div className="col-span-full">
                <Card>
                  <CardContent className="p-12 text-center">
                    <SiReddit className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No leads found</h3>
                    <p className="text-gray-600 mb-4">Try running the scraper or adjusting your filters.</p>
                    <Button
                      onClick={() => runScrapingMutation.mutate()}
                      disabled={runScrapingMutation.isPending}
                      className="bg-orange-600 hover:bg-orange-700"
                    >
                      {runScrapingMutation.isPending ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Play className="w-4 h-4 mr-2" />
                      )}
                      Run Scraping Now
                    </Button>
                  </CardContent>
                </Card>
              </div>
            ) : (
              leadsData?.leads.map((lead) => (
                <Card key={lead.id} className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 h-fit">
                  <CardContent className="p-4">
                    {/* Header with probability and subreddit */}
                    <div className="flex items-center justify-between mb-3">
                      <Badge className={`${getProbabilityColor(lead.ai_probability)} border text-xs`}>
                        {getProbabilityEmoji(lead.ai_probability)} {lead.ai_probability}%
                      </Badge>
                      <Badge variant="outline" className="text-orange-600 border-orange-200 text-xs">
                        r/{lead.subreddit}
                      </Badge>
                    </div>
                    
                    {/* Title */}
                    <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2 leading-tight">
                      {lead.title}
                    </h3>
                    
                    {/* Meta info */}
                    <div className="text-xs text-gray-500 mb-3">
                      u/{lead.author} • {formatTimeAgo(lead.created_date)} • {lead.upvotes} ↑
                    </div>
                    
                    {/* Content preview */}
                    {lead.content && (
                      <p className="text-xs text-gray-600 mb-3 line-clamp-3 leading-relaxed">
                        {lead.content}
                      </p>
                    )}
                    
                    {/* AI Analysis */}
                    {lead.ai_analysis && (
                      <div className="bg-blue-50 border border-blue-200 rounded-md p-2 mb-3">
                        <p className="text-xs text-blue-800 line-clamp-2">
                          <strong>AI:</strong> {lead.ai_analysis}
                        </p>
                      </div>
                    )}
                    
                    {/* Keywords */}
                    <div className="mb-3">
                      <div className="flex flex-wrap gap-1">
                        {lead.keywords_matched.slice(0, 3).map((keyword) => (
                          <Badge key={keyword} variant="secondary" className="text-xs px-2 py-0">
                            {keyword}
                          </Badge>
                        ))}
                        {lead.keywords_matched.length > 3 && (
                          <Badge variant="secondary" className="text-xs px-2 py-0">
                            +{lead.keywords_matched.length - 3}
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    {/* Action button */}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(lead.url, '_blank')}
                      className="w-full text-orange-600 border-orange-200 hover:bg-orange-50 text-xs"
                    >
                      <ExternalLink className="w-3 h-3 mr-1" />
                      View on Reddit
                    </Button>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
    </PageLayout>
  );
}