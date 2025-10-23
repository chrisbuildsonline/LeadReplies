import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  ArrowRight,
  CheckCircle,
  Zap,
  Target,
  TrendingUp,
  Clock,
  Bot,
  User,
} from "lucide-react";
import { SiReddit, SiX, SiLinkedin } from "react-icons/si";
import { Link } from "wouter";
import { motion } from "framer-motion";
import { DotPattern } from "@/components/ui/dot-pattern";
import { cn } from "@/lib/utils";
// Logo placeholder - using div instead of image
import { useState, useEffect } from "react";

const platformFeatures = [
  {
    name: "Reddit",
    icon: SiReddit,
    color: "text-orange-500",
    bgColor: "bg-orange-50",
    borderColor: "border-orange-200",
    status: "active",
    description:
      "Find and engage with relevant discussions in targeted subreddits",
    metrics: "10K+ opportunities/day",
  },
  {
    name: "Twitter/X",
    icon: SiX,
    color: "text-gray-400",
    bgColor: "bg-gray-50",
    borderColor: "border-gray-200",
    status: "coming-soon",
    description:
      "Engage with trending conversations and reply to relevant tweets",
    metrics: "Coming Q1 2025",
  },
  {
    name: "Hacker News",
    icon: () => (
      <div className="w-6 h-6 bg-orange-600 text-white text-xs font-bold flex items-center justify-center rounded">
        Y
      </div>
    ),
    color: "text-gray-400",
    bgColor: "bg-gray-50",
    borderColor: "border-gray-200",
    status: "coming-soon",
    description: "Connect with tech-savvy audiences discussing your industry",
    metrics: "Coming Q2 2025",
  },
  {
    name: "LinkedIn",
    icon: SiLinkedin,
    color: "text-gray-400",
    bgColor: "bg-gray-50",
    borderColor: "border-gray-200",
    status: "coming-soon",
    description: "Professional outreach and B2B lead generation at scale",
    metrics: "Coming Q2 2025",
  },
];

const benefits = [
  {
    icon: Zap,
    title: "AI-Powered Responses",
    description:
      "Our AI crafts contextual, helpful replies that naturally promote your product",
  },
  {
    icon: Target,
    title: "Precision Targeting",
    description: "Find conversations where your product is genuinely relevant",
  },
  {
    icon: TrendingUp,
    title: "Proven Results",
    description: "Users see 300% increase in qualified leads within 30 days",
  },
  {
    icon: Clock,
    title: "24/7 Automation",
    description:
      "Never miss an opportunity while you sleep or focus on other tasks",
  },
];

// Reply combinations that rotate every 4 seconds
const replyScenarios = [
  {
    cards: [
      {
        subreddit: "r/startups",
        username: "u/startup_founder", 
        question: "Looking for a good project management tool...",
        aiUsername: "u/sarah_tech_lead",
        aiReply: "I've been using TaskFlow for similar needs...",
        upvotes: "+12 upvotes"
      },
      {
        subreddit: "r/ecommerce",
        question: "Any recommendations for e-commerce analytics?", 
        aiReply: "For analytics, I'd recommend ShopInsights...",
        upvotes: "+8 upvotes"
      },
      {
        subreddit: "r/smallbusiness", 
        question: "Best marketing automation tools?",
        aiReply: "LeadGen Pro has been a game-changer...",
        upvotes: "+15 upvotes"
      }
    ]
  },
  {
    cards: [
      {
        subreddit: "r/webdev",
        username: "u/junior_dev",
        question: "What hosting platform do you recommend for Node.js apps?",
        aiUsername: "u/senior_architect", 
        aiReply: "I've had great success with CloudDeploy for Node.js...",
        upvotes: "+24 upvotes"
      },
      {
        subreddit: "r/marketing",
        question: "How to track email campaign effectiveness?",
        aiReply: "MailMetrics gives you deep insights into...",
        upvotes: "+19 upvotes"
      },
      {
        subreddit: "r/freelancers",
        question: "Time tracking apps that actually work?", 
        aiReply: "TimeSync has transformed how I bill clients...",
        upvotes: "+31 upvotes"
      }
    ]
  },
  {
    cards: [
      {
        subreddit: "r/saas",
        username: "u/product_manager",
        question: "Customer feedback tools for early-stage startups?",
        aiUsername: "u/growth_hacker",
        aiReply: "FeedbackFlow is perfect for early-stage validation...", 
        upvotes: "+18 upvotes"
      },
      {
        subreddit: "r/design",
        question: "Design collaboration tools for remote teams?",
        aiReply: "DesignSync keeps our remote team aligned...",
        upvotes: "+22 upvotes"
      },
      {
        subreddit: "r/productivity", 
        question: "Note-taking app that syncs everywhere?",
        aiReply: "NotePad Pro syncs seamlessly across all devices...",
        upvotes: "+16 upvotes"
      }
    ]
  }
];

