import api from './api';
import type { DashboardStats } from '../types/api.types';
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const res = await api.get<DashboardStats>('/api/dashboard/stats');
  return res.data;
};
