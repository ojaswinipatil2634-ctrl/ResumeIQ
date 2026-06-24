import api from './api';
import type { InterviewResponse } from '../types/api.types';
export const getInterviewQuestions = async (resumeId: number): Promise<InterviewResponse> => {
  const res = await api.get<InterviewResponse>(`/api/interview/${resumeId}`);
  return res.data;
};
