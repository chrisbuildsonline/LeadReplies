# Overview

LeadReplies is an AI automation platform that helps users promote their SaaS products across social media platforms (Twitter/X, Reddit, Quora) by automatically injecting relevant replies to discussions. The application provides a comprehensive dashboard for managing campaigns, tracking metrics, and monitoring AI-generated responses across multiple social platforms.

# Recent Changes

## August 15, 2025
- Updated branding from "ReplyLeads" to "LeadReplies" 
- Replaced account purchasing with external link to Gumroad to comply with platform TOS
- Added proper social media brand icons (X, Reddit, Quora) using react-icons/si
- Updated dashboard content to emphasize AI reply injection for SaaS/app promotion
- Fixed date formatting issues in ActivityFeed component

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend is built with **React** and **TypeScript**, using modern development practices:
- **Vite** as the build tool and development server for fast hot module replacement
- **Wouter** for lightweight client-side routing 
- **TanStack Query** for server state management and data fetching
- **Shadcn/ui** component library built on Radix UI primitives for consistent, accessible UI components
- **Tailwind CSS** for utility-first styling with CSS custom properties for theming
- **React Hook Form** with Zod validation for form handling

The application follows a component-based architecture with clear separation between UI components (`/components/ui`), dashboard-specific components (`/components/dashboard`), and layout components (`/components/layout`).

## Backend Architecture
The backend is an **Express.js** server with TypeScript:
- **RESTful API** design with endpoints for campaigns, metrics, platform stats, replies, and accounts
- **In-memory storage** implementation (`MemStorage`) for development/demo purposes
- **Middleware** for request logging and error handling
- **Type-safe** data validation using Zod schemas

The storage layer follows the Repository pattern with an `IStorage` interface, making it easy to swap between different storage implementations (currently in-memory, but designed for database integration).

## Data Storage Solutions
Currently uses an in-memory storage system for development, but the architecture is prepared for **PostgreSQL** integration:
- **Drizzle ORM** configured for PostgreSQL with migration support
- **Database schema** defined in TypeScript with proper relationships
- **Connection setup** for Neon Database serverless PostgreSQL
- **Type-safe** database operations with generated TypeScript types

## Authentication and Authorization
The current implementation uses **session-based authentication**:
- **Express sessions** with PostgreSQL session store (`connect-pg-simple`)
- Session cookies for maintaining user state
- Prepared for user authentication but currently operates in demo mode

## External Service Integrations
The application is designed to integrate with multiple social media platforms:
- **Platform abstraction** in the data model (Twitter, Reddit, Quora)
- **Account management** system for purchasing and managing social media accounts
- **Metrics tracking** across different platforms
- **Campaign management** with platform-specific targeting

The architecture supports future integration with:
- Social media APIs for automated posting
- AI services for content generation
- Payment systems for account purchasing
- Analytics and reporting services

## Development and Production Setup
- **Development**: Vite dev server with Express API backend
- **Production**: Optimized Vite build with esbuild for server bundling
- **TypeScript**: Full type safety across frontend, backend, and shared schemas
- **Hot reloading**: Integrated development experience with Vite and Express
- **Error handling**: Comprehensive error boundaries and API error handling