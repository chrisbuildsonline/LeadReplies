import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { redditStorage } from "./reddit-storage";
import { insertCampaignSchema } from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  // IMPORTANT: Proxy routes must come FIRST before any other API routes
  
  // Proxy all auth endpoints to the new multi-tenant API
  app.use("/api/auth", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
        body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("Auth proxy error:", error);
      res.status(500).json({ message: "Auth service unavailable" });
    }
  });

  // Proxy all business endpoints to the new multi-tenant API (catch-all for any business routes)
  app.use("/api/businesses", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
        body: req.method !== 'GET' && req.method !== 'DELETE' ? JSON.stringify(req.body) : undefined,
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("Business proxy error:", error);
      res.status(500).json({ message: "Business service unavailable" });
    }
  });

  // Proxy replies endpoints to the backend API
  app.use("/api/replies", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
        body: req.method !== 'GET' && req.method !== 'DELETE' ? JSON.stringify(req.body) : undefined,
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("Replies proxy error:", error);
      res.status(500).json({ message: "Replies service unavailable" });
    }
  });

  // Proxy platforms endpoints to the backend API
  app.use("/api/platforms", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
        body: req.method !== 'GET' && req.method !== 'DELETE' ? JSON.stringify(req.body) : undefined,
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("Platforms proxy error:", error);
      res.status(500).json({ message: "Platforms service unavailable" });
    }
  });

  // Catch-all proxy for any other API endpoints that should go to the backend
  app.use("/api", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
        body: req.method !== 'GET' && req.method !== 'DELETE' ? JSON.stringify(req.body) : undefined,
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("API proxy error:", error);
      res.status(500).json({ message: "API service unavailable" });
    }
  });

  // Proxy dashboard endpoint to the backend API
  app.get("/api/dashboard", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("Dashboard proxy error:", error);
      res.status(500).json({ message: "Dashboard service unavailable" });
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

  // Proxy accounts endpoints to the backend API (this should come before the old accounts endpoint)
  app.use("/api/accounts", async (req, res) => {
    try {
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}${req.originalUrl}`, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization || '',
        },
        body: req.method !== 'GET' && req.method !== 'DELETE' ? JSON.stringify(req.body) : undefined,
      });
      
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error) {
      console.error("Accounts proxy error:", error);
      res.status(500).json({ message: "Accounts service unavailable" });
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

  // Reddit leads endpoints (keep for backward compatibility)
  app.get("/api/reddit/leads", async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 50;
      const minProbability = req.query.min_probability ? parseInt(req.query.min_probability as string) : 0;
      
      const backendUrl = process.env.VITE_API_URL || 'http://localhost:6070';
      const response = await fetch(`${backendUrl}/api/leads?limit=${limit}&min_probability=${minProbability}`);
      const data = await response.json();
      
      res.json(data);
    } catch (error) {
      console.error("Reddit leads error:", error);
      res.status(500).json({ message: "Failed to fetch Reddit leads" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
