import { useState, useEffect } from "react";
import { useLocation } from 'wouter';
import PageLayout from "@/components/layout/page-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, Plus, Trash2, Eye, EyeOff, CheckCircle, XCircle, Clock, Users } from "lucide-react";
import { SiReddit, SiX, SiLinkedin } from "react-icons/si";

const API_URL = 'http://localhost:8001';

interface SocialAccount {
  id: number;
  platform: string;
  username: string;
  password?: string;
  is_active: boolean;
  is_verified: boolean;
  last_used?: string;
  created_at: string;
  notes?: string;
}

export default function Accounts() {
  const [, setLocation] = useLocation();
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [showPasswords, setShowPasswords] = useState<Record<number, boolean>>({});
  
  // New account form
  const [newAccount, setNewAccount] = useState({
    platform: 'reddit',
    username: '',
    password: '',
    notes: ''
  });

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

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoading(true);
    setError('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${API_URL}/api/accounts`, {
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          setLocation('/login');
        }
        throw new Error('Failed to fetch accounts');
      }

      const data = await response.json();
      setAccounts(data.accounts || []);
      
    } catch (err) {
      setError('Failed to load accounts. Please try again.');
      console.error('Fetch accounts error:', err);
    } finally {
      setLoading(false);
    }
  };

  const addAccount = async () => {
    if (!newAccount.username || !newAccount.password) {
      setError('Username and password are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${API_URL}/api/accounts`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newAccount),
      });

      if (!response.ok) {
        if (response.status === 401) {
          setLocation('/login');
        }
        throw new Error('Failed to add account');
      }

      const data = await response.json();
      
      // Refresh accounts list
      await fetchAccounts();
      
      // Reset form
      setNewAccount({
        platform: 'reddit',
        username: '',
        password: '',
        notes: ''
      });
      setShowAddForm(false);
      
    } catch (err) {
      setError('Failed to add account. Please try again.');
      console.error('Add account error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleAccountStatus = async (accountId: number, isActive: boolean) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${API_URL}/api/accounts/${accountId}/status`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ is_active: isActive }),
      });

      if (!response.ok) {
        throw new Error('Failed to update account status');
      }

      // Update local state
      setAccounts(prev => prev.map(account => 
        account.id === accountId 
          ? { ...account, is_active: isActive }
          : account
      ));
      
    } catch (err) {
      setError('Failed to update account status');
      console.error('Toggle account status error:', err);
    }
  };

  const deleteAccount = async (accountId: number) => {
    if (!confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${API_URL}/api/accounts/${accountId}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) {
        throw new Error('Failed to delete account');
      }

      // Remove from local state
      setAccounts(prev => prev.filter(account => account.id !== accountId));
      
    } catch (err) {
      setError('Failed to delete account');
      console.error('Delete account error:', err);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'reddit':
        return <SiReddit className="w-5 h-5 text-orange-600" />;
      case 'twitter':
      case 'x':
        return <SiX className="w-5 h-5 text-black" />;
      case 'linkedin':
        return <SiLinkedin className="w-5 h-5 text-blue-600" />;
      default:
        return <div className="w-5 h-5 bg-gray-400 rounded"></div>;
    }
  };

  const getStatusBadge = (account: SocialAccount) => {
    if (!account.is_active) {
      return <Badge variant="secondary" className="bg-gray-100 text-gray-600">Inactive</Badge>;
    }
    if (account.is_verified) {
      return <Badge className="bg-green-100 text-green-800 border-green-200">Verified</Badge>;
    }
    return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Pending</Badge>;
  };

  const togglePasswordVisibility = (accountId: number) => {
    setShowPasswords(prev => ({
      ...prev,
      [accountId]: !prev[accountId]
    }));
  };

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Social Accounts</h1>
            <p className="text-gray-600">Manage your social media accounts for automated posting</p>
          </div>
          
          <Button 
            onClick={() => setShowAddForm(true)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Account
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" />
            {error}
          </div>
        )}

        {/* Add Account Form */}
        {showAddForm && (
          <div className="max-w-2xl mx-auto">
            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-lg">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                      <Plus className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-xl font-semibold text-blue-900">Add New Account</CardTitle>
                      <p className="text-sm text-blue-700 mt-1">Connect your social media account for automation</p>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Platform</Label>
                    <div className="relative">
                      <select
                        value={newAccount.platform}
                        onChange={(e) => setNewAccount({...newAccount, platform: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
                      >
                        <option value="reddit">🔴 Reddit</option>
                        <option value="twitter" disabled>🐦 Twitter/X (Coming Soon)</option>
                        <option value="linkedin" disabled>💼 LinkedIn (Coming Soon)</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Username</Label>
                    <Input
                      value={newAccount.username}
                      onChange={(e) => setNewAccount({...newAccount, username: e.target.value})}
                      placeholder="your_username"
                      className="text-sm h-12 px-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-gray-700">Password</Label>
                  <Input
                    type="password"
                    value={newAccount.password}
                    onChange={(e) => setNewAccount({...newAccount, password: e.target.value})}
                    placeholder="Enter your password"
                    className="text-sm h-12 px-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-gray-700">Notes (Optional)</Label>
                  <Textarea
                    value={newAccount.notes}
                    onChange={(e) => setNewAccount({...newAccount, notes: e.target.value})}
                    placeholder="Add any notes about this account (e.g., 'Main business account', 'Personal account')..."
                    className="text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                  />
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-blue-200">
                  <div className="flex items-center space-x-2 text-sm text-blue-700">
                    <AlertCircle className="w-4 h-4" />
                    <span>Your credentials are encrypted and secure</span>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <Button 
                      variant="outline"
                      onClick={() => {
                        setShowAddForm(false);
                        setNewAccount({ platform: 'reddit', username: '', password: '', notes: '' });
                        setError('');
                      }}
                      className="px-6"
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={addAccount}
                      disabled={loading || !newAccount.username || !newAccount.password}
                      className="bg-blue-600 hover:bg-blue-700 px-6"
                    >
                      {loading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Adding...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Plus className="w-4 h-4" />
                          <span>Add Account</span>
                        </div>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Accounts List */}
        {loading && !showAddForm ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-5 h-5 bg-gray-200 rounded"></div>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-20"></div>
                      <div className="h-3 bg-gray-200 rounded w-16"></div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : accounts.length === 0 && !showAddForm ? (
          <div className="max-w-md mx-auto">
            <Card className="border-dashed border-2 border-gray-300 bg-gray-50/50">
              <CardContent className="p-12 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">No accounts connected</h3>
                <p className="text-gray-600 mb-8 leading-relaxed">
                  Connect your social media accounts to start automating replies and engaging with potential leads.
                </p>
                <Button 
                  onClick={() => setShowAddForm(true)}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-3 text-white font-medium"
                  size="lg"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Connect Your First Account
                </Button>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {accounts.map((account) => (
              <Card key={account.id} className="hover:shadow-lg transition-all duration-200 border-gray-200 hover:border-gray-300">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
                        {getPlatformIcon(account.platform)}
                      </div>
                      <div>
                        <CardTitle className="text-lg capitalize font-semibold">{account.platform}</CardTitle>
                        <p className="text-sm text-gray-500 font-medium">@{account.username}</p>
                      </div>
                    </div>
                    {getStatusBadge(account)}
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Account Status Toggle */}
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <Label className="text-sm font-medium text-gray-700">Active Status</Label>
                      <p className="text-xs text-gray-500">Enable for automation</p>
                    </div>
                    <Switch
                      checked={account.is_active}
                      onCheckedChange={(checked) => toggleAccountStatus(account.id, checked)}
                    />
                  </div>

                  {/* Account Details */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <Label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Password</Label>
                        <p className="text-sm font-mono text-gray-900 mt-1">
                          {showPasswords[account.id] ? account.password || '••••••••' : '••••••••'}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => togglePasswordVisibility(account.id)}
                        className="p-2 h-8 w-8 hover:bg-gray-100"
                      >
                        {showPasswords[account.id] ? (
                          <EyeOff className="w-4 h-4 text-gray-500" />
                        ) : (
                          <Eye className="w-4 h-4 text-gray-500" />
                        )}
                      </Button>
                    </div>

                    {account.notes && (
                      <div>
                        <Label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Notes</Label>
                        <p className="text-sm text-gray-700 mt-1 bg-gray-50 p-2 rounded text-xs">{account.notes}</p>
                      </div>
                    )}

                    {account.last_used && (
                      <div>
                        <Label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Last Used</Label>
                        <p className="text-sm text-gray-700 mt-1">{new Date(account.last_used).toLocaleDateString()}</p>
                      </div>
                    )}
                  </div>

                  {/* Account Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex items-center space-x-2">
                      {account.is_verified ? (
                        <div className="flex items-center text-green-600 bg-green-50 px-2 py-1 rounded-full">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          <span className="text-xs font-medium">Verified</span>
                        </div>
                      ) : (
                        <div className="flex items-center text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                          <Clock className="w-3 h-3 mr-1" />
                          <span className="text-xs font-medium">Pending</span>
                        </div>
                      )}
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteAccount(account.id)}
                      className="text-red-600 hover:bg-red-50 hover:text-red-700 px-3 py-1 h-8"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      <span className="text-xs">Delete</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Info Section */}
        {accounts.length > 0 && (
          <div className="max-w-4xl mx-auto">
            <Card className="bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-5 h-5 text-amber-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-amber-900 mb-3">Security & Usage Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-amber-800">
                      <div className="space-y-2">
                        <div className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 bg-amber-600 rounded-full mt-2 flex-shrink-0"></div>
                          <div>
                            <strong>Secure Storage:</strong> All passwords are encrypted using industry-standard encryption
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 bg-amber-600 rounded-full mt-2 flex-shrink-0"></div>
                          <div>
                            <strong>Account Verification:</strong> Accounts are verified before automation begins
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 bg-amber-600 rounded-full mt-2 flex-shrink-0"></div>
                          <div>
                            <strong>Active Control:</strong> Only active accounts participate in automated replies
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 bg-amber-600 rounded-full mt-2 flex-shrink-0"></div>
                          <div>
                            <strong>Platform Support:</strong> Reddit available now, Twitter & LinkedIn coming soon
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </PageLayout>
  );
}