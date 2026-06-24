// ── Auth ────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Resume ───────────────────────────────────────────────────────────────────

export interface ResumeOut {
  id: number;
  user_id: number;
  original_filename: string;
  file_type: 'pdf' | 'docx';
  file_size_bytes: number;
  uploaded_at: string;
}

export interface ResumeUploadResponse {
  resume: ResumeOut;
  extracted_text: string;
  text_length: number;
}

// ── Analysis ─────────────────────────────────────────────────────────────────

export interface SkillsOut {
  by_category: Record<string, string[]>;
  all_skills: string[];
}

export interface ExperienceOut {
  raw_text: string;
  job_titles: string[];
  companies: string[];
  years_of_experience: number | null;
  keywords: string[];
}

export interface EducationOut {
  raw_text: string;
  degrees: string[];
  institutions: string[];
  fields_of_study: string[];
}

export interface AnalysisResponse {
  resume_id: number;
  extracted_text: string;
  skills: SkillsOut;
  experience: ExperienceOut;
  education: EducationOut;
  career_insights: string[];
  improvement_suggestions: string[];
}

// ── ATS ──────────────────────────────────────────────────────────────────────

export interface ATSSectionScores {
  contact_info: number;
  summary: number;
  skills: number;
  experience: number;
  education: number;
  projects: number;
  keywords: number;
  formatting: number;
}

export interface ATSResponse {
  resume_id: number;
  overall_score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  section_scores: ATSSectionScores;
  missing_sections: string[];
  suggestions: string[];
}

// ── Job Match ────────────────────────────────────────────────────────────────

export interface JobMatchResponse {
  resume_id: number;
  match_score: number;
  match_grade: 'Excellent Fit' | 'Good Fit' | 'Fair Fit' | 'Low Fit';
  matching_skills: string[];
  missing_skills: string[];
  keyword_overlap: Record<string, string[]>;
  recommendations: string[];
}

// ── Improvement ──────────────────────────────────────────────────────────────

export interface ImprovementSection {
  area: string;
  issues: string[];
  tips: string[];
}

export interface ImprovementResponse {
  resume_id: number;
  overall_quality: 'Excellent' | 'Good' | 'Needs Work' | 'Poor';
  sections: ImprovementSection[];
  stronger_action_verbs: string[];
  writing_tips: string[];
}

// ── Interview ────────────────────────────────────────────────────────────────

export interface InterviewResponse {
  resume_id: number;
  technical_questions: string[];
  hr_questions: string[];
  project_questions: string[];
  behavioral_questions: string[];
  preparation_tips: string[];
}

// ── Career Roadmap ────────────────────────────────────────────────────────────

export interface RoadmapStep {
  order: number;
  title: string;
  description: string;
  estimated_time: string;
}

export interface CareerRoadmapResponse {
  resume_id: number;
  current_level: 'Junior' | 'Mid-Level' | 'Senior';
  target_role: string;
  recommended_technologies: string[];
  certifications: string[];
  courses: string[];
  next_roles: string[];
  learning_roadmap: RoadmapStep[];
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export interface UploadTrend {
  date: string;
  count: number;
}

export interface DashboardStats {
  total_users: number;
  total_resumes: number;
  average_ats_score: number | null;
  most_common_skills: string[];
  upload_trends: UploadTrend[];
  top_job_titles: string[];
}
