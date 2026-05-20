import { useEffect, useMemo, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const GUIDED_TOUR_STORAGE_KEY = "cryptofile_guided_tour_seen";
const GUIDED_TOUR_EVENT = "cryptofile:start-tour";

type GuidedTourStep = {
  path: string;
  selector: string;
  title: string;
  description: string;
  label: string;
};

type SpotlightRect = {
  top: number;
  left: number;
  width: number;
  height: number;
};

const guidedTourSteps: GuidedTourStep[] = [
  {
    path: "/dashboard",
    selector: ".dashboard-v2__hero-copy, .dashboard-v2__hero-actions",
    label: "Dashboard overview",
    title: "Your CryptoFile command center",
    description:
      "The dashboard is the starting point of the system. From here, users can quickly move to chat, the vault, the steganography lab and account security while also seeing a high-level snapshot of activity.",
  },
  {
    path: "/dashboard",
    selector: ".dashboard-v2__hero-actions",
    label: "Quick navigation",
    title: "Move between the main workflows",
    description:
      "These buttons are shortcuts to the most important workflows: secure conversations and the file vault. The tutorial does not require you to click them — it only shows where each action starts.",
  },
  {
    path: "/dashboard",
    selector: ".dashboard-v3__hero-status, .dashboard-v2__hero-status",
    label: "System snapshot",
    title: "Understand what is happening in the workspace",
    description:
      "This area summarizes the user's current workspace status, such as files, conversations and security-related signals. It helps users understand the state of the system at a glance.",
  },
  {
    path: "/chat",
    selector:
      ".chat-conversations__create, .chat-new-thread, .chat-sidebar__create, .chat-conversations__header, .chat-sidebar__header",
    label: "Create conversation",
    title: "Start a secure conversation",
    description:
      "The chat area is where users communicate with registered users. A conversation is created using another user's email, and the system keeps access limited to the conversation participants.",
  },
  {
    path: "/chat",
    selector:
      ".chat-thread__composer, .chat-thread__composer--premium, .chat-file-composer, .chat-thread",
    label: "Send protected content",
    title: "Send messages and steganographic files",
    description:
      "Inside a conversation, users can send text messages and attach supported media files. When sending a stego file, the hidden message is embedded into the media before it is shared.",
  },
  {
    path: "/files",
    selector: ".files-tabs, .files-panel, .vault-grid, .files-list",
    label: "Vault sections",
    title: "Separate owned files from shared files",
    description:
      "The vault separates files uploaded by the current user from files shared by others. This makes ownership and access permissions easier to understand.",
  },
  {
    path: "/files",
    selector: ".file-card__actions, .vault-card, .file-card, .files-panel",
    label: "Vault actions",
    title: "Preview, download, share and extract",
    description:
      "Each supported file can be previewed or downloaded. Owned files can be shared, and steganographic files can be extracted directly from the vault without moving back to the lab.",
  },
  {
    path: "/stego",
    selector: ".stego-mode-tabs, .stego-panel__top, .stego-panel",
    label: "Choose operation",
    title: "Embed or extract hidden data",
    description:
      "The Stego Lab has two main modes: embedding a secret message into a supported media file, or extracting a hidden message from a file that already contains one.",
  },
  {
    path: "/stego",
    selector: ".stego-type-grid, .stego-form, .stego-panel",
    label: "Supported media",
    title: "Use the right media type",
    description:
      "CryptoFile focuses on media-based steganography. Users should choose the matching media type — image, WAV audio or video — so the correct stego engine is used.",
  },
  {
    path: "/security",
    selector: ".security-v1__hero, .security-v2__status-grid, .security-v1__grid, .security-v1__card",
    label: "Account security",
    title: "Protect access to the account",
    description:
      "The security page centralizes account protection. Users can manage password-related actions, and the system also supports email verification during registration.",
  },
  {
    path: "/security",
    selector: ".security-v1__reauth-card, .security-v1__card--wide, .security-v1__grid, .security-v1__card",
    label: "Sensitive actions",
    title: "Re-authentication protects important changes",
    description:
      "Sensitive account operations should require clear validation and controlled flows. This reduces accidental changes and helps protect the user account.",
  },
];

function getSpotlightRect(selector: string): SpotlightRect | null {
  const element = document.querySelector(selector);

  if (!element) {
    return null;
  }

  const rect = element.getBoundingClientRect();
  const padding = 10;
  const maxWidth = Math.min(window.innerWidth - 32, 760);
  const maxHeight = Math.min(window.innerHeight - 32, 360);
  const width = Math.min(rect.width + padding * 2, maxWidth);
  const height = Math.min(rect.height + padding * 2, maxHeight);

  return {
    top: Math.min(
      Math.max(16, rect.top - padding),
      Math.max(16, window.innerHeight - height - 16)
    ),
    left: Math.min(
      Math.max(16, rect.left - padding),
      Math.max(16, window.innerWidth - width - 16)
    ),
    width,
    height,
  };
}

function getTooltipPosition(rect: SpotlightRect | null) {
  const tooltipWidth = 380;
  const gap = 18;

  if (!rect) {
    return {
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
    } as const;
  }

  const canPlaceRight = rect.left + rect.width + tooltipWidth + gap < window.innerWidth;
  const canPlaceBelow = rect.top + rect.height + 260 + gap < window.innerHeight;

  if (canPlaceRight) {
    return {
      top: `${Math.max(24, rect.top)}px`,
      left: `${rect.left + rect.width + gap}px`,
      transform: "none",
    } as const;
  }

  if (canPlaceBelow) {
    return {
      top: `${rect.top + rect.height + gap}px`,
      left: `${Math.min(Math.max(24, rect.left), window.innerWidth - tooltipWidth - 24)}px`,
      transform: "none",
    } as const;
  }

  return {
    top: `${Math.max(24, rect.top - 260 - gap)}px`,
    left: `${Math.min(Math.max(24, rect.left), window.innerWidth - tooltipWidth - 24)}px`,
    transform: "none",
  } as const;
}

function startGuidedTour() {
  window.dispatchEvent(new Event(GUIDED_TOUR_EVENT));
}

function GuidedTour() {
  const navigate = useNavigate();
  const location = useLocation();

  const [isOpen, setIsOpen] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [spotlightRect, setSpotlightRect] = useState<SpotlightRect | null>(null);

  const currentStep = guidedTourSteps[stepIndex];

  const tooltipStyle = useMemo(
    () => getTooltipPosition(spotlightRect),
    [spotlightRect]
  );

  useEffect(() => {
    const alreadySeen = window.localStorage.getItem(GUIDED_TOUR_STORAGE_KEY);

    if (!alreadySeen) {
      const timer = window.setTimeout(() => {
        setStepIndex(0);
        setIsOpen(true);
      }, 450);

      return () => window.clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    function handleStartTour() {
      window.localStorage.removeItem(GUIDED_TOUR_STORAGE_KEY);
      setStepIndex(0);
      setIsOpen(true);
    }

    window.addEventListener(GUIDED_TOUR_EVENT, handleStartTour);

    return () => {
      window.removeEventListener(GUIDED_TOUR_EVENT, handleStartTour);
    };
  }, []);

  useEffect(() => {
    if (!isOpen || !currentStep) return;

    if (location.pathname !== currentStep.path) {
      navigate(currentStep.path);
    }
  }, [currentStep, isOpen, location.pathname, navigate]);

  useEffect(() => {
    if (!isOpen || !currentStep) return;

    let frameId = 0;

    function updateSpotlight() {
      const element = document.querySelector(currentStep.selector);

      if (element) {
        element.scrollIntoView({
          behavior: "smooth",
          block: "center",
          inline: "nearest",
        });
      }

      window.setTimeout(() => {
        setSpotlightRect(getSpotlightRect(currentStep.selector));
      }, 240);
    }

    frameId = window.requestAnimationFrame(updateSpotlight);

    function handleViewportChange() {
      setSpotlightRect(getSpotlightRect(currentStep.selector));
    }

    window.addEventListener("resize", handleViewportChange);
    window.addEventListener("scroll", handleViewportChange, true);

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", handleViewportChange);
      window.removeEventListener("scroll", handleViewportChange, true);
    };
  }, [currentStep, isOpen, location.pathname]);

  function finishTour() {
    window.localStorage.setItem(GUIDED_TOUR_STORAGE_KEY, "true");
    setIsOpen(false);
  }

  function nextStep() {
    if (stepIndex >= guidedTourSteps.length - 1) {
      finishTour();
      return;
    }

    setStepIndex((current) => current + 1);
  }

  function previousStep() {
    setStepIndex((current) => Math.max(0, current - 1));
  }

  if (!isOpen || !currentStep) {
    return null;
  }

  const isLastStep = stepIndex === guidedTourSteps.length - 1;

  return (
    <div className="guided-tour" aria-live="polite">
      <div className="guided-tour__shade" onClick={finishTour} />

      {spotlightRect ? (
        <div
          className="guided-tour__spotlight"
          style={{
            top: spotlightRect.top,
            left: spotlightRect.left,
            width: spotlightRect.width,
            height: spotlightRect.height,
          }}
        />
      ) : null}

      <section className="guided-tour__card" style={tooltipStyle}>
        <button
          aria-label="Skip tutorial"
          className="guided-tour__close"
          onClick={finishTour}
          type="button"
        >
          <X size={18} />
        </button>

        <div className="guided-tour__meta">
          <span>{currentStep.label}</span>
          <strong>
            {stepIndex + 1}/{guidedTourSteps.length}
          </strong>
        </div>

        <h2>{currentStep.title}</h2>
        <p>{currentStep.description}</p>

        <div className="guided-tour__progress">
          {guidedTourSteps.map((step, index) => (
            <button
              key={step.label}
              aria-label={`Go to tutorial step ${index + 1}`}
              className={
                index === stepIndex
                  ? "guided-tour__dot guided-tour__dot--active"
                  : "guided-tour__dot"
              }
              onClick={() => setStepIndex(index)}
              type="button"
            />
          ))}
        </div>

        <div className="guided-tour__actions">
          <button className="button button--ghost" onClick={finishTour} type="button">
            Skip tutorial
          </button>

          <div className="guided-tour__nav">
            <button
              className="button button--secondary"
              disabled={stepIndex === 0}
              onClick={previousStep}
              type="button"
            >
              <ChevronLeft size={16} />
              Back
            </button>

            <button className="button button--primary" onClick={nextStep} type="button">
              {isLastStep ? "Finish tour" : "Next"}
              {!isLastStep ? <ChevronRight size={16} /> : null}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

export function AppShell() {
  return (
    <div className="app-shell-v2">
      <Sidebar />

      <div className="app-shell-v2__main">
        <Topbar />
        <main className="app-shell-v2__content">
          <Outlet />
        </main>
      </div>

      <button
        className="guided-tour-launcher"
        onClick={startGuidedTour}
        type="button"
      >
        <span className="guided-tour-launcher__dot" />
        Guided tour
      </button>

      <GuidedTour />
    </div>
  );
}
