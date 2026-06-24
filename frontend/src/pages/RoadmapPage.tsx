import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertCircle, Award, BookOpen, ChevronRight, Clock } from 'lucide-react';
import { getRoadmap } from '../services/roadmap.service';
import type { CareerRoadmapResponse, RoadmapStep } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton } from '../components/ui/index';

const levelColor: Record<string, string> = {
  Junior: '#38BDF8',
  'Mid-Level': '#8B5CF6',
  Senior: '#22C55E',
};

const RoadmapStepCard: React.FC<{ step: RoadmapStep; isLast: boolean; index: number }> = ({ step, isLast, index }) => (
  <motion.div
    initial={{ opacity: 0, x: -16 }}
    whileInView={{ opacity: 1, x: 0 }}
    viewport={{ once: true }}
    transition={{ delay: index * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    className="flex gap-4"
  >
    {/* Timeline spine */}
    <div className="flex flex-col items-center flex-shrink-0">
      <div className="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-white text-sm font-bold glow-primary">
        {step.order}
      </div>
      {!isLast && <div className="w-0.5 flex-1 mt-2 mb-0 bg-border-subtle min-h-[32px]" />}
    </div>

    {/* Card */}
    <div className="glass-card p-5 flex-1 mb-4">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <h3 className="font-semibold text-text-primary">{step.title}</h3>
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-bg-elevated border border-border-subtle text-text-muted flex-shrink-0">
          <Clock size={11} /> {step.estimated_time}
        </span>
      </div>
      <p className="text-sm text-text-secondary mt-2 leading-relaxed">{step.description}</p>
    </div>
  </motion.div>
);

export const RoadmapPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const [data, setData] = useState<CareerRoadmapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    if (!resumeId) return;
    setLoading(true); setError(null);
    getRoadmap(parseInt(resumeId))
      .then(setData)
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load roadmap.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [resumeId]);

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Career Roadmap</h1>
          <p className="text-text-muted text-sm mt-1">Your personalised path to the next level.</p>
        </div>

        {loading ? (
          <div className="flex flex-col gap-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-32" />)}</div>
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
            {/* Header: level + target */}
            <Card glow>
              <div className="flex items-center gap-4 flex-wrap">
                <span className="px-3 py-1.5 rounded-full text-sm font-semibold"
                  style={{
                    backgroundColor: (levelColor[data.current_level] || '#6366F1') + '20',
                    color: levelColor[data.current_level] || '#6366F1',
                    border: `1px solid ${(levelColor[data.current_level] || '#6366F1')}40`,
                  }}>
                  {data.current_level}
                </span>
                <ChevronRight size={16} className="text-text-muted" />
                <div>
                  <p className="text-xs text-text-muted">Your next target</p>
                  <p className="font-semibold text-text-primary">{data.target_role}</p>
                </div>
              </div>
            </Card>

            {/* Three info columns */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Technologies */}
              <Card>
                <h3 className="text-sm font-semibold text-text-primary mb-3">Technologies to Learn</h3>
                <div className="flex flex-wrap gap-1.5">
                  {data.recommended_technologies.map(t => (
                    <span key={t} className="px-2.5 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20">{t}</span>
                  ))}
                </div>
              </Card>

              {/* Certifications */}
              <Card>
                <h3 className="text-sm font-semibold text-text-primary mb-3">Certifications</h3>
                <ul className="flex flex-col gap-2">
                  {data.certifications.map(c => (
                    <li key={c} className="flex items-start gap-2 text-xs text-text-secondary">
                      <Award size={13} className="text-warning mt-0.5 flex-shrink-0" /> {c}
                    </li>
                  ))}
                </ul>
              </Card>

              {/* Courses */}
              <Card>
                <h3 className="text-sm font-semibold text-text-primary mb-3">Recommended Courses</h3>
                <ul className="flex flex-col gap-2">
                  {data.courses.map(c => (
                    <li key={c} className="flex items-start gap-2 text-xs text-text-secondary">
                      <BookOpen size={13} className="text-info mt-0.5 flex-shrink-0" /> {c}
                    </li>
                  ))}
                </ul>
              </Card>
            </div>

            {/* Next roles */}
            {data.next_roles.length > 0 && (
              <div>
                <h2 className="font-semibold text-text-primary mb-4">Career Progression</h2>
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                  {data.next_roles.map((role, i) => (
                    <React.Fragment key={role}>
                      <div className="flex-shrink-0 px-4 py-2.5 glass-card text-sm text-text-secondary whitespace-nowrap hover:text-text-primary transition-colors">
                        {role}
                      </div>
                      {i < data.next_roles.length - 1 && (
                        <ChevronRight size={16} className="text-text-muted flex-shrink-0" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}

            {/* Learning roadmap timeline */}
            {data.learning_roadmap.length > 0 && (
              <div>
                <h2 className="font-semibold text-text-primary mb-6">Learning Roadmap</h2>
                <div className="flex flex-col">
                  {data.learning_roadmap.map((step, i) => (
                    <RoadmapStepCard
                      key={step.order}
                      step={step}
                      isLast={i === data.learning_roadmap.length - 1}
                      index={i}
                    />
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  );
};
