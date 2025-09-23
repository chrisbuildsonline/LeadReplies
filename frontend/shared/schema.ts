import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, real, timestamp, boolean, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const campaigns = pgTable("campaigns", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  keywords: text("keywords").array().notNull(),
  platforms: text("platforms").array().notNull(), // ['twitter', 'reddit', 'quora']
  status: text("status").notNull().default("active"), // 'active', 'paused', 'stopped'
  productUrl: text("product_url"),
  description: text("description"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const metrics = pgTable("metrics", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  totalReplies: integer("total_replies").notNull().default(0),
  productsPromoted: integer("products_promoted").notNull().default(0),
  clickThroughRate: real("click_through_rate").notNull().default(0),
  engagementRate: real("engagement_rate").notNull().default(0),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const platformStats = pgTable("platform_stats", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  platform: text("platform").notNull(), // 'twitter', 'reddit', 'quora'
  repliesPosted: integer("replies_posted").notNull().default(0),
  accountsConnected: integer("accounts_connected").notNull().default(0),
  isActive: boolean("is_active").notNull().default(true),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const replies = pgTable("replies", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  platform: text("platform").notNull(),
  content: text("content").notNull(),
  originalPost: text("original_post"),
  username: text("username").notNull(),
  upvotes: integer("upvotes").notNull().default(0),
  campaignId: varchar("campaign_id").references(() => campaigns.id),
  createdAt: timestamp("created_at").defaultNow(),
});

export const accounts = pgTable("accounts", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  platform: text("platform").notNull(),
  username: text("username"),
  price: real("price").notNull().default(5.0),
  age: text("age"), // "6mo old", "1yr old"
  stats: text("stats"), // "200+ followers", "500+ karma"
  description: text("description"),
  available: boolean("available").notNull().default(true),
});

export const dailyStats = pgTable("daily_stats", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  date: text("date").notNull(), // YYYY-MM-DD format
  repliesPosted: integer("replies_posted").notNull().default(0),
  clicksGenerated: integer("clicks_generated").notNull().default(0),
  engagementRate: real("engagement_rate").notNull().default(0),
  keywordsTracked: integer("keywords_tracked").notNull().default(0),
});

export const insertCampaignSchema = createInsertSchema(campaigns).omit({
  id: true,
  createdAt: true,
});

export const insertMetricsSchema = createInsertSchema(metrics).omit({
  id: true,
  updatedAt: true,
});

export const insertPlatformStatsSchema = createInsertSchema(platformStats).omit({
  id: true,
  updatedAt: true,
});

export const insertReplySchema = createInsertSchema(replies).omit({
  id: true,
  createdAt: true,
});

export const insertAccountSchema = createInsertSchema(accounts).omit({
  id: true,
});

export const insertDailyStatsSchema = createInsertSchema(dailyStats).omit({
  id: true,
});

export type Campaign = typeof campaigns.$inferSelect;
export type InsertCampaign = z.infer<typeof insertCampaignSchema>;
export type Metrics = typeof metrics.$inferSelect;
export type InsertMetrics = z.infer<typeof insertMetricsSchema>;
export type PlatformStats = typeof platformStats.$inferSelect;
export type InsertPlatformStats = z.infer<typeof insertPlatformStatsSchema>;
export type Reply = typeof replies.$inferSelect;
export type InsertReply = z.infer<typeof insertReplySchema>;
export type Account = typeof accounts.$inferSelect;
export type InsertAccount = z.infer<typeof insertAccountSchema>;
export type DailyStats = typeof dailyStats.$inferSelect;
export type InsertDailyStats = z.infer<typeof insertDailyStatsSchema>;
