import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from 'wouter';
import PageLayout from "@/components/layout/page-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { 
  MessageSquare, 
  Send, 
  Edit3, 
  Trash2, 
  ExternalLink, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Eye,
  Filter,
  Calendar,
  TrendingUp
} from "lucide-react";
import { SiReddit } from "react-icons/si";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:6070';

interface Reply {
  id: number;
  business_lead_id: number;
  user_id: number;
  reply_content: string;
  status: 'draft' | 'pending' | 'posted' | 'failed';
  platform_reply_id?: string;
  created_at: string;
  updated_at: string;
  posted_at?: string;
  // Lead information
  lead_title: string;
  lead_url: string;
  lead_platform: string;

  lead_author: string;
  ai_score: number;
}

interface RepliesData {
  replies: Reply[];
  total: number;
  stats: {
    draft: number;
    pending: number;
    posted: number;
    failed: number;
  };
}

export default function Replies() {
  const [, setLocation] = useLocation();
  const [filter, setFilter] = useState<'all' | 'draft' | 'pending' | 'posted' | 'failed'>('all');
  const [editingReply, setEditingReply] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const queryClient = useQueryClient();

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLocation('/login');
      return undefined;
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  };

  const {
    data: repliesData,
    isLoading,
    error,
  } = useQuery<RepliesData>({
    queryKey: ["/api/replies", filter],
    queryFn: async () => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const statusParam = filter !== 'all' ? `?status=${filter}` : '';
      const response = await fetch(`${API_URL}/api/replies${statusParam}`, {
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          setLocation("/login");
        }
        throw new Error("Failed to fetch replies");
      }

      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const updateReplyMutation = useMutation({
    mutationFn: async ({ replyId, content }: { replyId: number, content: string }) => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/replies/${replyId}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ reply_content: content }),
      });

      if (!response.ok) throw new Error("Failed to update reply");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/replies"] });
      setEditingReply(null);
      setEditContent('');
    },
  });

  const deleteReplyMutation = useMutation({
    mutationFn: async (replyId: number) => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/replies/${replyId}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) throw new Error("Failed to delete reply");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/replies"] });
    },
  });

  const postReplyMutation = useMutation({
    mutationFn: async (replyId: number) => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/replies/${replyId}/post`, {
        method: 'POST',
        headers,
      });

      if (!response.ok) throw new Error("Failed to post reply");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/replies"] });
    },
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft':
        return <Edit3 className="w-4 h-4 text-gray-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'posted':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <MessageSquare className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return <Badge className="bg-gray-100 text-gray-700 border-gray-200">Draft</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Pending</Badge>;
      case 'posted':
        return <Badge className="bg-green-100 text-green-800 border-green-200">Posted</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800 border-red-200">Failed</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-700 border-gray-200">{status}</Badge>;
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'reddit':
        return <SiReddit className="w-5 h-5 text-orange-600" />;
      default:
        return <MessageSquare className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  const handleEditReply = (reply: Reply) => {
    setEditingReply(reply.id);
    setEditContent(reply.reply_content);
  };

  const handleSaveEdit = () => {
    if (editingReply && editContent.trim()) {
      updateReplyMutation.mutate({ replyId: editingReply, content: editContent.trim() });
    }
  };

  const handleCancelEdit = () => {
    setEditingReply(null);
    setEditContent('');
  };

  if (error) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Replies</h1>
            <p className="text-gray-600">Failed to load replies. Please try again.</p>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Replies</h1>
            <p className="text-gray-600">Manage your AI-generated replies and drafts</p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Draft Replies</CardTitle>
              <Edit3 className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {repliesData?.stats?.draft || 0}
              </div>
              <p className="text-xs text-gray-500 mt-1">Ready for review</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {repliesData?.stats?.pending || 0}
              </div>
              <p className="text-xs text-gray-500 mt-1">Being processed</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Posted</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {repliesData?.stats?.posted || 0}
              </div>
              <p className="text-xs text-gray-500 mt-1">Successfully posted</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Failed</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {repliesData?.stats?.failed || 0}
              </div>
              <p className="text-xs text-gray-500 mt-1">Need attention</p>
            </CardContent>
          </Card>
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          {[
            { key: 'all', label: 'All Replies' },
            { key: 'draft', label: 'Drafts' },
            { key: 'pending', label: 'Pending' },
            { key: 'posted', label: 'Posted' },
            { key: 'failed', label: 'Failed' },
          ].map((filterOption) => (
            <button
              key={filterOption.key}
              onClick={() => setFilter(filterOption.key as any)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === filterOption.key
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {filterOption.label}
            </button>
          ))}
        </div>

        {/* Replies List */}
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      <div className="h-20 bg-gray-200 rounded w-full"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : repliesData?.replies?.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {filter === 'all' ? 'No replies yet' : `No ${filter} replies`}
              </h3>
              <p className="text-gray-600">
                {filter === 'all' 
                  ? 'Replies will appear here when AI generates them for your leads.'
                  : `No replies with ${filter} status found.`
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {repliesData?.replies?.map((reply) => (
              <Card 
                key={reply.id} 
                className="bg-white/50 backdrop-blur-sm border-gray-200 hover:bg-white hover:shadow-md transition-all duration-200"
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="flex-shrink-0">
                        {getPlatformIcon(reply.lead_platform)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-base font-semibold text-gray-900 truncate">
                            {reply.lead_title}
                          </h3>
                          {getStatusBadge(reply.status)}
                        </div>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                          <span>u/{reply.lead_author}</span>

                          <span>AI Score: {reply.ai_score}%</span>
                          <span>{formatTimeAgo(reply.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      {getStatusIcon(reply.status)}
                    </div>
                  </div>

                  {/* Reply Content */}
                  <div className="mb-4">
                    <Label className="text-sm font-medium text-gray-700 mb-2 block">Reply Content</Label>
                    {editingReply === reply.id ? (
                      <div className="space-y-3">
                        <Textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          rows={4}
                          className="w-full"
                        />
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            onClick={handleSaveEdit}
                            disabled={updateReplyMutation.isPending}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            {updateReplyMutation.isPending ? 'Saving...' : 'Save'}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleCancelEdit}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                          {reply.reply_content}
                        </p>
                      </div>
                    )}
                  </div>

                  <Separator className="my-4" />

                  {/* Actions */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(reply.lead_url, '_blank')}
                        className="text-orange-600 border-orange-200 hover:bg-orange-50"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        View Lead
                      </Button>
                      
                      {reply.platform_reply_id && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(`${reply.lead_url}/${reply.platform_reply_id}`, '_blank')}
                          className="text-green-600 border-green-200 hover:bg-green-50"
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          View Reply
                        </Button>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      {reply.status === 'draft' && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditReply(reply)}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                          >
                            <Edit3 className="w-4 h-4 mr-1" />
                            Edit
                          </Button>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => postReplyMutation.mutate(reply.id)}
                            disabled={postReplyMutation.isPending}
                            className="text-green-600 hover:text-green-700 hover:bg-green-50"
                          >
                            <Send className="w-4 h-4 mr-1" />
                            Post
                          </Button>
                        </>
                      )}
                      
                      {(reply.status === 'draft' || reply.status === 'failed') && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteReplyMutation.mutate(reply.id)}
                          disabled={deleteReplyMutation.isPending}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Delete
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}