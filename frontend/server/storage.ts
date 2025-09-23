import { 
  type Campaign, type InsertCampaign,
  type Metrics, type InsertMetrics,
  type PlatformStats, type InsertPlatformStats,
  type Reply, type InsertReply,
  type Account, type InsertAccount,
  type DailyStats, type InsertDailyStats
} from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  // Campaigns
  getCampaigns(): Promise<Campaign[]>;
  getCampaign(id: string): Promise<Campaign | undefined>;
  createCampaign(campaign: InsertCampaign): Promise<Campaign>;
  updateCampaign(id: string, campaign: Partial<InsertCampaign>): Promise<Campaign | undefined>;
  deleteCampaign(id: string): Promise<boolean>;

  // Metrics
  getMetrics(): Promise<Metrics | undefined>;
  updateMetrics(metrics: InsertMetrics): Promise<Metrics>;

  // Platform Stats
  getPlatformStats(): Promise<PlatformStats[]>;
  getPlatformStat(platform: string): Promise<PlatformStats | undefined>;
  updatePlatformStats(platform: string, stats: InsertPlatformStats): Promise<PlatformStats>;

  // Replies
  getReplies(limit?: number): Promise<Reply[]>;
  createReply(reply: InsertReply): Promise<Reply>;

  // Accounts
  getAccounts(): Promise<Account[]>;
  getAccountsByPlatform(platform: string): Promise<Account[]>;
  purchaseAccount(id: string): Promise<boolean>;

  // Daily Stats
  getDailyStats(): Promise<DailyStats | undefined>;
  updateDailyStats(stats: InsertDailyStats): Promise<DailyStats>;
}

export class MemStorage implements IStorage {
  private campaigns: Map<string, Campaign> = new Map();
  private metrics: Metrics | undefined;
  private platformStats: Map<string, PlatformStats> = new Map();
  private replies: Reply[] = [];
  private accounts: Map<string, Account> = new Map();
  private dailyStats: DailyStats | undefined;

  constructor() {
    this.initializeData();
  }

  private initializeData() {
    // Initialize with realistic data
    const metricsId = randomUUID();
    this.metrics = {
      id: metricsId,
      totalReplies: 2847,
      productsPromoted: 127,
      clickThroughRate: 4.2,
      engagementRate: 89,
      updatedAt: new Date(),
    };

    // Platform stats
    const platforms = [
      { platform: 'twitter', repliesPosted: 1247, accountsConnected: 3, isActive: true },
      { platform: 'reddit', repliesPosted: 892, accountsConnected: 2, isActive: true },
      { platform: 'quora', repliesPosted: 708, accountsConnected: 4, isActive: true },
    ];

    platforms.forEach(stat => {
      const id = randomUUID();
      this.platformStats.set(stat.platform, {
        id,
        ...stat,
        updatedAt: new Date(),
      });
    });

    // Sample campaigns
    const campaignData = [
      {
        name: "SaaS Project Management Tool",
        keywords: ["project management", "team collaboration", "task tracking"],
        platforms: ["twitter", "reddit", "quora"],
        status: "active",
        productUrl: "https://projectflow.com",
        description: "Promoting our project management tool",
      },
      {
        name: "E-commerce Analytics Platform",
        keywords: ["ecommerce analytics", "sales tracking", "conversion optimization"],
        platforms: ["twitter", "quora"],
        status: "paused",
        productUrl: "https://shopinsights.com",
        description: "Analytics platform for e-commerce",
      },
    ];

    campaignData.forEach(campaign => {
      const id = randomUUID();
      this.campaigns.set(id, {
        id,
        ...campaign,
        createdAt: new Date(),
      });
    });

    // Sample replies
    const replyData = [
      {
        platform: "twitter",
        content: "I've been using ProjectFlow for similar needs - it has great team collaboration features and intuitive task tracking. Worth checking out!",
        username: "@sarah_tech_lead",
        upvotes: 3,
        createdAt: new Date(Date.now() - 2 * 60 * 1000), // 2 minutes ago
      },
      {
        platform: "reddit",
        content: "For analytics, I'd recommend looking into ShopInsights. It's specifically built for e-commerce and has really good conversion tracking.",
        username: "r/ecommerce",
        upvotes: 5,
        createdAt: new Date(Date.now() - 12 * 60 * 1000), // 12 minutes ago
      },
      {
        platform: "quora",
        content: "Based on my experience, TaskManager Pro handles team collaboration really well. The interface is clean and the reporting features are comprehensive.",
        username: "Business Management",
        upvotes: 8,
        createdAt: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
      },
      {
        platform: "twitter",
        content: "Have you tried DataTrack? It's fantastic for small businesses looking to understand their sales patterns better. Simple setup too.",
        username: "@marketing_mike",
        upvotes: 12,
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      },
    ];

    replyData.forEach(reply => {
      const id = randomUUID();
      this.replies.push({
        id,
        ...reply,
        originalPost: "",
        campaignId: null,
      });
    });

    // Sample accounts
    const accountData = [
      {
        platform: "twitter",
        username: "",
        price: 5.0,
        age: "6mo old",
        stats: "200+ followers",
        description: "verified email",
        available: true,
      },
      {
        platform: "reddit",
        username: "",
        price: 5.0,
        age: "1yr old",
        stats: "500+ karma",
        description: "active history",
        available: true,
      },
      {
        platform: "quora",
        username: "",
        price: 5.0,
        age: "8mo old",
        stats: "100+ answers",
        description: "good reputation",
        available: true,
      },
    ];

    accountData.forEach(account => {
      const id = randomUUID();
      this.accounts.set(id, {
        id,
        ...account,
      });
    });

    // Daily stats
    this.dailyStats = {
      id: randomUUID(),
      date: new Date().toISOString().split('T')[0],
      repliesPosted: 47,
      clicksGenerated: 23,
      engagementRate: 6.2,
      keywordsTracked: 15,
    };
  }

