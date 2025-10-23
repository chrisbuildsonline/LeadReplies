import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from 'wouter';
import PageLayout from "@/components/layout/page-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { 
  Bell, 
  BellOff, 
  Check, 
  CheckCheck, 
  Trash2, 
  AlertCircle, 
  TrendingUp, 
  MessageSquare, 
  Lightbulb,
  Settings,
  Mail,
  Smartphone
} from "lucide-react";
import { SiReddit } from "react-icons/si";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:6070';

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  data?: any;
  is_read: boolean;
  priority: string;
  created_at: string;
  read_at?: string;
}

interface NotificationPreference {
  notification_type: string;
  email_enabled: boolean;
  push_enabled: boolean;
}

interface NotificationsData {
  notifications: Notification[];
  unread_count: number;
  total_count: number;
}

export default function Notifications() {
  const [, setLocation] = useLocation();
  const [showSettings, setShowSettings] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
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
    data: notificationsData,
    isLoading,
    error,
  } = useQuery<NotificationsData>({
    queryKey: ["/api/notifications", filter],
    queryFn: async () => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/notifications?unread_only=${filter === 'unread'}`, {
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          setLocation("/login");
        }
        throw new Error("Failed to fetch notifications");
      }

      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const {
    data: preferences,
  } = useQuery<{preferences: NotificationPreference[]}>({
    queryKey: ["/api/notifications/preferences"],
    queryFn: async () => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/notifications/preferences`, {
        headers,
      });

      if (!response.ok) throw new Error("Failed to fetch preferences");
      return response.json();
    },
  });

  const markReadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers,
      });

      if (!response.ok) throw new Error("Failed to mark as read");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/notifications"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: async () => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/notifications/mark-all-read`, {
        method: 'PUT',
        headers,
      });

      if (!response.ok) throw new Error("Failed to mark all as read");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/notifications"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) throw new Error("Failed to delete notification");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/notifications"] });
    },
  });

  const updatePreferenceMutation = useMutation({
    mutationFn: async ({ type, email_enabled, push_enabled }: { type: string, email_enabled?: boolean, push_enabled?: boolean }) => {
      const headers = getAuthHeaders();
      if (!headers) throw new Error("No auth token");

      const response = await fetch(`${API_URL}/api/notifications/preferences`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({
          notification_type: type,
          email_enabled,
          push_enabled,
        }),
      });

      if (!response.ok) throw new Error("Failed to update preferences");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/notifications/preferences"] });
    },
  });

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'new_lead':
        return <TrendingUp className="w-5 h-5 text-blue-600" />;
      case 'reply_posted':
        return <MessageSquare className="w-5 h-5 text-green-600" />;
      case 'ai_suggestion_ready':
        return <Lightbulb className="w-5 h-5 text-yellow-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
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

  const getPreferenceForType = (type: string) => {
    return preferences?.preferences?.find(p => p.notification_type === type) || {
      notification_type: type,
      email_enabled: true,
      push_enabled: true,
    };
  };

  const notificationTypes = [
    { type: 'new_lead', label: 'New Lead Found', description: 'When a new lead is discovered and processed' },
    { type: 'reply_posted', label: 'Reply Posted', description: 'When an automated reply is successfully posted' },
    { type: 'ai_suggestion_ready', label: 'AI Suggestion Ready', description: 'When AI generates a reply suggestion for review' },
  ];

  if (error) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Notifications</h1>
            <p className="text-gray-600">Failed to load notifications. Please try again.</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="flex gap-8">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Notifications</h1>
              <p className="text-gray-600">Stay updated with your lead generation activity</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowSettings(!showSettings)}
                className="flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Button>
              
              {notificationsData?.unread_count > 0 && (
                <Button
                  onClick={() => markAllReadMutation.mutate()}
                  disabled={markAllReadMutation.isPending}
                  className="bg-purple-600 hover:bg-blue-700"
                >
                  <CheckCheck className="w-4 h-4 mr-2" />
                  Mark All Read
                </Button>
              )}
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              All ({notificationsData?.total_count || 0})
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === 'unread'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Unread ({notificationsData?.unread_count || 0})
            </button>
          </div>

          {/* Notifications List */}
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
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : notificationsData?.notifications?.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <BellOff className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
                </h3>
                <p className="text-gray-600">
                  {filter === 'unread' 
                    ? 'All caught up! Check back later for new updates.'
                    : 'Notifications will appear here when there\'s activity on your account.'
                  }
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {notificationsData?.notifications?.map((notification) => (
                <Card 
                  key={notification.id} 
                  className={`transition-all duration-200 hover:shadow-md ${
                    !notification.is_read ? 'border-l-4 border-l-blue-500 bg-blue-50/30' : ''
                  }`}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="flex-shrink-0">
                          {getNotificationIcon(notification.type)}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-base font-semibold text-gray-900">
                              {notification.title}
                            </h3>
                            {!notification.is_read && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            )}
                            <Badge className={getPriorityColor(notification.priority)}>
                              {notification.priority}
                            </Badge>
                          </div>
                          
                          <p className="text-gray-700 mb-3">{notification.message}</p>
                          
                          {notification.data && (
                            <div className="bg-gray-50 rounded-lg p-3 mb-3">
                              <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                                {JSON.stringify(notification.data, null, 2)}
                              </pre>
                            </div>
                          )}
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>{formatTimeAgo(notification.created_at)}</span>
                            {notification.is_read && notification.read_at && (
                              <span>Read {formatTimeAgo(notification.read_at)}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 ml-4">
                        {!notification.is_read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => markReadMutation.mutate(notification.id)}
                            disabled={markReadMutation.isPending}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                          >
                            <Check className="w-4 h-4" />
                          </Button>
                        )}
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteMutation.mutate(notification.id)}
                          disabled={deleteMutation.isPending}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Settings Sidebar */}
        {showSettings && (
          <div className="w-80 space-y-6">
            <Card className="bg-white border-gray-200 sticky top-6">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  Notification Settings
                </CardTitle>
                <p className="text-sm text-gray-600">Configure how you receive notifications</p>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {notificationTypes.map((notificationType) => {
                  const pref = getPreferenceForType(notificationType.type);
                  
                  return (
                    <div key={notificationType.type} className="space-y-3">
                      <div>
                        <h4 className="font-medium text-gray-900">{notificationType.label}</h4>
                        <p className="text-sm text-gray-600">{notificationType.description}</p>
                      </div>
                      
                      <div className="space-y-3 pl-4 border-l-2 border-gray-100">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Mail className="w-4 h-4 text-gray-500" />
                            <Label className="text-sm font-medium">Email</Label>
                          </div>
                          <Switch
                            checked={pref.email_enabled}
                            onCheckedChange={(checked) => 
                              updatePreferenceMutation.mutate({
                                type: notificationType.type,
                                email_enabled: checked,
                              })
                            }
                          />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Smartphone className="w-4 h-4 text-gray-500" />
                            <Label className="text-sm font-medium">Push</Label>
                          </div>
                          <Switch
                            checked={pref.push_enabled}
                            onCheckedChange={(checked) => 
                              updatePreferenceMutation.mutate({
                                type: notificationType.type,
                                push_enabled: checked,
                              })
                            }
                          />
                        </div>
                      </div>
                      
                      {notificationType !== notificationTypes[notificationTypes.length - 1] && (
                        <Separator />
                      )}
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </PageLayout>
  );
}