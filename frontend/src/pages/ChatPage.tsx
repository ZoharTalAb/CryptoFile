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
  Download,
  WandSparkles,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "../features/auth/context/AuthContext";
import {
  chatService,
  type ChatMessage,
  type ConversationItem,
  type ChatRealtimeEvent,
} from "../features/chat/chat.service";
import { useToast } from "../components/common/ToastProvider";
import { filesService, type FileItem } from "../features/files/files.service";

type StegoType = "image" | "audio" | "text" | "video";
type SocketStatus = "connecting" | "connected" | "offline";

type UploadingBubble = {
  tempId: number;
  fileName: string;
  stegoType: StegoType;
  caption: string;
  progress: number;
};

type FilePreviewState =
  | {
      kind: "image" | "audio" | "video";
      url: string;
      loading?: false;
    }
  | {
      kind: "text";
      text: string;
      loading?: false;
    }
  | {
      kind: "unknown";
      loading?: false;
      error?: string;
    }
  | {
      kind: "loading";
      loading: true;
    };

function buildFileIndex(items: FileItem[]) {
  return items.reduce<Record<number, FileItem>>((acc, item) => {
    acc[item.id] = item;
    return acc;
  }, {});
}

function inferMimeType(filename: string | undefined, stegoType?: string | null) {
  const extension = filename?.split(".").pop()?.toLowerCase();

  if (extension) {
    if (["png", "jpg", "jpeg", "gif", "webp", "bmp"].includes(extension)) {
      return `image/${extension === "jpg" ? "jpeg" : extension}`;
    }

    if (["mp3"].includes(extension)) return "audio/mpeg";
    if (["wav"].includes(extension)) return "audio/wav";
    if (["ogg"].includes(extension)) return "audio/ogg";
    if (["m4a"].includes(extension)) return "audio/mp4";
    if (["aac"].includes(extension)) return "audio/aac";

    if (["mp4"].includes(extension)) return "video/mp4";
    if (["webm"].includes(extension)) return "video/webm";

    if (["txt", "md", "csv", "json", "log"].includes(extension)) {
      return "text/plain";
    }
  }

  switch (stegoType) {
    case "image":
      return "image/png";
    case "audio":
      return "audio/wav";
    case "video":
      return "video/mp4";
    case "text":
      return "text/plain";
    default:
      return "application/octet-stream";
  }
}

function createPreviewFilename(fileId: number, stegoType?: string | null) {
  const extension =
    stegoType === "image"
      ? "png"
      : stegoType === "audio"
      ? "wav"
      : stegoType === "video"
      ? "mp4"
      : stegoType === "text"
      ? "txt"
      : "bin";

  return `protected-file-${fileId}.${extension}`;
}

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

function inferStegoTypeFromFile(file: File | null): StegoType | null {
  if (!file) return null;
  const ext = file.name.split(".").pop()?.toLowerCase();

  if (!ext) return null;
  if (["png", "jpg", "jpeg", "gif", "webp", "bmp"].includes(ext)) return "image";
  if (["wav", "mp3", "ogg", "m4a", "aac"].includes(ext)) return "audio";
  if (["txt", "md", "csv", "json", "log"].includes(ext)) return "text";
  if (["mp4", "mov", "webm", "avi"].includes(ext)) return "video";

  return null;
}

function validateCarrierFile(file: File | null, stegoType: StegoType) {
  if (!file) return "Please choose a file first";

  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";

  if (stegoType === "audio" && ext !== "wav") {
    return "Audio stego currently supports WAV files only";
  }

  if (
    stegoType === "image" &&
    !["png", "jpg", "jpeg", "gif", "webp", "bmp"].includes(ext)
  ) {
    return "Image stego supports image carrier files only";
  }

  if (
    stegoType === "text" &&
    !["txt", "md", "csv", "json", "log"].includes(ext)
  ) {
    return "Text stego supports text carrier files only";
  }

  if (
    stegoType === "video" &&
    !["mp4", "mov", "webm", "avi"].includes(ext)
  ) {
    return "Video stego supports video carrier files only";
  }

  return null;
}

