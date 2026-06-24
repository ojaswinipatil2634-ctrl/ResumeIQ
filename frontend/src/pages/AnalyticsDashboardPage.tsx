import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, FileText, Target, Zap, AlertCircle, TrendingUp } from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell,
} from 'recharts';
import { getDashboardStats } from '../services/dashboard.service';
import type { DashboardStats } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton } from '../components/ui/index';
import { scoreToColor } from '../utils/score.utils';
import { titleCase } from '../utils/format.utils';

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div className="bg-bg-elevated border border-border-subtle rounded-md px-3 py-2 text-xs shadow-lg">
        <p className="text-text-muted mb-1">{label}</p>
        <p className="font-medium text-primary">{payload[0].value} uploads</p>
      </div>
    );
  }
  return null;
};

export const AnalyticsDashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true); setError(null);
    getDashboardStats()
      .then(setData)
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load analytics.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const avgColor = data?.average_ats_score != null ? scoreToColor(data.average_ats_score) : '#A1A1AA';

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Analytics</h1>
          <p className="text-text-muted text-sm mt-1">Platform-wide usage and resume statistics.</p>
        </div>

        {loading ? (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
            </div>
            <Skeleton className="h-64" />
            <Skeleton className="h-64" />
          </div>
        ) : error ? (
          <div className="flex items-start gap-3 p-6 bg-danger/10 border border-danger/20 rounded-lg">
            <AlertCircle size={20} className="text-danger flex-shrink-0" />
            <div>
              <p className="text-danger">{error}</p>
              <button onClick={load} className="text-sm text-text-muted hover:text-text-primary mt-2 underline">Try Again</button>
            </div>
          </div>
        ) : data ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-6">
            {/* Stat cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { icon: <Users size={18} />, label: 'Total Users', value: data.total_users, color: '#6366F1' },
                { icon: <FileText size={18} />, label: 'Total Resumes', value: data.total_resumes, color: '#8B5CF6' },
                {
                  icon: <Target size={18} />,
                  label: 'Avg ATS Score',
                  value: data.average_ats_score != null ? `${data.average_ats_score.toFixed(1)}` : '—',
                  color: avgColor,
                },
                { icon: <Zap size={18} />, label: 'Skills Tracked', value: data.most_common_skills.length, color: '#38BDF8' },
              ].map((stat, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07 }}
                  className="glass-card p-5 flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: stat.color + '20', color: stat.color, border: `1px solid ${stat.color}30` }}>
                    {stat.icon}
                  </div>
                  <div>
                    <p className="text-xl font-bold font-mono text-text-primary">{stat.value}</p>
                    <p className="text-xs text-text-muted">{stat.label}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Upload trends */}
            {data.upload_trends.length > 0 ? (
              <Card>
                <div className="flex items-center gap-2 mb-6">
                  <TrendingUp size={16} className="text-primary" />
                  <h2 className="font-semibold text-text-primary">Upload Trends</h2>
                </div>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={data.upload_trends} margin={{ top: 4, right: 8, left: -24, bottom: 0 }}>
                    <defs>
                      <linearGradient id="uploadGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" tick={{ fill: '#52525B', fontSize: 11 }} tickLine={false} axisLine={false} />
                    <YAxis tick={{ fill: '#52525B', fontSize: 11 }} tickLine={false} axisLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="count" stroke="#6366F1" strokeWidth={2}
                      fill="url(#uploadGrad)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            ) : (
              <Card className="flex flex-col items-center justify-center py-12 gap-3 text-center">
                <TrendingUp size={32} className="text-text-muted" />
                <p className="text-text-muted text-sm">No upload data yet. Upload and analyse your first resume to start tracking.</p>
              </Card>
            )}

            {/* Top skills */}
            {data.most_common_skills.length > 0 && (
              <Card>
                <h2 className="font-semibold text-text-primary mb-6">Most Common Skills</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    layout="vertical"
                    data={data.most_common_skills.slice(0, 10).map((s, i) => ({ skill: s, count: 10 - i }))}
                    margin={{ top: 0, right: 8, left: 8, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#6366F1" />
                        <stop offset="100%" stopColor="#8B5CF6" />
                      </linearGradient>
                    </defs>
                    <XAxis type="number" hide />
                    <YAxis type="category" dataKey="skill" tick={{ fill: '#A1A1AA', fontSize: 12 }} tickLine={false} axisLine={false} width={100} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                      content={({ active, payload }) =>
                        active && payload?.length ? (
                          <div className="bg-bg-elevated border border-border-subtle rounded-md px-3 py-2 text-xs">
                            <p className="text-primary font-medium">{payload[0].payload.skill}</p>
                          </div>
                        ) : null
                      }
                    />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {data.most_common_skills.slice(0, 10).map((_, i) => (
                        <Cell key={i} fill="url(#barGrad)" />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            )}

            {/* Top job titles */}
            {data.top_job_titles.length > 0 && (
              <Card>
                <h2 className="font-semibold text-text-primary mb-4">Top Job Titles</h2>
                <div className="flex flex-col gap-1">
                  {data.top_job_titles.map((title, i) => (
                    <div key={title} className="flex items-center gap-4 py-2.5 relative">
                      <div
                        className="absolute inset-0 rounded opacity-40"
                        style={{ width: `${100 - i * 15}%`, backgroundColor: '#6366F110' }}
                      />
                      <span className="relative text-xs font-mono text-text-muted w-5">{i + 1}</span>
                      <span className="relative text-sm text-text-secondary">{titleCase(title)}</span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  );
};
