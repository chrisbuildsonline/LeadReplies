import { 
  type Campaign, type InsertCampaign,
  type Metrics, type InsertMetrics,
  type PlatformStats, type InsertPlatformStats,
  type Reply, type InsertReply,
  type Account, type InsertAccount,
  type DailyStats, type InsertDailyStats
} from "@shared/schema";
import { IStorage } from "./storage";

const REDDIT_API_BASE = `${process.env.VITE_API_URL || "http://localhost:6070"}/api`;

export class RedditAPIStorage implements IStorage {
  
  async getCampaigns(): Promise<Campaign[]> {
    try {
      const response = await fetch(`${REDDIT_API_BASE}/dashboard`);
      const data = await response.json();
      return data.campaigns || [];
    } catch (error) {
      console.error("Failed to fetch campaigns:", error);
      return [];
    }
  }

  async getCampaign(id: string): Promise<Campaign | undefined> {
    const campaigns = await this.getCampaigns();
    return campaigns.find(c => c.id === id);
  }

  async createCampaign(campaign: InsertCampaign): Promise<Campaign> {
    // For now, return a mock campaign since we don't have campaign creation in Reddit API
    const newCampaign: Campaign = {
      ...campaign,
      id: `campaign_${Date.now()}`,
      status: campaign.status || "active",
      productUrl: campaign.productUrl || null,
      description: campaign.description || null,
      createdAt: new Date(),
    };
    return newCampaign;
  }

  async updateCampaign(id: string, campaign: Partial<InsertCampaign>): Promise<Campaign | undefined> {
    // Mock update - in real implementation, this would call the Reddit API
    const existing = await this.getCampaign(id);
    if (!existing) return undefined;
    return { ...existing, ...campaign };
  }

  async deleteCampaign(id: string): Promise<boolean> {
    // Mock delete - in real implementation, this would call the Reddit API
    return true;
  }

  async getMetrics(): Promise<Metrics | undefined> {
    try {
      const response = await fetch(`${REDDIT_API_BASE}/dashboard`);
      const data = await response.json();
      return data.metrics;
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
      return undefined;
    }
  }

  async updateMetrics(metrics: InsertMetrics): Promise<Metrics> {
    // Mock update - metrics are calculated from Reddit data
    const existing = await this.getMetrics();
    return existing || {
      id: "1",
      totalReplies: metrics.totalReplies || 0,
      productsPromoted: metrics.productsPromoted || 0,
      clickThroughRate: metrics.clickThroughRate || 0,
      engagementRate: metrics.engagementRate || 0,
      updatedAt: new Date(),
    };
  }

  async getPlatformStats(): Promise<PlatformStats[]> {
    try {
      const response = await fetch(`${REDDIT_API_BASE}/dashboard`);
      const data = await response.json();
      return data.platformStats || [];
    } catch (error) {
      console.error("Failed to fetch platform stats:", error);
      return [];
    }
  }

  async getPlatformStat(platform: string): Promise<PlatformStats | undefined> {
    const stats = await this.getPlatformStats();
    return stats.find(s => s.platform === platform);
  }

  async updatePlatformStats(platform: string, stats: InsertPlatformStats): Promise<PlatformStats> {
    // Mock update - platform stats are calculated from Reddit data
    const existing = await this.getPlatformStat(platform);
    return existing || {
      id: platform,
      platform,
      repliesPosted: stats.repliesPosted || 0,
      accountsConnected: stats.accountsConnected || 0,
      isActive: stats.isActive !== undefined ? stats.isActive : true,
      updatedAt: new Date(),
    };
  }

  async getReplies(limit = 10): Promise<Reply[]> {
    try {
      const response = await fetch(`${REDDIT_API_BASE}/dashboard`);
      const data = await response.json();
      return data.replies || [];
    } catch (error) {
      console.error("Failed to fetch replies:", error);
      return [];
    }
  }

  async createReply(reply: InsertReply): Promise<Reply> {
    // Mock create - replies come from Reddit scraping
    const newReply: Reply = {
      ...reply,
      id: `reply_${Date.now()}`,
      originalPost: reply.originalPost || null,
      upvotes: reply.upvotes || 0,
      campaignId: reply.campaignId || null,
      createdAt: new Date(),
    };
    return newReply;
  }

  async getAccounts(): Promise<Account[]> {
    try {
      const response = await fetch(`${REDDIT_API_BASE}/dashboard`);
      const data = await response.json();
      return data.accounts || [];
    } catch (error) {
      console.error("Failed to fetch accounts:", error);
      return [];
    }
  }

  async getAccountsByPlatform(platform: string): Promise<Account[]> {
    const accounts = await this.getAccounts();
    return accounts.filter(account => account.platform === platform && account.available);
  }

  async purchaseAccount(id: string): Promise<boolean> {
    // Mock purchase - would integrate with actual account purchasing system
    return true;
  }

  async getDailyStats(): Promise<DailyStats | undefined> {
    try {
      const response = await fetch(`${REDDIT_API_BASE}/dashboard`);
      const data = await response.json();
      return data.dailyStats;
    } catch (error) {
      console.error("Failed to fetch daily stats:", error);
      return undefined;
    }
  }

  async updateDailyStats(stats: InsertDailyStats): Promise<DailyStats> {
    // Mock update - daily stats are calculated from Reddit data
    const existing = await this.getDailyStats();
    return existing || {
      id: "today",
      date: stats.date,
      repliesPosted: stats.repliesPosted || 0,
      clicksGenerated: stats.clicksGenerated || 0,
      engagementRate: stats.engagementRate || 0,
      keywordsTracked: stats.keywordsTracked || 0,
    };
  }
}

export const redditStorage = new RedditAPIStorage();