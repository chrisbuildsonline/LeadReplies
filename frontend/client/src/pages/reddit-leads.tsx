import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { useLocation } from 'wouter';
import PageLayout from '../components/layout/page-layout';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, ExternalLink, Play, RefreshCw, TrendingUp, Users, Zap } from "lucide-react";
import { SiReddit } from "react-icons/si";

const API_URL = '';

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

export default function RedditLeads() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState<number | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<"all" | "high" | "medium">("high");
  const [dateFilter, setDateFilter] = useState('all');
  const [, setLocation] = useLocation();
  const queryClient = useQueryClient();

  useEffect(() => {
    fetchBusinesses();
  }, []);

  // Fetch leads based on filter
  const getMinProbability = () => {
    switch (selectedFilter) {
      case "high": return 70;
      case "medium": return 40;
      case "all": return 0;
      default: return 70;
    }
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLocation('/login');
      return {};
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  };

  const fetchBusinesses = async () => {
    try {
      const response = await fetch(`${API_URL}/api/businesses`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        setBusinesses(data.businesses);
        if (data.businesses.length > 0) {
          setSelectedBusinessId(data.businesses[0].id);
        }
      } else if (response.status === 401) {
        setLocation('/login');
      }
    } catch (err) {
      console.error('Failed to fetch businesses');
    }
  };

  // Fetch leads using React Query
  const { data: leadsData, isLoading: leadsLoading, error: leadsError } = useQuery<LeadsResponse>({
    queryKey: [`/api/businesses/${selectedBusinessId}/leads`, selectedFilter, dateFilter],
    queryFn: async () => {
      if (!selectedBusinessId) throw new Error('No business selected');
      
      const response = await fetch(`${API_URL}/api/businesses/${selectedBusinessId}/leads?limit=100`, {
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          setLocation('/login');
        }
        throw new Error('Failed to fetch leads');
      }
      
      const data = await response.json();
      
      // Filter by minimum probability and date on frontend
      let filteredLeads = (data.leads || []).filter(
        (lead: Lead) => lead.ai_score >= getMinProbability()
      );

      // Apply date filter
      if (dateFilter !== 'all') {
        const now = new Date();
        const filterDate = new Date();
        
        switch (dateFilter) {
          case 'today':
            filterDate.setHours(0, 0, 0, 0);
            break;
          case 'week':
            filterDate.setDate(now.getDate() - 7);
            break;
          case 'month':
            filterDate.setMonth(now.getMonth() - 1);
            break;
          case '3months':
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

  const selectedBusiness = businesses.find(b => b.id === selectedBusinessId);

  if (leadsError) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Reddit Leads</h1>
            <p className="text-gray-600">Failed to load Reddit leads data. Please try again.</p>
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
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No businesses found</h2>
          <p className="text-gray-600 mb-6">
            You need to create a business first to view leads.
          </p>
          <button
            onClick={() => setLocation('/businesses')}
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Reddit Leads</h1>
            <p className="text-gray-600">AI-powered lead discovery from Reddit conversations</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Business:</label>
            <select
              value={selectedBusinessId || ''}
              onChange={(e) => setSelectedBusinessId(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <SiReddit className="w-6 h-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Leads</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {leadsLoading ? <Skeleton className="h-8 w-16" /> : leadsData?.total || 0}
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
                  <p className="text-sm font-medium text-gray-600">Business</p>
                  <p className="text-sm font-bold text-gray-900">
                    {selectedBusiness?.name || 'None'}
                  </p>
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
                  <p className="text-sm font-medium text-gray-600">Filter</p>
                  <p className="text-sm font-bold text-gray-900">
                    {selectedFilter === 'high' ? '70%+' : selectedFilter === 'medium' ? '40%+' : 'All'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center justify-between">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
            {[
              { key: "high", label: "High Quality (70%+)" },
              { key: "medium", label: "Medium Quality (40%+)" },
              { key: "all", label: "All Leads" }
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
                  <p className="text-gray-600 mb-4">Try adjusting your filters or check back later.</p>
                </CardContent>
              </Card>
            </div>
          ) : (
            leadsData?.leads.map((lead) => (
              <Card key={lead.id} className="hover:shadow-lg transition-all duration-200 hover:-translate-y-1 h-fit">
                <CardContent className="p-4">
                  {/* Header with probability and subreddit */}
                  <div className="flex items-center justify-between mb-3">
                    <Badge className={`${getProbabilityColor(lead.ai_score)} border text-xs`}>
                      {getProbabilityEmoji(lead.ai_score)} {lead.ai_score}%
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
                    u/{lead.author} • {formatTimeAgo(lead.created_at)} • {lead.score} ↑
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
                        <Badge key={keyword} variant="secondary" className="text-xs px-2 py-0">
                          {keyword}
                        </Badge>
                      ))}
                      {lead.matched_keywords.length > 3 && (
                        <Badge variant="secondary" className="text-xs px-2 py-0">
                          +{lead.matched_keywords.length - 3}
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