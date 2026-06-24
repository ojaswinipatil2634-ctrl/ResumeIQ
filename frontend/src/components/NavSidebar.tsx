import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Upload, BarChart2, User, Sparkles, Target,
  Briefcase, Pencil, MessageSquare, Map, LogOut, Menu, X, ChevronRight
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useResume } from '../hooks/useResume';
import { getInitials } from '../utils/format.utils';

const NavItem: React.FC<{
  to: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick?: () => void;
}> = ({ to, icon, label, active, onClick }) => (
  <Link
    to={to}
    onClick={onClick}
    className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all duration-150
      ${active
        ? 'bg-primary/15 text-primary'
        : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
      }`}
  >
    {icon}
    <span>{label}</span>
    {active && <ChevronRight size={14} className="ml-auto text-primary" />}
  </Link>
);

export const NavSidebar: React.FC<{ mobile?: boolean; onClose?: () => void }> = ({ mobile, onClose }) => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { currentResumeId, currentResumeFilename } = useResume();
  const p = location.pathname;

  const handleLogout = () => { logout(); window.location.href = '/'; };

  return (
    <div className={`flex flex-col h-full ${mobile ? 'bg-bg-elevated' : 'bg-bg-surface border-r border-border-subtle'}`}>
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-border-subtle">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md gradient-bg flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          <span className="font-bold text-text-primary tracking-tight">ResumeIQ</span>
        </Link>
        {mobile && onClose && (
          <button onClick={onClose} className="text-text-muted hover:text-text-primary">
            <X size={20} />
          </button>
        )}
      </div>

      {/* Main nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 flex flex-col gap-1">
        <NavItem to="/dashboard" icon={<LayoutDashboard size={16} />} label="Dashboard" active={p === '/dashboard'} onClick={onClose} />
        <NavItem to="/upload" icon={<Upload size={16} />} label="Upload Resume" active={p === '/upload'} onClick={onClose} />
        <NavItem to="/analytics" icon={<BarChart2 size={16} />} label="Analytics" active={p === '/analytics'} onClick={onClose} />
        <NavItem to="/profile" icon={<User size={16} />} label="Profile" active={p === '/profile'} onClick={onClose} />

        {currentResumeId && (
          <>
            <div className="my-3 border-t border-border-subtle" />
            <p className="px-3 text-xs font-medium text-text-muted uppercase tracking-wider mb-1">Current Resume</p>
            {currentResumeFilename && (
              <p className="px-3 text-xs text-text-muted truncate mb-2" title={currentResumeFilename}>
                {currentResumeFilename}
              </p>
            )}
            <NavItem to={`/analysis/${currentResumeId}`} icon={<Sparkles size={16} />} label="Analysis" active={p.startsWith('/analysis')} onClick={onClose} />
            <NavItem to={`/ats/${currentResumeId}`} icon={<Target size={16} />} label="ATS Score" active={p.startsWith('/ats')} onClick={onClose} />
            <NavItem to={`/job-match/${currentResumeId}`} icon={<Briefcase size={16} />} label="Job Match" active={p.startsWith('/job-match')} onClick={onClose} />
            <NavItem to={`/improve/${currentResumeId}`} icon={<Pencil size={16} />} label="Improvement" active={p.startsWith('/improve')} onClick={onClose} />
            <NavItem to={`/interview/${currentResumeId}`} icon={<MessageSquare size={16} />} label="Interview Prep" active={p.startsWith('/interview')} onClick={onClose} />
            <NavItem to={`/roadmap/${currentResumeId}`} icon={<Map size={16} />} label="Career Roadmap" active={p.startsWith('/roadmap')} onClick={onClose} />
          </>
        )}
      </nav>

      {/* User footer */}
      {user && (
        <div className="px-3 py-4 border-t border-border-subtle">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-white">
                {getInitials(user.full_name, user.email)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">
                {user.full_name || user.email}
              </p>
              <p className="text-xs text-text-muted truncate">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="text-text-muted hover:text-danger transition-colors p-1"
              title="Sign out"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export const MobileSidebarToggle: React.FC = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="lg:hidden text-text-secondary hover:text-text-primary"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-64">
            <NavSidebar mobile onClose={() => setOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
};
