import api from './api';
import type { AuthResponse, User } from '../types/api.types';

export const register = async (
  email: string,
  password: string,
  full_name: string
): Promise<AuthResponse> => {
  const res = await api.post<AuthResponse>('/api/auth/register', { email, password, full_name });
  return res.data;
};

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const res = await api.post<AuthResponse>('/api/auth/login', { email, password });
  return res.data;
};

export const getMe = async (): Promise<User> => {
  const res = await api.get<User>('/api/auth/me');
  return res.data;
};
