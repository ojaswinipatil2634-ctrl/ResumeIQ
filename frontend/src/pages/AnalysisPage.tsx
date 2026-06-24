import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, AlertCircle, Briefcase, Building2, GraduationCap, BookOpen, CheckCircle, AlertTriangle } from 'lucide-react';
import { getAnalysis } from '../services/analysis.service';
import type { AnalysisResponse } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton, Badge } from '../components/ui/index';
import { useResume } from '../hooks/useResume';

const categoryColors: Record<string, string> = {
  'Programming Languages': '#6366F1',
  'Cloud & DevOps': '#38BDF8',
  'Data & ML': '#8B5CF6',
  'Databases': '#22C55E',
  'Web & Frontend': '#F59E0B',
  'Tools & Others': '#A1A1AA',
};

const getCategoryColor = (cat: string) => categoryColors[cat] || '#6366F1';

export const AnalysisPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const { currentResumeFilename } = useResume();
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    if (!resumeId) return;
    setLoading(true);
    setError(null);
    getAnalysis(parseInt(resumeId))
      .then(d => {
        setData(d);
        // Cache skill count
        localStorage.setItem('resumeiq_last_skills', d.skills.all_skills.length.toString());
      })
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load analysis.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [resumeId]);

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Resume Analysis</h1>
            {currentResumeFilename && <p className="text-text-muted text-sm mt-1">{currentResumeFilename}</p>}
          </div>
          <div className="flex gap-2">
            <Link to={`/ats/${resumeId}`} className="text-sm px-4 py-2 gradient-bg text-white rounded-sm hover:opacity-90 transition-opacity">ATS Score →</Link>
            <Link to={`/job-match/${resumeId}`} className="text-sm px-4 py-2 border border-border-accent text-text-secondary hover:text-text-primary rounded-sm transition-colors">Match a Job →</Link>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col gap-6">
            {[1, 2, 3].map(i => <Skeleton key={i} className="h-48" />)}
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
            {/* Skills */}
            <Card>
              <h2 className="font-semibold text-text-primary mb-1">Detected Skills</h2>
              <p className="text-sm text-text-muted mb-5">
                {data.skills.all_skills.length} skills across {Object.keys(data.skills.by_category).length} categories
              </p>
              {Object.keys(data.skills.by_category).length === 0 ? (
                <p className="text-text-muted text-sm">No skills detected in this resume.</p>
              ) : (
                <div className="flex flex-col gap-5">
                  {Object.entries(data.skills.by_category).map(([cat, skills]) => (
                    <div key={cat}>
                      <p className="text-xs font-medium uppercase tracking-wider mb-2" style={{ color: getCategoryColor(cat) }}>{cat}</p>
                      <div className="flex flex-wrap gap-2">
                        {skills.map(s => (
                          <span key={s} className="px-2.5 py-1 rounded-full text-xs font-medium"
                            style={{ backgroundColor: getCategoryColor(cat) + '20', color: getCategoryColor(cat), border: `1px solid ${getCategoryColor(cat)}30` }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Experience */}
            <Card>
              <h2 className="font-semibold text-text-primary mb-4">Experience</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div>
                  <p className="text-4xl font-bold font-mono text-primary">{data.experience.years_of_experience ?? '?'}</p>
                  <p className="text-xs text-text-muted mt-1">Years of experience</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">Job Titles</p>
                  {data.experience.job_titles.length === 0 ? <p className="text-sm text-text-muted">None detected</p> : (
                    <ul className="flex flex-col gap-1.5">
                      {data.experience.job_titles.map(t => (
                        <li key={t} className="flex items-center gap-2 text-sm text-text-secondary">
                          <Briefcase size={12} className="text-text-muted flex-shrink-0" /> {t}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">Companies</p>
                  {data.experience.companies.length === 0 ? <p className="text-sm text-text-muted">None detected</p> : (
                    <ul className="flex flex-col gap-1.5">
                      {data.experience.companies.map(c => (
                        <li key={c} className="flex items-center gap-2 text-sm text-text-secondary">
                          <Building2 size={12} className="text-text-muted flex-shrink-0" /> {c}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
              {data.experience.keywords.length > 0 && (
                <div className="mt-5 pt-5 border-t border-border-subtle">
                  <p className="text-xs text-text-muted mb-2">Action keywords found</p>
                  <div className="flex flex-wrap gap-1.5">
                    {data.experience.keywords.map(k => (
                      <span key={k} className="px-2 py-0.5 rounded text-xs bg-success/10 text-success border border-success/20">{k}</span>
                    ))}
                  </div>
                </div>
              )}
            </Card>

            {/* Education */}
            <Card>
              <h2 className="font-semibold text-text-primary mb-4">Education</h2>
              <div className="flex flex-col gap-3">
                {data.education.degrees.map((d, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <GraduationCap size={16} className="text-text-muted mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="text-sm text-text-secondary">{d}</span>
                      {data.education.institutions[i] && <span className="text-xs text-text-muted ml-2">— {data.education.institutions[i]}</span>}
                    </div>
                  </div>
                ))}
                {data.education.fields_of_study.map((f, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <BookOpen size={14} className="text-text-muted flex-shrink-0" />
                    <span className="text-xs italic text-text-secondary">{f}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Insights */}
            {data.career_insights.length > 0 && (
              <Card glow>
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles size={18} className="text-primary" />
                  <h2 className="font-semibold text-text-primary">Career Insights</h2>
                </div>
                <ul className="flex flex-col gap-2">
                  {data.career_insights.map((ins, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                      <CheckCircle size={14} className="text-success mt-0.5 flex-shrink-0" /> {ins}
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {/* Suggestions */}
            {data.improvement_suggestions.length > 0 && (
              <Card className="border-warning/20">
                <div className="flex items-center gap-2 mb-4">
                  <AlertTriangle size={18} className="text-warning" />
                  <h2 className="font-semibold text-text-primary">Improvement Suggestions</h2>
                </div>
                <ul className="flex flex-col gap-2">
                  {data.improvement_suggestions.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                      <AlertTriangle size={14} className="text-warning mt-0.5 flex-shrink-0" /> {s}
                    </li>
                  ))}
                </ul>
              </Card>
            )}
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  );
};
