import api from './api';
import type { ImprovementResponse } from '../types/api.types';
export const getImprovements = async (resumeId: number): Promise<ImprovementResponse> => {
  const res = await api.get<ImprovementResponse>(`/api/improve/${resumeId}`);
  return res.data;
};
