import axios from "axios";
import { api } from "../../../lib/api";
import type {
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  TokenResponse,
  UserResponse,
} from "../types/auth.types";

type PasswordResetRequestResponse = {
  message: string;
  reset_token: string | null;
};

function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "Cannot connect to server";
    }

    const status = error.response.status;
    const data = error.response.data;

    if (status === 401) {
      return "The email or password is incorrect. Please check your details and try again.";
    }

    if (status === 423) {
      return "Too many failed sign-in attempts. Please wait a few minutes and try again.";
    }

    if (typeof data?.detail?.message === "string") {
      if (data.detail.code === "PASSWORD_EXPIRED") {
        return "Your password has expired. Please reset it before signing in.";
      }

      return data.detail.message;
    }

    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      const first = data.detail[0];
      if (typeof first?.msg === "string") {
        return first.msg;
      }
    }

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (typeof data?.message === "string") {
      return data.message;
    }

    switch (status) {
      case 400:
        return "Invalid request. Please check the details and try again.";
      case 403:
        return "Access denied. Please sign in again or reset your password.";
      case 500:
        return "Server error. Please try again later.";
    }
  }

  return "Something went wrong. Please try again.";
}

function getStoredToken() {
  return (
    localStorage.getItem("cryptofile_token") ??
    sessionStorage.getItem("cryptofile_token")
  );
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

  async requestPasswordReset(email: string): Promise<PasswordResetRequestResponse> {
    try {
      const response = await api.post<PasswordResetRequestResponse>(
        "/auth/password-reset/request",
        { email }
      );
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async confirmPasswordReset(
    token: string,
    newPassword: string
  ): Promise<MessageResponse> {
    try {
      const response = await api.post<MessageResponse>(
        "/auth/password-reset/confirm",
        {
          token,
          new_password: newPassword,
        }
      );
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  saveToken(token: string, persistent = true) {
    if (persistent) {
      localStorage.setItem("cryptofile_token", token);
      sessionStorage.removeItem("cryptofile_token");
      return;
    }

    sessionStorage.setItem("cryptofile_token", token);
    localStorage.removeItem("cryptofile_token");
  },

  getToken() {
    return getStoredToken();
  },

  clearToken() {
    localStorage.removeItem("cryptofile_token");
    sessionStorage.removeItem("cryptofile_token");
  },
};