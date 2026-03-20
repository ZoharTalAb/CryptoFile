import { api } from "../../../lib/api";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
} from "../types/auth.types";

export const authService = {
  async login(payload: LoginRequest) {
    const response = await api.post<TokenResponse>("/auth/login", payload);
    return response.data;
  },

  async register(payload: RegisterRequest) {
    const response = await api.post("/auth/register", payload);
    return response.data;
  },
};