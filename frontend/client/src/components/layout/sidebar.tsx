import {
  Home,
  BarChart3,
  Share2,
  Settings,
  Building2,
} from "lucide-react";
import { SiReddit } from "react-icons/si";
import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
// Logo placeholder - using div instead of image

import { Users } from "lucide-react";

const menuItems = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Businesses", href: "/businesses", icon: Building2 },
  { name: "Leads", href: "/leads", icon: SiReddit },
  { name: "Platforms", href: "/platforms", icon: Share2 },
  { name: "Accounts", href: "/accounts", icon: Users },
];

const favoriteItems = [
  { name: "High Quality Leads", href: "/leads?filter=high", current: false },
  { name: "Today's Leads", href: "/leads?date=today", current: false },
  { name: "Recent Activity", href: "/dashboard", current: false },
];

export default function Sidebar() {
  const [location] = useLocation();
  
  return (
    <div className="w-80 bg-gray-900 flex flex-col h-full shadow-inner border-r border-gray-800">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-700">
        <Link href="/dashboard">
          <div className="flex items-center space-x-3 cursor-pointer">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-2xl">LR</span>
            </div>
            <h1 className="text-xl font-bold text-white">LeadReplier</h1>
          </div>
        </Link>
      </div>

      {/* Menu Section */}
      <div className="flex-1">
        <div className="mb-6 mt-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4 px-6">Menu</h3>
          <nav className="space-y-1" data-testid="sidebar-navigation">
            {menuItems.map((item) => {
              const isActive = location === item.href;
              const ItemIcon = item.icon;
              
              return item.href.startsWith('#') ? (
                <a
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between py-3 px-6 text-sm relative text-gray-300 hover:text-white hover:bg-gray-800 pt-[20px] pb-[20px] pl-[23px] pr-[23px]",
                    isActive
                      ? "text-white bg-gray-800 border-l-4 border-orange-500"
                      : "text-gray-300 hover:text-white hover:bg-gray-800",
                  )}
                  data-testid={`nav-${item.name.toLowerCase().replace(" ", "-")}`}
                >
                  <div className="flex items-center space-x-3">
                    <ItemIcon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {item.badge}
                    </span>
                  )}
                </a>
              ) : (
                <Link key={item.name} href={item.href}>
                  <div
                    className={cn(
                      "flex items-center justify-between py-3 px-6 text-sm relative text-gray-300 hover:text-white hover:bg-gray-800 pt-[20px] pb-[20px] pl-[23px] pr-[23px] cursor-pointer",
                      isActive
                        ? "text-white bg-gray-800 border-l-4 border-orange-500"
                        : "text-gray-300 hover:text-white hover:bg-gray-800",
                    )}
                    data-testid={`nav-${item.name.toLowerCase().replace(" ", "-")}`}
                  >
                    <div className="flex items-center space-x-3">
                      <ItemIcon className="h-4 w-4" />
                      <span>{item.name}</span>
                    </div>

                  </div>
                </Link>
              );
            })}
          </nav>
        </div>
        
        {/* Favorites Section */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4 px-6">
            Favorites
          </h3>
          <nav className="space-y-1">
            {favoriteItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center space-x-3 py-3 px-6 text-sm text-gray-300 hover:text-white hover:bg-gray-800"
                data-testid={`fav-${item.name.toLowerCase().replace(/\s+/g, "-")}`}
              >
                <div className="w-2 h-2 rounded-full border border-gray-500"></div>
                <span>{item.name}</span>
              </a>
            ))}
          </nav>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="mt-auto border-t border-gray-700">
        {/* Profile Section */}
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">M</span>
            </div>
            <div className="flex-1">
              <h2 className="font-semibold text-white">Margaret</h2>
              <p className="text-xs text-gray-400">Sr. Marketing Manager</p>
            </div>
          </div>
          
          {/* Package and Settings Row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-transparent border border-orange-500 text-orange-400 shadow-sm">
                Starter Plan
              </span>
            </div>
            <a
              href="#"
              className="flex items-center space-x-2 text-sm text-gray-300 hover:text-white p-1 rounded hover:bg-gray-800"
              data-testid="nav-settings"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </a>
          </div>
        </div>

        <div className="px-6 pb-4 text-xs text-gray-500">
          2024 LeadReplies License
        </div>
      </div>
    </div>
  );
}
