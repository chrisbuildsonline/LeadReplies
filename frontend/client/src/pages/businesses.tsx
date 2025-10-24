import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "../contexts/AuthContext";
import PageLayout from "../components/layout/page-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Plus,
  Edit,
  Trash2,
  Globe,
  Calendar,
  Target,
  Hash,
  ExternalLink,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:6070";

interface Business {
  id: string; // Changed to string for UUID
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

export default function Businesses() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [businessStats, setBusinessStats] = useState<{
    [key: number]: { keywords: number };
  }>({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [, setLocation] = useLocation();
  const { session, signOut } = useAuth();

  const [newBusiness, setNewBusiness] = useState({
    name: "",
    website: "",
    description: "",
  });

  useEffect(() => {
    fetchBusinesses();
  }, []);

  const getAuthHeaders = () => {
    if (!session?.access_token) {
      console.log("🔐 No session token - redirecting to home");
      setLocation("/");
      return {};
    }
    return {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    };
  };

  const handleAuthError = async (response: Response) => {
    if (response.status === 401) {
      console.log(
        "🔐 Authentication failed - signing out and redirecting to home"
      );
      await signOut();
      setLocation("/");
      return true;
    }
    return false;
  };

  const fetchBusinesses = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/businesses`, {
        headers: getAuthHeaders(),
      });

      // Check for auth errors first
      if (await handleAuthError(response)) {
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setBusinesses(data.businesses);

        // Fetch stats for each business
        const stats: { [key: number]: { keywords: number } } = {};
        for (const business of data.businesses) {
          const keywordsRes = await fetch(
            `${API_URL}/api/businesses/${business.id}/keywords`,
            { headers: getAuthHeaders() }
          );

          if (keywordsRes.ok) {
            const keywordsData = await keywordsRes.json();
            stats[business.id] = {
              keywords: keywordsData.keywords?.length || 0,
            };
          }
        }
        setBusinessStats(stats);
      } else if (response.status === 401) {
        setLocation("/login");
      }
    } catch (err) {
      setError("Failed to fetch businesses");
    } finally {
      setLoading(false);
    }
  };

  const createBusiness = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/businesses`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(newBusiness),
      });

      // Check for auth errors first
      if (await handleAuthError(response)) {
        return;
      }

      if (response.ok) {
        setNewBusiness({ name: "", website: "", description: "" });
        setShowCreateForm(false);
        fetchBusinesses();
      } else {
        const data = await response.json();
        setError(data.error || "Failed to create business");
      }
    } catch (err) {
      setError("Network error");
    } finally {
      setCreating(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return "Unknown";
    }
  };

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Business Management
            </h1>
            <p className="text-gray-600">
              Manage your businesses and their lead generation settings
            </p>
          </div>

          <Button
            onClick={() => setShowCreateForm(true)}
            className="bg-purple-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Business
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Total Businesses
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {loading ? (
                      <Skeleton className="h-8 w-16" />
                    ) : (
                      businesses.length
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Hash className="w-6 h-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Total Keywords
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {loading ? (
                      <Skeleton className="h-8 w-16" />
                    ) : (
                      Object.values(businessStats).reduce(
                        (sum, stats) => sum + stats.keywords,
                        0
                      )
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Globe className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Calendar className="w-6 h-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Active Tracking
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {loading ? (
                      <Skeleton className="h-8 w-16" />
                    ) : (
                      businesses.length
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Businesses Table */}
        <Card>
          <CardContent className="p-0">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Your Businesses
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Manage and configure your business lead generation
              </p>
            </div>

            {loading ? (
              <div className="p-6">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex items-center space-x-4 py-4 border-b border-gray-100 last:border-0"
                  >
                    <Skeleton className="h-12 w-12 rounded-lg" />
                    <div className="flex-1">
                      <Skeleton className="h-5 w-48 mb-2" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                    <div className="flex space-x-2">
                      <Skeleton className="h-6 w-16" />
                      <Skeleton className="h-6 w-16" />
                    </div>
                    <Skeleton className="h-8 w-20" />
                  </div>
                ))}
              </div>
            ) : businesses.length === 0 ? (
              <div className="p-12 text-center">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No businesses yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Create your first business to start tracking leads
                </p>
                <Button
                  onClick={() => setShowCreateForm(true)}
                  className="bg-purple-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Business
                </Button>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {businesses.map((business) => (
                  <div
                    key={business.id}
                    className="p-6 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <span className="text-white font-bold text-lg">
                            {business.name.charAt(0).toUpperCase()}
                          </span>
                        </div>

                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {business.name}
                          </h3>
                          <p className="text-sm text-gray-600 mb-2 w-[80%]">
                            {business.description}
                          </p>

                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            {business.website && (
                              <a
                                href={business.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center hover:text-blue-600"
                              >
                                <Globe className="w-4 h-4 mr-1" />
                                Website
                                <ExternalLink className="w-3 h-3 ml-1" />
                              </a>
                            )}
                            <span className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              Created {formatDate(business.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            setLocation(`/businesses/${business.id}/edit`)
                          }
                          className="text-blue-600 border-blue-200 hover:bg-blue-50"
                        >
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Create Business Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardContent className="p-6">
                <h2 className="text-lg font-semibold mb-4">
                  Create New Business
                </h2>
                <form onSubmit={createBusiness} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Business Name
                    </label>
                    <input
                      type="text"
                      required
                      value={newBusiness.name}
                      onChange={(e) =>
                        setNewBusiness({ ...newBusiness, name: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter business name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Website URL
                    </label>
                    <input
                      type="url"
                      value={newBusiness.website}
                      onChange={(e) =>
                        setNewBusiness({
                          ...newBusiness,
                          website: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="https://example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Description
                    </label>
                    <textarea
                      value={newBusiness.description}
                      onChange={(e) =>
                        setNewBusiness({
                          ...newBusiness,
                          description: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      rows={3}
                      placeholder="Describe your business"
                    />
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button
                      type="submit"
                      disabled={creating}
                      className="flex-1 bg-purple-600 hover:bg-blue-700"
                    >
                      {creating ? "Creating..." : "Create Business"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowCreateForm(false)}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
