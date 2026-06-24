import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { ScoreRing } from '../components/ScoreRing';

const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen bg-bg-base flex">
    {/* Left panel */}
    <div className="hidden lg:flex flex-col items-center justify-center w-[45%] p-12"
      style={{ background: 'linear-gradient(135deg, #4338CA 0%, #6366F1 40%, #8B5CF6 100%)' }}>
      <div className="flex flex-col items-center gap-8 text-white text-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
            <Sparkles size={20} className="text-white" />
          </div>
          <span className="text-2xl font-bold tracking-tight">ResumeIQ</span>
        </div>
        <blockquote className="text-xl font-medium leading-relaxed max-w-xs opacity-90">
          "Understand your resume.<br />Land the role."
        </blockquote>
        <div className="mt-4 opacity-90">
          <ScoreRing score={82} size={140} grade="B+" label="Your potential score" animate={false} />
        </div>
      </div>
    </div>
    {/* Right panel */}
    <div className="flex-1 flex items-center justify-center p-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }} className="w-full max-w-md">
        {children}
      </motion.div>
    </div>
  </div>
);

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Incorrect email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h1 className="text-2xl font-bold text-text-primary mb-2">Welcome back</h1>
      <p className="text-text-secondary text-sm mb-8">Sign in to your ResumeIQ account.</p>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com" icon={<Mail size={16} />} required />
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-text-secondary">Password</label>
          <div className="relative">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
              <Lock size={16} />
            </div>
            <input type={showPw ? 'text' : 'password'} value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full bg-bg-elevated border border-border-subtle rounded-sm px-3 py-2.5 pl-10 pr-10 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              placeholder="••••••••" required />
            <button type="button" onClick={() => setShowPw(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors">
              {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
        {error && <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-sm px-3 py-2">{error}</p>}
        <Button type="submit" fullWidth loading={loading} size="lg" className="mt-2">Sign In</Button>
      </form>
      <p className="text-center text-sm text-text-muted mt-6">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary hover:underline">Register →</Link>
      </p>
    </AuthLayout>
  );
};

const passwordStrength = (pw: string): { label: string; color: string; width: string } => {
  const len = pw.length;
  const hasUpper = /[A-Z]/.test(pw);
  const hasNum = /\d/.test(pw);
  const score = (len >= 8 ? 1 : 0) + (len >= 12 ? 1 : 0) + (hasUpper ? 1 : 0) + (hasNum ? 1 : 0);
  if (!pw) return { label: '', color: '', width: '0%' };
  if (score <= 1) return { label: 'Weak', color: '#EF4444', width: '33%' };
  if (score <= 3) return { label: 'Fair', color: '#F59E0B', width: '66%' };
  return { label: 'Strong', color: '#22C55E', width: '100%' };
};

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const strength = passwordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password, fullName);
      navigate('/dashboard');
    } catch (err: any) {
      const status = err.response?.status;
      if (status === 409) setError('An account with this email already exists.');
      else setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h1 className="text-2xl font-bold text-text-primary mb-2">Create your account</h1>
      <p className="text-text-secondary text-sm mb-8">Start analysing your resume for free.</p>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input label="Full Name" type="text" value={fullName} onChange={e => setFullName(e.target.value)}
          placeholder="Jane Smith" required />
        <Input label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com" icon={<Mail size={16} />} required />
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-text-secondary">Password</label>
          <div className="relative">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
              <Lock size={16} />
            </div>
            <input type={showPw ? 'text' : 'password'} value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full bg-bg-elevated border border-border-subtle rounded-sm px-3 py-2.5 pl-10 pr-10 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              placeholder="••••••••" required minLength={8} />
            <button type="button" onClick={() => setShowPw(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors">
              {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {password && (
            <div className="flex items-center gap-2 mt-1">
              <div className="flex-1 h-1 bg-bg-elevated rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-300"
                  style={{ width: strength.width, backgroundColor: strength.color }} />
              </div>
              <span className="text-xs font-medium" style={{ color: strength.color }}>{strength.label}</span>
            </div>
          )}
        </div>
        {error && <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-sm px-3 py-2">{error}</p>}
        <Button type="submit" fullWidth loading={loading} size="lg" className="mt-2">Create Account</Button>
      </form>
      <p className="text-center text-sm text-text-muted mt-6">
        Already have an account?{' '}
        <Link to="/login" className="text-primary hover:underline">Sign in →</Link>
      </p>
    </AuthLayout>
  );
};
