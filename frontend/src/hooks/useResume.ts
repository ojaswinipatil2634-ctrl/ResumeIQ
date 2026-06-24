import { useContext } from 'react';
import { ResumeContext } from '../contexts/ResumeContext';
export const useResume = () => useContext(ResumeContext);
