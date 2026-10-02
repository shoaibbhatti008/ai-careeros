import { api } from "./api";

// ============================================================
// Types
// ============================================================

export interface SecurityOverview {
  user_id: string;
  email: string;
  last_login: string | null;
  account_created: string;
  is_active: boolean;
  recent_logins_count: number;
  failed_logins_count: number;
  unresolved_events_count: number;
}

export interface AuditLog {
  id: string;
  user_email: string | null;
  action: string;
  ip_address: string | null;
  user_agent: string;
  request_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface LoginAttempt {
  id: string;
  email: string;
  was_successful: boolean;
  ip_address: string | null;
  user_agent: string;
  created_at: string;
}

export interface SecurityEvent {
  id: string;
  event_type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  ip_address: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  resolved: boolean;
}

interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ============================================================
// API Functions
// ============================================================

export async function getOverview(): Promise<SecurityOverview> {
  const { data } = await api.get<SecurityOverview>("/security/overview/");
  return data;
}

export async function listAuditLogs(): Promise<AuditLog[]> {
  const { data } = await api.get<Paginated<AuditLog> | AuditLog[]>(
    "/security/audit-logs/"
  );
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function listLoginHistory(): Promise<LoginAttempt[]> {
  const { data } = await api.get<Paginated<LoginAttempt> | LoginAttempt[]>(
    "/security/login-history/"
  );
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function listSecurityEvents(): Promise<SecurityEvent[]> {
  const { data } = await api.get<Paginated<SecurityEvent> | SecurityEvent[]>(
    "/security/events/"
  );
  if (Array.isArray(data)) return data;
  return data.results;
}