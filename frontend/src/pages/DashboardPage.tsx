import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Upload, Target, Briefcase, FileText, Zap } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useResume } from '../hooks/useResume';
import { AppLayout } from '../layouts/Layouts';
import { Card } from '../components/ui/index';
import { getGreeting, getFirstName, formatDateShort } from '../utils/format.utils';

const StatCard: React.FC<{ icon: React.ReactNode; label: string; value: string | number; color?: string }> = ({ icon, label, value, color = '#6366F1' }) => (
  <div className="glass-card p-5 flex items-center gap-4 card-shadow">
    <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
      style={{ backgroundColor: color + '20', border: `1px solid ${color}30` }}>
      <div style={{ color }}>{icon}</div>
    </div>
    <div>
      <p className="text-2xl font-bold font-mono text-text-primary">{value}</p>
      <p className="text-xs text-text-muted mt-0.5">{label}</p>
    </div>
  </div>
);

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { currentResumeId, currentResumeFilename } = useResume();

  const storedAts = localStorage.getItem('resumeiq_last_ats');
  const storedMatch = localStorage.getItem('resumeiq_last_match');
  const storedSkills = localStorage.getItem('resumeiq_last_skills');

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">
            {getGreeting()}, {getFirstName(user?.full_name, user?.email ?? '')} 👋
          </h1>
          <p className="text-text-muted text-sm mt-1">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</p>
        </div>

        {!currentResumeId ? (
          /* Empty state */
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="glass-card p-16 flex flex-col items-center gap-6 text-center">
            <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center">
              <FileText size={32} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-text-primary">Upload your first resume</h2>
              <p className="text-text-muted text-sm mt-2 max-w-sm">Get ATS scoring, job matching, interview prep, and a personalized career roadmap.</p>
            </div>
            <Link to="/upload" className="flex items-center gap-2 px-6 py-3 gradient-bg text-white font-medium rounded-sm hover:opacity-90 transition-opacity text-sm">
              <Upload size={16} /> Upload Resume
            </Link>
          </motion.div>
        ) : (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <StatCard icon={<FileText size={18} />} label="Resume loaded" value={currentResumeFilename ? '1' : '—'} color="#6366F1" />
              <StatCard icon={<Target size={18} />} label="ATS Score" value={storedAts ? `${storedAts}%` : '—'} color="#22C55E" />
              <StatCard icon={<Briefcase size={18} />} label="Job Match" value={storedMatch ? `${storedMatch}%` : '—'} color="#8B5CF6" />
              <StatCard icon={<Zap size={18} />} label="Skills Found" value={storedSkills || '—'} color="#38BDF8" />
            </div>

            {/* Resume info */}
            {currentResumeFilename && (
              <Card className="mb-6">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <FileText size={20} className="text-primary" />
                    <div>
                      <p className="font-medium text-text-primary">{currentResumeFilename}</p>
                      <p className="text-xs text-text-muted">Active resume</p>
                    </div>
                  </div>
                  <Link to="/upload" className="text-xs text-text-muted hover:text-primary transition-colors border border-border-subtle rounded-sm px-3 py-1.5">
                    Upload New
                  </Link>
                </div>
              </Card>
            )}

            {/* Quick Actions */}
            <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                { to: `/analysis/${currentResumeId}`, icon: <Zap size={20} />, title: 'View Analysis', desc: 'Skills, experience & education breakdown', color: '#6366F1' },
                { to: `/ats/${currentResumeId}`, icon: <Target size={20} />, title: 'ATS Score', desc: 'See your score and section breakdown', color: '#22C55E' },
                { to: `/job-match/${currentResumeId}`, icon: <Briefcase size={20} />, title: 'Match a Job', desc: 'Paste a job description to check fit', color: '#8B5CF6' },
              ].map((action, i) => (
                <Link key={i} to={action.to} className="glass-card p-5 hover:border-primary/30 transition-all group">
                  <div className="w-9 h-9 rounded-lg mb-3 flex items-center justify-center"
                    style={{ backgroundColor: action.color + '20', color: action.color }}>
                    {action.icon}
                  </div>
                  <h3 className="font-medium text-text-primary text-sm group-hover:text-primary transition-colors">{action.title}</h3>
                  <p className="text-xs text-text-muted mt-1">{action.desc}</p>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
};
