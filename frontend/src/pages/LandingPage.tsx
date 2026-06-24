import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Target, Briefcase, MessageSquare, ArrowRight, CheckCircle, Upload, Zap } from 'lucide-react';
import { ScoreRing } from '../components/ScoreRing';

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
};

const stagger = { show: { transition: { staggerChildren: 0.15 } } };

export const LandingPage: React.FC = () => {
  return (
    <div className="bg-bg-base text-text-primary overflow-x-hidden">
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 pb-16">
        {/* Background orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full opacity-10"
            style={{ background: 'radial-gradient(circle, #6366F1 0%, transparent 70%)' }} />
          <div className="absolute top-1/3 left-1/4 w-64 h-64 rounded-full opacity-5 animate-spin-slow"
            style={{ background: 'radial-gradient(circle, #8B5CF6 0%, transparent 70%)' }} />
        </div>

        <div className="relative max-w-5xl mx-auto text-center">
          <motion.div variants={stagger} initial="hidden" animate="show" className="flex flex-col items-center gap-6">
            <motion.div variants={fadeUp}>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20 mb-4">
                <Zap size={12} /> AI-powered resume intelligence
              </span>
            </motion.div>

            <motion.h1 variants={fadeUp} className="text-5xl md:text-6xl font-extrabold leading-tight tracking-tight max-w-3xl">
              Your resume,{' '}
              <span className="gradient-text">scored before they ever see you.</span>
            </motion.h1>

            <motion.p variants={fadeUp} className="text-lg text-text-secondary max-w-xl leading-relaxed">
              ResumeIQ analyses your resume against real ATS systems, matches it to job descriptions, and tells you exactly what to fix.
            </motion.p>

            <motion.div variants={fadeUp} className="flex flex-col sm:flex-row items-center gap-3 mt-2">
              <Link to="/register" className="flex items-center gap-2 px-6 py-3 gradient-bg text-white font-medium rounded-sm hover:opacity-90 transition-opacity text-sm">
                Analyze My Resume <ArrowRight size={16} />
              </Link>
              <a href="#how-it-works" className="flex items-center gap-2 px-6 py-3 border border-border-accent text-text-secondary hover:text-text-primary hover:border-border-accent rounded-sm transition-all text-sm">
                See How It Works
              </a>
            </motion.div>

            <motion.div variants={fadeUp} className="mt-8 animate-float">
              <ScoreRing score={73} size={160} grade="B" label="ATS Score" animate={false} />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────── */}
      <section className="py-24 px-6 border-t border-border-subtle">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: <Target size={24} className="text-primary" />, title: 'ATS Scoring', desc: 'Know your score before you apply. See exactly which sections need work.' },
              { icon: <Briefcase size={24} className="text-secondary" />, title: 'Job Matching', desc: 'See exactly how you fit any role with skill-by-skill gap analysis.' },
              { icon: <MessageSquare size={24} className="text-info" />, title: 'Interview Prep', desc: 'Walk in with the right answers ready. Questions tailored to your resume.' },
            ].map((f, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.5 }}
                className="glass-card p-6 flex flex-col gap-4"
              >
                <div className="w-10 h-10 rounded-lg bg-bg-elevated flex items-center justify-center border border-border-subtle">
                  {f.icon}
                </div>
                <h3 className="font-semibold text-text-primary">{f.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────────────── */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Three steps to a stronger resume</h2>
          <p className="text-text-secondary mb-16">No fluff, no guesswork. Just clear, actionable feedback.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {[
              { num: '01', icon: <Upload size={28} />, title: 'Upload', desc: 'Drop your PDF or DOCX resume. We extract and parse every section automatically.' },
              { num: '02', icon: <Zap size={28} />, title: 'Analyze', desc: 'Our engine scores your ATS compatibility, skills, experience, and structure.' },
              { num: '03', icon: <CheckCircle size={28} />, title: 'Improve', desc: 'Get a personalized roadmap — what to fix, what to add, and how to stand out.' },
            ].map((step, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.15, duration: 0.5 }}
                className="flex flex-col items-center gap-4 text-center"
              >
                <div className="w-16 h-16 rounded-xl gradient-bg flex items-center justify-center text-white glow-primary">
                  {step.icon}
                </div>
                <div className="text-xs font-mono text-text-muted">{step.num}</div>
                <h3 className="font-semibold text-lg">{step.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ATS Preview ──────────────────────────────────────────────── */}
      <section className="py-24 px-6 border-t border-border-subtle">
        <div className="max-w-4xl mx-auto">
          <p className="text-center text-sm text-text-muted uppercase tracking-widest mb-4">ATS Scoring</p>
          <h2 className="text-3xl font-bold text-center mb-12">See what ATS systems actually look for</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-6 border-l-4 border-l-danger">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-text-muted">Before optimizing</span>
                <ScoreRing score={38} size={80} animate={false} />
              </div>
              {[['Contact Info', 40], ['Skills', 30], ['Experience', 35], ['Keywords', 20]].map(([k, v]) => (
                <div key={k as string} className="flex items-center gap-3 mt-2">
                  <span className="text-xs text-text-muted w-24 flex-shrink-0">{k}</span>
                  <div className="flex-1 h-1.5 bg-bg-elevated rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-danger" style={{ width: `${v}%` }} />
                  </div>
                  <span className="text-xs font-mono text-text-muted w-8 text-right">{v}</span>
                </div>
              ))}
            </div>
            <div className="glass-card p-6 border-l-4 border-l-success glow-primary">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-text-muted">After ResumeIQ</span>
                <ScoreRing score={88} size={80} animate={false} />
              </div>
              {[['Contact Info', 95], ['Skills', 90], ['Experience', 85], ['Keywords', 88]].map(([k, v]) => (
                <div key={k as string} className="flex items-center gap-3 mt-2">
                  <span className="text-xs text-text-muted w-24 flex-shrink-0">{k}</span>
                  <div className="flex-1 h-1.5 bg-bg-elevated rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-success" style={{ width: `${v}%` }} />
                  </div>
                  <span className="text-xs font-mono text-text-muted w-8 text-right">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Testimonials ─────────────────────────────────────────────── */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">What candidates are saying</h2>
          <div className="flex overflow-x-auto gap-4 pb-4 -mx-6 px-6 snap-x">
            {[
              { name: 'Alex Chen', role: 'Software Engineer', quote: "ResumeIQ told me I was missing Kubernetes from my DevOps resume — I added it and applied. Got 3 callbacks in a week." },
              { name: 'Maya Patel', role: 'Data Analyst', quote: "The ATS score breakdown showed me exactly which sections were hurting me. My contact rate doubled after fixing them." },
              { name: 'Jordan Smith', role: 'Product Manager', quote: "The interview prep questions were spot-on. Two of them came up in my actual interview. Landed the role at a Series B startup." },
            ].map((t, i) => (
              <div key={i} className="glass-card p-6 min-w-[300px] snap-start flex flex-col gap-4">
                <p className="text-sm text-text-secondary leading-relaxed italic">"{t.quote}"</p>
                <div className="flex items-center gap-3 mt-auto">
                  <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center">
                    <span className="text-xs font-bold text-white">{t.name.split(' ').map(n => n[0]).join('')}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text-primary">{t.name}</p>
                    <p className="text-xs text-text-muted">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pricing ──────────────────────────────────────────────────── */}
      <section className="py-24 px-6 border-t border-border-subtle">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-12">Simple pricing</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-8 flex flex-col gap-4">
              <h3 className="text-xl font-bold">Free</h3>
              <p className="text-3xl font-bold font-mono">$0</p>
              <ul className="flex flex-col gap-2 text-sm text-text-secondary mt-2">
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-success" /> Upload 1 resume</li>
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-success" /> Basic ATS scoring</li>
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-success" /> Resume analysis</li>
              </ul>
              <Link to="/register" className="mt-auto w-full text-center py-2.5 border border-border-accent rounded-sm text-sm text-text-secondary hover:text-text-primary hover:border-primary/50 transition-all">
                Get Started Free
              </Link>
            </div>
            <div className="glass-card p-8 flex flex-col gap-4 border-primary/30 glow-primary relative overflow-hidden">
              <span className="absolute top-4 right-4 px-2.5 py-0.5 text-xs font-medium bg-warning/20 text-warning border border-warning/30 rounded-full">Coming Soon</span>
              <h3 className="text-xl font-bold gradient-text">Pro</h3>
              <p className="text-3xl font-bold font-mono">$9<span className="text-base text-text-muted">/mo</span></p>
              <ul className="flex flex-col gap-2 text-sm text-text-secondary mt-2">
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-primary" /> Unlimited resumes</li>
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-primary" /> Job matching</li>
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-primary" /> Interview prep</li>
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-primary" /> Career roadmap</li>
                <li className="flex items-center gap-2"><CheckCircle size={14} className="text-primary" /> Priority support</li>
              </ul>
              <button disabled className="mt-auto w-full py-2.5 gradient-bg text-white rounded-sm text-sm opacity-60 cursor-not-allowed">
                Coming Soon
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className="border-t border-border-subtle py-12 px-6">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded gradient-bg flex items-center justify-center">
              <Zap size={12} className="text-white" />
            </div>
            <span className="font-bold text-text-primary">ResumeIQ</span>
          </div>
          <p className="text-xs text-text-muted">Your resume, intelligently understood.</p>
          <p className="text-xs text-text-muted">© {new Date().getFullYear()} ResumeIQ. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};
