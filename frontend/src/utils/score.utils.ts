export const scoreToColor = (score: number): string => {
  if (score >= 85) return '#22C55E';
  if (score >= 70) return '#84CC16';
  if (score >= 55) return '#F59E0B';
  if (score >= 40) return '#F97316';
  return '#EF4444';
};

export const scoreToGrade = (score: number): string => {
  if (score >= 85) return 'A';
  if (score >= 70) return 'B';
  if (score >= 55) return 'C';
  if (score >= 40) return 'D';
  return 'F';
};

export const scoreToLabel = (score: number): string => {
  if (score >= 85) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 55) return 'Needs Improvement';
  if (score >= 40) return 'Poor';
  return 'Critical';
};

export const matchGradeToColor = (grade: string): string => {
  switch (grade) {
    case 'Excellent Fit': return '#22C55E';
    case 'Good Fit': return '#84CC16';
    case 'Fair Fit': return '#F59E0B';
    case 'Low Fit': return '#EF4444';
    default: return '#6366F1';
  }
};

export const qualityToColor = (quality: string): string => {
  switch (quality) {
    case 'Excellent': return '#22C55E';
    case 'Good': return '#84CC16';
    case 'Needs Work': return '#F59E0B';
    case 'Poor': return '#EF4444';
    default: return '#6366F1';
  }
};
