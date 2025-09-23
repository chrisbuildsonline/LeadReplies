import {
  Home,
  Megaphone,
  BarChart3,
  Share2,
  Settings,
  Inbox,
  FolderOpen,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";
import logoImage from "@assets/eec88d00-05e8-49ae-bb82-c10a30a8143c_1755302202396.png";

const menuItems = [
  { name: "Dashboard", href: "#", icon: Home, current: true },
  { name: "Campaigns", href: "#", icon: Megaphone, current: false, badge: 3 },
  { name: "Analytics", href: "#", icon: BarChart3, current: false },
  { name: "Platforms", href: "#", icon: Share2, current: false },
];

const favoriteItems = [
  { name: "Active Campaigns", href: "#", current: false },
  { name: "Top Performers", href: "#", current: false },
  { name: "Recent Replies", href: "#", current: false },
];

export default function Sidebar() {
  return (
    <div className="w-80 bg-gray-50 flex flex-col h-full shadow-inner border-r border-gray-200">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <img src={logoImage} alt="LeadReplier" className="w-16 h-16" />
          <h1 className="text-xl font-bold text-gray-900">LeadReplier</h1>
        </div>
      </div>

      {/* Menu Section */}
      <div className="flex-1">
        <div className="mb-6 mt-6">
          <h3 className="text-sm font-medium text-gray-500 mb-4 px-6">Menu</h3>
          <nav className="space-y-1" data-testid="sidebar-navigation">
            {menuItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center justify-between py-3 px-6 text-sm relative text-gray-600 hover:text-gray-900 hover:bg-gray-100 pt-[20px] pb-[20px] pl-[23px] pr-[23px]",
                  item.current
                    ? "text-gray-900 bg-white border-l-4 border-red-500"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100",
                )}
                data-testid={`nav-${item.name.toLowerCase().replace(" ", "-")}`}
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {item.badge}
                  </span>
                )}
              </a>
            ))}
          </nav>
        </div>
        
        {/* Favorites Section */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 mb-4 px-6">
            Favorites
          </h3>
          <nav className="space-y-1">
            {favoriteItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center space-x-3 py-3 px-6 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                data-testid={`fav-${item.name.toLowerCase().replace(/\s+/g, "-")}`}
              >
                <div className="w-2 h-2 rounded-full border border-gray-400"></div>
                <span>{item.name}</span>
              </a>
            ))}
          </nav>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="mt-auto border-t border-gray-200">
        {/* Profile Section */}
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">M</span>
            </div>
            <div className="flex-1">
              <h2 className="font-semibold text-gray-900">Margaret</h2>
              <p className="text-xs text-gray-500">Sr. Marketing Manager</p>
            </div>
          </div>
          
          {/* Package and Settings Row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-transparent border border-gray-900 text-gray-900 shadow-sm">
                Starter Plan
              </span>
            </div>
            <a
              href="#"
              className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-100"
              data-testid="nav-settings"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </a>
          </div>
        </div>

        <div className="px-6 pb-4 text-xs text-gray-400">
          2024 LeadReplies License
        </div>
      </div>
    </div>
  );
}
