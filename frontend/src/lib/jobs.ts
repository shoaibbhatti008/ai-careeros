import { api } from "./api";

// ============================================================
// Types
// ============================================================

export interface JobSkill {
  id: string;
  name: string;
  slug: string;
  category: string;
}

export interface JobSource {
  id: string;
  name: string;
  slug: string;
  source_type: string;
  base_url: string;
  is_active: boolean;
  is_approved: boolean;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  employment_type: "full_time" | "part_time" | "contract" | "internship" | "freelance";
  remote_policy: "onsite" | "hybrid" | "remote";
  seniority: string;
  status: "open" | "closed" | "unknown";
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  source?: JobSource | null;
  source_url?: string;
  skills: JobSkill[];
  tags?: string[];
  posted_at: string | null;
  expires_at?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface JobFilters {
  search?: string;
  company?: string;
  location?: string;
  remote_policy?: string;
  employment_type?: string;
  status?: string;
}

export interface PaginatedJobs {
  count: number;
  next: string | null;
  previous: string | null;
  results: Job[];
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

export interface MatchComputeResponse {
  id: string;
  resume: string;
  job: Job;
  score: number;
  match_reasons: string[];
  missing_skills: string[];
  extra_skills: string[];
  is_saved: boolean;
  is_dismissed: boolean;
  user_notes: string;
  created_at: string;
  updated_at: string;
}

// ============================================================
// API Functions
// ============================================================

export async function listJobs(filters?: JobFilters): Promise<Job[]> {
  const { data } = await api.get<PaginatedJobs | Job[]>("/jobs/", {
    params: filters,
  });
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function getJob(id: string): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${id}/`);
  return data;
}

export async function listJobSources(): Promise<JobSource[]> {
  const { data } = await api.get<{ results: JobSource[] } | JobSource[]>(
    "/jobs/sources/"
  );
  if (Array.isArray(data)) return data;
  return data.results;
}

// ============================================================
// Match
// ============================================================

export async function computeMatch(
  resumeId: string,
  jobId: string
): Promise<MatchComputeResponse> {
  const { data } = await api.post<MatchComputeResponse>("/matches/compute/", {
    resume_id: resumeId,
    job_id: jobId,
  });
  return data;
}

export async function listMatches(params?: {
  saved?: boolean;
  min_score?: number;
}): Promise<JobMatch[]> {
  const { data } = await api.get<{ results: JobMatch[] } | JobMatch[]>(
    "/matches/",
    { params }
  );
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function updateMatch(
  id: string,
  payload: { is_saved?: boolean; is_dismissed?: boolean; user_notes?: string }
): Promise<JobMatch> {
  const { data } = await api.patch<JobMatch>(`/matches/${id}/`, payload);
  return data;
}