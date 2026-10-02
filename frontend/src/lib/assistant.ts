import { api } from "./api";

// ============================================================
// Types
// ============================================================

export type MessageRole = "user" | "assistant" | "system" | "tool";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  tokens_used: number;
  message_metadata?: Record<string, unknown>;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  is_archived: boolean;
  is_pinned: boolean;
  message_count: number;
  total_tokens: number;
  messages?: Message[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedConversations {
  count: number;
  next: string | null;
  previous: string | null;
  results: Conversation[];
}

// ============================================================
// API Functions
// ============================================================

export async function listConversations(params?: {
  archived?: boolean;
  pinned?: boolean;
}): Promise<Conversation[]> {
  const { data } = await api.get<
    PaginatedConversations | Conversation[]
  >("/conversations/", { params });
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function getConversation(id: string): Promise<Conversation> {
  const { data } = await api.get<Conversation>(`/conversations/${id}/`);
  return data;
}

export async function createConversation(payload: {
  title?: string;
}): Promise<Conversation> {
  const { data } = await api.post<Conversation>("/conversations/", payload);
  return data;
}

export async function updateConversation(
  id: string,
  payload: Partial<Conversation>
): Promise<Conversation> {
  const { data } = await api.patch<Conversation>(
    `/conversations/${id}/`,
    payload
  );
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  await api.delete(`/conversations/${id}/`);
}

export async function listMessages(conversationId: string): Promise<Message[]> {
  const { data } = await api.get<{ results: Message[] } | Message[]>(
    `/conversations/${conversationId}/messages/`
  );
  if (Array.isArray(data)) return data;
  return data.results;
}

export async function sendMessage(
  conversationId: string,
  payload: { content: string; role?: MessageRole }
): Promise<Message> {
  const { data } = await api.post<Message>(
    `/conversations/${conversationId}/messages/`,
    { role: "user", ...payload }
  );
  return data;
}