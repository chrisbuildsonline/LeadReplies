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
import { AlertCircle, Plus, Trash2, Eye, EyeOff, CheckCircle, XCircle, Clock, Users, Shield, Settings, Upload, FileText, Download } from "lucide-react";
import { SiReddit, SiX, SiLinkedin } from "react-icons/si";

const API_URL = 'http://localhost:6070';

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
  const [showCsvUpload, setShowCsvUpload] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvUploading, setCsvUploading] = useState(false);
  const [csvResults, setCsvResults] = useState<any>(null);
  
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
      return <Badge variant="secondary" className="bg-gray-100 text-gray-600 border-gray-200">Inactive</Badge>;
    }
    if (account.is_verified) {
      return <Badge className="bg-gray-100 text-gray-700 border-gray-200">Verified</Badge>;
    }
    return <Badge className="bg-gray-100 text-gray-600 border-gray-200">Pending</Badge>;
  };

  const togglePasswordVisibility = (accountId: number) => {
    setShowPasswords(prev => ({
      ...prev,
      [accountId]: !prev[accountId]
    }));
  };

  const handleCsvUpload = async () => {
    if (!csvFile) {
      setError('Please select a CSV file');
      return;
    }

    setCsvUploading(true);
    setError('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const fileContent = await csvFile.text();
      
      const response = await fetch(`${API_URL}/api/accounts/upload-csv`, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'text/plain',
        },
        body: fileContent,
      });

      if (!response.ok) {
        if (response.status === 401) {
          setLocation('/login');
        }
        throw new Error('Failed to upload CSV');
      }

      const results = await response.json();
      setCsvResults(results);
      
      // Refresh accounts list
      await fetchAccounts();
      
      // Reset form
      setCsvFile(null);
      
    } catch (err) {
      setError('Failed to upload CSV. Please try again.');
      console.error('CSV upload error:', err);
    } finally {
      setCsvUploading(false);
    }
  };

  const downloadCsvTemplate = () => {
    const csvContent = 'platform,username,password,notes\nreddit,example_user,example_password,Optional notes\n';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'accounts_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <PageLayout>
      <div className="flex gap-8">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Social Accounts</h1>
              <p className="text-gray-600">Manage your social media accounts for automated posting</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button 
                variant="outline"
                onClick={() => setShowCsvUpload(true)}
                className="border-gray-300 hover:bg-gray-50"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload CSV
              </Button>
              
              <Button 
                onClick={() => setShowAddForm(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Account
              </Button>
            </div>
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
                    <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
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
                      className="bg-purple-600 hover:bg-blue-700 px-6"
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

        {/* CSV Upload Form */}
        {showCsvUpload && (
          <div className="max-w-2xl mx-auto">
            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 shadow-lg">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                      <Upload className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-xl font-semibold text-green-900">Upload Accounts CSV</CardTitle>
                      <p className="text-sm text-green-700 mt-1">Bulk import multiple accounts from a CSV file</p>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* CSV Format Info */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    CSV Format Requirements
                  </h4>
                  <div className="text-sm text-blue-800 space-y-1">
                    <p><strong>Required columns:</strong> platform, username, password</p>
                    <p><strong>Optional columns:</strong> notes</p>
                    <p><strong>Supported platforms:</strong> reddit, twitter, linkedin</p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={downloadCsvTemplate}
                    className="mt-3 text-blue-700 border-blue-300 hover:bg-blue-100"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Template
                  </Button>
                </div>

                {/* File Upload */}
                <div className="space-y-3">
                  <Label htmlFor="csvFile" className="text-sm font-medium text-gray-700">
                    Select CSV File
                  </Label>
                  <div className="flex items-center space-x-3">
                    <input
                      id="csvFile"
                      type="file"
                      accept=".csv"
                      onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                      className="flex-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                    />
                  </div>
                  {csvFile && (
                    <p className="text-sm text-gray-600">
                      Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>

                {/* Upload Results */}
                {csvResults && (
                  <div className="space-y-3">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h4 className="font-medium text-green-900 mb-2">Upload Results</h4>
                      <div className="text-sm text-green-800 space-y-1">
                        <p><strong>Successfully added:</strong> {csvResults.added_accounts?.length || 0} accounts</p>
                        <p><strong>Errors:</strong> {csvResults.errors?.length || 0}</p>
                        <p><strong>Total processed:</strong> {csvResults.total_processed || 0} rows</p>
                      </div>
                    </div>
                    
                    {csvResults.errors && csvResults.errors.length > 0 && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <h4 className="font-medium text-red-900 mb-2">Errors</h4>
                        <div className="text-sm text-red-800 space-y-1 max-h-32 overflow-y-auto">
                          {csvResults.errors.map((error: string, index: number) => (
                            <p key={index}>• {error}</p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-4 border-t border-green-200">
                  <div className="flex items-center space-x-2 text-sm text-green-700">
                    <AlertCircle className="w-4 h-4" />
                    <span>Passwords will be encrypted securely</span>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <Button 
                      variant="outline"
                      onClick={() => {
                        setShowCsvUpload(false);
                        setCsvFile(null);
                        setCsvResults(null);
                        setError('');
                      }}
                      className="px-6"
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={handleCsvUpload}
                      disabled={csvUploading || !csvFile}
                      className="bg-green-600 hover:bg-green-700 px-6"
                    >
                      {csvUploading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Uploading...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Upload className="w-4 h-4" />
                          <span>Upload CSV</span>
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {accounts.map((account) => (
              <Card key={account.id} className="hover:shadow-md transition-all duration-200 border-gray-200 hover:border-gray-300">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
                        {getPlatformIcon(account.platform)}
                      </div>
                      <div>
                        <CardTitle className="text-base capitalize font-semibold">{account.platform}</CardTitle>
                        <p className="text-xs text-gray-500 font-medium">@{account.username}</p>
                      </div>
                    </div>
                    {getStatusBadge(account)}
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {/* Account Status Toggle */}
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div>
                      <Label className="text-xs font-medium text-gray-700">Active</Label>
                      <p className="text-xs text-gray-500">Enable automation</p>
                    </div>
                    <Switch
                      checked={account.is_active}
                      onCheckedChange={(checked) => toggleAccountStatus(account.id, checked)}
                    />
                  </div>

                  {/* Account Details */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <Label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Password</Label>
                        <p className="text-xs font-mono text-gray-900 mt-1">
                          {showPasswords[account.id] ? account.password || '••••••••' : '••••••••'}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => togglePasswordVisibility(account.id)}
                        className="p-1 h-6 w-6 hover:bg-gray-100"
                      >
                        {showPasswords[account.id] ? (
                          <EyeOff className="w-3 h-3 text-gray-500" />
                        ) : (
                          <Eye className="w-3 h-3 text-gray-500" />
                        )}
                      </Button>
                    </div>

                    {account.notes && (
                      <div>
                        <Label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Notes</Label>
                        <p className="text-xs text-gray-700 mt-1 bg-gray-50 p-2 rounded">{account.notes}</p>
                      </div>
                    )}

                    {account.last_used && (
                      <div>
                        <Label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Last Used</Label>
                        <p className="text-xs text-gray-700 mt-1">{new Date(account.last_used).toLocaleDateString()}</p>
                      </div>
                    )}
                  </div>

                  {/* Account Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <div className="flex items-center space-x-2">
                      {account.is_verified ? (
                        <div className="flex items-center text-gray-700 bg-gray-100 px-2 py-1 rounded-full">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          <span className="text-xs font-medium">Verified</span>
                        </div>
                      ) : (
                        <div className="flex items-center text-gray-600 bg-gray-50 px-2 py-1 rounded-full">
                          <Clock className="w-3 h-3 mr-1" />
                          <span className="text-xs font-medium">Pending</span>
                        </div>
                      )}
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteAccount(account.id)}
                      className="text-red-600 hover:bg-red-50 hover:text-red-700 px-2 py-1 h-7"
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

        </div>

        {/* Sidebar */}
        <div className="w-80 space-y-6">
          {/* Account Overview */}
          {accounts.length > 0 && (
            <Card className="bg-white border-gray-200 sticky top-6">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Account Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="text-center p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="text-2xl font-bold text-gray-900">{accounts.length}</div>
                    <div className="text-xs text-gray-600 font-medium">Total</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="text-2xl font-bold text-gray-900">
                      {accounts.filter(acc => acc.is_active).length}
                    </div>
                    <div className="text-xs text-gray-600 font-medium">Active</div>
                  </div>
                </div>
                
                <div className="space-y-3 pt-2 border-t border-gray-100">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Verified</span>
                    <span className="font-medium text-gray-900">
                      {accounts.filter(acc => acc.is_verified).length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Pending</span>
                    <span className="font-medium text-gray-900">
                      {accounts.filter(acc => !acc.is_verified).length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Reddit</span>
                    <span className="font-medium text-gray-900">
                      {accounts.filter(acc => acc.platform === 'reddit').length}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Security Information */}
          <Card className="bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900 flex items-center">
                <Shield className="w-5 h-5 mr-2 text-gray-600" />
                Security & Privacy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4 text-sm">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Data Protection</h4>
                  <p className="text-gray-600 text-xs leading-relaxed">
                    All account credentials are encrypted using industry-standard AES-256 encryption before storage.
                  </p>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Account Verification</h4>
                  <p className="text-gray-600 text-xs leading-relaxed">
                    Accounts are automatically verified to ensure they work correctly before being used for automation.
                  </p>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Access Control</h4>
                  <p className="text-gray-600 text-xs leading-relaxed">
                    Only active accounts participate in automated activities. You can disable accounts at any time.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Usage Guidelines */}
          <Card className="bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900 flex items-center">
                <Settings className="w-5 h-5 mr-2 text-gray-600" />
                Best Practices
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-xs text-gray-600">Use dedicated accounts for automation</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-xs text-gray-600">Keep credentials up to date</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-xs text-gray-600">Monitor account activity regularly</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-xs text-gray-600">Disable unused accounts</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageLayout>
  );
}