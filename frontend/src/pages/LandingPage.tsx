import { motion } from "framer-motion";
import {
  ArrowRight,
  FileLock2,
  Lock,
  MessageSquareMore,
  Wand2,
} from "lucide-react";
import { Link } from "react-router-dom";

const heroAppear = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: {
    duration: 0.75,
    delay,
    ease: "easeOut" as const,
  },
});

const appear = (delay = 0) => ({
  initial: { opacity: 0, y: 28 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 as const },
  transition: {
    duration: 0.7,
    delay,
    ease: "easeOut" as const,
  },
});

const featurePillars = [
  {
    icon: <MessageSquareMore size={18} />,
    title: "Secure communication",
    text: "Protected conversations designed around file delivery instead of disconnected tools.",
  },
  {
    icon: <Wand2 size={18} />,
    title: "Steganography workflow",
    text: "Hide sensitive payloads inside supported media through a guided product experience.",
  },
  {
    icon: <FileLock2 size={18} />,
    title: "Controlled file handling",
    text: "Keep protected assets, access flows, and delivery state inside one workspace.",
  },
];

export function LandingPage() {
  return (
    <div className="landing-v4">
      <div className="landing-v4__noise" />
      <div className="landing-v4__orb landing-v4__orb--one" />
      <div className="landing-v4__orb landing-v4__orb--two" />
      <div className="landing-v4__grid" />

      <header className="landing-v4__nav">
        <motion.div className="landing-v4__brand" {...heroAppear(0)}>
          <span className="landing-v4__brand-mark">C</span>
          <span>CryptoFile</span>
        </motion.div>

        <motion.nav className="landing-v4__links" {...heroAppear(0.08)}>
          <a href="#product">Product</a>
          <a href="#workflow">Workflow</a>
          <a href="#security">Security</a>
        </motion.nav>

        <motion.div className="landing-v4__actions" {...heroAppear(0.12)}>
          <Link to="/login" className="button button--ghost">
            Sign In
          </Link>
          <Link to="/register" className="button button--primary">
            Create account
          </Link>
        </motion.div>
      </header>

      <section className="landing-v4__hero">
        <div className="landing-v4__hero-copy">
          <motion.div className="landing-v4__badge" {...heroAppear(0)}>
            <span className="landing-v4__badge-dot" />
            <span>Vault-grade protocol active</span>
          </motion.div>

          <motion.h1 className="landing-v4__title" {...heroAppear(0.08)}>
            Secure messages.
            <br />
            <span>Hidden in plain sight.</span>
          </motion.h1>

          <motion.p className="landing-v4__description" {...heroAppear(0.16)}>
            CryptoFile combines protected messaging, steganographic embedding,
            and secure file handling in one premium workspace built for privacy-first communication.
          </motion.p>

          <motion.div className="landing-v4__hero-actions" {...heroAppear(0.24)}>
            <Link to="/register" className="button button--primary">
              Initiate secure workspace
              <ArrowRight size={16} />
            </Link>

            <a href="#product" className="button button--secondary">
              Product overview
            </a>
          </motion.div>
        </div>

        <motion.div
          className="landing-v4__hero-visual"
          initial={{ opacity: 0, y: 28, scale: 0.985 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.18, ease: "easeOut" }}
        >
          <div className="landing-v4__mockup-glow" />

          <div className="landing-v4__mockup">
            <div className="landing-v4__mockup-topbar">
              <div className="landing-v4__mockup-dots">
                <span />
                <span />
                <span />
              </div>

              <div className="landing-v4__mockup-title">CryptoFile Vault</div>

              <div className="landing-v4__mockup-status">
                <Lock size={14} />
                <span>Protected</span>
              </div>
            </div>

            <div className="landing-v4__mockup-body">
              <div className="landing-v4__mockup-sidebar">
                <div className="landing-v4__mockup-brand">
                  <span className="landing-v4__mockup-brand-mark">C</span>
                  <div>
                    <strong>CryptoFile</strong>
                    <p>Private workspace</p>
                  </div>
                </div>

                <div className="landing-v4__mockup-nav">
                  <div className="landing-v4__mockup-nav-item landing-v4__mockup-nav-item--active">
                    Dashboard
                  </div>
                  <div className="landing-v4__mockup-nav-item">Secure Chat</div>
                  <div className="landing-v4__mockup-nav-item">File Vault</div>
                  <div className="landing-v4__mockup-nav-item">Stego Lab</div>
                </div>
              </div>

              <div className="landing-v4__mockup-main">
                <div className="landing-v4__mockup-panel landing-v4__mockup-panel--hero">
                  <span className="landing-v4__panel-pill">Secure delivery</span>
                  <h3>Protected asset prepared for transmission</h3>
                  <p>
                    Payload encrypted, embedded, and ready for controlled delivery.
                  </p>
                </div>

                <div className="landing-v4__mockup-stats">
                  <div className="landing-v4__stat-card landing-v4__stat-card--primary">
                    <span>Protected files</span>
                    <strong>689</strong>
                  </div>
                  <div className="landing-v4__stat-card">
                    <span>Secure threads</span>
                    <strong>372</strong>
                  </div>
                  <div className="landing-v4__stat-card">
                    <span>Embedded payloads</span>
                    <strong>124</strong>
                  </div>
                </div>

                <div className="landing-v4__mockup-activity">
                  <div className="landing-v4__activity-row">
                    <span className="landing-v4__activity-dot landing-v4__activity-dot--primary" />
                    <p>Carrier file upload validated</p>
                  </div>
                  <div className="landing-v4__activity-row">
                    <span className="landing-v4__activity-dot" />
                    <p>Payload concealed successfully</p>
                  </div>
                  <div className="landing-v4__activity-row">
                    <span className="landing-v4__activity-dot landing-v4__activity-dot--success" />
                    <p>Protected thread ready</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section className="landing-v4__trust-strip">
        <div className="landing-v4__trust-inner">
          <span>SOC2-aligned design</span>
          <span>AES-backed workflows</span>
          <span>Private file exchange</span>
          <span>Stego-enabled delivery</span>
        </div>
      </section>

      <section className="landing-v4__section landing-v4__section--split" id="product">
        <motion.div className="landing-v4__section-copy" {...appear(0)}>
          <p className="landing-v4__section-eyebrow">The methodology</p>
          <h2 className="landing-v4__section-title">
            Digital invisibility,
            <br />
            by design.
          </h2>
          <p className="landing-v4__section-text">
            CryptoFile turns a technically complex protection process into a clean,
            controlled product flow with less friction and stronger trust.
          </p>
        </motion.div>

        <motion.div className="landing-v4__steps" {...appear(0.08)}>
          <article className="landing-v4__step-card landing-v4__step-card--active">
            <span className="landing-v4__step-number">01</span>
            <h3>Payload hardening</h3>
            <p>Your message is encrypted before it ever touches a carrier file.</p>
          </article>

          <article className="landing-v4__step-card">
            <span className="landing-v4__step-number">02</span>
            <h3>Stealth embedding</h3>
            <p>Hidden content is woven into supported media through guided workflows.</p>
          </article>

          <article className="landing-v4__step-card">
            <span className="landing-v4__step-number">03</span>
            <h3>Secure distribution</h3>
            <p>Share protected files through controlled communication channels.</p>
          </article>
        </motion.div>
      </section>

      <section className="landing-v4__section" id="workflow">
        <motion.div className="landing-v4__section-heading" {...appear(0)}>
          <p className="landing-v4__section-eyebrow">Core capabilities</p>
          <h2 className="landing-v4__section-title landing-v4__section-title--center">
            One workspace. Three strong pillars.
          </h2>
        </motion.div>

        <div className="landing-v4__pillar-grid">
          {featurePillars.map((item, index) => (
            <motion.article
              key={item.title}
              className="landing-v4__pillar-card"
              {...appear(index * 0.06)}
            >
              <div className="landing-v4__pillar-icon">{item.icon}</div>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="landing-v4__section landing-v4__section--security" id="security">
        <motion.div className="landing-v4__security-card" {...appear(0)}>
          <div className="landing-v4__security-copy">
            <p className="landing-v4__section-eyebrow">Security posture</p>
            <h2 className="landing-v4__section-title">
              Calm, clear, and built for control.
            </h2>
            <p className="landing-v4__section-text">
              The interface should feel trustworthy without becoming loud. Security is
              presented as clarity, not chaos.
            </p>
          </div>

          <div className="landing-v4__security-stack">
            <div className="landing-v4__security-layer">
              <span>Layer 1</span>
              <strong>Authenticated access</strong>
            </div>
            <div className="landing-v4__security-layer">
              <span>Layer 2</span>
              <strong>Encrypted communication</strong>
            </div>
            <div className="landing-v4__security-layer">
              <span>Layer 3</span>
              <strong>Steganographic concealment</strong>
            </div>
          </div>
        </motion.div>
      </section>

      <section className="landing-v4__cta">
        <motion.div className="landing-v4__cta-card" {...appear(0)}>
          <p className="landing-v4__section-eyebrow">Ready to begin</p>
          <h2 className="landing-v4__cta-title">
            Secure your digital shadow today.
          </h2>
          <p className="landing-v4__cta-text">
            Create your account and explore protected messaging, secure file handling,
            and steganographic delivery in one modern product surface.
          </p>

          <div className="landing-v4__cta-actions">
            <Link to="/register" className="button button--primary">
              Create account
            </Link>
            <Link to="/login" className="button button--secondary">
              Sign in
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}