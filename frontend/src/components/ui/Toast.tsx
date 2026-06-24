import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';
import { useToast } from '../../hooks/useToast';

const icons = {
  success: <CheckCircle size={16} className="text-success" />,
  error: <XCircle size={16} className="text-danger" />,
  info: <Info size={16} className="text-primary" />,
};

const borders = {
  success: 'border-l-success',
  error: 'border-l-danger',
  info: 'border-l-primary',
};

export const ToastContainer: React.FC = () => {
  const { toasts, dismiss } = useToast();

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2" aria-live="polite">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg border-l-4 ${borders[t.type]} bg-bg-elevated border border-border-subtle card-shadow min-w-[280px] max-w-[360px]`}
          >
            {icons[t.type]}
            <span className="flex-1 text-sm text-text-primary">{t.message}</span>
            <button onClick={() => dismiss(t.id)} className="text-text-muted hover:text-text-primary transition-colors">
              <X size={14} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