// Improved Floating Chat Hero with rotating reply cards
const ImprovedFloatingChatHero = () => {
  const [cardScenarios, setCardScenarios] = useState([0, 0, 0]); // Track scenario for each card individually
  const [activeCard, setActiveCard] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard((prevActiveCard) => {
        const newActiveCard = (prevActiveCard + 1) % 3;
        
        // Only update the content of the currently active card
        setCardScenarios((prevScenarios) => {
          const newScenarios = [...prevScenarios];
          newScenarios[newActiveCard] = (newScenarios[newActiveCard] + 1) % replyScenarios.length;
          return newScenarios;
        });
        
        return newActiveCard;
      });
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-[600px] flex items-center overflow-hidden">
      {/* Dot Pattern Background */}
      <DotPattern
        className={cn(
          "fill-gray-300/70 [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]",
        )}
      />
      <div className="relative z-10 max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Badge className="mb-6 bg-gradient-to-r from-orange-50 to-red-50 text-orange-700 border-orange-200">
              🚀 The #1 AI Lead Generation Tool
            </Badge>
            <h1
              className="text-6xl font-sans text-slate-900 mb-6 leading-tight font-[900]"
              style={{
                fontFamily:
                  '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif',
              }}
            >
              Turn Conversations
              <span className="bg-gradient-to-r from-orange-500 to-red-600 bg-clip-text text-transparent block font-semibold">
                Sales Opportunities
              </span>
            </h1>
            <p
              className="text-xl text-slate-600 mb-8 font-normal leading-relaxed"
              style={{
                fontFamily:
                  '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
              }}
            >
              Our AI finds perfect conversations and crafts replies that naturally
              promote your product.
              <strong className="text-orange-600 font-medium">
                {" "}
                Turn Reddit into your most powerful lead generation channel.
              </strong>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex items-center space-x-4"
          >
            <Link href="/dashboard">
              <Button
                size="lg"
                className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 shadow-lg text-lg px-8 py-6 font-semibold"
                style={{
                  fontFamily:
                    '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                }}
              >
                Start Free Trial <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Button
              variant="outline"
              size="lg"
              className="text-lg px-8 py-6 border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold"
              style={{
                fontFamily:
                  '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
              }}
            >
              Watch Demo
            </Button>
          </motion.div>
        </div>

        <div className="relative">
          {/* Card 1 - Top Right */}
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
            className="absolute top-0 right-0"
            style={{ zIndex: activeCard === 0 ? 30 : 20 }}
          >
            <motion.div
              key={`card1-${cardScenarios[0]}`}
              initial={{ opacity: 0, scale: 0.9, x: 20 }}
              animate={{ opacity: 1, scale: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 max-w-xs"
            >
              <div className="flex items-center space-x-2 mb-2">
                <SiReddit className="text-orange-500 text-sm" />
                <span className="text-xs font-medium text-gray-700">
                  {replyScenarios[cardScenarios[0]].cards[0].subreddit}
                </span>
              </div>

              <div className="space-y-2">
                <div className="bg-gray-50 rounded-md p-2">
                  {replyScenarios[cardScenarios[0]].cards[0].username && (
                    <div className="flex items-center space-x-1 mb-1">
                      <User className="w-3 h-3 text-gray-500" />
                      <span className="text-xs font-medium text-gray-600">
                        {replyScenarios[cardScenarios[0]].cards[0].username}
                      </span>
                    </div>
                  )}
                  <p className="text-xs text-gray-800">
                    {replyScenarios[cardScenarios[0]].cards[0].question}
                  </p>
                </div>

                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                  className="bg-gradient-to-r from-orange-50 to-red-50 rounded-md p-2 border-l-2 border-orange-500"
                >
                  <div className="flex items-center space-x-1 mb-1">
                    <Bot className="w-3 h-3 text-orange-600" />
                    {replyScenarios[cardScenarios[0]].cards[0].aiUsername && (
                      <span className="text-xs font-medium text-orange-700">
                        {replyScenarios[cardScenarios[0]].cards[0].aiUsername}
                      </span>
                    )}
                    <Badge className="bg-orange-100 text-orange-700 text-xs py-0 px-1">
                      AI
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-800">
                    {replyScenarios[cardScenarios[0]].cards[0].aiReply}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    <ArrowRight className="w-2 h-2 text-orange-600" />
                    <span className="text-xs text-orange-600 font-medium">
                      {replyScenarios[cardScenarios[0]].cards[0].upvotes}
                    </span>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </motion.div>

          {/* Card 2 - Left Center */}
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 5, repeat: Infinity }}
            className="absolute top-24 left-0"
            style={{ zIndex: activeCard === 1 ? 30 : 20 }}
          >
            <motion.div
              key={`card2-${cardScenarios[1]}`}
              initial={{ opacity: 0, scale: 0.9, x: -20 }}
              animate={{ opacity: 1, scale: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 max-w-xs"
            >
              <div className="flex items-center space-x-2 mb-2">
                <SiReddit className="text-orange-500 text-sm" />
                <span className="text-xs font-medium text-gray-700">
                  {replyScenarios[cardScenarios[1]].cards[1].subreddit}
                </span>
              </div>

              <div className="space-y-2">
                <div className="bg-gray-50 rounded-md p-2">
                  <p className="text-xs text-gray-800">
                    {replyScenarios[cardScenarios[1]].cards[1].question}
                  </p>
                </div>

                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.5, delay: 0.7 }}
                  className="bg-gradient-to-r from-orange-50 to-red-50 rounded-md p-2 border-l-2 border-orange-500"
                >
                  <div className="flex items-center space-x-1 mb-1">
                    <Bot className="w-3 h-3 text-orange-600" />
                    <Badge className="bg-orange-100 text-orange-700 text-xs py-0 px-1">
                      AI
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-800">
                    {replyScenarios[cardScenarios[1]].cards[1].aiReply}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    <ArrowRight className="w-2 h-2 text-orange-600" />
                    <span className="text-xs text-orange-600 font-medium">
                      {replyScenarios[cardScenarios[1]].cards[1].upvotes}
                    </span>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </motion.div>

          {/* Card 3 - Bottom Right */}
          <motion.div
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="absolute bottom-0 right-8"
            style={{ zIndex: activeCard === 2 ? 30 : 20 }}
          >
            <motion.div
              key={`card3-${cardScenarios[2]}`}
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 max-w-xs"
            >
              <div className="flex items-center space-x-2 mb-2">
                <SiReddit className="text-orange-500 text-sm" />
                <span className="text-xs font-medium text-gray-700">
                  {replyScenarios[cardScenarios[2]].cards[2].subreddit}
                </span>
              </div>

              <div className="space-y-2">
                <div className="bg-gray-50 rounded-md p-2">
                  <p className="text-xs text-gray-800">
                    {replyScenarios[cardScenarios[2]].cards[2].question}
                  </p>
                </div>

                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.5, delay: 0.9 }}
                  className="bg-gradient-to-r from-orange-50 to-red-50 rounded-md p-2 border-l-2 border-orange-500"
                >
                  <div className="flex items-center space-x-1 mb-1">
                    <Bot className="w-3 h-3 text-orange-600" />
                    <Badge className="bg-orange-100 text-orange-700 text-xs py-0 px-1">
                      AI
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-800">
                    {replyScenarios[cardScenarios[2]].cards[2].aiReply}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    <ArrowRight className="w-2 h-2 text-orange-600" />
                    <span className="text-xs text-orange-600 font-medium">
                      {replyScenarios[cardScenarios[2]].cards[2].upvotes}
                    </span>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

const LandingPage = () => (
  <div className="min-h-screen bg-white overflow-hidden">
    {/* Compact Header */}
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">LR</span>
            </div>
            <span className="text-xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>
              LeadReplies
            </span>
          </div>

          {/* Navigation Menu */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#platforms" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>Platforms</a>
            <a href="#pricing" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>Pricing</a>
            <Link href="/api">
              <a className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>API</a>
            </Link>
            <a href="#benefits" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>Benefits</a>
          </nav>

          {/* CTA Button */}
          <Link href="/dashboard">
            <Button size="sm" className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
              Start Free Trial
            </Button>
          </Link>
        </div>
      </div>
    </header>

    {/* Add padding top to account for fixed header */}
    <div className="pt-16">
      {/* Hero Section */}
      <section>
        <ImprovedFloatingChatHero />
      </section>

      {/* Platforms Section */}
      <section className="max-w-6xl mx-auto px-6 py-16" id="platforms">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Dominate Every Platform Where Your Customers Are
          </h2>
          <p className="text-lg text-gray-600">
            We monitor conversations across all major platforms and identify
            opportunities to engage naturally
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {platformFeatures.map((platform, index) => {
            const IconComponent = platform.icon;
            const isActive = platform.status === "active";

            return (
              <Card
                key={index}
                className={`relative transition-all duration-300 ${
                  isActive
                    ? `${platform.borderColor} border-2`
                    : "border-gray-200 border-2"
                }`}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-10 h-10 ${platform.bgColor} ${
                          isActive ? platform.borderColor : "border-gray-200"
                        } border-2 rounded-xl flex items-center justify-center`}
                      >
                        <IconComponent
                          className={`w-5 h-5 ${
                            isActive ? platform.color : "text-gray-400"
                          }`}
                        />
                      </div>
                      <h3 className="font-semibold text-gray-900">
                        {platform.name}
                      </h3>
                      {isActive ? (
                        <Badge className="bg-orange-100 text-orange-700 text-xs">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Live Now
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">
                          Coming Soon
                        </Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    {platform.description}
                  </p>
                  <p
                    className={`text-xs font-medium ${isActive ? "text-orange-600" : "text-gray-500"}`}
                  >
                    {platform.metrics}
                  </p>
                </CardContent>
                {!isActive && (
                  <div className="absolute inset-0 bg-white/40 backdrop-blur-[1px]" />
                )}
              </Card>
            );
          })}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white" id="pricing">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>
                Start free, scale as you grow
              </h2>
              <p className="text-xl text-gray-600" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Start free with 5 subreddits & 10 keywords. Upgrade when you're ready.
              </p>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Starter Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="relative h-full border-2 hover:border-orange-200 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>Starter</h3>
                    <p className="text-gray-600 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>For individual creators</p>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>$49</span>
                      <span className="text-gray-600 ml-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>/month</span>
                    </div>
                    <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>or $490/year (Save $98)</p>
                  </div>
                  
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">1 Project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">10 Subreddits monitored</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">20 Keywords tracked</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">600 AI replies/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">150 Reddit scans/month</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      Get Started Free
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>

            {/* Growing Business Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="relative h-full border-2 border-orange-500 shadow-xl">
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-orange-500 to-red-600 text-white px-4 py-2 text-sm font-semibold" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                    Most Popular
                  </Badge>
                </div>
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>Growing Business</h3>
                    <p className="text-gray-600 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>Scale your engagement</p>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>$199</span>
                      <span className="text-gray-600 ml-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>/month</span>
                    </div>
                    <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>or $1,990/year (Save $398)</p>
                  </div>
                  
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">1 Project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">50 Subreddits monitored</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">100 Keywords tracked</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">3,000 AI replies/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">300 Reddit scans/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">Advanced analytics</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      Get Started Free
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>

            {/* Enterprise Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              viewport={{ once: true }}
            >
              <Card className="relative h-full border-2 hover:border-orange-200 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>Marketing Teams</h3>
                    <p className="text-gray-600 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>For agencies & teams</p>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>$799</span>
                      <span className="text-gray-600 ml-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>/month</span>
                    </div>
                    <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>or $7,990/year (Save $1,598)</p>
                  </div>
                  
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">5 Projects</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">50 Subreddits/project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">100 Keywords/project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">18,000 AI replies/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">API access & team tools</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      Get Started Free
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-500 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
              Start free, upgrade anytime. No hidden fees. Cancel anytime.
            </p>
            <div className="max-w-md mx-auto p-6 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl border border-orange-200">
              <h4 className="text-lg font-semibold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>
                🚀 Need more? Let's talk Enterprise
              </h4>
              <p className="text-gray-600 text-sm mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Custom limits, dedicated support, SLAs, and volume pricing
              </p>
              <Button variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Book Enterprise Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-gradient-to-r from-orange-50 to-red-50 py-20" id="benefits">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why LeadReplier is Your Secret Weapon
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Stop manual prospecting. Let AI work 24/7 to find and engage your
              ideal customers naturally.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => {
              const IconComponent = benefit.icon;
              return (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-2xl mb-4">
                    <IconComponent className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {benefit.title}
                  </h3>
                  <p className="text-gray-600">{benefit.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Ready to 10x Your Lead Generation?
          </h2>
          <p className="text-xl text-gray-600 mb-8" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
            Join thousands of businesses using AI to find and convert leads automatically
          </p>
          <div className="flex justify-center items-center space-x-4">
            <Link href="/dashboard">
              <Button size="lg" className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-lg px-8 py-6 font-semibold" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Start Free Trial <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Button variant="outline" size="lg" className="text-lg px-8 py-6 border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
              Book Demo
            </Button>
          </div>
          <p className="text-sm text-gray-500 mt-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>
    </div>
  </div>
);

export default function Landing() {
  const [isHeaderFixed, setIsHeaderFixed] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPercentage = (window.scrollY / window.innerHeight) * 100;
      setIsHeaderFixed(scrollPercentage > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white relative">
      {/* Light Source Background */}
      <div className="fixed top-0 left-0 right-0 h-[900px] bg-gradient-radial pointer-events-none z-0"></div>
      {/* Header */}
      <motion.header
        className={`mx-auto rounded-2xl max-w-6xl border border-gray-200/50 bg-white/70 backdrop-blur-xl z-50 overflow-hidden ${
          isHeaderFixed ? "fixed top-4 left-4 right-4" : "relative mt-4"
        }`}
        animate={{
          y: isHeaderFixed ? 0 : 0,
          scale: isHeaderFixed ? 1 : 1,
          backdropFilter: isHeaderFixed
            ? "blur(20px) saturate(150%)"
            : "blur(12px) saturate(100%)",
          boxShadow: isHeaderFixed
            ? "0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 0 rgba(255, 255, 255, 0.1)"
            : "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        }}
        initial={false}
        transition={{
          type: "spring",
          stiffness: 400,
          damping: 25,
          mass: 0.8,
        }}
      >
        {/* Glossy gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/0 via-white/0 to-white/20 pointer-events-none z-10"></div>{" "}
        <div className="relative max-w-6xl mx-auto px-6 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">LR</span>
              </div>
              <h1
                className="text-xl font-bold text-gray-900"
                style={{
                  fontFamily:
                    '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif',
                }}
              >
                LeadReplier
              </h1>
            </div>

            {/* Navigation Menu */}
            <nav className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                style={{
                  fontFamily:
                    '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                }}
              >
                How It Works
              </a>
              <a
                href="#pricing"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                style={{
                  fontFamily:
                    '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                }}
              >
                Pricing
              </a>
              <Link href="/api">
                <a
                  className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                  style={{
                    fontFamily:
                      '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                  }}
                >
                  API
                </a>
              </Link>
              <a
                href="#faq"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                style={{
                  fontFamily:
                    '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                }}
              >
                FAQ
              </a>
            </nav>

            <div className="flex items-center space-x-3">
              <Link href="/dashboard">
                <Button
                  size="sm"
                  variant="outline"
                  className="text-sm font-medium border-gray-300 text-gray-700 hover:bg-gray-50 transition-all duration-200"
                  style={{
                    fontFamily:
                      '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                  }}
                >
                  Sign In
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button
                  size="sm"
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-md transition-all duration-200 font-semibold text-sm px-4"
                  style={{
                    fontFamily:
                      '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
                  }}
                >
                  Start Free Trial
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <section>
        <ImprovedFloatingChatHero />
      </section>

      {/* Platforms Section */}
      <section className="max-w-6xl mx-auto px-6 py-16" id="platforms">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Dominate Every Platform Where Your Customers Are
          </h2>
          <p className="text-lg text-gray-600">
            We monitor conversations across all major platforms and identify
            perfect opportunities for organic promotion
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {platformFeatures.map((platform) => {
            const IconComponent = platform.icon;
            const isActive = platform.status === "active";

            return (
              <Card
                key={platform.name}
                className={`relative overflow-hidden transition-all duration-300 ${
                  isActive
                    ? `${platform.borderColor} border-2 shadow-lg hover:shadow-xl`
                    : "border-gray-200 opacity-60"
                }`}
              >
                <CardContent className="p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div
                      className={`p-2 rounded-lg ${isActive ? platform.bgColor : "bg-gray-50"}`}
                    >
                      <IconComponent
                        className={`text-xl ${isActive ? platform.color : "text-gray-400"}`}
                      />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {platform.name}
                      </h3>
                      {isActive ? (
                        <Badge className="bg-orange-100 text-orange-700 text-xs">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Live Now
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">
                          Coming Soon
                        </Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    {platform.description}
                  </p>
                  <p
                    className={`text-xs font-medium ${isActive ? "text-orange-600" : "text-gray-500"}`}
                  >
                    {platform.metrics}
                  </p>
                </CardContent>
                {!isActive && (
                  <div className="absolute inset-0 bg-white/40 backdrop-blur-[1px]" />
                )}
              </Card>
            );
          })}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white" id="pricing">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>
                Start free, scale as you grow
              </h2>
              <p className="text-xl text-gray-600" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Start free with 5 subreddits & 10 keywords. Upgrade when you're ready.
              </p>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Starter Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="relative h-full border-2 hover:border-orange-200 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>Starter</h3>
                    <p className="text-gray-600 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>For individual creators</p>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>$49</span>
                      <span className="text-gray-600 ml-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>/month</span>
                    </div>
                    <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>or $490/year (Save $98)</p>
                  </div>
                  
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">1 Project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">10 Subreddits monitored</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">20 Keywords tracked</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">600 AI replies/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">150 Reddit scans/month</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      Get Started Free
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>

            {/* Growing Business Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="relative h-full border-2 border-orange-500 shadow-xl">
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-orange-500 to-red-600 text-white px-4 py-2 text-sm font-semibold" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                    Most Popular
                  </Badge>
                </div>
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>Growing Business</h3>
                    <p className="text-gray-600 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>Scale your engagement</p>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>$199</span>
                      <span className="text-gray-600 ml-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>/month</span>
                    </div>
                    <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>or $1,990/year (Save $398)</p>
                  </div>
                  
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">1 Project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">50 Subreddits monitored</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">100 Keywords tracked</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">3,000 AI replies/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">300 Reddit scans/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">Advanced analytics</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      Get Started Free
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>

            {/* Enterprise Plan */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              viewport={{ once: true }}
            >
              <Card className="relative h-full border-2 hover:border-orange-200 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>Marketing Teams</h3>
                    <p className="text-gray-600 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>For agencies & teams</p>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>$799</span>
                      <span className="text-gray-600 ml-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>/month</span>
                    </div>
                    <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>or $7,990/year (Save $1,598)</p>
                  </div>
                  
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">5 Projects</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">50 Subreddits/project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">100 Keywords/project</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">18,000 AI replies/month</span>
                    </li>
                    <li className="flex items-center" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      <CheckCircle className="w-5 h-5 text-orange-600 mr-3" />
                      <span className="text-gray-700">API access & team tools</span>
                    </li>
                  </ul>
                  
                  <Link href="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                      Get Started Free
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-500 mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
              Start free, upgrade anytime. No hidden fees. Cancel anytime.
            </p>
            <div className="max-w-md mx-auto p-6 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl border border-orange-200">
              <h4 className="text-lg font-semibold text-gray-900 mb-2" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif'}}>
                🚀 Need more? Let's talk Enterprise
              </h4>
              <p className="text-gray-600 text-sm mb-4" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Custom limits, dedicated support, SLAs, and volume pricing
              </p>
              <Button variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'}}>
                Book Enterprise Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-gradient-to-r from-orange-50 to-red-50 py-20" id="benefits">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why LeadReplier is Your Secret Weapon
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Stop manual prospecting. Let AI work 24/7 to find and engage your
              ideal customers naturally.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => {
              const IconComponent = benefit.icon;
              return (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-2xl mb-4">
                    <IconComponent className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {benefit.title}
                  </h3>
                  <p className="text-gray-600">{benefit.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Ready to 10x Your Lead Generation?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of entrepreneurs who've already automated their
            outreach
          </p>
          <Link href="/dashboard">
            <Button
              size="lg"
              className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 shadow-lg text-lg px-12 py-6"
            >
              Start Your Free Trial Today{" "}
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
          <p className="text-sm text-gray-500 mt-4">
            No credit card required • 14-day free trial
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">LR</span>
              </div>
              <span className="text-xl font-bold">LeadReplier</span>
            </div>
            <div className="text-sm text-gray-400">
              © 2024 LeadReplier. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
