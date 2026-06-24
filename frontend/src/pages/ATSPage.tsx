import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lightbulb, AlertCircle, AlertTriangle } from 'lucide-react';
import { getATSScore } from '../services/ats.service';
import type { ATSResponse } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton } from '../components/ui/index';
import { ScoreRing } from '../components/ScoreRing';
import { scoreToColor, scoreToLabel } from '../utils/score.utils';
import { prettifyKey } from '../utils/format.utils';

export const ATSPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const [data, setData] = useState<ATSResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    if (!resumeId) return;
    setLoading(true); setError(null);
    getATSScore(parseInt(resumeId))
      .then(d => {
        setData(d);
        localStorage.setItem('resumeiq_last_ats', Math.round(d.overall_score).toString());
      })
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load ATS score.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [resumeId]);

  const sortedSections = data
    ? Object.entries(data.section_scores).sort((a, b) => a[1] - b[1])
    : [];

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">ATS Score</h1>
          <p className="text-text-muted text-sm mt-1">How well your resume passes Applicant Tracking Systems.</p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Skeleton className="h-80" />
            <Skeleton className="h-80" />
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Score ring */}
              <Card className="flex flex-col items-center justify-center gap-4 py-8">
                <ScoreRing score={data.overall_score} size={200} strokeWidth={14} grade={data.grade} label="Overall ATS Score" />
                <div className="text-center">
                  <p className="text-lg font-semibold" style={{ color: scoreToColor(data.overall_score) }}>
                    {scoreToLabel(data.overall_score)}
                  </p>
                  <p className="text-xs text-text-muted mt-1">out of 100 points</p>
                </div>
              </Card>

              {/* Section breakdown */}
              <Card>
                <h2 className="font-semibold text-text-primary mb-5">Section Breakdown</h2>
                <div className="flex flex-col gap-4">
                  {sortedSections.map(([key, val], i) => {
                    const color = scoreToColor(val);
                    return (
                      <motion.div key={key} initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                        className="flex items-center gap-3">
                        <span className="text-xs text-text-secondary w-28 flex-shrink-0">{prettifyKey(key)}</span>
                        <div className="flex-1 h-2 bg-bg-base rounded-full overflow-hidden">
                          <motion.div className="h-full rounded-full"
                            initial={{ width: '0%' }} animate={{ width: `${val}%` }}
                            transition={{ duration: 0.8, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}
                            style={{ backgroundColor: color }} />
                        </div>
                        <span className="text-xs font-mono w-8 text-right" style={{ color }}>{Math.round(val)}</span>
                      </motion.div>
                    );
                  })}
                </div>
              </Card>
            </div>

            {/* Missing sections */}
            {data.missing_sections.length > 0 && (
              <div className="flex items-start gap-3 p-4 bg-danger/10 border border-danger/20 rounded-lg">
                <AlertTriangle size={18} className="text-danger flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-danger mb-1">Missing Sections</p>
                  <p className="text-sm text-text-secondary">{data.missing_sections.join(', ')}</p>
                </div>
              </div>
            )}

            {/* Suggestions */}
            <Card>
              <h2 className="font-semibold text-text-primary mb-4">Recommendations</h2>
              <div className="flex flex-col gap-3">
                {data.suggestions.map((s, i) => (
                  <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.07 }}
                    className="flex items-start gap-3 p-3 rounded-md bg-bg-elevated hover:bg-bg-elevated/80 transition-colors">
                    <div className="w-6 h-6 rounded gradient-bg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Lightbulb size={12} className="text-white" />
                    </div>
                    <p className="text-sm text-text-secondary">{s}</p>
                  </motion.div>
                ))}
              </div>
            </Card>
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  );
};
