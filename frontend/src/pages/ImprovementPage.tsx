import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, ChevronDown, ChevronUp, AlertTriangle, CheckCircle, Lightbulb } from 'lucide-react';
import { getImprovements } from '../services/improvement.service';
import type { ImprovementResponse, ImprovementSection } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton } from '../components/ui/index';
import { qualityToColor } from '../utils/score.utils';
import { useToast } from '../hooks/useToast';

const SectionCard: React.FC<{ section: ImprovementSection; defaultOpen?: boolean }> = ({ section, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);
  const isGood = section.issues.some(i => i.toLowerCase().includes('good') || i.toLowerCase().includes('no ') && i.toLowerCase().includes('detected'));
  const issueCount = section.issues.filter(i => !i.toLowerCase().includes('good') && !(i.toLowerCase().includes('no ') && i.toLowerCase().includes('detected'))).length;

  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between p-5 text-left hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${isGood ? 'bg-success' : issueCount > 0 ? 'bg-warning' : 'bg-text-muted'}`} />
          <span className="font-medium text-text-primary">{section.area}</span>
          {issueCount > 0 && (
            <span className="px-2 py-0.5 rounded-full text-xs bg-warning/10 text-warning border border-warning/20">
              {issueCount} issue{issueCount > 1 ? 's' : ''}
            </span>
          )}
          {isGood && (
            <span className="px-2 py-0.5 rounded-full text-xs bg-success/10 text-success border border-success/20">
              Looks good
            </span>
          )}
        </div>
        {open ? <ChevronUp size={16} className="text-text-muted" /> : <ChevronDown size={16} className="text-text-muted" />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-border-subtle pt-4 flex flex-col gap-4">
              {section.issues.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">Issues</p>
                  <ul className="flex flex-col gap-1.5">
                    {section.issues.map((issue, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        {issue.toLowerCase().includes('good') || (issue.toLowerCase().includes('no ') && issue.toLowerCase().includes('detected'))
                          ? <CheckCircle size={14} className="text-success mt-0.5 flex-shrink-0" />
                          : <AlertTriangle size={14} className="text-warning mt-0.5 flex-shrink-0" />}
                        <span className="text-text-secondary">{issue}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {section.tips.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">How to Fix</p>
                  <ul className="flex flex-col gap-1.5">
                    {section.tips.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Lightbulb size={14} className="text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-text-secondary">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export const ImprovementPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const { show } = useToast();
  const [data, setData] = useState<ImprovementResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    if (!resumeId) return;
    setLoading(true); setError(null);
    getImprovements(parseInt(resumeId))
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load improvements.'))
      .then(d => { if (d) setData(d); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [resumeId]);

  const copyVerb = (verb: string) => {
    navigator.clipboard.writeText(verb);
    show(`Copied "${verb}"`, 'success');
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Resume Improvement</h1>
          <p className="text-text-muted text-sm mt-1">Actionable suggestions to make your resume stand out.</p>
        </div>

        {loading ? (
          <div className="flex flex-col gap-4">{[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-16" />)}</div>
        ) : error ? (
          <div className="flex items-start gap-3 p-6 bg-danger/10 border border-danger/20 rounded-lg">
            <AlertCircle size={20} className="text-danger flex-shrink-0" />
            <div>
              <p className="text-danger">{error}</p>
              <button onClick={load} className="text-sm text-text-muted hover:text-text-primary mt-2 underline">Try Again</button>
            </div>
          </div>
        ) : data ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-8">
            {/* Quality badge */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-text-muted">Overall Quality:</span>
              <span className="px-4 py-1.5 rounded-full text-sm font-semibold"
                style={{
                  backgroundColor: qualityToColor(data.overall_quality) + '20',
                  color: qualityToColor(data.overall_quality),
                  border: `1px solid ${qualityToColor(data.overall_quality)}40`
                }}>
                {data.overall_quality}
              </span>
            </div>

            {/* Sections */}
            <div>
              <h2 className="font-semibold text-text-primary mb-4">Section Analysis</h2>
              <div className="flex flex-col gap-3">
                {data.sections.map((section, i) => (
                  <motion.div key={section.area} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}>
                    <SectionCard section={section} defaultOpen={i === 0} />
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Action verbs */}
            {data.stronger_action_verbs.length > 0 && (
              <Card>
                <h2 className="font-semibold text-text-primary mb-2">Replace Weak Verbs With These</h2>
                <p className="text-xs text-text-muted mb-4">Click any verb to copy it.</p>
                <div className="flex flex-wrap gap-2">
                  {data.stronger_action_verbs.map(verb => (
                    <button key={verb} onClick={() => copyVerb(verb)}
                      className="px-3 py-1.5 rounded-sm text-sm font-medium bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 active:scale-95 transition-all">
                      {verb}
                    </button>
                  ))}
                </div>
              </Card>
            )}

            {/* Writing tips */}
            {data.writing_tips.length > 0 && (
              <Card>
                <h2 className="font-semibold text-text-primary mb-4">Writing Tips</h2>
                <ol className="flex flex-col gap-0">
                  {data.writing_tips.map((tip, i) => (
                    <li key={i} className={`flex items-start gap-4 py-3 ${i % 2 === 0 ? 'bg-transparent' : 'bg-white/[0.02]'} px-2 rounded`}>
                      <span className="text-xs font-mono text-text-muted w-5 flex-shrink-0 mt-0.5">{String(i + 1).padStart(2, '0')}</span>
                      <span className="text-sm text-text-secondary">{tip}</span>
                    </li>
                  ))}
                </ol>
              </Card>
            )}
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  );
};
