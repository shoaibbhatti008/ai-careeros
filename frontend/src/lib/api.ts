import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const ACCESS_TOKEN_KEY = "careeros_access_token";
export const REFRESH_TOKEN_KEY = "careeros_refresh_token";

// ============================================================
// Axios client
// ============================================================

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

// ============================================================
// Request interceptor — attach access token
// ============================================================

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================
// Response interceptor — refresh token on 401
// ============================================================

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

      if (!refreshToken) {
        // No refresh token — clear and redirect to login
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          addRefreshSubscriber((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await axios.post(`${API_URL}/users/token/refresh/`, {
          refresh: refreshToken,
        });
        const newAccess = data.access as string;
        localStorage.setItem(ACCESS_TOKEN_KEY, newAccess);
        onRefreshed(newAccess);
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch (refreshError) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ============================================================
// Helpers
// ============================================================

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function hasAccessToken(): boolean {
  return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
}

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined;
    if (data) {
      if (typeof data.detail === "string") return data.detail;
      const firstKey = Object.keys(data)[0];
      if (firstKey) {
        const value = data[firstKey];
        if (Array.isArray(value)) return String(value[0]);
        if (typeof value === "string") return value;
      }
    }
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}