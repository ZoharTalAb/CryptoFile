import { Bell, LogOut, Settings } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { chatService, type ConversationItem } from "../../features/chat/chat.service";
import { useAuth } from "../../features/auth/context/AuthContext";

type NotificationItem = {
  id: number;
  name: string;
  message: string;
  time: string;
  unreadCount: number;
};

function formatRelative(value?: string | null) {
  if (!value) return "";

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";

  const diffMs = Date.now() - parsed.getTime();
  const diffMinutes = Math.max(1, Math.floor(diffMs / 1000 / 60));

  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function getTopbarTitle(pathname: string) {
  if (pathname.startsWith("/chat")) return "Secure Chat";
  if (pathname.startsWith("/files")) return "Vault Files";
  if (pathname.startsWith("/stego")) return "Stego Lab";
  if (pathname.startsWith("/security")) return "Security";
  return "Dashboard";
}

function buildNotifications(conversations: ConversationItem[]): NotificationItem[] {
  return conversations
    .filter((conversation) => (conversation.unread_count ?? 0) > 0)
    .map((conversation) => ({
      id: conversation.id,
      name: conversation.other_user?.email ?? "Unknown sender",
      message:
        conversation.last_message?.text_content?.trim() ||
        (conversation.last_message?.message_type === "stego_file"
          ? "Sent you a protected file"
          : "New secure message"),
      time: formatRelative(conversation.last_message?.created_at),
      unreadCount: conversation.unread_count ?? 0,
    }))
    .sort((a, b) => b.unreadCount - a.unreadCount);
}

export function Topbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const { logout } = useAuth();

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadNotifications() {
      try {
        const conversations = await chatService.listConversations();
        if (!active) return;
        setNotifications(buildNotifications(conversations));
      } catch (error) {
        if (!active) return;
        console.error("Failed to load notifications", error);
      }
    }

    loadNotifications();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (!dropdownRef.current) return;
      if (!dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open]);

  const unreadCount = useMemo(
    () => notifications.reduce((sum, item) => sum + item.unreadCount, 0),
    [notifications]
  );

  const title = getTopbarTitle(location.pathname);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="topbar-v2">
      <div className="topbar-v2__left">
        <p className="topbar-v2__eyebrow">CryptoFile workspace</p>
        <h2 className="topbar-v2__title">{title}</h2>
      </div>

      <div className="topbar-v2__right">
        <div className="topbar-v2__status">
          <span className="topbar-v2__status-dot" />
          SYSTEM ENCRYPTED
        </div>

        <div className="topbar-v2__icon-wrapper" ref={dropdownRef}>
          <button
            type="button"
            className="topbar-v2__icon-button"
            onClick={() => setOpen((prev) => !prev)}
            aria-label="Open notifications"
          >
            <Bell size={18} />
            {unreadCount > 0 ? (
              <span className="topbar-v2__badge">{unreadCount}</span>
            ) : null}
          </button>

          {open ? (
            <div className="topbar-v2__dropdown">
              <div className="topbar-v2__dropdown-header">
                <strong>Notifications</strong>
                <span>{unreadCount} unread</span>
              </div>

              {notifications.length === 0 ? (
                <p className="topbar-v2__empty">No new secure notifications</p>
              ) : (
                <div className="topbar-v2__notification-list">
                  {notifications.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className="topbar-v2__notification"
                      onClick={() => {
                        navigate("/chat");
                        setOpen(false);
                      }}
                    >
                      <div className="topbar-v2__notification-top">
                        <strong>{item.name}</strong>
                        <span>{item.time}</span>
                      </div>
                      <p>{item.message}</p>
                      <small>{item.unreadCount} unread message(s)</small>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>

        <button
          type="button"
          className="topbar-v2__icon-button"
          onClick={() => navigate("/security")}
          aria-label="Open security settings"
        >
          <Settings size={18} />
        </button>

        <button
          type="button"
          className="button button--secondary topbar-v2__logout-button"
          onClick={handleLogout}
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </header>
  );
}