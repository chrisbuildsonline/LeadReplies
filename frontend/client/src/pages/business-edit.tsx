import { useState, useEffect } from 'react';
import { useLocation, useRoute } from 'wouter';
import PageLayout from '../components/layout/page-layout';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, Plus, X, Globe, Hash, Target, Sparkles, Trash2 } from "lucide-react";

const API_URL = '';

interface Business {
  id: number;
  name: string;
  website: string;
  description: string;
  created_at: string;
}

interface Keyword {
  id: number;
  keyword: string;
  source: string;
}

interface Subreddit {
  id: number;
  subreddit: string;
  source: string;
}

export default function BusinessEdit() {
  const [, params] = useRoute('/businesses/:id/edit');
  const [, setLocation] = useLocation();
  const businessId = params?.id ? parseInt(params.id) : null;

  const [business, setBusiness] = useState<Business | null>(null);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [subreddits, setSubreddits] = useState<Subreddit[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  const [editedBusiness, setEditedBusiness] = useState({
    name: '',
    website: '',
    description: ''
  });

  const [newKeyword, setNewKeyword] = useState('');
  const [newSubreddit, setNewSubreddit] = useState('');

  useEffect(() => {
    if (businessId) {
      fetchBusinessData();
    }
  }, [businessId]);

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

  const fetchBusinessData = async () => {
    if (!businessId) return;

    try {
      setLoading(true);
      const [businessRes, keywordsRes, subredditsRes] = await Promise.all([
        fetch(`${API_URL}/api/businesses/${businessId}`, { headers: getAuthHeaders() }),
        fetch(`${API_URL}/api/businesses/${businessId}/keywords`, { headers: getAuthHeaders() }),
        fetch(`${API_URL}/api/businesses/${businessId}/subreddits`, { headers: getAuthHeaders() })
      ]);

      if (businessRes.ok) {
        const businessData = await businessRes.json();
        setBusiness(businessData.business);
        setEditedBusiness({
          name: businessData.business.name,
          website: businessData.business.website || '',
          description: businessData.business.description || ''
        });
      }

      if (keywordsRes.ok) {
        const keywordsData = await keywordsRes.json();
        setKeywords(keywordsData.keywords || []);
      }

      if (subredditsRes.ok) {
        const subredditsData = await subredditsRes.json();
        setSubreddits(subredditsData.subreddits || []);
      }

      if (!businessRes.ok && businessRes.status === 401) {
        setLocation('/login');
      }
    } catch (err) {
      setError('Failed to load business data');
    } finally {
      setLoading(false);
    }
  };

  const saveBusiness = async () => {
    if (!businessId) return;

    setSaving(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(editedBusiness),
      });

      if (response.ok) {
        setBusiness({ ...business!, ...editedBusiness });
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to save business');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setSaving(false);
    }
  };

  const analyzeWebsite = async () => {
    if (!businessId || !editedBusiness.website) {
      setError('Please add a website URL first');
      return;
    }

    setAnalyzing(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}/analyze-website`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          website_url: editedBusiness.website,
          business_name: editedBusiness.name,
          business_description: editedBusiness.description
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add suggested keywords
        if (data.keywords && data.keywords.length > 0) {
          for (const kw of data.keywords) {
            await addKeyword(kw.keyword, 'ai_website');
          }
        }

        // Add suggested subreddits
        if (data.subreddits && data.subreddits.length > 0) {
          for (const sub of data.subreddits) {
            await addSubreddit(sub.subreddit, 'ai_suggested');
          }
        }

        fetchBusinessData();
      } else {
        const data = await response.json();
        setError(data.error || 'Website analysis failed');
      }
    } catch (err) {
      setError('Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const addKeyword = async (keyword: string, source: string = 'manual') => {
    if (!businessId || !keyword.trim()) return;

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}/keywords`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ keyword: keyword.trim(), source }),
      });

      if (response.ok) {
        if (source === 'manual') {
          setNewKeyword('');
          fetchBusinessData();
        }
      }
    } catch (err) {
      console.error('Failed to add keyword');
    }
  };

  const addSubreddit = async (subreddit: string, source: string = 'manual') => {
    if (!businessId || !subreddit.trim()) return;

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}/subreddits`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ subreddit: subreddit.trim(), source }),
      });

      if (response.ok) {
        if (source === 'manual') {
          setNewSubreddit('');
          fetchBusinessData();
        }
      }
    } catch (err) {
      console.error('Failed to add subreddit');
    }
  };

  const removeKeyword = async (keywordId: number) => {
    if (!businessId) return;

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}/keywords/${keywordId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        fetchBusinessData();
      }
    } catch (err) {
      console.error('Failed to remove keyword');
    }
  };

  const removeSubreddit = async (subredditId: number) => {
    if (!businessId) return;

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}/subreddits/${subredditId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        fetchBusinessData();
      }
    } catch (err) {
      console.error('Failed to remove subreddit');
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-10" />
            <Skeleton className="h-8 w-48" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardContent className="p-6">
                <Skeleton className="h-6 w-32 mb-4" />
                <Skeleton className="h-10 w-full mb-4" />
                <Skeleton className="h-10 w-full mb-4" />
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <Skeleton className="h-6 w-32 mb-4" />
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (!business) {
    return (
      <PageLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Business not found</h2>
          <p className="text-gray-600 mb-6">The business you're looking for doesn't exist.</p>
          <Button onClick={() => setLocation('/businesses')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Businesses
          </Button>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              onClick={() => setLocation('/businesses')}
              className="p-2"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Edit Business</h1>
              <p className="text-gray-600">Configure your business settings and lead generation</p>
            </div>
          </div>

          <div className="flex space-x-2">
            <Button
              onClick={analyzeWebsite}
              disabled={analyzing || !editedBusiness.website}
              variant="outline"
              className="text-purple-600 border-purple-200 hover:bg-purple-50"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              {analyzing ? 'Analyzing...' : 'AI Analyze'}
            </Button>
            <Button
              onClick={saveBusiness}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Business Details */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center mb-4">
                <Target className="w-5 h-5 text-blue-600 mr-2" />
                <h2 className="text-lg font-semibold">Business Details</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Business Name</label>
                  <input
                    type="text"
                    value={editedBusiness.name}
                    onChange={(e) => setEditedBusiness({ ...editedBusiness, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Website URL</label>
                  <input
                    type="url"
                    value={editedBusiness.website}
                    onChange={(e) => setEditedBusiness({ ...editedBusiness, website: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="https://example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Description</label>
                  <textarea
                    value={editedBusiness.description}
                    onChange={(e) => setEditedBusiness({ ...editedBusiness, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={4}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Keywords */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Hash className="w-5 h-5 text-green-600 mr-2" />
                  <h2 className="text-lg font-semibold">Keywords ({keywords.length})</h2>
                </div>
              </div>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  placeholder="Add keyword..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && addKeyword(newKeyword)}
                />
                <Button
                  onClick={() => addKeyword(newKeyword)}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
                {keywords.map((keyword) => (
                  <Badge
                    key={keyword.id}
                    className={`inline-flex items-center gap-1 ${
                      keyword.source === 'ai_website'
                        ? 'bg-purple-100 text-purple-800 border-purple-200'
                        : 'bg-blue-100 text-blue-800 border-blue-200'
                    }`}
                  >
                    {keyword.keyword}
                    {keyword.source === 'ai_website' && <Sparkles className="w-3 h-3" />}
                    <button
                      onClick={() => removeKeyword(keyword.id)}
                      className="ml-1 text-red-500 hover:text-red-700"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Subreddits */}
          <Card className="lg:col-span-2">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Globe className="w-5 h-5 text-orange-600 mr-2" />
                  <h2 className="text-lg font-semibold">Subreddits ({subreddits.length})</h2>
                </div>
              </div>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={newSubreddit}
                  onChange={(e) => setNewSubreddit(e.target.value)}
                  placeholder="Add subreddit (without r/)..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && addSubreddit(newSubreddit)}
                />
                <Button
                  onClick={() => addSubreddit(newSubreddit)}
                  size="sm"
                  className="bg-orange-600 hover:bg-orange-700"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex flex-wrap gap-2">
                {subreddits.map((subreddit) => (
                  <Badge
                    key={subreddit.id}
                    className={`inline-flex items-center gap-1 ${
                      subreddit.source === 'ai_suggested'
                        ? 'bg-purple-100 text-purple-800 border-purple-200'
                        : 'bg-orange-100 text-orange-800 border-orange-200'
                    }`}
                  >
                    r/{subreddit.subreddit}
                    {subreddit.source === 'ai_suggested' && <Sparkles className="w-3 h-3" />}
                    <button
                      onClick={() => removeSubreddit(subreddit.id)}
                      className="ml-1 text-red-500 hover:text-red-700"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageLayout>
  );
}