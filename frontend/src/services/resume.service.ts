import api from './api';
import type { ResumeUploadResponse } from '../types/api.types';

export const uploadResume = async (
  file: File,
  onProgress?: (pct: number) => void
): Promise<ResumeUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post<ResumeUploadResponse>('/api/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
    },
  });
  return res.data;
};
