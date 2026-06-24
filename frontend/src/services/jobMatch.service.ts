import api from './api';
import type { JobMatchResponse } from '../types/api.types';
export const matchJob = async (resumeId: number, jobDescription: string): Promise<JobMatchResponse> => {
  const res = await api.post<JobMatchResponse>(`/api/job-match/${resumeId}`, { job_description: jobDescription });
  return res.data;
};
