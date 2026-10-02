import { api } from "./api";

// ============================================================
// Types
// ============================================================

export interface ResumeVersion {
  id: string;
  version_number: number;
  source: "upload" | "manual" | "ai_generated";
  is_current: boolean;
  file_size: number;
  file_hash: string;
  skills: ResumeSkill[];
  analysis?: ResumeAnalysis;
  created_at: string;
  updated_at: string;
}

export interface ResumeSkill {
  id: string;
  name: string;
  slug: string;
  category: string;
}

export interface Resume {
  id: string;
  title: string;
  status: "draft" | "active" | "archived";
  is_primary: boolean;
  language: string;
  versions_count?: number;
  versions?: ResumeVersion[];
  created_at: string;
  updated_at: string;
}

export interface ResumeAnalysis {
  skills: string[];
  strengths: string[];
  improvements: string[];
  ats_hints: string[];
  word_count: number;
  target_role?: string | null;
  seniority_estimate?: string;
  target_role_fit?: string | null;
}

export interface AnalyzeResponse {
  resume_id: string;
  version_id: string;
  analysis: ResumeAnalysis;
  summary: string;
  provider: string;
  model: string;
  tokens_used: number;
}

export interface PaginatedResumes {
  count: number;
  next: string | null;
  previous: string | null;
  results: Resume[];
}

// ============================================================
// API Functions
// ============================================================

export async function listResumes(params?: {
  search?: string;
  status?: string;
}): Promise<Resume[]> {
  const { data } = await api.get<PaginatedResumes | Resume[]>("/resumes/", {
    params,
  });
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function getResume(id: string): Promise<Resume> {
  const { data } = await api.get<Resume>(`/resumes/${id}/`);
  return data;
}

export async function createResume(payload: {
  title: string;
  raw_text?: string;
  is_primary?: boolean;
  status?: string;
}): Promise<Resume> {
  const { data } = await api.post<Resume>("/resumes/", payload);
  return data;
}

export async function updateResume(
  id: string,
  payload: Partial<Resume>
): Promise<Resume> {
  const { data } = await api.patch<Resume>(`/resumes/${id}/`, payload);
  return data;
}

export async function deleteResume(id: string): Promise<void> {
  await api.delete(`/resumes/${id}/`);
}

export async function listSkills(params?: {
  category?: string;
  search?: string;
}): Promise<ResumeSkill[]> {
  const { data } = await api.get<{ results: ResumeSkill[] } | ResumeSkill[]>(
    "/resumes/skills/",
    { params }
  );
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function analyzeResume(
  resumeId: string
): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>(
    `/resumes/${resumeId}/analyze/`
  );
  return data;
}