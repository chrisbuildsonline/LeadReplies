import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  CheckCircle, 
  ArrowRight, 
  Code, 
  Zap, 
  Target, 
  TrendingUp,
  Key,
  Server,
  Database
} from "lucide-react";
import { Link } from "wouter";
import { motion } from "framer-motion";

const features = [
  {
    icon: Code,
    title: "Full API Access",
    description: "Complete programmatic access to all LeadReplier features"
  },
  {
    icon: Zap,
    title: "Real-time Data",
    description: "Get live lead data and analytics as they're processed"
  },
  {
    icon: Target,
    title: "Custom Integrations",
    description: "Build custom workflows and integrate with your existing tools"
  },
  {
    icon: TrendingUp,
    title: "Scalable Solutions",
    description: "Handle high-volume requests with enterprise-grade infrastructure"
  }
];

const apiFeatures = [
  "RESTful API with JSON responses",
  "JWT authentication + API key security",
  "Rate limiting and usage analytics",
  "Comprehensive documentation",
  "SDKs for popular languages",
  "Webhook support for real-time updates",
  "99.9% uptime SLA",
  "24/7 developer support"
];

export default function ApiPricingPage() {
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
              <h1 className="text-xl font-semibold text-gray-900">API Pricing</h1>
            </div>
            <div className="flex items-center space-x-3">
              <Link href="/api">
                <Button variant="outline">
                  View Documentation
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-2xl mb-6">
              <Server className="w-8 h-8" />
            </div>
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              LeadReplier API
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Integrate powerful lead generation directly into your applications. 
              Build custom workflows, automate processes, and scale your lead generation with our robust API.
            </p>
            <div className="flex justify-center space-x-4">
              <Link href="/dashboard">
                <Button size="lg" className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-lg px-8 py-6">
                  Start Free Trial <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link href="/api">
                <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                  View Documentation
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-xl mb-4">
                  <IconComponent className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Pricing Plans */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent API Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your keyword tracking needs
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Starter API Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <Card className="relative h-full border-2 hover:border-orange-200 transition-all duration-300">
                <CardHeader className="text-center pb-8">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl mb-4">
                    <Key className="w-6 h-6" />
                  </div>
                  <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                    API Starter
                  </CardTitle>
                  <p className="text-gray-600 mb-4">Perfect for small projects</p>
                  <div className="mb-4">
                    <span className="text-5xl font-bold text-gray-900">$9</span>
                    <span className="text-gray-600 ml-2">/month</span>
                  </div>
                  <p className="text-sm text-gray-500">Billed monthly</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-gray-700">3 Keywords tracked</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-gray-700">1,000 API calls/month</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-gray-700">Real-time lead data</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-gray-700">JSON API responses</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-gray-700">Basic documentation</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-gray-700">Email support</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                      Start API Trial
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>

            {/* Professional API Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card className="relative h-full border-2 border-orange-500 shadow-xl">
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-orange-500 to-red-600 text-white px-4 py-2 text-sm font-semibold">
                    Most Popular
                  </Badge>
                </div>
                <CardHeader className="text-center pb-8">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-xl mb-4">
                    <Database className="w-6 h-6" />
                  </div>
                  <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                    API Professional
                  </CardTitle>
                  <p className="text-gray-600 mb-4">For serious integrations</p>
                  <div className="mb-4">
                    <span className="text-5xl font-bold text-gray-900">$70</span>
                    <span className="text-gray-600 ml-2">/month</span>
                  </div>
                  <p className="text-sm text-gray-500">Billed monthly</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">100+ Keywords tracked</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">50,000 API calls/month</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">Real-time webhooks</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">Advanced analytics API</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">Priority support</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">Custom rate limits</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">99.9% uptime SLA</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700">
                      Start Professional Trial
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-500 mb-4">
              Need more keywords or higher limits? Contact us for enterprise pricing.
            </p>
            <Button variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50">
              Contact Sales
            </Button>
          </div>
        </div>

        {/* API Features */}
        <Card className="mb-16">
          <CardHeader>
            <CardTitle className="text-2xl text-center">What's Included in Every API Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {apiFeatures.map((feature, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span className="text-gray-700">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Use Cases */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Perfect for Developers & Businesses
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 text-blue-600 rounded-xl mb-4">
                <Code className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-3">SaaS Integrations</h3>
              <p className="text-gray-600 text-sm">
                Integrate lead generation directly into your SaaS platform for your customers
              </p>
            </Card>
            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 text-green-600 rounded-xl mb-4">
                <TrendingUp className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Marketing Automation</h3>
              <p className="text-gray-600 text-sm">
                Build custom workflows that automatically respond to new leads
              </p>
            </Card>
            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 text-purple-600 rounded-xl mb-4">
                <Target className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Custom Dashboards</h3>
              <p className="text-gray-600 text-sm">
                Create personalized analytics and reporting for your team
              </p>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center p-8 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl border border-orange-200">
          <h3 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Build with LeadReplier API?
          </h3>
          <p className="text-gray-600 mb-6 text-lg">
            Start your free trial today and see how easy it is to integrate powerful lead generation into your applications.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/dashboard">
              <Button size="lg" className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-lg px-8 py-6">
                Start Free Trial <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="/api">
              <Button size="lg" variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50 text-lg px-8 py-6">
                View Documentation
              </Button>
            </Link>
          </div>
          <p className="text-sm text-gray-500 mt-4">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </div>
    </div>
  );
}