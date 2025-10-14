import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import PageLayout from "../components/layout/page-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertCircle,
  ExternalLink,
  TrendingUp,
  Calendar,
  BarChart3,
  Grid3X3,
  List,
  MessageSquare,
} from "lucide-react";
import { SiReddit } from "react-icons/si";

const API_URL = "";

interface Lead {
  id: string;
  business_id: number;
  global_lead_id: number;
  ai_score: number;
  ai_reasoning: string;
  matched_keywords: string[];
  processed_at: string;
  platform: string;
  platform_id: string;
  title: string;
  content: string;
  author: string;
  url: string;
  subreddit: string;
  score: number;
  created_at: string;
}

interface Business {
  id: number;
  name: string;
  website: string;
  description: string;
  created_at: string;
}

interface LeadsResponse {
  leads: Lead[];
  total: number;
}

export default function LeadsDashboard() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState<number | null>(
    null
  );
  const [selectedFilter, setSelectedFilter] = useState<
    "all" | "high" | "medium"
  >("high");
  const [dateFilter, setDateFilter] = useState("all");
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  const [, setLocation] = useLocation();

  useEffect(() => {
    fetchBusinesses();
  }, []);

  // Filter leads based on score ranges
  const filterByScoreRange = (leads: Lead[]) => {
    switch (selectedFilter) {
      case "high":
        return leads.filter((lead) => lead.ai_score >= 80);
      case "medium":
        return leads.filter((lead) => lead.ai_score < 80);
      case "all":
        return leads;
      default:
        return leads.filter((lead) => lead.ai_score >= 80);
    }
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLocation("/login");
      return undefined;
    }
    return {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
  };

  const fetchBusinesses = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${API_URL}/api/businesses`, {
        headers,
      });

      if (response.ok) {
        const data = await response.json();
        setBusinesses(data.businesses);
        if (data.businesses.length > 0) {
          setSelectedBusinessId(data.businesses[0].id);
        }
      } else if (response.status === 401) {
        setLocation("/login");
      }
    } catch (err) {
      console.error("Failed to fetch businesses");
    }
  };

  // Fetch ALL leads for metrics (unfiltered)
  const { data: allLeadsData, isLoading: allLeadsLoading } =
    useQuery<LeadsResponse>({
      queryKey: [`/api/businesses/${selectedBusinessId}/leads/all`],
      queryFn: async () => {
        if (!selectedBusinessId) throw new Error("No business selected");

        const headers = getAuthHeaders();
        if (!headers) throw new Error("No auth token");

        const response = await fetch(
          `${API_URL}/api/businesses/${selectedBusinessId}/leads?limit=1000`,
          {
            headers,
          }
        );

        if (!response.ok) {
          if (response.status === 401) {
            setLocation("/login");
          }
          throw new Error("Failed to fetch leads");
        }

        const data = await response.json();
        return { leads: data.leads || [], total: (data.leads || []).length };
      },
      enabled: !!selectedBusinessId,
      refetchInterval: 30000,
    });

  // Fetch filtered leads for display
  const {
    data: leadsData,
    isLoading: leadsLoading,
    error: leadsError,
  } = useQuery<LeadsResponse>({
    queryKey: [
      `/api/businesses/${selectedBusinessId}/leads`,
      selectedFilter,
      dateFilter,
    ],
    queryFn: async () => {
      if (!selectedBusinessId) throw new Error("No business selected");

      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(
        `${API_URL}/api/businesses/${selectedBusinessId}/leads?limit=100`,
        {
          headers,
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          setLocation("/login");
        }
        throw new Error("Failed to fetch leads");
      }

      const data = await response.json();

      // Filter by score range and date on frontend
      let filteredLeads = filterByScoreRange(data.leads || []);

      // Apply date filter
      if (dateFilter !== "all") {
        const now = new Date();
        const filterDate = new Date();

        switch (dateFilter) {
          case "today":
            filterDate.setHours(0, 0, 0, 0);
            break;
          case "week":
            filterDate.setDate(now.getDate() - 7);
            break;
          case "month":
            filterDate.setMonth(now.getMonth() - 1);
            break;
          case "3months":
            filterDate.setMonth(now.getMonth() - 3);
            break;
        }

        filteredLeads = filteredLeads.filter((lead: Lead) => {
          const leadDate = new Date(lead.processed_at);
          return leadDate >= filterDate;
        });
      }

      return { leads: filteredLeads, total: filteredLeads.length };
    },
    enabled: !!selectedBusinessId,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Calculate dashboard metrics from ALL leads (not filtered)
  const getDashboardMetrics = () => {
    if (!allLeadsData?.leads)
      return { today: 0, thisWeek: 0, highQuality: 0, platforms: {} };

    const now = new Date();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const weekAgo = new Date();
    weekAgo.setDate(now.getDate() - 7);

    let todayCount = 0;
    let thisWeekCount = 0;
    let highQualityCount = 0;
    const platforms: Record<string, number> = {};

    // Use ALL leads for metrics, not filtered leads
    allLeadsData.leads.forEach((lead) => {
      const leadDate = new Date(lead.processed_at);

      // Count by date
      if (leadDate >= today) todayCount++;
      if (leadDate >= weekAgo) thisWeekCount++;

      // Count high quality (80%+)
      if (lead.ai_score >= 80) highQualityCount++;

      // Count by platform
      platforms[lead.platform] = (platforms[lead.platform] || 0) + 1;
    });

    return {
      today: todayCount,
      thisWeek: thisWeekCount,
      highQuality: highQualityCount,
      platforms,
    };
  };

  const metrics = getDashboardMetrics();

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
    const diffInHours = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    );

    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  if (leadsError) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Error Loading Dashboard
            </h1>
            <p className="text-gray-600">
              Failed to load leads data. Please try again.
            </p>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (businesses.length === 0) {
    return (
      <PageLayout>
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">🏢</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No businesses found
          </h2>
          <p className="text-gray-600 mb-6">
            You need to create a business first to view leads.
          </p>
          <button
            onClick={() => setLocation("/businesses")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Create Your First Business
          </button>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Lead Dashboard
            </h1>
            <p className="text-gray-600">
              AI-powered lead discovery across multiple platforms
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">
              Business:
            </label>
            <select
              value={selectedBusinessId || ""}
              onChange={(e) => setSelectedBusinessId(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Dashboard Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Leads Today */}
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Leads Today
              </CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {allLeadsLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  metrics.today
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                New opportunities discovered
              </p>
            </CardContent>
          </Card>

          {/* Leads This Week */}
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Leads This Week
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {allLeadsLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  metrics.thisWeek
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">Last 7 days activity</p>
            </CardContent>
          </Card>

          {/* High Quality Leads */}
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                High Quality (80%+)
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {allLeadsLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  metrics.highQuality
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Premium opportunities
              </p>
            </CardContent>
          </Card>

          {/* All Replies Posted (Future Feature) */}
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                All Replies Posted
              </CardTitle>
              <MessageSquare className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                Coming Soon
              </div>
              <p className="text-xs text-gray-500 mt-1">Track your responses</p>
            </CardContent>
          </Card>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center justify-between">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
            {[
              { key: "high", label: "High Quality (80-100%)" },
              { key: "medium", label: "Medium Quality (0-79%)" },
              { key: "all", label: "All Leads" },
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

          <div className="flex items-center space-x-4">
            {/* View Mode Toggle */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">View:</label>
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => setViewMode("cards")}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === "cards"
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                  title="Card View"
                >
                  <Grid3X3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode("table")}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === "table"
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                  title="Table View"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Date Filter */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Date:</label>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last Week</option>
                <option value="month">Last Month</option>
                <option value="3months">Last 3 Months</option>
              </select>
            </div>
          </div>
        </div>

        {/* Leads Display */}
        {viewMode === "cards" ? (
          /* Cards View */
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
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No leads found
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Try adjusting your filters or check back later.
                    </p>
                  </CardContent>
                </Card>
              </div>
            ) : (
              leadsData?.leads.map((lead) => (
                <Card
                  key={lead.id}
                  className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 h-fit"
                >
                  <CardContent className="p-4">
                    {/* Header with probability and subreddit */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center text-xs font-medium">
                        <span className="mr-1">
                          {getProbabilityEmoji(lead.ai_score)}
                        </span>
                        <span className="text-gray-900">{lead.ai_score}%</span>
                      </div>
                      <Badge
                        variant="outline"
                        className="text-orange-600 border-orange-200 text-xs"
                      >
                        r/{lead.subreddit}
                      </Badge>
                    </div>

                    {/* Title */}
                    <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2 leading-tight">
                      {lead.title}
                    </h3>

                    {/* Meta info */}
                    <div className="text-xs text-gray-500 mb-3">
                      u/{lead.author} • {formatTimeAgo(lead.created_at)} •{" "}
                      {lead.score} ↑
                    </div>

                    {/* Content preview */}
                    {lead.content && (
                      <p className="text-xs text-gray-600 mb-3 line-clamp-3 leading-relaxed">
                        {lead.content}
                      </p>
                    )}

                    {/* AI Analysis */}
                    {lead.ai_reasoning && (
                      <div className="bg-blue-50 border border-blue-200 rounded-md p-2 mb-3">
                        <p className="text-xs text-blue-800 line-clamp-2">
                          <strong>AI:</strong> {lead.ai_reasoning}
                        </p>
                      </div>
                    )}

                    {/* Keywords */}
                    <div className="mb-3">
                      <div className="flex flex-wrap gap-1">
                        {lead.matched_keywords.slice(0, 3).map((keyword) => (
                          <Badge
                            key={keyword}
                            variant="secondary"
                            className="text-xs px-2 py-0"
                          >
                            {keyword}
                          </Badge>
                        ))}
                        {lead.matched_keywords.length > 3 && (
                          <Badge
                            variant="secondary"
                            className="text-xs px-2 py-0"
                          >
                            +{lead.matched_keywords.length - 3}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Action button */}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(lead.url, "_blank")}
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
        ) : (
          /* Table View */
          <Card>
            <CardContent className="p-0">
              {leadsLoading ? (
                <div className="p-6">
                  <Skeleton className="h-8 w-full mb-4" />
                  {Array.from({ length: 10 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full mb-2" />
                  ))}
                </div>
              ) : leadsData?.leads.length === 0 ? (
                <div className="p-12 text-center">
                  <SiReddit className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No leads found
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Try adjusting your filters or check back later.
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-16">Score</TableHead>
                      <TableHead className="w-20">Subreddit</TableHead>
                      <TableHead>Title</TableHead>
                      <TableHead className="w-24">Author</TableHead>
                      <TableHead className="w-20">Date</TableHead>
                      <TableHead className="w-32">Keywords</TableHead>
                      <TableHead className="w-32">AI Analysis</TableHead>
                      <TableHead className="w-20">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {leadsData?.leads.map((lead) => (
                      <TableRow key={lead.id} className="hover:bg-gray-50">
                        <TableCell>
                          <div className="flex items-center text-xs font-medium">
                            <span className="mr-1">
                              {getProbabilityEmoji(lead.ai_score)}
                            </span>
                            <span className="text-gray-900">
                              {lead.ai_score}%
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className="text-orange-600 border-orange-200 text-xs"
                          >
                            r/{lead.subreddit}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-md">
                          <div>
                            <h4 className="font-medium text-sm text-gray-900 line-clamp-2 mb-1">
                              {lead.title}
                            </h4>
                            {lead.content && (
                              <p className="text-xs text-gray-600 line-clamp-2">
                                {lead.content}
                              </p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          u/{lead.author}
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {formatTimeAgo(lead.created_at)}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {lead.matched_keywords
                              .slice(0, 2)
                              .map((keyword) => (
                                <Badge
                                  key={keyword}
                                  variant="secondary"
                                  className="text-xs px-2 py-0"
                                >
                                  {keyword}
                                </Badge>
                              ))}
                            {lead.matched_keywords.length > 2 && (
                              <Badge
                                variant="secondary"
                                className="text-xs px-2 py-0"
                              >
                                +{lead.matched_keywords.length - 2}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="max-w-xs">
                          {lead.ai_reasoning && (
                            <p className="text-xs text-gray-600 line-clamp-2">
                              {lead.ai_reasoning}
                            </p>
                          )}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(lead.url, "_blank")}
                            className="text-orange-600 border-orange-200 hover:bg-orange-50 text-xs"
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </PageLayout>
  );
}
