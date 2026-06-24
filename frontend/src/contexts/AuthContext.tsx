import React, { createContext, useState, useEffect, useCallback } from 'react';
import type { User } from '../types/api.types';
import { login as loginService, register as registerService, getMe } from '../services/auth.service';
import { getToken, setToken, clearToken } from '../utils/storage.utils';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue>({} as AuthContextValue);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(getToken());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (storedToken) {
      getMe()
        .then(setUser)
        .catch(() => { clearToken(); setTokenState(null); })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await loginService(email, password);
    setToken(data.access_token);
    setTokenState(data.access_token);
    setUser(data.user);
  }, []);

  const register = useCallback(async (email: string, password: string, full_name: string) => {
    const data = await registerService(email, password, full_name);
    setToken(data.access_token);
    setTokenState(data.access_token);
    setUser(data.user);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
