// ============================================================
// API Types — matches backend serializers
// ============================================================

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  profile?: UserProfile;
}

export interface UserProfile {
  headline: string;
  bio: string;
  location: string;
  target_role: string;
  years_of_experience: number | null;
  allow_ai_processing: boolean;
  allow_marketing_emails: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse extends AuthTokens {
  user: User;
}

export interface Resume {
  id: string;
  title: string;
  status: "draft" | "active" | "archived";
  is_primary: boolean;
  language: string;
  versions_count?: number;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  name: string;
  slug: string;
  category: string;
  description: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  employment_type: string;
  remote_policy: string;
  seniority: string;
  status: string;
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  skills: Skill[];
  posted_at: string | null;
  created_at: string;
}

export interface JobMatch {
  id: string;
  job: Job;
  score: number;
  is_saved: boolean;
  is_dismissed: boolean;
  created_at: string;
  updated_at: string;
}

export interface SkillGap {
  id: string;
  skill: Skill;
  target_role: string;
  priority: "low" | "medium" | "high" | "critical";
  importance: number;
  is_resolved: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: string | string[] | undefined;
}