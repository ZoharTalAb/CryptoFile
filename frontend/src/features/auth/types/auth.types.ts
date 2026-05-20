export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type MessageResponse = {
  message: string;
};

export type UserResponse = {
  id: number;
  email: string;
  created_at: string;
};

export type VerifyEmailRequest = {
  email: string;
  code: string;
};

export type ResendVerificationCodeRequest = {
  email: string;
};
