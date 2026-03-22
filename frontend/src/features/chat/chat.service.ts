import { api } from "../../lib/api";
import { authService } from "../auth/services/auth.service";

export type ChatMessage = {
  id: number;
  conversation_id: number;
  sender_id: number;
  text_content: string | null;
  message_type: string;
  file_id: number | null;
  stego_type: string | null;
  status: string;
  created_at: string;
};

export type ConversationItem = {
  id: number;
  created_at: string;
  other_user: {
    id: number;
    email: string;
  } | null;
  last_message: ChatMessage | null;
  unread_count: number;
};

export type ConversationResponse = {
  id: number;
  created_at: string;
  other_user: {
    id: number;
    email: string;
  } | null;
};

export type SendFileMessagePayload = {
  conversationId: number;
  file: File;
  stegoType: "image" | "audio" | "text" | "video";
  secretData: string;
  caption?: string;
};

export type ExtractMessageResponse = {
  message_id: number;
  file_id: number;
  stego_type: string;
  extracted_message: string;
};

export type ChatRealtimeEvent =
  | {
      event: "connected";
      user_id: number;
      message: string;
    }
  | {
      event: "message_created";
      conversation_id: number;
      message: ChatMessage;
    }
  | {
      event: "conversation_read";
      conversation_id: number;
      reader_user_id: number;
      updated_count: number;
    }
  | {
      event: "pong";
    }
  | {
      event: "ignored";
      message: string;
    };

function extractErrorMessage(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof (error as any).response === "object"
  ) {
    const response = (error as any).response;
    const detail = response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
  }

  if (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    (error as { code?: string }).code === "ECONNABORTED"
  ) {
    return "The request took too long. Please try again.";
  }

  return "Something went wrong. Please try again.";
}

function getWebSocketBaseUrl() {
  const httpBase =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  if (httpBase.startsWith("https://")) {
    return httpBase.replace("https://", "wss://");
  }

  if (httpBase.startsWith("http://")) {
    return httpBase.replace("http://", "ws://");
  }

  return httpBase;
}

export const chatService = {
  async createConversation(targetEmail: string): Promise<ConversationResponse> {
    try {
      const res = await api.post("/chat/conversations", {
        target_email: targetEmail,
      });
      return res.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async listConversations(): Promise<ConversationItem[]> {
    try {
      const res = await api.get("/chat/conversations");
      return res.data.conversations ?? [];
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async getMessages(
    conversationId: number
  ): Promise<{ messages: ChatMessage[] }> {
    try {
      const res = await api.get(`/chat/conversations/${conversationId}/messages`);
      return res.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async sendMessage(conversationId: number, text: string): Promise<ChatMessage> {
    try {
      const res = await api.post(
        `/chat/conversations/${conversationId}/messages/text`,
        { text }
      );
      return res.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async sendFileMessage(
    payload: SendFileMessagePayload,
    onProgress?: (percent: number) => void
  ): Promise<ChatMessage> {
    try {
      const formData = new FormData();
      formData.append("file", payload.file);
      formData.append("stego_type", payload.stegoType);
      formData.append("secret_data", payload.secretData);

      if (payload.caption?.trim()) {
        formData.append("caption", payload.caption.trim());
      }

      const res = await api.post(
        `/chat/conversations/${payload.conversationId}/messages/file`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 20000,
          onUploadProgress: (event) => {
            if (!event.total) return;

            const percent = Math.round((event.loaded * 100) / event.total);

            if (onProgress) {
              onProgress(percent);
            }
          },
        }
      );

      return res.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async extractMessage(messageId: number): Promise<ExtractMessageResponse> {
    try {
      const res = await api.post(`/chat/messages/${messageId}/extract`);
      return res.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async markConversationRead(conversationId: number) {
    try {
      const res = await api.post(`/chat/conversations/${conversationId}/read`);
      return res.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  createRealtimeSocket() {
    const token = authService.getToken();

    if (!token) {
      return null;
    }

    const wsBaseUrl = getWebSocketBaseUrl();
    return new WebSocket(`${wsBaseUrl}/chat/ws?token=${encodeURIComponent(token)}`);
  },

  parseRealtimeEvent(raw: string): ChatRealtimeEvent | null {
    try {
      return JSON.parse(raw) as ChatRealtimeEvent;
    } catch {
      return null;
    }
  },
};