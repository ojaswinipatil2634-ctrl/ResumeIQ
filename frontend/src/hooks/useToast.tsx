import { useState, useCallback, useContext, createContext } from 'react';
import React from 'react';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

interface ToastContextValue {
  toasts: Toast[];
  show: (message: string, type?: 'success' | 'error' | 'info') => void;
  dismiss: (id: number) => void;
}

export const ToastContext = createContext<ToastContextValue>({} as ToastContextValue);

let nextId = 0;

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = ++nextId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => dismiss(id), 3000);
  }, [dismiss]);

  return (
    <ToastContext.Provider value={{ toasts, show, dismiss }}>
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = () => useContext(ToastContext);
