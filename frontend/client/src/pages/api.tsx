import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Code, 
  Copy, 
  ExternalLink, 
  Server, 
  Key, 
  Database,
  ArrowRight,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { Link } from "wouter";

// API endpoint data based on the backend
const apiEndpoints = [
  {
    method: "GET",
    path: "/",
    description: "API root endpoint with version info",
    category: "General",
    auth: false,
    response: {
      message: "Lead Finder API v2",
      status: "running",
      version: "2.1.0-uuid-fix",
      timestamp: "2024-10-23T12:00:00.000Z"
    }
  },
  {
    method: "GET",
    path: "/health",
    description: "Health check endpoint for monitoring",
    category: "General",
    auth: false,
    response: {
      status: "healthy",
      service: "Lead Finder API v2",
      timestamp: "2024-10-23T12:00:00.000Z",
      database: "connected"
    }
  },
  {
    method: "POST",
    path: "/api/auth/login",
    description: "Authenticate user and get JWT token",
    category: "Authentication",
    auth: false,
    requestBody: {
      email: "user@example.com",
      password: "password123"
    },
    response: {
      token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      user: {
        id: 1,
        email: "user@example.com"
      }
    }
  },
  {
    method: "GET",
    path: "/api/auth/me",
    description: "Get current authenticated user info",
    category: "Authentication",
    auth: true,
    response: {
      user: {
        id: 1,
        email: "user@example.com",
        created_at: "2024-10-23T12:00:00.000Z"
      }
    }
  },
  {
    method: "GET",
    path: "/api/businesses",
    description: "Get all businesses for authenticated user",
    category: "Businesses",
    auth: true,
    response: {
      businesses: [
        {
          id: "uuid-string",
          name: "My Business",
          website: "https://example.com",
          description: "Business description",
          created_at: "2024-10-23T12:00:00.000Z"
        }
      ]
    }
  },
  {
    method: "POST",
    path: "/api/businesses",
    description: "Create a new business",
    category: "Businesses",
    auth: true,
    requestBody: {
      name: "My New Business",
      website: "https://example.com",
      description: "Business description"
    },
    response: {
      business_id: "uuid-string",
      id: "uuid-string"
    }
  },
  {
    method: "GET",
    path: "/api/businesses/{business_id}",
    description: "Get specific business details",
    category: "Businesses",
    auth: true,
    response: {
      business: {
        id: "uuid-string",
        name: "My Business",
        website: "https://example.com",
        description: "Business description"
      }
    }
  },
  {
    method: "GET",
    path: "/api/businesses/{business_id}/keywords",
    description: "Get keywords for a business",
    category: "Keywords",
    auth: true,
    response: {
      keywords: [
        {
          id: 1,
          keyword: "project management",
          source: "manual",
          created_at: "2024-10-23T12:00:00.000Z"
        }
      ]
    }
  },
  {
    method: "POST",
    path: "/api/businesses/{business_id}/keywords",
    description: "Add keyword to business",
    category: "Keywords",
    auth: true,
    requestBody: {
      keyword: "project management",
      source: "manual"
    },
    response: {
      success: true
    }
  },
  {
    method: "GET",
    path: "/api/businesses/{business_id}/leads",
    description: "Get leads for a business",
    category: "Leads",
    auth: true,
    parameters: {
      limit: "50 (optional)"
    },
    response: {
      leads: [
        {
          id: 1,
          title: "Looking for project management tool",
          platform: "reddit",
          ai_score: 85,
          processed_at: "2024-10-23T12:00:00.000Z"
        }
      ],
      total: 1
    }
  },
  {
    method: "GET",
    path: "/api/dashboard",
    description: "Get dashboard metrics and stats",
    category: "Dashboard",
    auth: true,
    response: {
      metrics: {
        totalLeads: 150,
        leadsToday: 12,
        leadsThisWeek: 45,
        highQualityLeads: 38
      },
      platformStats: [
        {
          platform: "reddit",
          leads: 120,
          businesses: 3
        }
      ],
      recentActivity: [],
      businessStats: []
    }
  }
];

const categories = ["All", "General", "Authentication", "Businesses", "Keywords", "Leads", "Dashboard"];

const methodColors = {
  GET: "bg-green-100 text-green-800 border-green-200",
  POST: "bg-blue-100 text-blue-800 border-blue-200",
  PUT: "bg-yellow-100 text-yellow-800 border-yellow-200",
  DELETE: "bg-red-100 text-red-800 border-red-200"
};

