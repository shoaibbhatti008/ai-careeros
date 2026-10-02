import { api, AuthResponse, clearTokens, setTokens } from "./api";
import type { User } from "@/types";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const { data } = await api.post("/users/login/", credentials);

  // Login endpoint returns { access, refresh } only — fetch user separately
  setTokens(data.access, data.refresh);
  const user = await getCurrentUser();
  return { access: data.access, refresh: data.refresh, user };
}

export async function register(payload: RegisterData): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/users/register/", payload);
  setTokens(data.access, data.refresh);
  return data;
}

export async function logout(): Promise<void> {
  const refresh = localStorage.getItem("careeros_refresh_token");
  try {
    if (refresh) {
      await api.post("/users/logout/", { refresh });
    }
  } finally {
    clearTokens();
  }
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/users/me/");
  return data;
}

export async function updateProfile(payload: Partial<User>): Promise<User> {
  const { data } = await api.patch<User>("/users/me/", payload);
  return data;
}