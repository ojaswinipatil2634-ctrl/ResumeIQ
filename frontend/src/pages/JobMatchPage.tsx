import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, X, AlertCircle, Lightbulb, Loader2 } from 'lucide-react';
import { matchJob } from '../services/jobMatch.service';
import type { JobMatchResponse } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card } from '../components/ui/index';
import { ScoreRing } from '../components/ScoreRing';
import { matchGradeToColor } from '../utils/score.utils';

export const JobMatchPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const [jd, setJd] = useState('');
  const [data, setData] = useState<JobMatchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isValid = jd.trim().length >= 50;

  const handleMatch = async () => {
    if (!resumeId || !isValid) return;
    setLoading(true); setError('');
    try {
      const res = await matchJob(parseInt(resumeId), jd);
      setData(res);
      localStorage.setItem('resumeiq_last_match', Math.round(res.match_score).toString());
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Match failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const gradeColor = data ? matchGradeToColor(data.match_grade) : '#6366F1';

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Job Match</h1>
          <p className="text-text-muted text-sm mt-1">See how well your resume fits a specific role.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left — Input */}
          <Card className="flex flex-col gap-4">
            <h2 className="font-semibold text-text-primary">Paste a Job Description</h2>
            <div className="relative flex-1">
              <textarea
                value={jd}
                onChange={e => setJd(e.target.value)}
                rows={14}
                placeholder="Paste the full job description here — include requirements, responsibilities, and skills…"
                className="w-full bg-bg-base border border-border-subtle rounded-md p-4 text-sm text-text-primary placeholder:text-text-muted resize-none focus:outline-none focus:border-primary transition-colors"
              />
              <span className={`absolute bottom-3 right-3 text-xs font-mono ${jd.length < 50 && jd.length > 0 ? 'text-danger' : 'text-text-muted'}`}>
                {jd.length} chars {jd.length < 50 ? `(${50 - jd.length} more needed)` : '✓'}
              </span>
            </div>
            {error && (
              <div className="flex items-center gap-2 text-sm text-danger bg-danger/10 border border-danger/20 rounded-md p-3">
                <AlertCircle size={16} /> {error}
              </div>
            )}
            <button
              onClick={handleMatch}
              disabled={!isValid || loading}
              className="flex items-center justify-center gap-2 w-full py-3 gradient-bg text-white text-sm font-medium rounded-sm hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? <><Loader2 size={16} className="animate-spin" /> Analysing…</> : 'Find My Match →'}
            </button>
          </Card>

          {/* Right — Results */}
          <div className="relative min-h-[400px]">
            {loading && (
              <div className="absolute inset-0 bg-bg-surface/80 backdrop-blur-sm rounded-lg flex items-center justify-center z-10">
                <div className="flex flex-col items-center gap-3">
                  <Loader2 size={32} className="animate-spin text-primary" />
                  <p className="text-sm text-text-muted">Matching your resume…</p>
                </div>
              </div>
            )}

            <AnimatePresence mode="wait">
              {!data && !loading ? (
                <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="h-full min-h-[400px] glass-card flex items-center justify-center p-8 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-bg-elevated border border-border-subtle flex items-center justify-center">
                      <span className="text-2xl">🎯</span>
                    </div>
                    <p className="text-text-muted text-sm">Paste a job description on the left to see how well your resume matches.</p>
                  </div>
                </motion.div>
              ) : data ? (
                <motion.div key="results" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col gap-4">
                  {/* Score */}
                  <Card className="flex flex-col items-center gap-4 py-6">
                    <ScoreRing score={data.match_score} size={160} label="Match Score" />
                    <span className="px-4 py-1.5 rounded-full text-sm font-medium"
                      style={{ backgroundColor: gradeColor + '20', color: gradeColor, border: `1px solid ${gradeColor}40` }}>
                      {data.match_grade}
                    </span>
                  </Card>

                  {/* Skill comparison */}
                  <Card>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-medium text-success uppercase tracking-wider mb-3">Matching Skills</p>
                        <div className="flex flex-wrap gap-1.5">
                          {data.matching_skills.length === 0
                            ? <p className="text-xs text-text-muted">None found</p>
                            : data.matching_skills.map(s => (
                              <span key={s} className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-success/10 text-success border border-success/20">
                                <CheckCircle size={10} /> {s}
                              </span>
                            ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-danger uppercase tracking-wider mb-3">Missing Skills</p>
                        <div className="flex flex-wrap gap-1.5">
                          {data.missing_skills.length === 0
                            ? <p className="text-xs text-text-muted">None!</p>
                            : data.missing_skills.map(s => (
                              <span key={s} className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-danger/10 text-danger border border-danger/20">
                                <X size={10} /> {s}
                              </span>
                            ))}
                        </div>
                      </div>
                    </div>
                  </Card>

                  {/* Keyword overlap */}
                  {Object.keys(data.keyword_overlap).length > 0 && (
                    <Card>
                      <h3 className="text-sm font-semibold text-text-primary mb-3">Keyword Overlap by Category</h3>
                      <div className="flex flex-col gap-3">
                        {Object.entries(data.keyword_overlap).map(([cat, skills]) => (
                          <div key={cat}>
                            <p className="text-xs text-text-muted mb-1.5">{cat}</p>
                            <div className="flex flex-wrap gap-1.5">
                              {skills.map(s => (
                                <span key={s} className="px-2 py-0.5 rounded text-xs bg-primary/10 text-primary border border-primary/20">{s}</span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>
                  )}

                  {/* Recommendations */}
                  {data.recommendations.length > 0 && (
                    <Card>
                      <h3 className="text-sm font-semibold text-text-primary mb-3">Recommendations</h3>
                      <div className="flex flex-col gap-2">
                        {data.recommendations.map((r, i) => (
                          <div key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                            <Lightbulb size={14} className="text-warning mt-0.5 flex-shrink-0" /> {r}
                          </div>
                        ))}
                      </div>
                    </Card>
                  )}
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
