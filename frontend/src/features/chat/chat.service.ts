import { api } from "../../lib/api";

export const chatService = {
  createConversation: async (targetEmail: string) => {
    const res = await api.post("/chat/conversations", {
      target_email: targetEmail,
    });
    return res.data;
  },

  getMessages: async (conversationId: number) => {
    const res = await api.get(
      `/chat/conversations/${conversationId}/messages`
    );
    return res.data;
  },

  sendMessage: async (conversationId: number, text: string) => {
    const res = await api.post(
      `/chat/conversations/${conversationId}/messages/text`,
      { text }
    );
    return res.data;
  },
};