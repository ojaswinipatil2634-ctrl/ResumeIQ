import api from './api';
import type { AnalysisResponse } from '../types/api.types';
export const getAnalysis = async (resumeId: number): Promise<AnalysisResponse> => {
  const res = await api.get<AnalysisResponse>(`/api/analysis/${resumeId}`);
  return res.data;
};
