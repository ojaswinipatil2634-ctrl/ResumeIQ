import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, Code2, Users, FolderOpen, Star, Lightbulb, RotateCcw, CheckCircle } from 'lucide-react';
import { getInterviewQuestions } from '../services/interview.service';
import type { InterviewResponse } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton } from '../components/ui/index';

type TabKey = 'technical' | 'hr' | 'project' | 'behavioral';

const TABS: { key: TabKey; label: string; icon: React.ReactNode; hint: string }[] = [
  { key: 'technical', label: 'Technical', icon: <Code2 size={15} />, hint: 'Think out loud. Walk through your approach step by step. Explain trade-offs.' },
  { key: 'hr', label: 'HR', icon: <Users size={15} />, hint: 'Be authentic and specific. Research the company before your interview.' },
  { key: 'project', label: 'Project', icon: <FolderOpen size={15} />, hint: 'Cover: problem → solution → your role → outcome. Use real numbers if you have them.' },
  { key: 'behavioral', label: 'Behavioral', icon: <Star size={15} />, hint: 'Use the STAR format: Situation, Task, Action, Result.' },
];

const QuestionCard: React.FC<{ question: string; index: number; hint: string; category: TabKey }> = ({ question, index, hint }) => {
  const [flipped, setFlipped] = useState(false);
  const [reviewed, setReviewed] = useState(false);

  return (
    <div className={`flip-card h-40 ${flipped ? 'flipped' : ''} cursor-pointer`} onClick={() => setFlipped(v => !v)}>
      <div className="flip-card-inner">
        {/* Front */}
        <div className={`flip-card-front glass-card p-5 flex flex-col justify-between transition-opacity ${reviewed ? 'opacity-40' : ''}`}>
          <div className="flex items-start gap-3">
            <span className="text-xs font-mono text-text-muted flex-shrink-0 mt-0.5">Q{String(index + 1).padStart(2, '0')}</span>
            <p className="text-sm text-text-primary leading-relaxed">{question}</p>
          </div>
          <div className="flex items-center justify-between mt-3">
            <span className="text-xs text-text-muted flex items-center gap-1"><RotateCcw size={11} /> Click to flip</span>
            {!reviewed && (
              <button
                onClick={e => { e.stopPropagation(); setReviewed(true); }}
                className="text-xs text-text-muted hover:text-success transition-colors flex items-center gap-1"
              >
                <CheckCircle size={12} /> Mark reviewed
              </button>
            )}
            {reviewed && <span className="text-xs text-success flex items-center gap-1"><CheckCircle size={11} /> Reviewed</span>}
          </div>
        </div>
        {/* Back */}
        <div className="flip-card-back glass-card p-5 flex flex-col justify-center border-primary/30 bg-primary/5">
          <div className="flex items-start gap-3">
            <Lightbulb size={16} className="text-primary flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-medium text-primary mb-1">Preparation Tip</p>
              <p className="text-sm text-text-secondary leading-relaxed">{hint}</p>
            </div>
          </div>
          <span className="text-xs text-text-muted mt-4 flex items-center gap-1 self-end"><RotateCcw size={11} /> Click to flip back</span>
        </div>
      </div>
    </div>
  );
};

export const InterviewPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const [data, setData] = useState<InterviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('technical');

  const load = () => {
    if (!resumeId) return;
    setLoading(true); setError(null);
    getInterviewQuestions(parseInt(resumeId))
      .then(setData)
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load interview questions.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [resumeId]);

  const questionMap: Record<TabKey, string[]> = {
    technical: data?.technical_questions ?? [],
    hr: data?.hr_questions ?? [],
    project: data?.project_questions ?? [],
    behavioral: data?.behavioral_questions ?? [],
  };

  const activeHint = TABS.find(t => t.key === activeTab)?.hint ?? '';

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Interview Preparation</h1>
          <p className="text-text-muted text-sm mt-1">Questions tailored to your resume. Click any card to reveal the preparation tip.</p>
        </div>

        {loading ? (
          <div className="flex flex-col gap-4">{[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-40" />)}</div>
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
            {/* Tabs */}
            <div className="flex gap-1 p-1 bg-bg-elevated rounded-lg border border-border-subtle w-fit">
              {TABS.map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                    activeTab === tab.key
                      ? 'bg-primary text-white shadow-sm'
                      : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
                  }`}
                >
                  {tab.icon}
                  <span className="hidden sm:inline">{tab.label}</span>
                  <span className="text-xs opacity-60">({questionMap[tab.key].length})</span>
                </button>
              ))}
            </div>

            {/* Questions grid */}
            <AnimatePresence mode="wait">
              <motion.div key={activeTab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2 }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {questionMap[activeTab].length === 0 ? (
                  <p className="text-text-muted text-sm col-span-2 py-8 text-center">No questions in this category.</p>
                ) : (
                  questionMap[activeTab].map((q, i) => (
                    <QuestionCard key={i} question={q} index={i} hint={activeHint} category={activeTab} />
                  ))
                )}
              </motion.div>
            </AnimatePresence>

            {/* Prep tips */}
            {data.preparation_tips.length > 0 && (
              <Card className="border-primary/20">
                <div className="flex items-center gap-2 mb-4">
                  <Lightbulb size={16} className="text-primary" />
                  <h2 className="font-semibold text-text-primary">General Preparation Tips</h2>
                </div>
                <ol className="flex flex-col gap-2">
                  {data.preparation_tips.map((tip, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-text-secondary">
                      <span className="text-xs font-mono text-text-muted w-5 flex-shrink-0 mt-0.5">{i + 1}.</span>
                      {tip}
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
