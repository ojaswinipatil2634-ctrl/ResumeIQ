import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { NavSidebar, MobileSidebarToggle } from '../components/NavSidebar';

export const PublicLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen bg-bg-base">
    <header className="fixed top-0 left-0 right-0 z-40 border-b border-border-subtle bg-bg-base/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md gradient-bg flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          <span className="font-bold text-text-primary tracking-tight">ResumeIQ</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm text-text-secondary hover:text-text-primary transition-colors">Sign In</Link>
          <Link to="/register" className="text-sm px-4 py-1.5 gradient-bg rounded-sm text-white font-medium hover:opacity-90 transition-opacity">
            Get Started
          </Link>
        </div>
      </div>
    </header>
    <main className="pt-14">{children}</main>
  </div>
);

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex h-screen bg-bg-base overflow-hidden">
    {/* Desktop sidebar */}
    <aside className="hidden lg:flex flex-col w-60 flex-shrink-0">
      <NavSidebar />
    </aside>
    {/* Main */}
    <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
      {/* Mobile header */}
      <header className="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-border-subtle">
        <MobileSidebarToggle />
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded gradient-bg flex items-center justify-center">
            <Sparkles size={12} className="text-white" />
          </div>
          <span className="font-bold text-text-primary text-sm">ResumeIQ</span>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  </div>
);
