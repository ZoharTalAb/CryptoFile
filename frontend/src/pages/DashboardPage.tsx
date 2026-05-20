import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  FileKey2,
  Files,
  FolderLock,
  KeyRound,
  MessageSquareLock,
  ShieldCheck,
  Share2,
  Sparkles,
  Vault,
  X,
} from "lucide-react";

import { useAuth } from "../features/auth/context/AuthContext";
import { chatService, type ConversationItem } from "../features/chat/chat.service";
import {
  filesService,
  type FileItem,
} from "../features/files/files.service";

type DashboardActivity =
  | {
      id: string;
      type: "conversation";
      title: string;
      subtitle: string;
      createdAt: string;
    }
  | {
      id: string;
      type: "file";
      title: string;
      subtitle: string;
      createdAt: string;
    };


type OnboardingStep = {
  title: string;
  eyebrow: string;
  description: string;
  icon: React.ComponentType<{ size?: number }>;
  highlights: string[];
  actionLabel?: string;
  actionPath?: string;
};

const ONBOARDING_STORAGE_KEY = "cryptofile_onboarding_seen";

const onboardingSteps: OnboardingStep[] = [
  {
    title: "Welcome to CryptoFile",
    eyebrow: "Start here",
    description:
      "CryptoFile combines secure messaging, protected file sharing and steganography in one private workspace.",
    icon: ShieldCheck,
    highlights: [
      "Your account is protected with secure authentication.",
      "Files and messages are managed through a controlled workspace.",
      "Hidden payloads can be embedded inside supported media files.",
    ],
  },
  {
    title: "Secure Chat",
    eyebrow: "Conversations",
    description:
      "Use the chat to communicate with other users and send protected media files with hidden messages.",
    icon: MessageSquareLock,
    highlights: [
      "Create a conversation with another registered user.",
      "Attach image, audio or video files.",
      "Send steganographic files directly inside the conversation.",
    ],
    actionLabel: "Open chat later",
    actionPath: "/chat",
  },
  {
    title: "Files Vault",
    eyebrow: "Protected assets",
    description:
      "The vault gives you one place to preview, download, share and extract hidden data from files.",
    icon: Vault,
    highlights: [
      "See files you own and files shared with you.",
      "Download or preview supported media.",
      "Extract hidden messages directly from the vault.",
    ],
    actionLabel: "Open vault later",
    actionPath: "/files",
  },
  {
    title: "Stego Lab",
    eyebrow: "Embed and extract",
    description:
      "The lab is a focused area for testing steganography operations without opening a chat.",
    icon: Sparkles,
    highlights: [
      "Upload supported media files.",
      "Embed a secret message into the file.",
      "Extract a hidden message from a prepared file.",
    ],
    actionLabel: "Open lab later",
    actionPath: "/stego",
  },
  {
    title: "Account Security",
    eyebrow: "Stay protected",
    description:
      "CryptoFile includes email verification, password controls and account security tools to protect access.",
    icon: KeyRound,
    highlights: [
      "New accounts are verified using an email code.",
      "Passwords can be updated from the Security page.",
      "Access is controlled before sensitive actions are allowed.",
    ],
    actionLabel: "Review security later",
    actionPath: "/security",
  },
];

