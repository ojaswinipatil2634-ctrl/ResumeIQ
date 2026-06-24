import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle, LogOut } from 'lucide-react';
import { getMe } from '../services/auth.service';
import type { User } from '../types/api.types';
import { AppLayout } from '../layouts/Layouts';
import { Card, Skeleton } from '../components/ui/index';
import { useAuth } from '../hooks/useAuth';
import { getInitials, formatDate } from '../utils/format.utils';

export const ProfilePage: React.FC = () => {
  const { logout } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load profile.'))
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Profile</h1>
          <p className="text-text-muted text-sm mt-1">Your account details.</p>
        </div>

        {loading ? (
          <div className="flex flex-col gap-4">
            <Skeleton className="h-40" />
            <Skeleton className="h-32" />
          </div>
        ) : error ? (
          <div className="flex items-start gap-3 p-6 bg-danger/10 border border-danger/20 rounded-lg">
            <AlertCircle size={20} className="text-danger flex-shrink-0" />
            <p className="text-danger">{error}</p>
          </div>
        ) : user ? (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
            {/* Avatar card */}
            <Card className="flex flex-col items-center gap-4 py-8">
              <div className="w-20 h-20 rounded-full gradient-bg flex items-center justify-center glow-primary">
                <span className="text-2xl font-bold text-white">
                  {getInitials(user.full_name, user.email)}
                </span>
              </div>
              <div className="text-center">
                <h2 className="text-xl font-semibold text-text-primary">{user.full_name || '—'}</h2>
                <p className="text-text-muted text-sm mt-1">{user.email}</p>
              </div>
              {user.is_active && (
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-success/10 text-success border border-success/20">
                  <CheckCircle size={12} /> Active account
                </span>
              )}
            </Card>

            {/* Details */}
            <Card>
              <h3 className="font-semibold text-text-primary mb-4">Account Details</h3>
              <dl className="flex flex-col gap-4">
                {[
                  { label: 'Full Name', value: user.full_name || '—' },
                  { label: 'Email Address', value: user.email },
                  { label: 'Member Since', value: formatDate(user.created_at) },
                  { label: 'Account Status', value: user.is_active ? 'Active' : 'Inactive' },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between py-2 border-b border-border-subtle last:border-0">
                    <dt className="text-sm text-text-muted">{item.label}</dt>
                    <dd className="text-sm text-text-primary font-medium">{item.value}</dd>
                  </div>
                ))}
              </dl>
              <p className="text-xs text-text-muted mt-4 italic">Contact support to update your account details.</p>
            </Card>

            {/* Danger zone */}
            <Card className="border-danger/20">
              <h3 className="font-semibold text-text-primary mb-3">Danger Zone</h3>
              <p className="text-sm text-text-muted mb-4">Signing out will clear your session. You'll need to log in again.</p>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-sm text-sm font-medium text-danger border border-danger/30 hover:bg-danger/10 transition-colors"
              >
                <LogOut size={15} /> Sign Out
              </button>
            </Card>
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  );
};
