import { ReactNode } from "react";
import Sidebar from "./sidebar";

interface PageLayoutProps {
  children: ReactNode;
  className?: string;
}

export default function PageLayout({ children, className = "" }: PageLayoutProps) {
  return (
    <div className="flex h-screen bg-gray-900 p-10">
      <Sidebar />
      <div className={`flex-1 overflow-auto ${className}`}>
              <div className="p-8 bg-[#ffffff]">

        {children}
        </div>
      </div>
    </div>
  );
}