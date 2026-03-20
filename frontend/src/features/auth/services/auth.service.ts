import axios from "axios";
import { api } from "../../../lib/api";
import type {
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  TokenResponse,
  UserResponse,
} from "../types/auth.types";

function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    // ❌ אין חיבור לבקאנד
    if (!error.response) {
      return "Cannot connect to server";
    }

    const data = error.response.data;

    // ✅ FastAPI רגיל: { detail: "..." }
    if (typeof data?.detail === "string") {
      return data.detail;
    }

    // ✅ FastAPI validation: { detail: [{ msg: "..." }] }
    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      const first = data.detail[0];
      if (typeof first?.msg === "string") {
        return first.msg;
      }
    }

    // ✅ מקרה כללי
    if (typeof data?.message === "string") {
      return data.message;
    }

    // ✅ fallback לפי סטטוס
    switch (error.response.status) {
      case 401:
        return "Invalid email or password";
      case 400:
        return "Invalid request";
      case 403:
        return "Access denied";
      case 500:
        return "Server error";
    }
  }

  return "Something went wrong. Please try again.";
}

export const authService = {
  async login(payload: LoginRequest): Promise<TokenResponse> {
    try {
      const response = await api.post<TokenResponse>("/auth/login", payload);
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async register(payload: RegisterRequest): Promise<MessageResponse> {
    try {
      const response = await api.post<MessageResponse>("/auth/register", payload);
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async getCurrentUser(): Promise<UserResponse> {
    try {
      const response = await api.get<UserResponse>("/users/me");
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  saveToken(token: string) {
    localStorage.setItem("cryptofile_token", token);
  },

  getToken() {
    return localStorage.getItem("cryptofile_token");
  },

  clearToken() {
    localStorage.removeItem("cryptofile_token");
  },
};