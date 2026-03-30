import { useEffect, useMemo, useRef, useState } from "react";
import {
  Download,
  Files,
  FolderLock,
  RefreshCw,
  Share2,
  ImageIcon,
  FileAudio2,
  FileText,
  Film,
  File as FileIcon,
} from "lucide-react";
import { filesService, type FileItem } from "../features/files/files.service";

type ActiveTab = "owned" | "shared";

type FilePreviewState =
  | { kind: "loading" }
  | { kind: "image"; url: string }
  | { kind: "audio"; url: string }
  | { kind: "video"; url: string }
  | { kind: "text"; text: string }
  | { kind: "other" }
  | { kind: "error"; message: string };

function inferKind(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";

  if (["png", "jpg", "jpeg", "gif", "webp", "bmp"].includes(ext)) return "image";
  if (["mp3", "wav", "ogg", "m4a", "aac"].includes(ext)) return "audio";
  if (["mp4", "webm", "mov", "avi", "ogg"].includes(ext)) return "video";
  if (["txt", "md", "csv", "json", "log"].includes(ext)) return "text";
  return "other";
}

function inferMimeType(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";

  if (["png", "jpg", "jpeg", "gif", "webp", "bmp"].includes(ext)) {
    return `image/${ext === "jpg" ? "jpeg" : ext}`;
  }

  if (["mp3", "wav", "ogg", "m4a", "aac"].includes(ext)) {
    if (ext === "mp3") return "audio/mpeg";
    if (ext === "m4a") return "audio/mp4";
    return `audio/${ext}`;
  }

  if (["mp4", "webm", "mov", "avi", "ogg"].includes(ext)) {
    if (ext === "mov") return "video/quicktime";
    if (ext === "avi") return "video/x-msvideo";
    return `video/${ext}`;
  }

  if (["txt", "md", "csv", "json", "log"].includes(ext)) {
    return "text/plain";
  }

  return "application/octet-stream";
}

