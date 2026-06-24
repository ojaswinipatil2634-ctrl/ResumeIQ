import React, { createContext, useState, useCallback } from 'react';
import { getResumeId, getResumeName, setResumeId, setResumeName } from '../utils/storage.utils';

interface ResumeContextValue {
  currentResumeId: number | null;
  currentResumeFilename: string | null;
  setCurrentResume: (id: number, filename: string) => void;
}

export const ResumeContext = createContext<ResumeContextValue>({} as ResumeContextValue);

export const ResumeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentResumeId, setCurrentResumeId] = useState<number | null>(getResumeId());
  const [currentResumeFilename, setCurrentResumeFilename] = useState<string | null>(getResumeName());

  const setCurrentResume = useCallback((id: number, filename: string) => {
    setResumeId(id);
    setResumeName(filename);
    setCurrentResumeId(id);
    setCurrentResumeFilename(filename);
  }, []);

  return (
    <ResumeContext.Provider value={{ currentResumeId, currentResumeFilename, setCurrentResume }}>
      {children}
    </ResumeContext.Provider>
  );
};
