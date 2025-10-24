import { useState, useEffect } from "react";
import { useLocation, useRoute } from "wouter";
import { useAuth } from "../contexts/AuthContext";
import PageLayout from "../components/layout/page-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import {
  ArrowLeft,
  Plus,
  X,
  Hash,
  Target,
  Sparkles,
  Trash2,
  Bot,
  Settings,
  MessageSquare,
  Shield,
  Link as LinkIcon,
  Sliders,
} from "lucide-react";
import { ClipLoader } from "react-spinners";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:6070";

interface Business {
  id: string; // Changed to string for UUID
  name: string;
  website: string;
  description: string;
  buying_intent: string;
  created_at: string;
}

interface Keyword {
  id: number;
  keyword: string;
  source: string;
}

interface AISettings {
  persona: string;
  instructions: string;
  bad_words: string[];
  service_links: Record<string, string>;
  tone: string;
  max_reply_length: number;
  include_links: boolean;
  auto_reply_enabled: boolean;
  confidence_threshold: number;
}

export default function BusinessEdit() {
  const [, params] = useRoute("/businesses/:id/edit");
  const [, setLocation] = useLocation();
  const { session } = useAuth();
  const { toast } = useToast();
  const businessId = params?.id || null;

  const [activeTab, setActiveTab] = useState("general");
  const [business, setBusiness] = useState<Business | null>(null);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [aiSettings, setAiSettings] = useState<AISettings>({
    persona: "",
    instructions: "",
    bad_words: [],
    service_links: {},
    tone: "professional",
    max_reply_length: 500,
    include_links: true,
    auto_reply_enabled: false,
    confidence_threshold: 0.8,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [websiteUrlForSetup, setWebsiteUrlForSetup] = useState("");
  const [setupMode, setSetupMode] = useState<"website" | "text">("website");
  const [businessPrompt, setBusinessPrompt] = useState("");
  const [clearingKeywords, setClearingKeywords] = useState(false);

  const [editedBusiness, setEditedBusiness] = useState({
    name: "",
    website: "",
    description: "",
    buying_intent: "",
  });

  const [newKeyword, setNewKeyword] = useState("");
  const [newBadWord, setNewBadWord] = useState("");
  const [newServiceName, setNewServiceName] = useState("");
  const [newServiceUrl, setNewServiceUrl] = useState("");

  useEffect(() => {
    if (businessId && session?.access_token) {
      fetchBusinessData();
    }
  }, [businessId, session?.access_token]);

  // Debug: Log when business name changes
  useEffect(() => {
    console.log("🏢 Business name changed to:", editedBusiness.name);
  }, [editedBusiness.name]);

  const getAuthHeaders = (): Record<string, string> => {
    if (!session?.access_token) {
      console.log("🔐 No session token - redirecting to home");
      setLocation("/");
      throw new Error("No auth token");
    }
    return {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    };
  };

  const fetchBusinessData = async () => {
    if (!businessId || !session?.access_token) return;

    try {
      setLoading(true);
      console.log("🔍 Fetching business data for ID:", businessId);
      console.log(
        "🔐 Using session token:",
        session.access_token.substring(0, 20) + "..."
      );

      const [businessRes, keywordsRes, aiSettingsRes] = await Promise.all([
        fetch(`${API_URL}/api/businesses/${businessId}`, {
          headers: getAuthHeaders(),
        }),
        fetch(`${API_URL}/api/businesses/${businessId}/keywords`, {
          headers: getAuthHeaders(),
        }),
        fetch(`${API_URL}/api/businesses/${businessId}/ai-settings`, {
          headers: getAuthHeaders(),
        }),
      ]);

      console.log("📊 API Response Status:", {
        business: businessRes.status,
        keywords: keywordsRes.status,
        aiSettings: aiSettingsRes.status,
      });

      if (businessRes.ok) {
        const businessData = await businessRes.json();
        console.log("✅ Business data:", businessData);
        setBusiness(businessData.business);
        setEditedBusiness({
          name: businessData.business.name,
          website: businessData.business.website || "",
          description: businessData.business.description || "",
          buying_intent: businessData.business.buying_intent || "",
        });
      } else {
        console.error(
          "❌ Business fetch failed:",
          businessRes.status,
          await businessRes.text()
        );
      }

      if (keywordsRes.ok) {
        const keywordsData = await keywordsRes.json();
        console.log("✅ Keywords data:", keywordsData);
        setKeywords(keywordsData.keywords || []);
      } else {
        console.error(
          "❌ Keywords fetch failed:",
          keywordsRes.status,
          await keywordsRes.text()
        );
      }

      if (aiSettingsRes.ok) {
        const aiSettingsData = await aiSettingsRes.json();
        console.log("✅ AI Settings data:", aiSettingsData);
        setAiSettings(aiSettingsData.ai_settings);
      } else {
        console.error(
          "❌ AI Settings fetch failed:",
          aiSettingsRes.status,
          await aiSettingsRes.text()
        );
      }

      if (!businessRes.ok && businessRes.status === 401) {
        setLocation("/login");
      }
    } catch (err) {
      console.error("❌ Fetch error:", err);
      setError("Failed to load business data");
    } finally {
      setLoading(false);
    }
  };

  const saveBusiness = async () => {
    if (!businessId) return;

    setSaving(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/businesses/${businessId}`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(editedBusiness),
      });

      if (response.ok) {
        setBusiness({ ...business!, ...editedBusiness });
      } else {
        const data = await response.json();
        setError(data.error || "Failed to save business");
      }
    } catch (err) {
      setError("Network error");
    } finally {
      setSaving(false);
    }
  };

  const analyzeWebsite = async () => {
    if (!businessId || !editedBusiness.website) {
      setError("Please add a website URL first");
      return;
    }

    setAnalyzing(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/businesses/${businessId}/analyze-website`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            website_url: editedBusiness.website,
            business_name: editedBusiness.name,
            business_description: editedBusiness.description,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();

        // Add suggested keywords
        if (data.keywords && data.keywords.length > 0) {
          for (const kw of data.keywords) {
            await addKeyword(kw.keyword, "ai_website");
          }
        }

        fetchBusinessData();
      } else {
        const data = await response.json();
        setError(data.error || "Website analysis failed");
      }
    } catch (err) {
      setError("Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const addKeyword = async (keyword: string, source: string = "manual") => {
    if (!businessId || !keyword.trim()) return;
    
    // Check keyword limit
    if (keywords.length >= 10) {
      toast({
        title: "Keyword Limit Reached",
        description: "Maximum 10 keywords allowed per business. Remove some keywords to add new ones.",
        variant: "destructive",
        duration: 4000,
      });
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/businesses/${businessId}/keywords`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ keyword: keyword.trim(), source }),
        }
      );

      if (response.ok) {
        if (source === "manual") {
          setNewKeyword("");
          toast({
            title: "Keyword Added",
            description: `"${keyword.trim()}" has been added to your keywords.`,
            duration: 2000,
          });
          fetchBusinessData();
        }
      }
    } catch (err) {
      console.error("Failed to add keyword");
    }
  };

  const clearAllKeywords = async () => {
    if (!businessId) return;
    
    if (!confirm("Are you sure you want to remove all keywords? This action cannot be undone.")) {
      return;
    }

    try {
      setClearingKeywords(true);
      setError(""); // Clear any previous errors
      
      // Use the new bulk delete endpoint
      const response = await fetch(
        `${API_URL}/api/businesses/${businessId}/keywords`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        // Immediately update the keywords state to show 0 keywords
        setKeywords([]);
        
        // Show success toast
        toast({
          title: "Keywords Cleared",
          description: "All keywords have been successfully removed!",
          duration: 3000,
        });
        
        // Refresh the data to ensure consistency
        fetchBusinessData();
      } else {
        throw new Error("Failed to clear keywords");
      }
    } catch (err) {
      console.error("Failed to clear keywords");
      toast({
        title: "Error",
        description: "Failed to clear keywords. Please try again.",
        variant: "destructive",
        duration: 4000,
      });
    } finally {
      setClearingKeywords(false);
    }
  };

  const removeKeyword = async (keywordId: number) => {
    if (!businessId) return;

    try {
      const response = await fetch(
        `${API_URL}/api/businesses/${businessId}/keywords/${keywordId}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        fetchBusinessData();
      }
    } catch (err) {
      console.error("Failed to remove keyword");
    }
  };

  const saveAISettings = async () => {
    if (!businessId) return;

    setSaving(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/businesses/${businessId}/ai-settings`,
        {
          method: "PUT",
          headers: getAuthHeaders(),
          body: JSON.stringify(aiSettings),
        }
      );

      if (response.ok) {
        // Settings saved successfully
      } else {
        const data = await response.json();
        setError(data.error || "Failed to save AI settings");
      }
    } catch (err) {
      setError("Network error");
    } finally {
      setSaving(false);
    }
  };

  const addBadWord = () => {
    if (
      newBadWord.trim() &&
      !aiSettings.bad_words.includes(newBadWord.trim())
    ) {
      setAiSettings({
        ...aiSettings,
        bad_words: [...aiSettings.bad_words, newBadWord.trim()],
      });
      setNewBadWord("");
    }
  };

  const removeBadWord = (word: string) => {
    setAiSettings({
      ...aiSettings,
      bad_words: aiSettings.bad_words.filter((w) => w !== word),
    });
  };

  const addServiceLink = () => {
    if (newServiceName.trim() && newServiceUrl.trim()) {
      setAiSettings({
        ...aiSettings,
        service_links: {
          ...aiSettings.service_links,
          [newServiceName.trim()]: newServiceUrl.trim(),
        },
      });
      setNewServiceName("");
      setNewServiceUrl("");
    }
  };

  const removeServiceLink = (serviceName: string) => {
    const newLinks = { ...aiSettings.service_links };
    delete newLinks[serviceName];
    setAiSettings({
      ...aiSettings,
      service_links: newLinks,
    });
  };

  const handleAIAutoSetup = () => {
    // Check if website URL is available for website mode
    const websiteUrl = editedBusiness.website?.trim();

    if (websiteUrl) {
      setWebsiteUrlForSetup(websiteUrl);
      setSetupMode("website");
    } else {
      // Default to text mode if no website
      setSetupMode("text");
    }

    // Show confirmation dialog
    setShowConfirmDialog(true);
  };

  const performAIAutoSetup = async () => {
    if (!businessId) return;

    setAnalyzing(true);
    setError("");
    setShowConfirmDialog(false);

    try {
      const requestBody =
        setupMode === "website"
          ? {
              mode: "website",
              website_url: websiteUrlForSetup,
              business_name: editedBusiness.name,
            }
          : {
              mode: "text",
              business_prompt: businessPrompt,
              business_name: editedBusiness.name,
            };

      const response = await fetch(
        `${API_URL}/api/businesses/${businessId}/ai-auto-setup`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify(requestBody),
        }
      );

      if (response.ok) {
        const data = await response.json();

        // Debug logging
        console.log("🔍 AI Setup Response:", data);
        if (data.business_info) {
          console.log("📝 Business Name from AI:", data.business_info.name);
          console.log("📝 Current Name:", editedBusiness.name);
        }

        // Update all fields with AI-generated data
        if (data.business_info) {
          const newBusinessData = {
            ...editedBusiness,
            name: data.business_info.name || editedBusiness.name,
            description:
              data.business_info.description || editedBusiness.description,
            buying_intent:
              data.business_info.buying_intent || editedBusiness.buying_intent,
            website:
              setupMode === "website"
                ? websiteUrlForSetup
                : editedBusiness.website,
          };

          console.log("🔄 Updating business data:", newBusinessData);
          setEditedBusiness(newBusinessData);
        }

        if (data.ai_settings) {
          setAiSettings({
            ...aiSettings,
            persona: data.ai_settings.persona || aiSettings.persona,
            instructions:
              data.ai_settings.instructions || aiSettings.instructions,
            tone: data.ai_settings.tone || aiSettings.tone,
            service_links:
              setupMode === "website"
                ? data.ai_settings.service_links || aiSettings.service_links
                : aiSettings.service_links, // Don't overwrite service links in text mode
          });
        }

        // Refresh data to get new keywords
        await fetchBusinessData();

        // Auto-save the business info
        await saveBusiness();
        await saveAISettings();
      } else {
        const data = await response.json();
        setError(data.error || "AI Auto-Setup failed");
      }
    } catch (err) {
      setError("AI Auto-Setup failed");
    } finally {
      setAnalyzing(false);
    }
  };

  // Show loading while waiting for session
  if (!session) {
    return (
      <PageLayout>
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-10" />
            <Skeleton className="h-8 w-48" />
          </div>
          <div className="text-center text-gray-500 mt-8">
            Loading session...
          </div>
        </div>
      </PageLayout>
    );
  }

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
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Business not found
          </h2>
          <p className="text-gray-600 mb-6">
            The business you're looking for doesn't exist.
          </p>
          <Button onClick={() => setLocation("/businesses")}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Businesses
          </Button>
        </div>
      </PageLayout>
    );
  }

  const tabs = [
    { id: "general", name: "General", icon: Target },
    { id: "targeting", name: "Targeting", icon: Hash },
    { id: "ai-replies", name: "AI Replies", icon: Bot },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "general":
        return (
          <div className="space-y-6">
            <Card className="bg-gradient-to-br from-white to-gray-50/50 border-gray-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r border-b border-gray-200">
                <CardTitle className="flex items-center text-gray-800">
                  <Target className="w-5 h-5 text-blue-600 mr-2" />
                  Business Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 p-6">
                <div className="space-y-2">
                  <Label
                    htmlFor="name"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Business Name
                  </Label>
                  <Input
                    id="name"
                    value={editedBusiness.name}
                    onChange={(e) =>
                      setEditedBusiness({
                        ...editedBusiness,
                        name: e.target.value,
                      })
                    }
                    placeholder="Enter business name"
                    disabled={analyzing}
                    className="border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <div className="space-y-2">
                  <Label
                    htmlFor="website"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Website URL
                  </Label>
                  <Input
                    id="website"
                    type="url"
                    value={editedBusiness.website}
                    onChange={(e) =>
                      setEditedBusiness({
                        ...editedBusiness,
                        website: e.target.value,
                      })
                    }
                    placeholder="https://example.com"
                    disabled={analyzing}
                    className="border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <div className="space-y-2">
                  <Label
                    htmlFor="description"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Description
                  </Label>
                  <Textarea
                    id="description"
                    value={editedBusiness.description}
                    onChange={(e) =>
                      setEditedBusiness({
                        ...editedBusiness,
                        description: e.target.value,
                      })
                    }
                    placeholder="Describe your business..."
                    rows={4}
                    disabled={analyzing}
                    className="border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <div className="space-y-2">
                  <Label
                    htmlFor="buying_intent"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Buying Intent
                    <span className="text-xs text-blue-600 font-normal ml-2 bg-blue-50 px-2 py-1 rounded-full">
                      Recommended for better AI scoring
                    </span>
                  </Label>
                  <Textarea
                    id="buying_intent"
                    value={editedBusiness.buying_intent}
                    onChange={(e) =>
                      setEditedBusiness({
                        ...editedBusiness,
                        buying_intent: e.target.value,
                      })
                    }
                    placeholder="Describe what constitutes a qualified lead for your business. Examples: 'Someone wanting to buy a car', 'Someone looking for help switching an exhaust pipe on their car', 'People seeking web development services for their startup'..."
                    rows={3}
                    disabled={analyzing}
                    className="border-2 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-3">
                    <p className="text-xs text-purple-700 leading-relaxed">
                      💡 This helps AI better identify high-quality leads by
                      understanding what type of customer intent you're looking
                      for. Be specific about the problems your customers are
                      trying to solve.
                    </p>
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-gray-200">
                  <Button
                    onClick={saveBusiness}
                    disabled={saving || analyzing}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                  >
                    {saving ? "Saving..." : "Save Changes"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case "targeting":
        return (
          <div className="space-y-6">
            {/* Keywords */}
            <Card className="bg-gradient-to-br from-white to-green-50/30 border-gray-200 shadow-lg">
              <CardHeader className=" border-b border-gray-200">
                <CardTitle className="flex items-center justify-between text-gray-800">
                  <div className="flex items-center">
                    <Hash className="w-5 h-5 text-green-600 mr-2" />
                    Keywords ({keywords.length}/10)
                  </div>
                  {keywords.length > 0 && (
                    <Button
                      onClick={clearAllKeywords}
                      variant="outline"
                      size="sm"
                      disabled={clearingKeywords}
                      className="text-red-600 border-red-200 hover:bg-red-50 disabled:opacity-50"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      {clearingKeywords ? "Clearing..." : "Clear All"}
                    </Button>
                  )}
                </CardTitle>
                </CardHeader>
              <CardContent className="space-y-4 p-6">
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Input
                      value={newKeyword}
                      onChange={(e) => setNewKeyword(e.target.value)}
                      placeholder={keywords.length >= 10 ? "Maximum keywords reached" : "Add keyword..."}
                      onKeyPress={(e) =>
                        e.key === "Enter" && addKeyword(newKeyword)
                      }
                      disabled={keywords.length >= 10}
                      className="border-2 border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                    <Button
                      onClick={() => addKeyword(newKeyword)}
                      size="sm"
                      disabled={keywords.length >= 10 || !newKeyword.trim()}
                      className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  {keywords.length >= 8 && (
                    <p className={`text-xs ${keywords.length >= 10 ? 'text-red-600' : 'text-orange-600'}`}>
                      {keywords.length >= 10 
                        ? "Maximum of 10 keywords reached. Remove some keywords to add new ones."
                        : `${10 - keywords.length} keywords remaining`
                      }
                    </p>
                  )}
                </div>

                <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 bg-gradient-to-br from-gray-50 to-green-50/50 rounded-lg border border-gray-200">
                  {keywords.map((keyword) => (
                    <Badge
                      key={keyword.id}
                      className={`inline-flex items-center gap-1 shadow-sm transition-all duration-200 hover:scale-105 ${
                        keyword.source === "ai_website"
                          ? "bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800 border-purple-300"
                          : "bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 border-blue-300"
                      }`}
                    >
                      {keyword.keyword}
                      {keyword.source === "ai_website" && (
                        <Sparkles className="w-3 h-3" />
                      )}
                      <button
                        onClick={() => removeKeyword(keyword.id)}
                        className="ml-1 text-red-500 hover:text-red-700 transition-colors duration-200"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case "ai-replies":
        return (
          <div className="space-y-6">
            {/* AI Configuration */}
            <Card className="bg-gradient-to-br from-white to-purple-50/30 border-gray-200 shadow-lg">
              <CardHeader className="border-b border-gray-200">
                <CardTitle className="flex items-center text-gray-800">
                  <Bot className="w-5 h-5 text-purple-600 mr-2" />
                  AI Reply Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 p-6">
                {/* Auto Reply Toggle */}
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border-2 border-purple-200 shadow-sm">
                  <div>
                    <Label className="text-base font-semibold text-gray-800">
                      Auto Reply
                    </Label>
                    <p className="text-sm text-gray-600">
                      Automatically post AI-generated replies to high-quality
                      leads
                    </p>
                  </div>
                  <Switch
                    checked={aiSettings.auto_reply_enabled}
                    onCheckedChange={(checked) =>
                      setAiSettings({
                        ...aiSettings,
                        auto_reply_enabled: checked,
                      })
                    }
                  />
                </div>

                {/* Persona */}
                <div className="space-y-2">
                  <Label
                    htmlFor="persona"
                    className="text-sm font-semibold text-gray-700"
                  >
                    AI Persona
                  </Label>
                  <Textarea
                    id="persona"
                    value={aiSettings.persona}
                    onChange={(e) =>
                      setAiSettings({ ...aiSettings, persona: e.target.value })
                    }
                    placeholder="Describe how the AI should present itself (e.g., 'You are a helpful software consultant with 10 years of experience...')"
                    rows={3}
                    className="border-2 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 resize-none"
                  />
                </div>

                {/* Instructions */}
                <div className="space-y-2">
                  <Label
                    htmlFor="instructions"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Reply Instructions
                  </Label>
                  <Textarea
                    id="instructions"
                    value={aiSettings.instructions}
                    onChange={(e) =>
                      setAiSettings({
                        ...aiSettings,
                        instructions: e.target.value,
                      })
                    }
                    placeholder="Specific instructions for generating replies (e.g., 'Always mention our free trial', 'Keep responses under 200 words', etc.)"
                    rows={4}
                    className="border-2 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400 resize-none"
                  />
                </div>

                {/* Tone Selection */}
                <div className="space-y-2">
                  <Label
                    htmlFor="tone"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Reply Tone
                  </Label>
                  <select
                    id="tone"
                    value={aiSettings.tone}
                    onChange={(e) =>
                      setAiSettings({ ...aiSettings, tone: e.target.value })
                    }
                    className="w-full border-2 border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 shadow-sm transition-all duration-200 hover:border-gray-400"
                  >
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="casual">Casual</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="helpful">Helpful</option>
                  </select>
                </div>

                {/* Settings Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label
                      htmlFor="maxLength"
                      className="text-sm font-semibold text-gray-700"
                    >
                      Max Reply Length
                    </Label>
                    <Input
                      id="maxLength"
                      type="number"
                      value={aiSettings.max_reply_length}
                      onChange={(e) =>
                        setAiSettings({
                          ...aiSettings,
                          max_reply_length: parseInt(e.target.value),
                        })
                      }
                      min="100"
                      max="1000"
                      className="border-2 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="confidence"
                      className="text-sm font-semibold text-gray-700"
                    >
                      Confidence Threshold
                    </Label>
                    <Input
                      id="confidence"
                      type="number"
                      step="0.1"
                      min="0.1"
                      max="1.0"
                      value={aiSettings.confidence_threshold}
                      onChange={(e) =>
                        setAiSettings({
                          ...aiSettings,
                          confidence_threshold: parseFloat(e.target.value),
                        })
                      }
                      className="border-2 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400"
                    />
                  </div>
                </div>

                {/* Include Links Toggle */}
                <div className="flex items-center justify-between p-4rounded-lg shadow-sm">
                  <div>
                    <Label className="text-base font-semibold text-gray-800">
                      Include Service Links
                    </Label>
                    <p className="text-sm text-gray-600">
                      Allow AI to include links to your services in replies
                    </p>
                  </div>
                  <Switch
                    checked={aiSettings.include_links}
                    onCheckedChange={(checked) =>
                      setAiSettings({ ...aiSettings, include_links: checked })
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* Service Links */}
            <Card className="bg-gradient-to-br from-white to-blue-50/30 border-gray-200 shadow-lg">
              <CardHeader className=" border-b border-gray-200">
                <CardTitle className="flex items-center text-gray-800">
                  <LinkIcon className="w-5 h-5 text-blue-600 mr-2" />
                  Service Links
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <Input
                    value={newServiceName}
                    onChange={(e) => setNewServiceName(e.target.value)}
                    placeholder="Service name (e.g., 'Free Trial')"
                    className="border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400"
                  />
                  <div className="flex gap-2">
                    <Input
                      value={newServiceUrl}
                      onChange={(e) => setNewServiceUrl(e.target.value)}
                      placeholder="https://example.com/trial"
                      className="border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400"
                    />
                    <Button
                      onClick={addServiceLink}
                      size="sm"
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="space-y-3">
                  {Object.entries(aiSettings.service_links).map(
                    ([name, url]) => (
                      <div
                        key={name}
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200 shadow-sm"
                      >
                        <div>
                          <span className="font-semibold text-gray-800">
                            {name}
                          </span>
                          <p className="text-sm text-gray-600 break-all">
                            {url}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeServiceLink(name)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50 transition-all duration-200"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Bad Words Filter */}
            <Card className="bg-gradient-to-br from-white to-red-50/30 border-gray-200 shadow-lg">
              <CardHeader className="border-b border-gray-200">
                <CardTitle className="flex items-center text-gray-800">
                  <Shield className="w-5 h-5 text-red-600 mr-2" />
                  Content Filter
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 p-6">
                <div className="flex gap-2">
                  <Input
                    value={newBadWord}
                    onChange={(e) => setNewBadWord(e.target.value)}
                    placeholder="Add word/phrase to avoid..."
                    onKeyPress={(e) => e.key === "Enter" && addBadWord()}
                    className="border-2 border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-400"
                  />
                  <Button
                    onClick={addBadWord}
                    size="sm"
                    className="bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105"
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>

                <div className="flex flex-wrap gap-2">
                  {aiSettings.bad_words.map((word, index) => (
                    <Badge
                      key={index}
                      className="inline-flex items-center gap-1 bg-gradient-to-r from-red-100 to-pink-100 text-red-800 border-red-200 shadow-sm"
                    >
                      {word}
                      <button
                        onClick={() => removeBadWord(word)}
                        className="ml-1 text-red-500 hover:text-red-700 transition-colors duration-200"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  ))}
                </div>

                <div className="mt-6 pt-4 border-t border-gray-200">
                  <Button
                    onClick={saveAISettings}
                    disabled={saving}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105"
                  >
                    {saving ? "Saving..." : "Save AI Settings"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <PageLayout>
      <div className="space-y-6 relative">
        {/* Loading Overlay */}
        {analyzing && (
          <div className="absolute inset-0 bg-white/90 z-50 flex items-center justify-center">
            <div className="bg-white p-8 text-center">
              <ClipLoader
                color="#7c3aed"
                loading={analyzing}
                size={40}
                aria-label="Loading Spinner"
                data-testid="loader"
              />
              <h3 className="text-lg font-semibold text-gray-900 mb-2 mt-4">
                AI Setting Up Your Business
              </h3>
              <p className="text-sm text-gray-600">
                Analyzing and generating your complete setup...
              </p>
            </div>
          </div>
        )}
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              onClick={() => setLocation("/businesses")}
              className="p-2"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Edit Business
              </h1>
              <p className="text-gray-600">
                Configure your business settings and AI automation
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Button
              onClick={handleAIAutoSetup}
              disabled={analyzing}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg transition-all duration-200 transform hover:scale-105"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              {analyzing ? "AI Setting Up..." : "AI Auto-Setup"}
            </Button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className=" rounded-t-lg">
          <nav className="-mb-px flex space-x-1 p-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-3 px-4 rounded-lg font-medium text-sm transition-all duration-200 ${
                    activeTab === tab.id
                      ? "bg-white text-blue-600 shadow-md border-2 border-blue-200 transform scale-105"
                      : "text-gray-600 hover:text-gray-800 hover:bg-white/50 border-2 border-transparent"
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {loading ? (
          <div className="space-y-6">
            <Card>
              <CardContent className="p-6">
                <Skeleton className="h-6 w-32 mb-4" />
                <Skeleton className="h-10 w-full mb-4" />
                <Skeleton className="h-10 w-full mb-4" />
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          </div>
        ) : !business ? (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Business not found
            </h2>
            <p className="text-gray-600 mb-6">
              The business you're looking for doesn't exist.
            </p>
            <Button onClick={() => setLocation("/businesses")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Businesses
            </Button>
          </div>
        ) : (
          renderTabContent()
        )}

        {/* AI Auto-Setup Confirmation Dialog */}
        <AlertDialog
          open={showConfirmDialog}
          onOpenChange={setShowConfirmDialog}
        >
          <AlertDialogContent className="max-w-lg">
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center">
                <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
                AI Auto-Setup Configuration
              </AlertDialogTitle>
              <AlertDialogDescription className="space-y-4">
                {/* Setup Mode Toggle */}
                <div className="space-y-3">
                  <Label className="text-sm font-semibold text-gray-700">
                    Setup Method:
                  </Label>
                  <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                    <button
                      onClick={() => setSetupMode("website")}
                      className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        setupMode === "website"
                          ? "bg-white text-purple-600 shadow-sm"
                          : "text-gray-600 hover:text-gray-900"
                      }`}
                    >
                      Website Analysis
                    </button>
                    <button
                      onClick={() => setSetupMode("text")}
                      className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        setupMode === "text"
                          ? "bg-white text-purple-600 shadow-sm"
                          : "text-gray-600 hover:text-gray-900"
                      }`}
                    >
                      Text Description
                    </button>
                  </div>
                </div>

                {/* Website Mode */}
                {setupMode === "website" && (
                  <div className="space-y-3">
                    <Label
                      htmlFor="website-url"
                      className="text-sm font-semibold text-gray-700"
                    >
                      Website URL:
                    </Label>
                    <Input
                      id="website-url"
                      value={websiteUrlForSetup}
                      onChange={(e) => setWebsiteUrlForSetup(e.target.value)}
                      placeholder="https://example.com"
                      className="border-2 border-gray-300 focus:border-purple-500"
                    />
                    <p className="text-xs text-gray-600">
                      AI will analyze your website and populate all fields
                      including service links.
                    </p>
                  </div>
                )}

                {/* Text Mode */}
                {setupMode === "text" && (
                  <div className="space-y-3">
                    <Label
                      htmlFor="business-prompt"
                      className="text-sm font-semibold text-gray-700"
                    >
                      Describe Your Business:
                    </Label>
                    <Textarea
                      id="business-prompt"
                      value={businessPrompt}
                      onChange={(e) => setBusinessPrompt(e.target.value)}
                      placeholder="e.g., I sell fishing gear and equipment for recreational anglers..."
                      rows={3}
                      className="border-2 border-gray-300 focus:border-purple-500 resize-none"
                    />
                    <p className="text-xs text-gray-600">
                      AI will generate setup based on your description (no
                      website or service links).
                    </p>
                  </div>
                )}

                {/* What will be populated */}
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-blue-800 mb-2">
                    AI will automatically populate:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-xs text-blue-700">
                    <li>Business description and buying intent</li>
                    <li>Relevant targeting keywords (10 max)</li>
                    <li>AI reply persona and instructions</li>
                    {setupMode === "website" && (
                      <li>Service links and website URL</li>
                    )}
                  </ul>
                </div>

                <p className="text-red-600 font-medium text-sm">
                  ⚠️ This will overwrite your current data. Continue?
                </p>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={performAIAutoSetup}
                disabled={
                  (setupMode === "website" && !websiteUrlForSetup.trim()) ||
                  (setupMode === "text" && !businessPrompt.trim())
                }
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
              >
                {setupMode === "website"
                  ? "Analyze & Setup"
                  : "Generate & Setup"}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </PageLayout>
  );
}