function formatDate(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

function cleanFilename(filename: string) {
  const underscoreIndex = filename.indexOf("_");
  if (underscoreIndex > 20) {
    return filename.slice(underscoreIndex + 1);
  }
  return filename;
}

export function FilesPage() {
  const [ownedFiles, setOwnedFiles] = useState<FileItem[]>([]);
  const [sharedFiles, setSharedFiles] = useState<FileItem[]>([]);
  const [activeTab, setActiveTab] = useState<ActiveTab>("owned");

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [pageError, setPageError] = useState("");
  const [downloadLoadingId, setDownloadLoadingId] = useState<number | null>(null);

  const [shareFileId, setShareFileId] = useState<number | null>(null);
  const [targetEmail, setTargetEmail] = useState("");
  const [shareLoading, setShareLoading] = useState(false);
  const [shareError, setShareError] = useState("");
  const [shareSuccess, setShareSuccess] = useState("");

  const [previews, setPreviews] = useState<Record<number, FilePreviewState>>({});
  const previewUrlsRef = useRef<Record<number, string>>({});

  const visibleFiles = useMemo(() => {
    return activeTab === "owned" ? ownedFiles : sharedFiles;
  }, [activeTab, ownedFiles, sharedFiles]);

  async function loadFiles(showRefreshState = false) {
    try {
      if (showRefreshState) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setPageError("");

      const data = await filesService.listFiles();
      setOwnedFiles(data.owned_files ?? []);
      setSharedFiles(data.shared_with_me ?? []);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to load files. Please try again.";
      setPageError(message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadFiles();
  }, []);

  useEffect(() => {
    const onFocus = () => {
      void loadFiles(true);
    };

    const onVisibility = () => {
      if (document.visibilityState === "visible") {
        void loadFiles(true);
      }
    };

    const interval = window.setInterval(() => {
      void loadFiles(true);
    }, 15000);

    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      window.clearInterval(interval);
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, []);

  useEffect(() => {
    return () => {
      Object.values(previewUrlsRef.current).forEach((url) => URL.revokeObjectURL(url));
      previewUrlsRef.current = {};
    };
  }, []);

  useEffect(() => {
    visibleFiles.forEach((file) => {
      if (previews[file.id]) return;
      void preparePreview(file);
    });
  }, [visibleFiles]);

  async function preparePreview(file: FileItem) {
    setPreviews((prev) => ({ ...prev, [file.id]: { kind: "loading" } }));

    try {
      const blob = await filesService.getFileBlob(file.id);
      const kind = inferKind(file.filename);

      if (kind === "text") {
        const text = await new Blob([blob], { type: inferMimeType(file.filename) }).text();
        setPreviews((prev) => ({
          ...prev,
          [file.id]: { kind: "text", text: text.slice(0, 500) },
        }));
        return;
      }

      if (kind === "image" || kind === "audio" || kind === "video") {
        const objectUrl = URL.createObjectURL(
          new Blob([blob], { type: inferMimeType(file.filename) })
        );
        previewUrlsRef.current[file.id] = objectUrl;

        setPreviews((prev) => ({
          ...prev,
          [file.id]: { kind, url: objectUrl } as FilePreviewState,
        }));
        return;
      }

      setPreviews((prev) => ({
        ...prev,
        [file.id]: { kind: "other" },
      }));
    } catch (error) {
      setPreviews((prev) => ({
        ...prev,
        [file.id]: {
          kind: "error",
          message: error instanceof Error ? error.message : "Preview unavailable",
        },
      }));
    }
  }

  async function handleShareSubmit(fileId: number) {
    if (!targetEmail.trim()) {
      setShareError("Please enter an email address");
      return;
    }

    try {
      setShareLoading(true);
      setShareError("");
      setShareSuccess("");

      const result = await filesService.shareFile({
        file_id: fileId,
        target_email: targetEmail.trim(),
      });

      setShareSuccess(`Shared successfully with ${result.shared_with_email}`);
      setTargetEmail("");
      setShareFileId(null);
      await loadFiles(true);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to share file";
      setShareError(message);
    } finally {
      setShareLoading(false);
    }
  }

  async function handleDownload(file: FileItem) {
    try {
      setPageError("");
      setDownloadLoadingId(file.id);
      await filesService.downloadFile(file.id, file.filename);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to download file";
      setPageError(message);
    } finally {
      setDownloadLoadingId(null);
    }
  }

  function openSharePanel(fileId: number) {
    setShareFileId(fileId);
    setTargetEmail("");
    setShareError("");
    setShareSuccess("");
  }

  function closeSharePanel() {
    setShareFileId(null);
    setTargetEmail("");
    setShareError("");
  }

  function renderPreview(file: FileItem) {
    const preview = previews[file.id];

    if (!preview || preview.kind === "loading") {
      return <div className="vault-preview vault-preview--loading">Preparing preview…</div>;
    }

    if (preview.kind === "image") {
      return (
        <div className="vault-preview">
          <img
            src={preview.url}
            alt={file.filename}
            className="vault-preview__image"
          />
        </div>
      );
    }

    if (preview.kind === "audio") {
      return (
        <div className="vault-preview">
          <div className="vault-preview__media-top">
            <FileAudio2 size={16} />
            <span>Audio preview</span>
          </div>
          <audio controls src={preview.url} className="vault-preview__audio" />
        </div>
      );
    }

    if (preview.kind === "video") {
      return (
        <div className="vault-preview">
          <video controls src={preview.url} className="vault-preview__video" />
        </div>
      );
    }

    if (preview.kind === "text") {
      return (
        <div className="vault-preview vault-preview--text">
          <div className="vault-preview__media-top">
            <FileText size={16} />
            <span>Text snippet</span>
          </div>
          <pre className="vault-preview__text">{preview.text || "Empty text file"}</pre>
        </div>
      );
    }

    if (preview.kind === "error") {
      return (
        <div className="vault-preview vault-preview--error">
          Preview unavailable: {preview.message}
        </div>
      );
    }

    return (
      <div className="vault-preview vault-preview--other">
        <div className="vault-preview__placeholder">
          <FileIcon size={20} />
          <span>No inline preview</span>
        </div>
      </div>
    );
  }

  function renderTypeIcon(file: FileItem) {
    const kind = inferKind(file.filename);

    if (kind === "image") return <ImageIcon size={16} />;
    if (kind === "audio") return <FileAudio2 size={16} />;
    if (kind === "video") return <Film size={16} />;
    if (kind === "text") return <FileText size={16} />;
    return <FileIcon size={16} />;
  }

  return (
    <div className="files-page">
      <div className="files-page__header">
        <div>
          <p className="section-eyebrow">My Files</p>
          <h1 className="section-title">File Vault</h1>
          <p className="section-text">
            Browse your protected files, preview them inline, access shared assets,
            and grant access to other users.
          </p>
        </div>

        <button
          className="button button--secondary"
          onClick={() => void loadFiles(true)}
          disabled={refreshing}
          type="button"
        >
          <RefreshCw size={16} className={refreshing ? "spin" : ""} />
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="files-summary-grid">
        <article className="files-summary-card">
          <div className="files-summary-card__icon">
            <FolderLock size={18} />
          </div>
          <span className="files-summary-card__label">Owned files</span>
          <strong className="files-summary-card__value">{ownedFiles.length}</strong>
        </article>

        <article className="files-summary-card">
          <div className="files-summary-card__icon">
            <Files size={18} />
          </div>
          <span className="files-summary-card__label">Shared with me</span>
          <strong className="files-summary-card__value">{sharedFiles.length}</strong>
        </article>
      </div>

      <div className="files-panel">
        <div className="files-tabs">
          <button
            className={`files-tab ${activeTab === "owned" ? "files-tab--active" : ""}`}
            onClick={() => setActiveTab("owned")}
            type="button"
          >
            Owned Files
          </button>
          <button
            className={`files-tab ${activeTab === "shared" ? "files-tab--active" : ""}`}
            onClick={() => setActiveTab("shared")}
            type="button"
          >
            Shared With Me
          </button>
        </div>

        {pageError ? (
          <div className="auth-alert auth-alert--error">{pageError}</div>
        ) : null}

        {shareSuccess ? (
          <div className="files-alert files-alert--success">{shareSuccess}</div>
        ) : null}

        {loading ? (
          <div className="files-empty-state">
            <p>Loading files...</p>
          </div>
        ) : visibleFiles.length === 0 ? (
          <div className="files-empty-state">
            <p className="files-empty-state__title">
              {activeTab === "owned" ? "No owned files yet" : "No shared files yet"}
            </p>
            <p className="files-empty-state__text">
              {activeTab === "owned"
                ? "Files created through steganography flows will appear here."
                : "Files shared by other users will appear here."}
            </p>
          </div>
        ) : (
          <div className="vault-grid">
            {visibleFiles.map((file) => (
              <article key={file.id} className="vault-card">
                <div className="vault-card__top">
                  <div className="vault-card__badge-group">
                    <span className="file-card__badge">
                      {file.is_owner ? "Owner" : "Shared"}
                    </span>
                    <span className="vault-card__type-badge">
                      {renderTypeIcon(file)}
                      {inferKind(file.filename)}
                    </span>
                  </div>

                  <span className="file-card__date">{formatDate(file.created_at)}</span>
                </div>

                <div className="vault-card__title-group">
                  <h3 className="file-card__title">{cleanFilename(file.filename)}</h3>
                  <p className="file-card__subtitle">
                    File ID: {file.id} · Protected asset ready for download
                  </p>
                </div>

                {renderPreview(file)}

                <div className="file-card__actions">
                  <button
                    className="button button--secondary"
                    onClick={() => void handleDownload(file)}
                    type="button"
                    disabled={downloadLoadingId === file.id}
                  >
                    <Download size={16} />
                    {downloadLoadingId === file.id ? "Downloading..." : "Download"}
                  </button>

                  {file.is_owner ? (
                    <button
                      className="button button--primary"
                      onClick={() => openSharePanel(file.id)}
                      type="button"
                    >
                      <Share2 size={16} />
                      Share
                    </button>
                  ) : null}
                </div>

                {shareFileId === file.id ? (
                  <div className="file-share-panel">
                    <div className="file-share-panel__header">
                      <h4>Share this file</h4>
                      <button
                        className="file-share-panel__close"
                        onClick={closeSharePanel}
                        type="button"
                      >
                        Close
                      </button>
                    </div>

                    <div className="file-share-panel__form">
                      <input
                        className="auth-input"
                        type="email"
                        placeholder="Enter recipient email"
                        value={targetEmail}
                        onChange={(e) => setTargetEmail(e.target.value)}
                      />

                      <button
                        className="button button--primary"
                        onClick={() => void handleShareSubmit(file.id)}
                        disabled={shareLoading}
                        type="button"
                      >
                        {shareLoading ? "Sharing..." : "Confirm Share"}
                      </button>
                    </div>

                    {shareError ? (
                      <div className="auth-alert auth-alert--error">{shareError}</div>
                    ) : null}
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}