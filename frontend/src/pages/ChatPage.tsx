import { useState } from "react";
import { chatService } from "../features/chat/chat.service";

type ChatMessage = {
  id: number;
  conversation_id: number;
  sender_id: number;
  message_type: string;
  text_content: string | null;
  file_id: number | null;
  stego_type: string | null;
  status: string;
  created_at: string;
};

export function ChatPage() {
  const [email, setEmail] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);

  const handleCreateConversation = async () => {
    try {
      const data = await chatService.createConversation(email);
      setConversationId(data.id);
      setMessages([]);
    } catch (e: any) {
      alert(e.response?.data?.detail || "Failed to create conversation");
    }
  };

  const loadMessages = async () => {
    if (!conversationId) return;

    try {
      setLoadingMessages(true);
      const data = await chatService.getMessages(conversationId);
      setMessages(data.messages ?? []);
    } catch (e: any) {
      alert(e.response?.data?.detail || "Failed to load messages");
    } finally {
      setLoadingMessages(false);
    }
  };

  const sendMessage = async () => {
    if (!conversationId || !text.trim()) return;

    try {
      setSending(true);
      await chatService.sendMessage(conversationId, text.trim());
      setText("");
      await loadMessages();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Failed to send message");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <p className="section-eyebrow">Secure Chat</p>
        <h1 className="section-title">Conversations</h1>
        <p className="section-text">
          Start a protected conversation and exchange secure messages.
        </p>
      </div>

      {!conversationId && (
        <div className="card">
          <div style={{ display: "grid", gap: "12px" }}>
            <input
              className="auth-input"
              placeholder="Enter user email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <button className="button button--primary" onClick={handleCreateConversation}>
              Start Conversation
            </button>
          </div>
        </div>
      )}

      {conversationId && (
        <>
          <div className="card" style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center" }}>
            <div>
              <p className="card__label">Conversation ID</p>
              <h2 className="card__value">{conversationId}</h2>
            </div>

            <button className="button button--secondary" onClick={loadMessages} disabled={loadingMessages}>
              {loadingMessages ? "Loading..." : "Load Messages"}
            </button>
          </div>

          <div className="card" style={{ minHeight: "260px" }}>
            {messages.length === 0 ? (
              <p className="card__meta">No messages yet</p>
            ) : (
              <div style={{ display: "grid", gap: "12px" }}>
                {messages.map((m) => (
                  <div
                    key={m.id}
                    style={{
                      padding: "14px 16px",
                      borderRadius: "14px",
                      background: "rgba(255,255,255,0.04)",
                      border: "1px solid rgba(255,255,255,0.05)",
                    }}
                  >
                    <div style={{ fontSize: "12px", opacity: 0.6, marginBottom: "6px" }}>
                      Sender #{m.sender_id}
                    </div>

                    <div>
                      {m.text_content || (
                        <span style={{ opacity: 0.6 }}>
                          {m.message_type === "stego_file"
                            ? "Stego file message"
                            : "Empty message"}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <div style={{ display: "flex", gap: "12px" }}>
              <input
                className="auth-input"
                placeholder="Write a message..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    void sendMessage();
                  }
                }}
              />
              <button className="button button--primary" onClick={sendMessage} disabled={sending}>
                {sending ? "Sending..." : "Send"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}