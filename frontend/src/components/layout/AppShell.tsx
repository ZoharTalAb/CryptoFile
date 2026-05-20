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
    selector: ".dashboard-v2__hero-actions",
    label: "Dashboard shortcuts",
    title: "Start from your workspace",
    description:
      "These shortcuts take you to the main areas of CryptoFile. The tour will move between pages and highlight what each area is used for.",
  },
  {
    path: "/chat",
    selector:
      ".chat-conversations__create, .chat-new-thread, .chat-sidebar__create, .chat-conversations__header",
    label: "Secure chat",
    title: "Create conversations and send protected files",
    description:
      "The chat is where users communicate, send media files and share steganographic files inside a secure conversation.",
  },
  {
    path: "/files",
    selector: ".files-tabs, .files-panel, .vault-grid, .files-list",
    label: "Files vault",
    title: "Preview, download, share and extract",
    description:
      "The vault stores files you own and files shared with you. From here you can preview media, download files, share owned files and extract hidden messages.",
  },
  {
    path: "/stego",
    selector: ".stego-panel, .stego-mode-tabs, .stego-type-grid",
    label: "Stego Lab",
    title: "Test embedding and extraction",
    description:
      "The Stego Lab lets you embed a secret message into supported media or extract hidden content from a prepared file without opening a chat.",
  },
  {
    path: "/security",
    selector: ".security-v1__grid, .security-v1__hero, .security-v1__card",
    label: "Account security",
    title: "Manage access and password security",
    description:
      "The security area helps users manage account protection, including password updates and security controls around access.",
  },
];

function getSpotlightRect(selector: string): SpotlightRect | null {
  const element = document.querySelector(selector);

  if (!element) {
    return null;
  }

  const rect = element.getBoundingClientRect();
  const padding = 12;

  return {
    top: Math.max(12, rect.top - padding),
    left: Math.max(12, rect.left - padding),
    width: Math.min(window.innerWidth - 24, rect.width + padding * 2),
    height: Math.min(window.innerHeight - 24, rect.height + padding * 2),
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
          inline: "center",
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

      <GuidedTour />
    </div>
  );
}
