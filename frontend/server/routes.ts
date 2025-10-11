import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { redditStorage } from "./reddit-storage";
import { insertCampaignSchema } from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  // Dashboard data - use Reddit API
  app.get("/api/dashboard", async (req, res) => {
    try {
      const [metrics, platformStats, campaigns, replies, accounts, dailyStats] = await Promise.all([
        redditStorage.getMetrics(),
        redditStorage.getPlatformStats(),
        redditStorage.getCampaigns(),
        redditStorage.getReplies(4),
        redditStorage.getAccounts(),
        redditStorage.getDailyStats(),
      ]);

      res.json({
        metrics,
        platformStats,
        campaigns,
        replies,
        accounts,
        dailyStats,
      });
    } catch (error) {
      console.error("Dashboard error:", error);
      res.status(500).json({ message: "Failed to fetch dashboard data" });
    }
  });

  // Campaigns
  app.get("/api/campaigns", async (req, res) => {
    try {
      const campaigns = await storage.getCampaigns();
      res.json(campaigns);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch campaigns" });
    }
  });

  app.post("/api/campaigns", async (req, res) => {
    try {
      const validatedData = insertCampaignSchema.parse(req.body);
      const campaign = await storage.createCampaign(validatedData);
      res.status(201).json(campaign);
    } catch (error) {
      res.status(400).json({ message: "Invalid campaign data" });
    }
  });

  app.patch("/api/campaigns/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const updates = req.body;
      const campaign = await storage.updateCampaign(id, updates);
      
      if (!campaign) {
        return res.status(404).json({ message: "Campaign not found" });
      }
      
      res.json(campaign);
    } catch (error) {
      res.status(400).json({ message: "Failed to update campaign" });
    }
  });

  app.delete("/api/campaigns/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const deleted = await storage.deleteCampaign(id);
      
      if (!deleted) {
        return res.status(404).json({ message: "Campaign not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to delete campaign" });
    }
  });

  // Platform stats
  app.get("/api/platform-stats", async (req, res) => {
    try {
      const stats = await storage.getPlatformStats();
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch platform stats" });
    }
  });

  // Replies
  app.get("/api/replies", async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;
      const replies = await storage.getReplies(limit);
      res.json(replies);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch replies" });
    }
  });

  // Accounts
  app.get("/api/accounts", async (req, res) => {
    try {
      const accounts = await storage.getAccounts();
      res.json(accounts);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch accounts" });
    }
  });

  app.post("/api/accounts/:id/purchase", async (req, res) => {
    try {
      const { id } = req.params;
      const success = await storage.purchaseAccount(id);
      
      if (!success) {
        return res.status(400).json({ message: "Account not available or not found" });
      }
      
      res.json({ message: "Account purchased successfully" });
    } catch (error) {
      res.status(500).json({ message: "Failed to purchase account" });
    }
  });

  // Metrics
  app.get("/api/metrics", async (req, res) => {
    try {
      const metrics = await storage.getMetrics();
      res.json(metrics);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch metrics" });
    }
  });

  // Daily stats
  app.get("/api/daily-stats", async (req, res) => {
    try {
      const stats = await storage.getDailyStats();
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch daily stats" });
    }
  });

  // Reddit leads endpoints
  app.get("/api/reddit/leads", async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 50;
      const minProbability = req.query.min_probability ? parseInt(req.query.min_probability as string) : 0;
      
      const response = await fetch(`http://localhost:6070/api/leads?limit=${limit}&min_probability=${minProbability}`);
      const data = await response.json();
      
      res.json(data);
    } catch (error) {
      console.error("Reddit leads error:", error);
      res.status(500).json({ message: "Failed to fetch Reddit leads" });
    }
  });

  app.get("/api/reddit/leads/high-quality", async (req, res) => {
    try {
      const response = await fetch("http://localhost:6070/api/leads/high-quality");
      const data = await response.json();
      
      res.json(data);
    } catch (error) {
      console.error("High quality leads error:", error);
      res.status(500).json({ message: "Failed to fetch high quality leads" });
    }
  });

  app.post("/api/reddit/scraping/run-once", async (req, res) => {
    try {
      const response = await fetch("http://localhost:6070/api/scraping/run-once", {
        method: "POST"
      });
      const data = await response.json();
      
      res.json(data);
    } catch (error) {
      console.error("Scraping error:", error);
      res.status(500).json({ message: "Failed to run scraping" });
    }
  });

  app.get("/api/reddit/scraping/status", async (req, res) => {
    try {
      const response = await fetch("http://localhost:6070/api/scraping/status");
      const data = await response.json();
      
      res.json(data);
    } catch (error) {
      console.error("Scraping status error:", error);
      res.status(500).json({ message: "Failed to get scraping status" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