function parseServerDate(value?: string | null) {
  if (!value) return null;

  const hasTimezone = /([zZ]|[+\-]\d{2}:\d{2})$/.test(value);
  const normalized = hasTimezone ? value : `${value}Z`;
  const parsed = new Date(normalized);

  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function formatRelative(value?: string | null) {
  const parsed = parseServerDate(value);
  if (!parsed) return "Recently";

  const diffMs = Date.now() - parsed.getTime();
  const diffMinutes = Math.max(1, Math.floor(diffMs / 1000 / 60));

  if (diffMinutes < 60) {
    return `${diffMinutes} min ago`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) {
    return `${diffDays}d ago`;
  }

  return parsed.toLocaleDateString();
}

function getConversationName(conversation: ConversationItem) {
  return conversation.other_user?.email ?? "Secure contact";
}

function getConversationTimestamp(conversation: ConversationItem) {
  return conversation.last_message?.created_at ?? conversation.created_at;
}

function getConversationPreview(conversation: ConversationItem) {
  const lastMessage = conversation.last_message;

  if (!lastMessage) {
    return "Conversation created";
  }

  if (lastMessage.message_type === "stego_file") {
    return "Protected file exchanged";
  }

  if (lastMessage.text_content?.trim()) {
    return lastMessage.text_content;
  }

  return "Secure thread updated";
}

function buildActivity(
  conversations: ConversationItem[],
  ownedFiles: FileItem[],
  sharedFiles: FileItem[]
): DashboardActivity[] {
  const conversationActivity: DashboardActivity[] = conversations.map(
    (conversation) => ({
      id: `conversation-${conversation.id}`,
      type: "conversation",
      title: getConversationName(conversation),
      subtitle: getConversationPreview(conversation),
      createdAt: getConversationTimestamp(conversation) ?? "",
    })
  );

  const fileActivity: DashboardActivity[] = [...ownedFiles, ...sharedFiles].map(
    (file) => ({
      id: `file-${file.id}`,
      type: "file",
      title: file.filename,
      subtitle: file.is_owner
        ? "Protected file stored in your vault"
        : "Shared with you securely",
      createdAt: file.created_at ?? "",
    })
  );

  return [...conversationActivity, ...fileActivity]
    .sort((a, b) => {
      const aTime = parseServerDate(a.createdAt)?.getTime() ?? 0;
      const bTime = parseServerDate(b.createdAt)?.getTime() ?? 0;
      return bTime - aTime;
    })
    .slice(0, 6);
}

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [ownedFiles, setOwnedFiles] = useState<FileItem[]>([]);
  const [sharedFiles, setSharedFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState("");
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingStep, setOnboardingStep] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        setLoading(true);
        setPageError("");

        const [conversationData, fileData] = await Promise.all([
          chatService.listConversations(),
          filesService.listFiles(),
        ]);

        if (!active) return;

        setConversations(conversationData ?? []);
        setOwnedFiles(fileData.owned_files ?? []);
        setSharedFiles(fileData.shared_with_me ?? []);
      } catch (error) {
        if (!active) return;

        const message =
          error instanceof Error ? error.message : "Failed to load dashboard";
        setPageError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const alreadySeen = window.localStorage.getItem(ONBOARDING_STORAGE_KEY);

    if (!alreadySeen) {
      setShowOnboarding(true);
    }
  }, []);

  function openOnboarding() {
    setOnboardingStep(0);
    setShowOnboarding(true);
  }

  function closeOnboarding() {
    window.localStorage.setItem(ONBOARDING_STORAGE_KEY, "true");
    setShowOnboarding(false);
  }

  function nextOnboardingStep() {
    if (onboardingStep >= onboardingSteps.length - 1) {
      closeOnboarding();
      return;
    }

    setOnboardingStep((current) => current + 1);
  }

  function previousOnboardingStep() {
    setOnboardingStep((current) => Math.max(0, current - 1));
  }

  const totalFiles = ownedFiles.length + sharedFiles.length;
  const totalUnread = conversations.reduce(
    (sum, conversation) => sum + (conversation.unread_count ?? 0),
    0
  );
  const activeThreads = conversations.length;

  const recentActivity = useMemo(
    () => buildActivity(conversations, ownedFiles, sharedFiles),
    [conversations, ownedFiles, sharedFiles]
  );

  const recentContacts = useMemo(
    () =>
      conversations
        .slice()
        .sort((a, b) => {
          const aTime = parseServerDate(getConversationTimestamp(a))?.getTime() ?? 0;
          const bTime = parseServerDate(getConversationTimestamp(b))?.getTime() ?? 0;
          return bTime - aTime;
        })
        .slice(0, 3),
    [conversations]
  );

  const latestOwnedFile = useMemo(() => {
    return ownedFiles
      .slice()
      .sort((a, b) => {
        const aTime = parseServerDate(a.created_at)?.getTime() ?? 0;
        const bTime = parseServerDate(b.created_at)?.getTime() ?? 0;
        return bTime - aTime;
      })[0];
  }, [ownedFiles]);

  const firstName = user?.email?.split("@")[0] ?? "Operator";

  return (
    <div className="dashboard-v2 dashboard-v3">
      <div className="dashboard-v2__backdrop">
        <div className="dashboard-v2__orb dashboard-v2__orb--one" />
        <div className="dashboard-v2__orb dashboard-v2__orb--two" />
        <div className="dashboard-v2__grid" />
      </div>

      <section className="dashboard-v2__hero dashboard-v3__hero">
        <div className="dashboard-v2__hero-copy dashboard-v3__hero-copy">
          <div className="dashboard-v2__eyebrow">
            <ShieldCheck size={16} />
            Secure workspace
          </div>

          <h1 className="dashboard-v2__title dashboard-v3__title">
            <span className="dashboard-v3__title-line">Command your</span>
            <span className="dashboard-v3__title-line dashboard-v3__title-line--accent">
              secure workspace, {firstName}.
            </span>
          </h1>

          <p className="dashboard-v2__text dashboard-v3__hero-text">
            Encrypted chat, protected assets and steganographic operations —
            organized in one command surface built for secure flow.
          </p>

          <div className="dashboard-v2__hero-actions dashboard-v3__hero-actions">
            <button
              className="button button--primary dashboard-v2__cta"
              onClick={() => navigate("/chat")}
              type="button"
            >
              Open secure chat
              <ArrowRight size={16} />
            </button>

            <button
              className="button button--secondary dashboard-v2__cta"
              onClick={() => navigate("/files")}
              type="button"
            >
              Open vault files
            </button>

            <button
              className="button button--ghost dashboard-v2__cta"
              onClick={openOnboarding}
              type="button"
            >
              View quick tour
            </button>
          </div>
        </div>

        <div className="dashboard-v2__hero-status dashboard-v3__hero-status">
          <div className="dashboard-v3__hero-status-top">
            <p className="dashboard-v3__hero-panel-label">Live command matrix</p>
            <div className="dashboard-v2__status-pill">
              <Sparkles size={14} />
              Real workspace data
            </div>
          </div>

          <div className="dashboard-v3__hero-matrix">
            <div className="dashboard-v3__hero-metric">
              <span>Protected files</span>
              <strong>{loading ? "—" : totalFiles}</strong>
              <small>
                {loading
                  ? "Loading vault state"
                  : `${ownedFiles.length} owned · ${sharedFiles.length} shared`}
              </small>
            </div>

            <div className="dashboard-v3__hero-metric">
              <span>Secure threads</span>
              <strong>{loading ? "—" : activeThreads}</strong>
              <small>
                {loading ? "Loading conversations" : "Active encrypted threads"}
              </small>
            </div>

            <div className="dashboard-v3__hero-metric">
              <span>Unread queue</span>
              <strong>{loading ? "—" : totalUnread}</strong>
              <small>
                {loading ? "Loading alerts" : "Pending secure attention"}
              </small>
            </div>
          </div>
        </div>
      </section>

      {pageError ? (
        <div className="files-alert auth-alert--error">{pageError}</div>
      ) : null}

      <section className="dashboard-v2__top-grid dashboard-v3__top-grid">
        <button
          className="dashboard-v2__action-panel dashboard-v2__action-panel--primary"
          onClick={() => navigate("/chat")}
          type="button"
        >
          <div className="dashboard-v2__action-icon">
            <MessageSquareLock size={24} />
          </div>

          <div className="dashboard-v2__action-copy">
            <h3>Send Secure Message</h3>
            <p>
              Open realtime encrypted conversations and continue protected
              threads with live delivery.
            </p>
          </div>
        </button>

        <button
          className="dashboard-v2__action-panel"
          onClick={() => navigate("/files")}
          type="button"
        >
          <div className="dashboard-v2__action-icon">
            <FolderLock size={24} />
          </div>

          <div className="dashboard-v2__action-copy">
            <h3>Vault Files</h3>
            <p>
              Access owned and shared files stored inside your protected
              workspace.
            </p>
          </div>
        </button>

        <button
          className="dashboard-v2__action-panel"
          onClick={() => navigate("/stego")}
          type="button"
        >
          <div className="dashboard-v2__action-icon">
            <Sparkles size={24} />
          </div>

          <div className="dashboard-v2__action-copy">
            <h3>Open Stego Lab</h3>
            <p>
              Create hidden payload assets and extract embedded content from
              supported media.
            </p>
          </div>
        </button>
      </section>

      <section className="dashboard-v2__content-grid dashboard-v3__content-grid">
        <div className="dashboard-v2__main-column">
          <div className="dashboard-v2__panel dashboard-v3__panel">
            <div className="dashboard-v2__panel-header">
              <div>
                <p className="dashboard-v2__panel-eyebrow">Live metrics</p>
                <h2 className="dashboard-v2__panel-title">Workspace overview</h2>
              </div>

              <div className="dashboard-v2__panel-badge">
                <Activity size={14} />
                Real data
              </div>
            </div>

            <div className="dashboard-v2__stats-grid dashboard-v3__stats-grid">
              <div className="dashboard-v2__stat-card dashboard-v3__stat-card dashboard-v3__stat-card--featured">
                <div className="dashboard-v2__stat-icon">
                  <Files size={18} />
                </div>
                <span className="dashboard-v2__stat-label">Protected files</span>
                <strong className="dashboard-v2__stat-value">
                  {loading ? "—" : totalFiles}
                </strong>
                <span className="dashboard-v2__stat-meta">
                  {loading
                    ? "Loading vault state"
                    : `${ownedFiles.length} owned · ${sharedFiles.length} shared`}
                </span>
              </div>

              <div className="dashboard-v2__stat-card dashboard-v3__stat-card">
                <div className="dashboard-v2__stat-icon">
                  <MessageSquareLock size={18} />
                </div>
                <span className="dashboard-v2__stat-label">Secure threads</span>
                <strong className="dashboard-v2__stat-value">
                  {loading ? "—" : activeThreads}
                </strong>
                <span className="dashboard-v2__stat-meta">
                  {loading
                    ? "Loading conversations"
                    : `${totalUnread} unread messages`}
                </span>
              </div>
            </div>

            <div className="dashboard-v3__micro-grid">
              <div className="dashboard-v3__micro-card">
                <span className="dashboard-v3__micro-label">Latest stored asset</span>
                <strong className="dashboard-v3__micro-title">
                  {latestOwnedFile?.filename ?? "No vault file yet"}
                </strong>
                <p className="dashboard-v3__micro-text">
                  {latestOwnedFile
                    ? `Stored ${formatRelative(latestOwnedFile.created_at)}`
                    : "Your next protected upload will appear here."}
                </p>
              </div>

              <div className="dashboard-v3__micro-card">
                <span className="dashboard-v3__micro-label">Attention state</span>
                <strong className="dashboard-v3__micro-title">
                  {totalUnread > 0 ? `${totalUnread} unread secure updates` : "All caught up"}
                </strong>
                <p className="dashboard-v3__micro-text">
                  {totalUnread > 0
                    ? "Unread messages are waiting in your encrypted inbox."
                    : "There are no unread secure messages right now."}
                </p>
              </div>
            </div>
          </div>

          <div className="dashboard-v2__panel dashboard-v3__panel">
            <div className="dashboard-v2__panel-header">
              <div>
                <p className="dashboard-v2__panel-eyebrow">Recent secure activity</p>
                <h2 className="dashboard-v2__panel-title">Latest operations</h2>
              </div>

              <button
                className="dashboard-v2__mini-link"
                onClick={() => navigate("/chat")}
                type="button"
              >
                View conversations
              </button>
            </div>

            {loading ? (
              <div className="dashboard-v2__activity-list">
                <div className="dashboard-v2__activity-item dashboard-v2__activity-item--loading" />
                <div className="dashboard-v2__activity-item dashboard-v2__activity-item--loading" />
                <div className="dashboard-v2__activity-item dashboard-v2__activity-item--loading" />
              </div>
            ) : recentActivity.length > 0 ? (
              <div className="dashboard-v2__activity-list dashboard-v3__activity-list">
                {recentActivity.map((item) => (
                  <div key={item.id} className="dashboard-v2__activity-item dashboard-v3__activity-item">
                    <div className="dashboard-v2__activity-icon">
                      {item.type === "conversation" ? (
                        <MessageSquareLock size={18} />
                      ) : (
                        <FileKey2 size={18} />
                      )}
                    </div>

                    <div className="dashboard-v2__activity-copy">
                      <div className="dashboard-v2__activity-topline">
                        <strong>{item.title}</strong>
                        <span>{formatRelative(item.createdAt)}</span>
                      </div>
                      <p>{item.subtitle}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="dashboard-v2__empty-state">
                <Clock3 size={18} />
                <div>
                  <strong>No secure activity yet</strong>
                  <p>Your latest conversations and files will appear here.</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <aside className="dashboard-v2__side-column dashboard-v3__side-column">
          <div className="dashboard-v2__panel dashboard-v2__panel--side dashboard-v3__panel">
            <div className="dashboard-v2__panel-header">
              <div>
                <p className="dashboard-v2__panel-eyebrow">Pinned resources</p>
                <h2 className="dashboard-v2__panel-title">Workspace focus</h2>
              </div>
            </div>

            <div className="dashboard-v2__resource-list">
              <button
                className="dashboard-v2__resource-card"
                onClick={() => navigate("/files")}
                type="button"
              >
                <div className="dashboard-v2__resource-icon">
                  <Vault size={18} />
                </div>
                <div>
                  <strong>Vault files</strong>
                  <p>{ownedFiles.length} protected assets in your workspace</p>
                </div>
              </button>

              <button
                className="dashboard-v2__resource-card"
                onClick={() => navigate("/chat")}
                type="button"
              >
                <div className="dashboard-v2__resource-icon">
                  <Share2 size={18} />
                </div>
                <div>
                  <strong>Secure chat</strong>
                  <p>{activeThreads} conversation threads available</p>
                </div>
              </button>

              <button
                className="dashboard-v2__resource-card"
                onClick={() => navigate("/stego")}
                type="button"
              >
                <div className="dashboard-v2__resource-icon">
                  <Sparkles size={18} />
                </div>
                <div>
                  <strong>Stego lab</strong>
                  <p>Embed and extract hidden payloads from supported media</p>
                </div>
              </button>
            </div>

            <div className="dashboard-v3__contact-block">
              <div className="dashboard-v3__contact-header">
                <span>Recent secure contacts</span>
              </div>

              {recentContacts.length > 0 ? (
                <div className="dashboard-v3__contact-list">
                  {recentContacts.map((conversation) => {
                    const name = getConversationName(conversation);
                    const initial = name.charAt(0).toUpperCase();

                    return (
                      <button
                        key={conversation.id}
                        className="dashboard-v3__contact-item"
                        onClick={() => navigate("/chat")}
                        type="button"
                      >
                        <div className="dashboard-v3__contact-avatar">{initial}</div>
                        <div className="dashboard-v3__contact-copy">
                          <strong>{name}</strong>
                          <span>
                            {formatRelative(getConversationTimestamp(conversation))}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="dashboard-v3__contact-empty">
                  No secure contacts yet.
                </div>
              )}
            </div>
          </div>
        </aside>
      </section>

      {showOnboarding ? (
        <div className="onboarding-modal__overlay" role="dialog" aria-modal="true">
          <div className="onboarding-modal">
            <button
              aria-label="Skip tutorial"
              className="onboarding-modal__close"
              onClick={closeOnboarding}
              type="button"
            >
              <X size={18} />
            </button>

            <div className="onboarding-modal__progress">
              {onboardingSteps.map((step, index) => (
                <button
                  key={step.title}
                  aria-label={`Go to tutorial step ${index + 1}`}
                  className={
                    index === onboardingStep
                      ? "onboarding-modal__dot onboarding-modal__dot--active"
                      : "onboarding-modal__dot"
                  }
                  onClick={() => setOnboardingStep(index)}
                  type="button"
                />
              ))}
            </div>

            {(() => {
              const step = onboardingSteps[onboardingStep];
              const StepIcon = step.icon;
              const isLastStep = onboardingStep === onboardingSteps.length - 1;

              return (
                <>
                  <div className="onboarding-modal__icon">
                    <StepIcon size={28} />
                  </div>

                  <p className="onboarding-modal__eyebrow">{step.eyebrow}</p>
                  <h2 className="onboarding-modal__title">{step.title}</h2>
                  <p className="onboarding-modal__text">{step.description}</p>

                  <div className="onboarding-modal__highlights">
                    {step.highlights.map((highlight) => (
                      <div key={highlight} className="onboarding-modal__highlight">
                        <CheckCircle2 size={16} />
                        <span>{highlight}</span>
                      </div>
                    ))}
                  </div>

                  <div className="onboarding-modal__footer">
                    <button
                      className="button button--ghost"
                      onClick={closeOnboarding}
                      type="button"
                    >
                      Skip tour
                    </button>

                    <div className="onboarding-modal__nav">
                      <button
                        className="button button--secondary"
                        disabled={onboardingStep === 0}
                        onClick={previousOnboardingStep}
                        type="button"
                      >
                        <ChevronLeft size={16} />
                        Back
                      </button>

                      {step.actionPath && step.actionLabel ? (
                        <button
                          className="button button--secondary"
                          onClick={() => {
                            closeOnboarding();
                            navigate(step.actionPath!);
                          }}
                          type="button"
                        >
                          {step.actionLabel}
                        </button>
                      ) : null}

                      <button
                        className="button button--primary"
                        onClick={nextOnboardingStep}
                        type="button"
                      >
                        {isLastStep ? "Start using CryptoFile" : "Next"}
                        {!isLastStep ? <ChevronRight size={16} /> : null}
                      </button>
                    </div>
                  </div>
                </>
              );
            })()}
          </div>
        </div>
      ) : null}

    </div>
  );
}