  async getCampaigns(): Promise<Campaign[]> {
    return Array.from(this.campaigns.values());
  }

  async getCampaign(id: string): Promise<Campaign | undefined> {
    return this.campaigns.get(id);
  }

  async createCampaign(campaign: InsertCampaign): Promise<Campaign> {
    const id = randomUUID();
    const newCampaign: Campaign = {
      ...campaign,
      id,
      status: campaign.status || "active",
      productUrl: campaign.productUrl || null,
      description: campaign.description || null,
      createdAt: new Date(),
    };
    this.campaigns.set(id, newCampaign);
    return newCampaign;
  }

  async updateCampaign(id: string, campaign: Partial<InsertCampaign>): Promise<Campaign | undefined> {
    const existing = this.campaigns.get(id);
    if (!existing) return undefined;
    
    const updated = { ...existing, ...campaign };
    this.campaigns.set(id, updated);
    return updated;
  }

  async deleteCampaign(id: string): Promise<boolean> {
    return this.campaigns.delete(id);
  }

  async getMetrics(): Promise<Metrics | undefined> {
    return this.metrics;
  }

  async updateMetrics(metrics: InsertMetrics): Promise<Metrics> {
    const id = this.metrics?.id || randomUUID();
    const updated: Metrics = {
      id,
      totalReplies: metrics.totalReplies || 0,
      productsPromoted: metrics.productsPromoted || 0,
      clickThroughRate: metrics.clickThroughRate || 0,
      engagementRate: metrics.engagementRate || 0,
      updatedAt: new Date(),
    };
    this.metrics = updated;
    return updated;
  }

  async getPlatformStats(): Promise<PlatformStats[]> {
    return Array.from(this.platformStats.values());
  }

  async getPlatformStat(platform: string): Promise<PlatformStats | undefined> {
    return this.platformStats.get(platform);
  }

  async updatePlatformStats(platform: string, stats: InsertPlatformStats): Promise<PlatformStats> {
    const existing = this.platformStats.get(platform);
    const id = existing?.id || randomUUID();
    
    const updated: PlatformStats = {
      id,
      platform,
      repliesPosted: stats.repliesPosted || 0,
      accountsConnected: stats.accountsConnected || 0,
      isActive: stats.isActive !== undefined ? stats.isActive : true,
      updatedAt: new Date(),
    };
    
    this.platformStats.set(platform, updated);
    return updated;
  }

  async getReplies(limit = 10): Promise<Reply[]> {
    return this.replies
      .sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0))
      .slice(0, limit);
  }

  async createReply(reply: InsertReply): Promise<Reply> {
    const id = randomUUID();
    const newReply: Reply = {
      ...reply,
      id,
      originalPost: reply.originalPost || null,
      upvotes: reply.upvotes || 0,
      campaignId: reply.campaignId || null,
      createdAt: new Date(),
    };
    this.replies.unshift(newReply);
    return newReply;
  }

  async getAccounts(): Promise<Account[]> {
    return Array.from(this.accounts.values()).filter(account => account.available);
  }

  async getAccountsByPlatform(platform: string): Promise<Account[]> {
    return Array.from(this.accounts.values()).filter(
      account => account.platform === platform && account.available
    );
  }

  async purchaseAccount(id: string): Promise<boolean> {
    const account = this.accounts.get(id);
    if (!account || !account.available) return false;
    
    account.available = false;
    this.accounts.set(id, account);
    return true;
  }

  async getDailyStats(): Promise<DailyStats | undefined> {
    return this.dailyStats;
  }

  async updateDailyStats(stats: InsertDailyStats): Promise<DailyStats> {
    const id = this.dailyStats?.id || randomUUID();
    const updated: DailyStats = {
      id,
      date: stats.date,
      repliesPosted: stats.repliesPosted || 0,
      clicksGenerated: stats.clicksGenerated || 0,
      engagementRate: stats.engagementRate || 0,
      keywordsTracked: stats.keywordsTracked || 0,
    };
    this.dailyStats = updated;
    return updated;
  }
}

export const storage = new MemStorage();