export default function ApiPage() {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const filteredEndpoints = selectedCategory === "All" 
    ? apiEndpoints 
    : apiEndpoints.filter(endpoint => endpoint.category === selectedCategory);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const generateCurlExample = (endpoint: any) => {
    let curl = `curl -X ${endpoint.method} \\
  "${window.location.origin}${endpoint.path}"`;
    
    if (endpoint.auth) {
      curl += ` \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "X-API-Key: YOUR_API_KEY"`;
    }
    
    if (endpoint.requestBody) {
      curl += ` \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(endpoint.requestBody, null, 2)}'`;
    }
    
    return curl;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">LR</span>
                  </div>
                  <span className="text-xl font-bold text-gray-900">LeadReplier</span>
                </div>
              </Link>
              <ArrowRight className="w-4 h-4 text-gray-400" />
              <h1 className="text-xl font-semibold text-gray-900">API Documentation</h1>
            </div>
            <Link href="/dashboard">
              <Button className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700">
                Go to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-2xl mb-6">
            <Server className="w-8 h-8" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            LeadReplier API Documentation
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Integrate with our powerful lead generation API. Access all the features of LeadReplier 
            programmatically to build custom workflows and integrations.
          </p>
        </div>

        {/* Quick Start Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="border-2 border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center text-blue-900">
                <Key className="w-5 h-5 mr-2" />
                Authentication
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-blue-800 text-sm mb-4">
                All API requests require both JWT authentication and an API key.
              </p>
              <div className="space-y-2">
                <code className="text-xs bg-blue-100 p-2 rounded block">
                  Authorization: Bearer YOUR_JWT_TOKEN
                </code>
                <code className="text-xs bg-blue-100 p-2 rounded block">
                  X-API-Key: YOUR_API_KEY
                </code>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="flex items-center text-green-900">
                <Database className="w-5 h-5 mr-2" />
                Base URL
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-green-800 text-sm mb-4">
                All API endpoints are relative to the base URL:
              </p>
              <code className="text-xs bg-green-100 p-2 rounded block break-all">
                {window.location.origin}
              </code>
            </CardContent>
          </Card>

          <Card className="border-2 border-purple-200 bg-purple-50">
            <CardHeader>
              <CardTitle className="flex items-center text-purple-900">
                <Code className="w-5 h-5 mr-2" />
                Response Format
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-purple-800 text-sm mb-4">
                All responses are in JSON format with consistent structure.
              </p>
              <code className="text-xs bg-purple-100 p-2 rounded block">
                Content-Type: application/json
              </code>
            </CardContent>
          </Card>
        </div>

        {/* API Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">API Endpoints</CardTitle>
            <div className="flex flex-wrap gap-2 mt-4">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                  className={selectedCategory === category ? "bg-orange-600 hover:bg-orange-700" : ""}
                >
                  {category}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {filteredEndpoints.map((endpoint, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <Badge className={`${methodColors[endpoint.method as keyof typeof methodColors]} font-mono`}>
                        {endpoint.method}
                      </Badge>
                      <code className="text-lg font-mono text-gray-900">{endpoint.path}</code>
                      {endpoint.auth && (
                        <Badge variant="outline" className="text-xs">
                          <Key className="w-3 h-3 mr-1" />
                          Auth Required
                        </Badge>
                      )}
                    </div>
                    <Badge variant="secondary">{endpoint.category}</Badge>
                  </div>
                  
                  <p className="text-gray-600 mb-6">{endpoint.description}</p>

                  <Tabs defaultValue="response" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="response">Response</TabsTrigger>
                      <TabsTrigger value="curl">cURL Example</TabsTrigger>
                      {endpoint.requestBody && <TabsTrigger value="request">Request Body</TabsTrigger>}
                    </TabsList>
                    
                    <TabsContent value="response" className="mt-4">
                      <div className="relative">
                        <Button
                          size="sm"
                          variant="outline"
                          className="absolute top-2 right-2 z-10"
                          onClick={() => copyToClipboard(JSON.stringify(endpoint.response, null, 2), `response-${index}`)}
                        >
                          {copiedCode === `response-${index}` ? (
                            <CheckCircle className="w-4 h-4" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </Button>
                        <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                          <code>{JSON.stringify(endpoint.response, null, 2)}</code>
                        </pre>
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="curl" className="mt-4">
                      <div className="relative">
                        <Button
                          size="sm"
                          variant="outline"
                          className="absolute top-2 right-2 z-10"
                          onClick={() => copyToClipboard(generateCurlExample(endpoint), `curl-${index}`)}
                        >
                          {copiedCode === `curl-${index}` ? (
                            <CheckCircle className="w-4 h-4" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </Button>
                        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                          <code>{generateCurlExample(endpoint)}</code>
                        </pre>
                      </div>
                    </TabsContent>
                    
                    {endpoint.requestBody && (
                      <TabsContent value="request" className="mt-4">
                        <div className="relative">
                          <Button
                            size="sm"
                            variant="outline"
                            className="absolute top-2 right-2 z-10"
                            onClick={() => copyToClipboard(JSON.stringify(endpoint.requestBody, null, 2), `request-${index}`)}
                          >
                            {copiedCode === `request-${index}` ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                          <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                            <code>{JSON.stringify(endpoint.requestBody, null, 2)}</code>
                          </pre>
                        </div>
                      </TabsContent>
                    )}
                  </Tabs>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Error Codes */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>HTTP Status Codes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Badge className="bg-green-100 text-green-800">200</Badge>
                  <span>OK - Request successful</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge className="bg-blue-100 text-blue-800">201</Badge>
                  <span>Created - Resource created successfully</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge className="bg-red-100 text-red-800">400</Badge>
                  <span>Bad Request - Invalid request data</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Badge className="bg-red-100 text-red-800">401</Badge>
                  <span>Unauthorized - Invalid or missing token</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge className="bg-red-100 text-red-800">404</Badge>
                  <span>Not Found - Resource not found</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge className="bg-red-100 text-red-800">500</Badge>
                  <span>Internal Server Error - Server error</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rate Limits */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              Rate Limits & Best Practices
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3">Rate Limits</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• 1000 requests per hour per API key</li>
                  <li>• 100 requests per minute per endpoint</li>
                  <li>• Rate limit headers included in responses</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Best Practices</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Cache responses when possible</li>
                  <li>• Use pagination for large datasets</li>
                  <li>• Handle rate limit responses gracefully</li>
                  <li>• Keep JWT tokens secure</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CTA Section */}
        <div className="text-center mt-12 p-8 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl border border-orange-200">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to integrate with LeadReplier?
          </h3>
          <p className="text-gray-600 mb-6">
            Get started with our API today and automate your lead generation workflow.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/api/pricing">
              <Button className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700">
                Get API Access
              </Button>
            </Link>
            <Button variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50">
              <ExternalLink className="w-4 h-4 mr-2" />
              View Examples
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}