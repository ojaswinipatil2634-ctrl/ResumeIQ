import api from './api';
import type { CareerRoadmapResponse } from '../types/api.types';
export const getRoadmap = async (resumeId: number): Promise<CareerRoadmapResponse> => {
  const res = await api.get<CareerRoadmapResponse>(`/api/roadmap/${resumeId}`);
  return res.data;
};
