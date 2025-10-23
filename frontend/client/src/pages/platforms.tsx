import { useState, useEffect } from "react";
import { useLocation } from 'wouter';
import { useAuth } from '../contexts/AuthContext';
import PageLayout from "@/components/layout/page-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, Settings, CheckCircle, Clock } from "lucide-react";
import { SiReddit, SiX, SiLinkedin } from "react-icons/si";

const API_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:6070');

interface PlatformSettings {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  isActive: boolean;
  isAvailable: boolean;
  autoReply: boolean;
  confidenceThreshold: number;
  writeReplySuggestion: boolean;
  description: string;
}

export default function Platforms() {
  const [, setLocation] = useLocation();
  const { session } = useAuth();
  const [platforms, setPlatforms] = useState<PlatformSettings[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const platformIcons = {
    reddit: SiReddit,
    twitter: SiX,
    linkedin: SiLinkedin
  };

  const platformDefaults = {
    reddit: {
      name: 'Reddit',
      description: 'Track leads from Reddit posts and comments',
      isAvailable: true
    },
    twitter: {
      name: 'Twitter/X', 
      description: 'Track leads from Twitter posts and mentions',
      isAvailable: false
    },
    linkedin: {
      name: 'LinkedIn',
      description: 'Track leads from LinkedIn posts and comments', 
      isAvailable: false
    }
  };

  const getAuthHeaders = () => {
    if (!session?.access_token) {
      console.log('🔐 No session token - redirecting to home');
      setLocation('/');
      return undefined;
    }
    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
    };
  };

  useEffect(() => {
    fetchPlatformSettings();
  }, []);

  const fetchPlatformSettings = async () => {
    setLoading(true);
    setError('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      // Fetch available platforms and user settings
      const [platformsResponse, settingsResponse] = await Promise.all([
        fetch(`${API_URL}/api/platforms`, { headers }),
        fetch(`${API_URL}/api/platforms/settings`, { headers })
      ]);

      if (!platformsResponse.ok || !settingsResponse.ok) {
        if (platformsResponse.status === 401 || settingsResponse.status === 401) {
          setLocation('/login');
        }
        throw new Error('Failed to fetch platform data');
      }

      const platformsData = await platformsResponse.json();
      const settingsData = await settingsResponse.json();

      // Merge platform info with user settings
      const mergedPlatforms = platformsData.platforms.map((platform: any) => {
        const userSetting = settingsData.settings.find((s: any) => s.platform_id === platform.id);
        
        return {
          id: platform.id,
          name: platform.name,
          icon: platformIcons[platform.id as keyof typeof platformIcons] || SiReddit,
          isActive: userSetting?.is_active || false,
          isAvailable: platform.isAvailable,
          autoReply: userSetting?.auto_reply || false,
          confidenceThreshold: userSetting?.confidence_threshold || 80,
          writeReplySuggestion: userSetting?.write_reply_suggestion || false,
          description: platform.description
        };
      });

      setPlatforms(mergedPlatforms);
      
    } catch (err) {
      setError('Failed to load platform settings. Please try again.');
      console.error('Fetch platform settings error:', err);
    } finally {
      setLoading(false);
    }
  };

  const updatePlatformSetting = (platformId: string, setting: string, value: any) => {
    setPlatforms(prev => prev.map(platform => 
      platform.id === platformId 
        ? { ...platform, [setting]: value }
        : platform
    ));
  };

  const savePlatformSettings = async (platformId: string) => {
    setLoading(true);
    setError('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const platform = platforms.find(p => p.id === platformId);
      if (!platform) return;

      const response = await fetch(`${API_URL}/api/platforms/${platformId}/settings`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({
          isActive: platform.isActive,
          autoReply: platform.autoReply,
          confidenceThreshold: platform.confidenceThreshold,
          writeReplySuggestion: platform.writeReplySuggestion
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          setLocation('/login');
        }
        throw new Error('Failed to save platform settings');
      }

      // Show success message or update UI
      console.log('Platform settings saved successfully');
      
    } catch (err) {
      setError('Failed to save platform settings. Please try again.');
      console.error('Save platform settings error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (IconComponent: React.ComponentType<any>, isActive: boolean, isAvailable: boolean) => {
    const baseClasses = "w-8 h-8";
    if (!isAvailable) {
      return <IconComponent className={`${baseClasses} text-gray-400`} />;
    }
    if (isActive) {
      return <IconComponent className={`${baseClasses} text-orange-600`} />;
    }
    return <IconComponent className={`${baseClasses} text-gray-600`} />;
  };

  const getPlatformStatus = (platform: PlatformSettings) => {
    if (!platform.isAvailable) {
      return <Badge variant="secondary" className="bg-gray-100 text-gray-600">Coming Soon</Badge>;
    }
    if (platform.isActive) {
      return <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>;
    }
    return <Badge variant="outline" className="text-gray-600 border-gray-300">Inactive</Badge>;
  };

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Platforms</h1>
          <p className="text-gray-600">Configure which platforms to track for leads and set up automation settings</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" />
            {error}
          </div>
        )}

        {/* Platform Cards */}
        {loading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded"></div>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-20"></div>
                      <div className="h-3 bg-gray-200 rounded w-32"></div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {platforms.map((platform) => (
            <Card key={platform.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getPlatformIcon(platform.icon, platform.isActive, platform.isAvailable)}
                    <div>
                      <CardTitle className="text-lg">{platform.name}</CardTitle>
                      <p className="text-sm text-gray-500 mt-1">{platform.description}</p>
                    </div>
                  </div>
                  {getPlatformStatus(platform)}
                </div>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Platform Activation */}
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-sm font-medium">Track Leads</Label>
                    <p className="text-xs text-gray-500">Enable lead tracking for this platform</p>
                  </div>
                  <Switch
                    checked={platform.isActive}
                    onCheckedChange={(checked) => updatePlatformSetting(platform.id, 'isActive', checked)}
                    disabled={!platform.isAvailable}
                  />
                </div>

                {platform.isActive && platform.isAvailable && (
                  <>
                    <Separator />

                    {/* Auto Reply Setting */}
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-sm font-medium">Auto Reply</Label>
                          <p className="text-xs text-gray-500">Automatically post replies to high-confidence leads</p>
                        </div>
                        <Switch
                          checked={platform.autoReply}
                          onCheckedChange={(checked) => updatePlatformSetting(platform.id, 'autoReply', checked)}
                        />
                      </div>

                      {/* Confidence Threshold */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm font-medium">Confidence Threshold</Label>
                          <span className="text-sm font-semibold text-gray-900">{platform.confidenceThreshold}%</span>
                        </div>
                        <Slider
                          value={[platform.confidenceThreshold]}
                          onValueChange={(value) => updatePlatformSetting(platform.id, 'confidenceThreshold', value[0])}
                          max={100}
                          min={50}
                          step={5}
                          className="w-full"
                        />
                        <p className="text-xs text-gray-500">
                          {platform.autoReply 
                            ? `Auto-reply when AI confidence is ${platform.confidenceThreshold}% or higher`
                            : `Set minimum confidence for auto-reply (currently disabled)`
                          }
                        </p>
                      </div>
                    </div>

                    <Separator />

                    {/* Write Reply Suggestion */}
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-sm font-medium">Write Reply Suggestion</Label>
                        <p className="text-xs text-gray-500">Generate reply drafts automatically (not posted)</p>
                      </div>
                      <Switch
                        checked={platform.writeReplySuggestion}
                        onCheckedChange={(checked) => updatePlatformSetting(platform.id, 'writeReplySuggestion', checked)}
                      />
                    </div>

                    <Separator />

                    {/* Settings Summary */}
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                      <h4 className="text-sm font-medium text-gray-900 flex items-center">
                        <Settings className="w-4 h-4 mr-2" />
                        Current Settings
                      </h4>
                      <div className="space-y-1 text-xs text-gray-600">
                        <div className="flex items-center">
                          {platform.autoReply ? (
                            <CheckCircle className="w-3 h-3 text-green-600 mr-2" />
                          ) : (
                            <Clock className="w-3 h-3 text-gray-400 mr-2" />
                          )}
                          Auto-reply: {platform.autoReply ? `Enabled (${platform.confidenceThreshold}%+)` : 'Disabled'}
                        </div>
                        <div className="flex items-center">
                          {platform.writeReplySuggestion ? (
                            <CheckCircle className="w-3 h-3 text-green-600 mr-2" />
                          ) : (
                            <Clock className="w-3 h-3 text-gray-400 mr-2" />
                          )}
                          Reply suggestions: {platform.writeReplySuggestion ? 'Enabled' : 'Disabled'}
                        </div>
                      </div>
                    </div>

                    {/* Save Button */}
                    <Button 
                      onClick={() => savePlatformSettings(platform.id)}
                      disabled={loading}
                      className="w-full"
                    >
                      {loading ? 'Saving...' : 'Save Settings'}
                    </Button>
                  </>
                )}

                {!platform.isAvailable && (
                  <div className="text-center py-6">
                    <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Coming soon! We're working on {platform.name} integration.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
        )}

        {/* Info Section */}
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-start space-x-3">
              <Settings className="w-5 h-5 text-gray-600 mt-0.5" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Platform Configuration</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Lead Tracking</h4>
                    <p className="text-gray-600 text-xs leading-relaxed">
                      Enable or disable lead discovery for each platform. When enabled, the system will monitor for relevant posts and comments.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Auto Reply</h4>
                    <p className="text-gray-600 text-xs leading-relaxed">
                      Automatically post generated replies when the confidence score meets your threshold. Requires active lead tracking.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Confidence Threshold</h4>
                    <p className="text-gray-600 text-xs leading-relaxed">
                      Set the minimum confidence score (50-100%) required before auto-posting replies. Higher values mean more selective posting.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Reply Suggestions</h4>
                    <p className="text-gray-600 text-xs leading-relaxed">
                      Generate reply drafts for manual review and posting. Useful for maintaining control while getting assistance.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  );
}