const TOKEN_KEY = 'resumeiq_token';
const RESUME_ID_KEY = 'resumeiq_resume_id';
const RESUME_NAME_KEY = 'resumeiq_resume_name';

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);
export const setToken = (token: string): void => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = (): void => localStorage.removeItem(TOKEN_KEY);

export const getResumeId = (): number | null => {
  const val = localStorage.getItem(RESUME_ID_KEY);
  return val ? parseInt(val, 10) : null;
};
export const setResumeId = (id: number): void => localStorage.setItem(RESUME_ID_KEY, id.toString());

export const getResumeName = (): string | null => localStorage.getItem(RESUME_NAME_KEY);
export const setResumeName = (name: string): void => localStorage.setItem(RESUME_NAME_KEY, name);

export const clearResumeData = (): void => {
  localStorage.removeItem(RESUME_ID_KEY);
  localStorage.removeItem(RESUME_NAME_KEY);
};
