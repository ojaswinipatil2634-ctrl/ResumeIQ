import api from './api';
import type { ATSResponse } from '../types/api.types';
export const getATSScore = async (resumeId: number): Promise<ATSResponse> => {
  const res = await api.get<ATSResponse>(`/api/ats/${resumeId}`);
  return res.data;
};
