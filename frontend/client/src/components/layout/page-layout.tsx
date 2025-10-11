import { ReactNode } from "react";
import Sidebar from "./sidebar";

interface PageLayoutProps {
  children: ReactNode;
  className?: string;
}

export default function PageLayout({ children, className = "" }: PageLayoutProps) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className={`flex-1 overflow-auto ${className}`}>
        {children}
      </div>
    </div>
  );
}