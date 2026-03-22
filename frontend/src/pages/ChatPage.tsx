import { useEffect, useMemo, useRef, useState } from "react";
import {
  Search,
  RefreshCw,
  SendHorizonal,
  Shield,
  Paperclip,
  X,
  Wifi,
  WifiOff,
  LoaderCircle,
  ImageIcon,
  FileAudio2,
  FileText,
  Film,
  Sparkles,
  Check,
  CheckCheck,
} from "lucide-react";
import { useAuth } from "../features/auth/context/AuthContext";
import {
  chatService,
  type ChatMessage,
  type ConversationItem,
  type ChatRealtimeEvent,
} from "../features/chat/chat.service";
import { useToast } from "../components/common/ToastProvider";

type StegoType = "image" | "audio" | "text" | "video";
type SocketStatus = "connecting" | "connected" | "offline";

type UploadingBubble = {
  tempId: number;
  fileName: string;
  stegoType: StegoType;
  caption: string;
  progress: number;
};

function parseServerDate(value?: string | null) {
  if (!value) return null;

  const hasTimezone = /([zZ]|[+\-]\d{2}:\d{2})$/.test(value);
  const normalized = hasTimezone ? value : `${value}Z`;
  const parsed = new Date(normalized);

  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function formatTime(value?: string | null) {
  const parsed = parseServerDate(value);
  if (!parsed) return "";

  return parsed.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function sortConversations(items: ConversationItem[]) {
  return [...items].sort((a, b) => {
    const aTime =
      parseServerDate(a.last_message?.created_at)?.getTime() ??
      parseServerDate(a.created_at)?.getTime() ??
      0;
    const bTime =
      parseServerDate(b.last_message?.created_at)?.getTime() ??
      parseServerDate(b.created_at)?.getTime() ??
      0;

    return bTime - aTime;
  });
}

function upsertConversationPreview(
  conversations: ConversationItem[],
  message: ChatMessage,
  currentUserId?: number,
  activeConversationId?: number | null
) {
  const index = conversations.findIndex(
    (conversation) => conversation.id === message.conversation_id
  );

  if (index === -1) {
    return conversations;
  }

  const target = conversations[index];
  const shouldIncrementUnread =
    message.sender_id !== currentUserId &&
    message.conversation_id !== activeConversationId;

  const updated: ConversationItem = {
    ...target,
    last_message: message,
    unread_count: shouldIncrementUnread
      ? target.unread_count + 1
      : target.unread_count,
  };

  const next = [...conversations];
  next.splice(index, 1);
  next.unshift(updated);

  return next;
}

function getStegoIcon(type?: string | null) {
  switch (type) {
    case "image":
      return <ImageIcon size={16} />;
    case "audio":
      return <FileAudio2 size={16} />;
    case "text":
      return <FileText size={16} />;
    case "video":
      return <Film size={16} />;
    default:
      return <Sparkles size={16} />;
  }
}

function getSelectedFileMeta(file: File | null) {
  if (!file) return null;

  const sizeInKb = Math.max(1, Math.round(file.size / 1024));
  return `${file.name} · ${sizeInKb} KB`;
}

function renderMessageStatus(status?: string, isMe?: boolean) {
  if (!isMe) return null;

  if (status === "read") {
    return <CheckCheck size={14} className="chat-status-icon chat-status-icon--read" />;
  }

  return <Check size={14} className="chat-status-icon" />;
}

export function ChatPage() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [email, setEmail] = useState("");
  const [text, setText] = useState("");
  const [conversationSearch, setConversationSearch] = useState("");

  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const [activeConversationId, setActiveConversationId] = useState<number | null>(
    null
  );

  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendingFile, setSendingFile] = useState(false);

  const [pageError, setPageError] = useState("");
  const [socketStatus, setSocketStatus] = useState<SocketStatus>("connecting");

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [secretData, setSecretData] = useState("");
  const [caption, setCaption] = useState("");
  const [stegoType, setStegoType] = useState<StegoType>("image");
  const [showFileComposer, setShowFileComposer] = useState(false);

  const [extractingMessageId, setExtractingMessageId] = useState<number | null>(null);
  const [extractedData, setExtractedData] = useState<Record<number, string>>({});
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadingBubble, setUploadingBubble] = useState<UploadingBubble | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const pingIntervalRef = useRef<number | null>(null);
  const activeConversationIdRef = useRef<number | null>(null);
  const currentUserIdRef = useRef<number | undefined>(undefined);
  const notifiedSocketOfflineRef = useRef(false);

  const activeConversation = useMemo(
    () =>
      conversations.find((conversation) => conversation.id === activeConversationId) ??
      null,
    [conversations, activeConversationId]
  );

  const selectedFileMeta = useMemo(
    () => getSelectedFileMeta(selectedFile),
    [selectedFile]
  );
  const myUserId = user?.id;

  function formatConversationPreview(conversation: ConversationItem) {
    if (!conversation.last_message) {
      return "No messages yet";
    }

    if (conversation.last_message.message_type === "stego_file") {
      return "Protected file sent";
    }

    if (conversation.last_message.text_content) {
      return conversation.last_message.text_content;
    }

    return "Unsupported message";
  }

  const filteredConversations = useMemo(() => {
    const query = conversationSearch.trim().toLowerCase();

    if (!query) {
      return conversations;
    }

    return conversations.filter((conversation) => {
      const userEmail = conversation.other_user?.email?.toLowerCase() ?? "";
      const preview = formatConversationPreview(conversation).toLowerCase();

      return userEmail.includes(query) || preview.includes(query);
    });
  }, [conversationSearch, conversations]);

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  useEffect(() => {
    currentUserIdRef.current = myUserId;
  }, [myUserId]);

  async function loadConversations(keepSelected = true) {
    try {
      setLoadingConversations(true);
      setPageError("");

      const data = await chatService.listConversations();
      const sorted = sortConversations(data);

      setConversations(sorted);

      if (!keepSelected && sorted.length > 0) {
        setActiveConversationId(sorted[0].id);
      }

      if (!activeConversationIdRef.current && sorted.length > 0) {
        setActiveConversationId(sorted[0].id);
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to load conversations";
      setPageError(message);
      showToast(message, "error");
    } finally {
      setLoadingConversations(false);
    }
  }

  async function loadMessages(conversationId: number) {
    try {
      setLoadingMessages(true);
      setPageError("");

      const data = await chatService.getMessages(conversationId);
      setMessages(data.messages ?? []);

      await chatService.markConversationRead(conversationId);

      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === conversationId
            ? { ...conversation, unread_count: 0 }
            : conversation
        )
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to load messages";
      setPageError(message);
      showToast(message, "error");
    } finally {
      setLoadingMessages(false);
    }
  }

  async function handleCreateConversation() {
    if (!email.trim()) return;

    try {
      setCreatingConversation(true);
      setPageError("");

      const created = await chatService.createConversation(email.trim());

      await loadConversations(false);
      setActiveConversationId(created.id);
      setEmail("");
      showToast("Conversation created", "success");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to create conversation";
      setPageError(message);
      showToast(message, "error");
    } finally {
      setCreatingConversation(false);
    }
  }

  async function handleSelectConversation(conversationId: number) {
    setActiveConversationId(conversationId);
  }

  async function handleSendMessage() {
    if (!activeConversationId || !text.trim()) return;

    try {
      setSending(true);
      setPageError("");

      await chatService.sendMessage(activeConversationId, text.trim());
      setText("");

      await loadMessages(activeConversationId);
      await loadConversations();
      showToast("Message sent", "success");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to send message";
      setPageError(message);
      showToast(message, "error");
    } finally {
      setSending(false);
    }
  }

  async function handleSendFileMessage() {
    if (!activeConversationId) return;
    if (!selectedFile) {
      const message = "Please choose a file first";
      setPageError(message);
      showToast(message, "error");
      return;
    }
    if (!secretData.trim()) {
      const message = "Please enter secret data for the secure file";
      setPageError(message);
      showToast(message, "error");
      return;
    }

    const tempId = Date.now();

    try {
      setSendingFile(true);
      setUploadProgress(0);
      setPageError("");

      setUploadingBubble({
        tempId,
        fileName: selectedFile.name,
        stegoType,
        caption,
        progress: 0,
      });

      await chatService.sendFileMessage(
        {
          conversationId: activeConversationId,
          file: selectedFile,
          stegoType,
          secretData: secretData.trim(),
          caption: caption.trim(),
        },
        (progress) => {
          setUploadProgress(progress);
          setUploadingBubble((prev) => (prev ? { ...prev, progress } : prev));
        }
      );

      setSelectedFile(null);
      setSecretData("");
      setCaption("");
      setShowFileComposer(false);
      setUploadProgress(0);
      setUploadingBubble(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadMessages(activeConversationId);
      await loadConversations();
      showToast("Secure file sent 🔐", "success");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to send secure file";
      setPageError(message);
      setUploadingBubble(null);
      showToast(message, "error");
    } finally {
      setSendingFile(false);
    }
  }

  async function handleExtract(messageId: number) {
    try {
      setExtractingMessageId(messageId);
      setPageError("");

      const result = await chatService.extractMessage(messageId);

      setExtractedData((prev) => ({
        ...prev,
        [messageId]: result.extracted_message,
      }));

      showToast("Hidden message extracted ✨", "success");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to extract message";
      setPageError(message);
      showToast(message, "error");
    } finally {
      setExtractingMessageId(null);
    }
  }

  function resetFileComposer() {
    setSelectedFile(null);
    setSecretData("");
    setCaption("");
    setShowFileComposer(false);
    setUploadProgress(0);
    setUploadingBubble(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function appendUniqueMessage(message: ChatMessage) {
    setMessages((prev) => {
      if (prev.some((item) => item.id === message.id)) {
        return prev;
      }

      return [...prev, message];
    });
  }

  function handleRealtimeEvent(event: ChatRealtimeEvent) {
    if (event.event === "connected") {
      setSocketStatus("connected");
      notifiedSocketOfflineRef.current = false;
      return;
    }

    if (event.event === "pong" || event.event === "ignored") {
      return;
    }

    if (event.event === "message_created") {
      const { conversation_id, message } = event;

      setConversations((prev) => {
        const updated = upsertConversationPreview(
          prev,
          message,
          currentUserIdRef.current,
          activeConversationIdRef.current
        );

        if (updated !== prev) {
          return updated;
        }

        void loadConversations();
        return prev;
      });

      if (conversation_id === activeConversationIdRef.current) {
        appendUniqueMessage(message);

        if (message.sender_id !== currentUserIdRef.current) {
          void chatService.markConversationRead(conversation_id);
          setConversations((prev) =>
            prev.map((conversation) =>
              conversation.id === conversation_id
                ? { ...conversation, unread_count: 0 }
                : conversation
            )
          );
        }
      } else if (message.sender_id !== currentUserIdRef.current) {
        showToast("New secure message received", "info");
      }

      return;
    }

    if (event.event === "conversation_read") {
      if (event.reader_user_id === currentUserIdRef.current) {
        return;
      }

      if (event.conversation_id === activeConversationIdRef.current) {
        setMessages((prev) =>
          prev.map((message) =>
            message.sender_id === currentUserIdRef.current
              ? { ...message, status: "read" }
              : message
          )
        );
      }
    }
  }

  useEffect(() => {
    void loadConversations();
  }, []);

  useEffect(() => {
    if (activeConversationId) {
      void loadMessages(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, uploadingBubble]);

  useEffect(() => {
    let isUnmounted = false;

    function clearSocketArtifacts() {
      if (pingIntervalRef.current) {
        window.clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }

      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    }

    function connectSocket() {
      clearSocketArtifacts();

      const socket = chatService.createRealtimeSocket();

      if (!socket) {
        setSocketStatus("offline");
        if (!notifiedSocketOfflineRef.current) {
          showToast("Realtime connection unavailable", "info");
          notifiedSocketOfflineRef.current = true;
        }
        return;
      }

      socketRef.current = socket;
      setSocketStatus("connecting");

      socket.onopen = () => {
        if (isUnmounted) return;

        setSocketStatus("connected");
        notifiedSocketOfflineRef.current = false;

        pingIntervalRef.current = window.setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "ping" }));
          }
        }, 25000);
      };

      socket.onmessage = (wsEvent) => {
        const parsed = chatService.parseRealtimeEvent(wsEvent.data);
        if (!parsed) return;

        handleRealtimeEvent(parsed);
      };

      socket.onerror = () => {
        if (isUnmounted) return;
        setSocketStatus("offline");
      };

      socket.onclose = () => {
        clearSocketArtifacts();

        if (isUnmounted) return;

        setSocketStatus("offline");

        if (!notifiedSocketOfflineRef.current) {
          showToast("Realtime disconnected. Reconnecting...", "info");
          notifiedSocketOfflineRef.current = true;
        }

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connectSocket();
        }, 2000);
      };
    }

    connectSocket();

    return () => {
      isUnmounted = true;
      clearSocketArtifacts();

      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [showToast]);

  return (
    <div className="chat-workspace chat-workspace--two-columns">
      <section className="chat-conversations chat-conversations--wide">
        <div className="chat-conversations__header">
          <div>
            <p className="section-eyebrow">Secure Chat</p>
            <h2 className="chat-conversations__title">Inbox</h2>
          </div>

          <div className="chat-conversations__header-actions">
            <div
              className={`chat-live-badge chat-live-badge--${socketStatus}`}
              title={`Realtime status: ${socketStatus}`}
            >
              {socketStatus === "connected" ? (
                <Wifi size={14} />
              ) : socketStatus === "connecting" ? (
                <LoaderCircle size={14} className="spin" />
              ) : (
                <WifiOff size={14} />
              )}
              <span>{socketStatus}</span>
            </div>

            <button
              className="button button--secondary"
              type="button"
              onClick={() => void loadConversations()}
              disabled={loadingConversations}
            >
              <RefreshCw size={16} className={loadingConversations ? "spin" : ""} />
              Refresh
            </button>
          </div>
        </div>

        <div className="chat-conversations__create">
          <div className="chat-search">
            <Search size={16} />
            <input
              className="chat-search__input"
              placeholder="Search conversations..."
              value={conversationSearch}
              onChange={(e) => setConversationSearch(e.target.value)}
            />
          </div>

          <div className="chat-new-thread">
            <div className="chat-new-thread__top">
              <Shield size={16} />
              <span>Start new secure conversation</span>
            </div>

            <div className="chat-new-thread__form">
              <input
                className="auth-input"
                placeholder="Enter recipient email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <button
                className="button button--primary"
                onClick={handleCreateConversation}
                disabled={creatingConversation}
                type="button"
              >
                {creatingConversation ? "Creating..." : "Start Secure Chat"}
              </button>
            </div>
          </div>
        </div>

        {pageError ? (
          <div className="auth-alert auth-alert--error">{pageError}</div>
        ) : null}

        <div className="chat-conversations__list">
          {loadingConversations ? (
            <div className="chat-empty-state">Loading conversations...</div>
          ) : filteredConversations.length === 0 ? (
            <div className="chat-empty-state">
              {conversations.length === 0
                ? "No conversations yet. Start one above."
                : "No conversations match your search."}
            </div>
          ) : (
            filteredConversations.map((conversation) => {
              const isActive = conversation.id === activeConversationId;

              return (
                <button
                  key={conversation.id}
                  type="button"
                  className={`chat-conversation-card ${
                    isActive ? "chat-conversation-card--active" : ""
                  }`}
                  onClick={() => void handleSelectConversation(conversation.id)}
                >
                  <div className="chat-conversation-card__avatar">
                    {conversation.other_user?.email?.slice(0, 1).toUpperCase() ?? "?"}
                  </div>

                  <div className="chat-conversation-card__body">
                    <div className="chat-conversation-card__top">
                      <strong>
                        {conversation.other_user?.email ?? "Unknown participant"}
                      </strong>
                      <span>{formatTime(conversation.last_message?.created_at)}</span>
                    </div>

                    <p>{formatConversationPreview(conversation)}</p>

                    <div className="chat-conversation-card__bottom">
                      <span className="chat-conversation-card__meta">
                        End-to-end protected
                      </span>

                      {conversation.unread_count > 0 ? (
                        <span className="chat-conversation-card__badge">
                          {conversation.unread_count}
                        </span>
                      ) : null}
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </section>

      <section className="chat-thread">
        <div className="chat-thread__header">
          {activeConversation ? (
            <div className="chat-thread__user">
              <div className="chat-thread__avatar">
                {activeConversation.other_user?.email?.slice(0, 1).toUpperCase() ?? "?"}
              </div>

              <div>
                <strong>
                  {activeConversation.other_user?.email ?? "Unknown participant"}
                </strong>
                <span>Active protected thread</span>
              </div>
            </div>
          ) : (
            <div className="chat-empty-state chat-empty-state--inline">
              Select a conversation to view messages
            </div>
          )}
        </div>

        <div className="chat-thread__messages">
          {!activeConversationId ? (
            <div className="chat-empty-state">
              Start or select a secure conversation to begin messaging.
            </div>
          ) : loadingMessages ? (
            <div className="chat-empty-state">Loading messages...</div>
          ) : (
            <>
              {messages.map((message) => {
                const isMe = message.sender_id === myUserId;
                const isFileMessage = message.message_type === "stego_file";

                return (
                  <div
                    key={message.id}
                    className={`chat-message-row ${
                      isMe ? "chat-message-row--me" : "chat-message-row--other"
                    }`}
                  >
                    <div
                      className={`chat-message-bubble ${
                        isMe
                          ? "chat-message-bubble--me"
                          : "chat-message-bubble--other"
                      }`}
                    >
                      {isFileMessage ? (
                        <div className="chat-file-message">
                          <div className="chat-file-message__topline">
                            <span className="chat-file-message__icon">
                              {getStegoIcon(message.stego_type)}
                            </span>
                            <span className="chat-file-message__badge">
                              {message.stego_type ?? "unknown"}
                            </span>
                          </div>

                          <div className="chat-file-message__title">
                            Protected file attached
                          </div>

                          {message.text_content ? (
                            <div className="chat-file-message__caption">
                              {message.text_content}
                            </div>
                          ) : null}

                          <button
                            className="button button--secondary"
                            style={{ marginTop: "10px" }}
                            onClick={() => void handleExtract(message.id)}
                            disabled={extractingMessageId === message.id}
                            type="button"
                          >
                            {extractingMessageId === message.id
                              ? "Extracting..."
                              : "Extract hidden message"}
                          </button>

                          {extractedData[message.id] ? (
                            <div className="chat-file-message__extract-result">
                              <strong>Hidden data:</strong>
                              <div>{extractedData[message.id]}</div>
                            </div>
                          ) : null}
                        </div>
                      ) : (
                        <div className="chat-message-bubble__text">
                          {message.text_content || "Unsupported message"}
                        </div>
                      )}

                      <div className="chat-message-bubble__meta chat-message-bubble__meta--row">
                        <span>{formatTime(message.created_at)}</span>
                        {renderMessageStatus(message.status, isMe)}
                      </div>
                    </div>
                  </div>
                );
              })}

              {uploadingBubble ? (
                <div className="chat-message-row chat-message-row--me">
                  <div className="chat-message-bubble chat-message-bubble--me">
                    <div className="chat-file-message">
                      <div className="chat-file-message__topline">
                        <span className="chat-file-message__icon">
                          {getStegoIcon(uploadingBubble.stegoType)}
                        </span>
                        <span className="chat-file-message__badge">
                          {uploadingBubble.stegoType}
                        </span>
                      </div>

                      <div className="chat-file-message__title">
                        Uploading protected file...
                      </div>

                      <div className="chat-file-message__caption">
                        {uploadingBubble.fileName}
                      </div>

                      {uploadingBubble.caption ? (
                        <div className="chat-file-message__caption">
                          {uploadingBubble.caption}
                        </div>
                      ) : null}

                      <div className="upload-progress upload-progress--bubble">
                        <div
                          className="upload-progress__bar"
                          style={{ width: `${uploadingBubble.progress}%` }}
                        />
                      </div>

                      <div className="chat-message-bubble__meta">
                        {uploadingBubble.progress}% · uploading
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}

              {!messages.length && !uploadingBubble ? (
                <div className="chat-empty-state">No messages yet</div>
              ) : null}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {activeConversationId ? (
          <div className="chat-thread__composer chat-thread__composer--stacked">
            {showFileComposer ? (
              <div className="chat-file-composer">
                <div className="chat-file-composer__header">
                  <strong>Send secure file</strong>
                  <button
                    type="button"
                    className="chat-file-composer__close"
                    onClick={resetFileComposer}
                  >
                    <X size={16} />
                  </button>
                </div>

                <div className="chat-file-composer__grid">
                  <input
                    ref={fileInputRef}
                    className="auth-input"
                    type="file"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                  />

                  <select
                    value={stegoType}
                    onChange={(e) => setStegoType(e.target.value as StegoType)}
                    className="chat-thread__select"
                  >
                    <option value="image">Image</option>
                    <option value="audio">Audio</option>
                    <option value="text">Text</option>
                    <option value="video">Video</option>
                  </select>

                  <input
                    className="auth-input"
                    placeholder="Secret data hidden inside the file"
                    value={secretData}
                    onChange={(e) => setSecretData(e.target.value)}
                  />

                  <input
                    className="auth-input"
                    placeholder="Caption (optional)"
                    value={caption}
                    onChange={(e) => setCaption(e.target.value)}
                  />
                </div>

                {selectedFileMeta ? (
                  <div className="chat-file-composer__preview">
                    <span className="chat-file-composer__preview-icon">
                      {getStegoIcon(stegoType)}
                    </span>

                    <div style={{ flex: 1 }}>
                      <strong>Ready to send</strong>
                      <div>{selectedFileMeta}</div>

                      {sendingFile ? (
                        <div className="upload-progress">
                          <div
                            className="upload-progress__bar"
                            style={{ width: `${uploadProgress}%` }}
                          />
                        </div>
                      ) : null}
                    </div>

                    {sendingFile ? <span>{uploadProgress}%</span> : null}
                  </div>
                ) : null}

                <div className="chat-file-composer__actions">
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={resetFileComposer}
                  >
                    Cancel
                  </button>

                  <button
                    className="button button--primary"
                    type="button"
                    onClick={() => void handleSendFileMessage()}
                    disabled={sendingFile}
                  >
                    {sendingFile ? "Sending file..." : "Send File Securely"}
                  </button>
                </div>
              </div>
            ) : null}

            <div className="chat-thread__composer-row">
              <button
                className="button button--secondary"
                type="button"
                onClick={() => setShowFileComposer((prev) => !prev)}
              >
                <Paperclip size={16} />
                {showFileComposer ? "Hide File Upload" : "Attach Secure File"}
              </button>

              <input
                className="chat-thread__input"
                placeholder="Type a secure message..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    void handleSendMessage();
                  }
                }}
              />

              <button
                className="button button--primary"
                onClick={() => void handleSendMessage()}
                disabled={sending}
                type="button"
              >
                <SendHorizonal size={16} />
                {sending ? "Sending..." : "Send"}
              </button>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}