export function ChatPage() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [email, setEmail] = useState("");
  const [text, setText] = useState("");
  const [conversationSearch, setConversationSearch] = useState("");

  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [fileIndex, setFileIndex] = useState<Record<number, FileItem>>({});
  const [filePreviews, setFilePreviews] = useState<Record<number, FilePreviewState>>({});
  const previewUrlsRef = useRef<Record<number, string>>({});

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

  const fileValidationError = useMemo(
    () => validateCarrierFile(selectedFile, stegoType),
    [selectedFile, stegoType]
  );

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
      const participant = conversation.other_user?.email?.toLowerCase() ?? "";
      const preview = formatConversationPreview(conversation).toLowerCase();

      return participant.includes(query) || preview.includes(query);
    });
  }, [conversationSearch, conversations]);

  async function loadConversations(showRefresh = false) {
    try {
      if (!showRefresh) {
        setLoadingConversations(true);
      }

      setPageError("");

      const data = await chatService.listConversations();
      setConversations(sortConversations(data));
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
      setExtractedData({});
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
    const targetEmail = email.trim();

    if (!targetEmail) {
      const message = "Please enter an email address";
      setPageError(message);
      showToast(message, "error");
      return;
    }

    try {
      setCreatingConversation(true);
      setPageError("");

      const conversation = await chatService.createConversation(targetEmail);

      setEmail("");
      setActiveConversationId(conversation.id);
      await loadConversations();

      showToast("Secure conversation ready", "success");
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

    try {
      await chatService.markConversationRead(conversationId);

      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === conversationId
            ? { ...conversation, unread_count: 0 }
            : conversation
        )
      );
    } catch {
      // keep smooth UX
    }
  }

  async function handleSendMessage() {
    if (!activeConversationId) return;

    const content = text.trim();
    if (!content) return;

    try {
      setSending(true);
      setPageError("");

      await chatService.sendMessage(activeConversationId, content);
      setText("");

      await loadMessages(activeConversationId);
      await loadConversations();
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

    if (fileValidationError) {
      setPageError(fileValidationError);
      showToast(fileValidationError, "error");
      return;
    }

    if (!secretData.trim()) {
      const message = "Please enter secret data for the secure file";
      setPageError(message);
      showToast(message, "error");
      return;
    }

    if (!selectedFile) {
      const message = "Please choose a file first";
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
      await loadAccessibleFiles();
      showToast("Secure file sent", "success");
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

      showToast("Hidden message extracted", "success");
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

  async function loadAccessibleFiles() {
    try {
      const data = await filesService.listFiles();
      const allFiles = [...(data.owned_files ?? []), ...(data.shared_with_me ?? [])];
      setFileIndex(buildFileIndex(allFiles));
    } catch (error) {
      console.error("Failed to load accessible files", error);
    }
  }

  async function prepareFilePreview(message: ChatMessage) {
    if (!message.file_id) return;
    if (filePreviews[message.file_id]) return;

    const fallbackName = createPreviewFilename(message.file_id, message.stego_type);
    const fileMeta = fileIndex[message.file_id];

    setFilePreviews((prev) => ({
      ...prev,
      [message.file_id as number]: { kind: "loading", loading: true },
    }));

    try {
      const blob = await filesService.getFileBlob(message.file_id);
      const mimeType = inferMimeType(fileMeta?.filename ?? fallbackName, message.stego_type);

      if (message.stego_type === "text") {
        const text = await new Blob([blob], { type: mimeType }).text();
        setFilePreviews((prev) => ({
          ...prev,
          [message.file_id as number]: {
            kind: "text",
            text: text.slice(0, 1200),
          },
        }));
        return;
      }

      const previewBlob = blob.type ? blob : new Blob([blob], { type: mimeType });
      const objectUrl = URL.createObjectURL(previewBlob);
      previewUrlsRef.current[message.file_id] = objectUrl;

      if (
        message.stego_type === "image" ||
        message.stego_type === "audio" ||
        message.stego_type === "video"
      ) {
        setFilePreviews((prev) => ({
          ...prev,
          [message.file_id as number]: {
            kind: message.stego_type as "image" | "audio" | "video",
            url: objectUrl,
          },
        }));
        return;
      }

      setFilePreviews((prev) => ({
        ...prev,
        [message.file_id as number]: {
          kind: "unknown",
        },
      }));
    } catch (error) {
      setFilePreviews((prev) => ({
        ...prev,
        [message.file_id as number]: {
          kind: "unknown",
          error: error instanceof Error ? error.message : "Preview unavailable",
        },
      }));
    }
  }

  async function handleDownloadFile(message: ChatMessage) {
    if (!message.file_id) return;

    const filename =
      fileIndex[message.file_id]?.filename ??
      createPreviewFilename(message.file_id, message.stego_type);

    try {
      await filesService.downloadFile(message.file_id, filename);
      showToast("File download started", "success");
    } catch (error) {
      const msg =
        error instanceof Error ? error.message : "Failed to download file";
      setPageError(msg);
      showToast(msg, "error");
    }
  }

  function renderFilePreview(message: ChatMessage) {
    if (!message.file_id) return null;

    const preview = filePreviews[message.file_id];

    if (!preview || preview.kind === "loading") {
      return (
        <div className="cf-preview-shell cf-preview-shell--loading">
          Preparing preview...
        </div>
      );
    }

    if (preview.kind === "image") {
      return (
        <div className="cf-preview-shell">
          <img
            src={preview.url}
            alt="preview"
            className="cf-preview-image"
          />
        </div>
      );
    }

    if (preview.kind === "audio") {
      return (
        <div className="cf-preview-shell">
          <audio controls className="cf-preview-audio">
            <source src={preview.url} type="audio/wav" />
            Your browser does not support audio
          </audio>
        </div>
      );
    }

    if (preview.kind === "video") {
      return (
        <div className="cf-preview-shell">
          <video
            controls
            playsInline
            preload="metadata"
            className="cf-preview-video"
          >
            <source src={preview.url} type="video/mp4" />
            Your browser does not support video
          </video>
        </div>
      );
    }

    if (preview.kind === "text") {
  return (
    <div className="cf-preview-shell">
      <pre
        className="cf-preview-shell--text"
        style={{
          margin: 0,
          background: "rgba(15, 23, 42, 0.96)",
          color: "#e5edf7",
          fontFamily: '"JetBrains Mono", "Fira Code", monospace',
          fontSize: "13px",
          lineHeight: 1.65,
          padding: "14px",
          borderRadius: "14px",
          maxHeight: "220px",
          overflow: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          border: "1px solid rgba(148, 163, 184, 0.14)",
        }}
      >
        {preview.text || "Empty text file"}
      </pre>
    </div>
  );
}

    if (preview.kind === "unknown") {
      return (
        <div className="cf-preview-shell cf-preview-shell--error">
          {preview.error ?? "Preview unavailable"}
        </div>
      );
    }

    return null;
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

      if (message.message_type === "stego_file") {
        void loadAccessibleFiles();
      }

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
        showToast(
          message.message_type === "stego_file"
            ? "New protected file received"
            : "New secure message received",
          "info"
        );
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
    void loadAccessibleFiles();
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
    for (const message of messages) {
      if (message.message_type === "stego_file" && message.file_id) {
        void prepareFilePreview(message);
      }
    }
  }, [messages, fileIndex]);

  useEffect(() => {
    return () => {
      Object.values(previewUrlsRef.current).forEach((url) => URL.revokeObjectURL(url));
      previewUrlsRef.current = {};
    };
  }, []);

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
          showToast("Realtime connection lost. Reconnecting...", "info");
          notifiedSocketOfflineRef.current = true;
        }

        reconnectTimeoutRef.current = window.setTimeout(connectSocket, 2000);
      };
    }

    connectSocket();

    return () => {
      isUnmounted = true;
      clearSocketArtifacts();
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [showToast]);

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  useEffect(() => {
    currentUserIdRef.current = myUserId;
  }, [myUserId]);

  useEffect(() => {
    if (!selectedFile) return;

    const inferred = inferStegoTypeFromFile(selectedFile);
    if (!inferred) return;

    if (inferred === "audio") {
      setStegoType("audio");
    } else if (inferred === "image") {
      setStegoType("image");
    } else if (inferred === "text") {
      setStegoType("text");
    } else if (inferred === "video") {
      setStegoType("video");
    }
  }, [selectedFile]);

  const hasConversation = Boolean(activeConversationId);

  return (
    <div className="chat-page chat-page--premium">
      <section className="chat-sidebar">
        <div className="chat-sidebar__header">
          <div>
            <p className="section-eyebrow">Secure Chat</p>
            <h1 className="section-title">Protected Conversations</h1>
            <p className="chat-sidebar__subtext">
              End-to-end protected messaging with inline secure file sharing.
            </p>
          </div>

          <button
            className="button button--secondary"
            onClick={() => void loadConversations(true)}
            disabled={loadingConversations}
            type="button"
            title="Refresh conversations"
            aria-label="Refresh conversations"
          >
            <RefreshCw size={16} className={loadingConversations ? "spin" : ""} />
          </button>
        </div>

        <div
          className={`chat-connection-pill chat-connection-pill--${socketStatus}`}
        >
          {socketStatus === "connected" ? (
            <>
              <Wifi size={16} />
              <span>Realtime active</span>
            </>
          ) : socketStatus === "connecting" ? (
            <>
              <LoaderCircle size={16} className="spin" />
              <span>Connecting…</span>
            </>
          ) : (
            <>
              <WifiOff size={16} />
              <span>Offline</span>
            </>
          )}
        </div>

        <div className="chat-sidebar__create">
          <div className="chat-sidebar__create-label">
            <Shield size={16} />
            <span>Start a new protected thread</span>
          </div>

          <div className="chat-sidebar__create-row">
            <input
              className="auth-input"
              type="email"
              placeholder="Start chat with email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  void handleCreateConversation();
                }
              }}
            />

            <button
              className="button button--primary"
              onClick={() => void handleCreateConversation()}
              disabled={creatingConversation}
              type="button"
            >
              {creatingConversation ? "Creating..." : "New chat"}
            </button>
          </div>
        </div>

        <div className="chat-sidebar__search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search conversations"
            value={conversationSearch}
            onChange={(e) => setConversationSearch(e.target.value)}
          />
        </div>

        {pageError ? <div className="auth-alert auth-alert--error">{pageError}</div> : null}

        <div className="chat-conversation-list">
          {loadingConversations ? (
            <div className="chat-empty-state">Loading conversations…</div>
          ) : !filteredConversations.length ? (
            <div className="chat-empty-state">No conversations yet</div>
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
                <span>Protected live conversation</span>
              </div>
            </div>
          ) : (
            <div className="chat-empty-state chat-empty-state--inline">
              Select a conversation to view messages
            </div>
          )}
        </div>

        <div className="chat-thread__messages">
          {!hasConversation ? (
            <div className="chat-empty-state">
              Start or select a secure conversation to begin messaging.
            </div>
          ) : loadingMessages ? (
            <div className="chat-empty-state">Loading messages…</div>
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
                            {fileIndex[message.file_id ?? -1]?.filename ??
                              "Protected file attached"}
                          </div>

                          {renderFilePreview(message)}

                          {message.text_content ? (
                            <div className="chat-file-message__caption">
                              {message.text_content}
                            </div>
                          ) : null}

                          <div className="chat-file-message__actions">
                            <button
                              className="button button--secondary"
                              onClick={() => void handleDownloadFile(message)}
                              disabled={!message.file_id}
                              type="button"
                            >
                              <Download size={16} />
                              Download
                            </button>

                            <button
                              className="button button--secondary"
                              onClick={() => void handleExtract(message.id)}
                              disabled={extractingMessageId === message.id}
                              type="button"
                            >
                              <WandSparkles size={16} />
                              {extractingMessageId === message.id
                                ? "Extracting..."
                                : "Extract hidden data"}
                            </button>
                          </div>

                          {extractedData[message.id] ? (
                            <div className="chat-file-message__extract-result">
                              <strong>Hidden data</strong>
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
                <div className="chat-empty-state">
                  No messages yet. Send your first protected message.
                </div>
              ) : null}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {hasConversation ? (
          <div className="chat-thread__composer chat-thread__composer--premium">
            {showFileComposer ? (
              <div className="chat-file-composer">
                <div className="chat-file-composer__header">
                  <div>
                    <strong>Attach secure file</strong>
                    <p>Embed hidden data and send it as a protected message.</p>
                  </div>

                  <button
                    className="chat-file-composer__close"
                    onClick={resetFileComposer}
                    type="button"
                  >
                    <X size={16} />
                  </button>
                </div>

                <div className="chat-file-composer__grid">
                  <label className="chat-file-composer__field chat-file-composer__field--full">
                    <span>Carrier file</span>
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={(event) =>
                        setSelectedFile(event.target.files?.[0] ?? null)
                      }
                    />
                    <small>{selectedFileMeta ?? "Choose a supported file"}</small>
                  </label>

                  <label className="chat-file-composer__field">
                    <span>Stego type</span>
                    <select
                      className="chat-thread__select"
                      value={stegoType}
                      onChange={(event) =>
                        setStegoType(event.target.value as StegoType)
                      }
                    >
                      <option value="image">Image</option>
                      <option value="audio">Audio (WAV only)</option>
                      <option value="text">Text</option>
                      <option value="video">Video</option>
                    </select>
                  </label>

                  <label className="chat-file-composer__field">
                    <span>Message caption</span>
                    <input
                      value={caption}
                      onChange={(event) => setCaption(event.target.value)}
                      placeholder="Add context for the receiver"
                    />
                  </label>

                  <label className="chat-file-composer__field chat-file-composer__field--full">
                    <span>Secret data</span>
                    <textarea
                      rows={4}
                      value={secretData}
                      onChange={(event) => setSecretData(event.target.value)}
                      placeholder="Enter the hidden message you want to embed..."
                    />
                  </label>
                </div>

                {selectedFile ? (
                  <div className="chat-file-composer__meta-card">
                    <div className="chat-file-composer__meta-icon">
                      {getStegoIcon(stegoType)}
                    </div>
                    <div>
                      <strong>{selectedFile.name}</strong>
                      <p>
                        Carrier ready for {stegoType} steganography
                        {stegoType === "audio" ? " · WAV only" : ""}
                      </p>
                    </div>
                  </div>
                ) : null}

                {fileValidationError ? (
                  <div className="cf-inline-alert cf-inline-alert--error">
                    <AlertCircle size={16} />
                    <span>{fileValidationError}</span>
                  </div>
                ) : null}

                {sendingFile ? (
                  <div className="upload-progress">
                    <div
                      className="upload-progress__bar"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                ) : null}

                <div className="chat-file-composer__actions">
                  <button
                    className="button button--secondary"
                    onClick={resetFileComposer}
                    type="button"
                  >
                    Cancel
                  </button>

                  <button
                    className="button button--primary"
                    onClick={() => void handleSendFileMessage()}
                    disabled={sendingFile || Boolean(fileValidationError)}
                    type="button"
                  >
                    {sendingFile ? "Sending..." : "Send Secure File"}
                  </button>
                </div>
              </div>
            ) : null}

            <div className="chat-thread__input-row">
              <button
                className="button button--secondary chat-thread__attach-button"
                onClick={() => setShowFileComposer((prev) => !prev)}
                type="button"
              >
                <Paperclip size={16} />
                Attach Secure File
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