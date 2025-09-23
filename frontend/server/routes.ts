import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertCampaignSchema } from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  // Dashboard data
  app.get("/api/dashboard", async (req, res) => {
    try {
      const [metrics, platformStats, campaigns, replies, accounts, dailyStats] = await Promise.all([
        storage.getMetrics(),
        storage.getPlatformStats(),
        storage.getCampaigns(),
        storage.getReplies(4),
        storage.getAccounts(),
        storage.getDailyStats(),
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

  const httpServer = createServer(app);
  return httpServer;
}
