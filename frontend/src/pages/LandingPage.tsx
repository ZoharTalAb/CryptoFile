import { motion, useScroll, useTransform } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  FileLock2,
  Lock,
  MessageSquareMore,
  ShieldCheck,
  Sparkles,
  Wand2,
} from "lucide-react";
import { Link } from "react-router-dom";

const pillars = [
  {
    icon: <MessageSquareMore size={18} />,
    title: "Secure communication",
    text: "Private file-oriented conversations with a clear and understandable workflow.",
  },
  {
    icon: <Wand2 size={18} />,
    title: "Steganography workflow",
    text: "Hide sensitive payloads inside supported carrier files through a guided product flow.",
  },
  {
    icon: <FileLock2 size={18} />,
    title: "Protected file handling",
    text: "Manage protected assets in one organized workspace instead of scattered tools.",
  },
  {
    icon: <ShieldCheck size={18} />,
    title: "Access and control",
    text: "Keep sessions, routes, and critical actions inside a controlled security-first experience.",
  },
];

const workflow = [
  {
    step: "01",
    title: "Prepare",
    text: "Choose a carrier file and the sensitive content you want to protect.",
  },
  {
    step: "02",
    title: "Embed",
    text: "Use the steganography flow to conceal data without breaking usability.",
  },
  {
    step: "03",
    title: "Deliver",
    text: "Share the protected asset through secure communication channels.",
  },
  {
    step: "04",
    title: "Control",
    text: "Track files, access, and delivery state from one workspace.",
  },
];

const productHighlights = [
  {
    title: "Private Chat",
    text: "Secure conversation-based file delivery",
  },
  {
    title: "Stego Lab",
    text: "Hide sensitive content inside files",
  },
  {
    title: "File Vault",
    text: "Protected and organized file management",
  },
  {
    title: "Access Control",
    text: "Security-focused account handling",
  },
];

const appear = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 as const },
  transition: {
    duration: 0.7,
    delay,
    ease: "easeOut" as const,
  },
});

const heroAppear = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: {
    duration: 0.75,
    delay,
    ease: "easeOut" as const,
  },
});

export function LandingPage() {
  const { scrollYProgress } = useScroll();

  const heroY = useTransform(scrollYProgress, [0, 0.28], [0, 56]);
  const heroTextY = useTransform(scrollYProgress, [0, 0.22], [0, 28]);
  const backgroundDrift = useTransform(scrollYProgress, [0, 1], [0, 180]);

  return (
    <div className="landing-page landing-page--v3">
      <div className="landing-noise" />
      <motion.div className="landing-radial landing-radial--one" style={{ y: backgroundDrift }} />
      <motion.div className="landing-radial landing-radial--two" style={{ y: backgroundDrift }} />
      <motion.div className="landing-radial landing-radial--three" style={{ y: backgroundDrift }} />
      <div className="landing-grid-overlay" />
      <div className="landing-lines landing-lines--left" />
      <div className="landing-lines landing-lines--right" />

      <header className="landing-nav landing-nav--v3">
        <motion.div className="landing-nav__brand landing-nav__brand--strong" {...heroAppear(0)}>
          <span className="brand-mark">C</span>
          <span>CryptoFile</span>
        </motion.div>

        <motion.nav className="landing-nav__center" {...heroAppear(0.08)}>
          <a href="#product">Product</a>
          <a href="#workflow">Workflow</a>
          <a href="#security">Security</a>
        </motion.nav>

        <motion.div className="landing-nav__actions" {...heroAppear(0.14)}>
          <Link to="/login" className="button button--ghost">
            Sign In
          </Link>
          <Link to="/register" className="button button--primary">
            Get Started
          </Link>
        </motion.div>
      </header>

      <section className="hero hero--v3">
        <div className="hero__backdrop">
          <div className="hero__grid" />
          <motion.div
            className="hero-orb hero-orb--one"
            animate={{ x: [0, 18, -10, 0], y: [0, -10, 18, 0] }}
            transition={{ duration: 7, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
          />
          <motion.div
            className="hero-orb hero-orb--two"
            animate={{ x: [0, -18, 10, 0], y: [0, 16, -10, 0] }}
            transition={{ duration: 8, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
          />
          <motion.div
            className="hero-orb hero-orb--three"
            animate={{ x: [0, 12, -14, 0], y: [0, -8, 10, 0] }}
            transition={{ duration: 9, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
          />
        </div>

        <motion.div className="hero__content hero__content--v3" style={{ y: heroTextY }}>
          <motion.div className="hero-badge" {...heroAppear(0)}>
            <Sparkles size={14} />
            <span>Private communication meets steganography</span>
          </motion.div>

          <motion.p className="hero__eyebrow" {...heroAppear(0.06)}>
            Secure communication platform
          </motion.p>

          <motion.h1 className="hero__title hero__title--v3" {...heroAppear(0.12)}>
            Secure files. Hidden signals. Clear control.
          </motion.h1>

          <motion.p className="hero__description hero__description--v3" {...heroAppear(0.18)}>
            CryptoFile combines protected messaging, steganographic embedding,
            and secure file management in one modern workspace designed for
            privacy-oriented communication.
          </motion.p>

          <motion.div className="hero__actions" {...heroAppear(0.24)}>
            <Link to="/register" className="button button--primary">
              Create Account
              <ArrowRight size={16} />
            </Link>

            <a href="#product" className="button button--secondary">
              Explore Product
            </a>
          </motion.div>

          <motion.div className="hero-proof" {...heroAppear(0.3)}>
            <div className="hero-proof__item">
              <CheckCircle2 size={16} />
              <span>Encrypted workflows</span>
            </div>
            <div className="hero-proof__item">
              <CheckCircle2 size={16} />
              <span>Stego-enabled delivery</span>
            </div>
            <div className="hero-proof__item">
              <CheckCircle2 size={16} />
              <span>Unified secure workspace</span>
            </div>
          </motion.div>
        </motion.div>

        <motion.div
          className="hero-product"
          style={{ y: heroY }}
          initial={{ opacity: 0, y: 28, scale: 0.985 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.18, ease: "easeOut" }}
        >
          <div className="hero-product__halo" />

          <div className="product-frame">
            <div className="product-frame__topbar">
              <div className="product-frame__dots">
                <span />
                <span />
                <span />
              </div>

              <div className="product-frame__title">CryptoFile Workspace</div>

              <div className="product-frame__status">
                <Lock size={14} />
                <span>Protected</span>
              </div>
            </div>

            <div className="product-frame__body">
              <aside className="product-sidebar">
                <div className="product-sidebar__brand">
                  <span className="brand-mark brand-mark--small">C</span>
                  <div>
                    <strong>CryptoFile</strong>
                    <p>Private workspace</p>
                  </div>
                </div>

                <div className="product-sidebar__nav">
                  <div className="product-sidebar__item product-sidebar__item--active">
                    Dashboard
                  </div>
                  <div className="product-sidebar__item">Secure Chat</div>
                  <div className="product-sidebar__item">Stego Lab</div>
                  <div className="product-sidebar__item">File Vault</div>
                  <div className="product-sidebar__item">Security</div>
                </div>

                <div className="product-sidebar__footer">
                  <p>Security posture</p>
                  <strong>Stable</strong>
                </div>
              </aside>

              <section className="product-main">
                <div className="product-main__stats">
                  <div className="product-stat product-stat--primary">
                    <span className="product-stat__label">Protected files</span>
                    <strong>689</strong>
                    <small>+18 this week</small>
                  </div>

                  <div className="product-stat">
                    <span className="product-stat__label">Secure threads</span>
                    <strong>372</strong>
                    <small>Active conversations</small>
                  </div>

                  <div className="product-stat">
                    <span className="product-stat__label">Embedded payloads</span>
                    <strong>124</strong>
                    <small>Across supported media</small>
                  </div>
                </div>

                <div className="product-main__grid">
                  <div className="product-panel product-panel--chat">
                    <div className="panel-topline">
                      <span className="panel-pill">Secure Delivery</span>
                      <span className="panel-muted">Live flow</span>
                    </div>

                    <h4>Message and file protection in one thread</h4>

                    <div className="message-stack">
                      <div className="message-bubble message-bubble--left">
                        Carrier file uploaded successfully
                      </div>
                      <div className="message-bubble message-bubble--right">
                        Sensitive payload embedded and encrypted
                      </div>
                      <div className="message-bubble message-bubble--left">
                        Protected asset ready for sharing
                      </div>
                    </div>
                  </div>

                  <div className="product-panel product-panel--workflow">
                    <div className="panel-topline">
                      <span className="panel-pill panel-pill--soft">Workflow</span>
                    </div>

                    <h4>Delivery path</h4>

                    <div className="mini-timeline">
                      <div className="mini-timeline__row">
                        <span className="mini-timeline__dot" />
                        <p>Encrypt payload</p>
                      </div>
                      <div className="mini-timeline__row">
                        <span className="mini-timeline__dot" />
                        <p>Embed into carrier</p>
                      </div>
                      <div className="mini-timeline__row">
                        <span className="mini-timeline__dot" />
                        <p>Send through secure chat</p>
                      </div>
                    </div>
                  </div>

                  <div className="product-panel product-panel--media">
                    <div className="panel-topline">
                      <span className="panel-pill panel-pill--soft">Supported</span>
                    </div>
                    <h4>Media types</h4>
                    <div className="media-grid media-grid--v3">
                      <span>Image</span>
                      <span>Audio</span>
                      <span>Text</span>
                      <span>Video</span>
                    </div>
                  </div>

                  <div className="product-panel product-panel--activity">
                    <div className="panel-topline">
                      <span className="panel-pill panel-pill--soft">Activity</span>
                    </div>
                    <h4>Recent system state</h4>
                    <div className="activity-list">
                      <div className="activity-list__item">
                        <span className="activity-list__state activity-list__state--success" />
                        <p>Protected upload completed</p>
                      </div>
                      <div className="activity-list__item">
                        <span className="activity-list__state activity-list__state--info" />
                        <p>Secure thread opened</p>
                      </div>
                      <div className="activity-list__item">
                        <span className="activity-list__state activity-list__state--success" />
                        <p>Payload extraction validated</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </motion.div>
      </section>

      <section className="trust-strip">
        <div className="trust-strip__inner">
          {productHighlights.map((item) => (
            <article key={item.title} className="trust-stat trust-stat--interactive">
              <span className="trust-stat__value">{item.title}</span>
              <span className="trust-stat__label">{item.text}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section landing-section--intro" id="product">
        <motion.div className="section-heading section-heading--center" {...appear(0)}>
          <p className="section-eyebrow section-eyebrow--center">Product overview</p>
          <h2 className="section-title section-title--center">
            Secure communication built around real workflows
          </h2>
          <p className="section-text section-text--center">
            CryptoFile is designed to make protected communication feel usable,
            structured, and trustworthy across messaging, steganography, and file
            management.
          </p>
        </motion.div>

        <div className="bento-grid bento-grid--refined">
          <motion.article className="bento-card bento-card--feature" {...appear(0)}>
            <div className="bento-card__icon">
              <MessageSquareMore size={18} />
            </div>
            <h3>Conversation-led secure delivery</h3>
            <p>
              File protection is part of the communication flow, making the platform
              feel more natural, connected, and product-ready.
            </p>
          </motion.article>

          <motion.article className="bento-card bento-card--feature" {...appear(0.05)}>
            <div className="bento-card__icon">
              <Wand2 size={18} />
            </div>
            <h3>Steganography with clarity</h3>
            <p>
              Sensitive operations are presented through a guided interface rather
              than raw technical complexity.
            </p>
          </motion.article>

          <motion.article className="bento-card bento-card--feature" {...appear(0.1)}>
            <div className="bento-card__icon">
              <FileLock2 size={18} />
            </div>
            <h3>Unified file workspace</h3>
            <p>
              Secure chat, protected files, and embedded payload operations live
              inside one coherent environment.
            </p>
          </motion.article>

          <motion.article className="bento-card bento-card--feature" {...appear(0.15)}>
            <div className="bento-card__icon">
              <ShieldCheck size={18} />
            </div>
            <h3>Security with product polish</h3>
            <p>
              The experience is meant to feel serious and trustworthy while staying
              modern, clean, and easy to navigate.
            </p>
          </motion.article>
        </div>
      </section>

      <section className="landing-section landing-section--split" id="workflow">
        <motion.div className="workflow-board" {...appear(0)}>
          {workflow.map((item) => (
            <article key={item.step} className="workflow-card workflow-card--interactive">
              <span className="workflow-card__step">{item.step}</span>
              <h4>{item.title}</h4>
              <p>{item.text}</p>
            </article>
          ))}
        </motion.div>

        <motion.div className="section-copy section-copy--plain" {...appear(0.06)}>
          <p className="section-eyebrow">Workflow</p>
          <h2 className="section-title">A clear flow for protected delivery</h2>
          <p className="section-text">
            CryptoFile turns a complex protection process into a structured user
            journey: prepare the asset, embed the sensitive content, deliver it
            securely, and keep everything under control.
          </p>
        </motion.div>
      </section>

      <section
        className="landing-section landing-section--split landing-section--security"
        id="security"
      >
        <motion.div className="section-copy section-copy--plain" {...appear(0)}>
          <p className="section-eyebrow">Security</p>
          <h2 className="section-title">
            Security, visibility, and control in one experience
          </h2>
          <p className="section-text">
            Trust comes from both technical protection and product clarity. The
            interface should help users understand what is happening without turning
            the experience into noise.
          </p>

          <div className="pillar-list">
            {pillars.map((pillar, index) => (
              <motion.article key={pillar.title} className="pillar-item" {...appear(index * 0.05)}>
                <div className="pillar-item__icon">{pillar.icon}</div>
                <div>
                  <h3>{pillar.title}</h3>
                  <p>{pillar.text}</p>
                </div>
              </motion.article>
            ))}
          </div>
        </motion.div>

        <motion.div className="security-visual" {...appear(0.08)}>
          <div className="security-visual__main">
            <div className="security-visual__header">
              <span>Workspace status</span>
              <strong>Protected environment</strong>
            </div>

            <div className="security-visual__stack">
              <div className="security-layer">
                <span className="security-layer__tag">Layer 1</span>
                <h4>Authenticated access</h4>
                <p>Controlled entry points and protected session handling.</p>
              </div>

              <div className="security-layer">
                <span className="security-layer__tag">Layer 2</span>
                <h4>Encrypted delivery</h4>
                <p>Messages and file flows designed around protected exchange.</p>
              </div>

              <div className="security-layer">
                <span className="security-layer__tag">Layer 3</span>
                <h4>Steganographic concealment</h4>
                <p>Hidden payload workflows across supported carrier media.</p>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section className="landing-cta landing-cta--v3">
        <motion.div {...appear(0)}>
          <p className="landing-cta__eyebrow">Get started</p>
          <h2 className="landing-cta__title">
            Start building secure communication flows with CryptoFile
          </h2>
          <p className="landing-cta__text">
            Create your account and explore protected messaging, steganography,
            and secure file collaboration in one polished workspace.
          </p>

          <div className="landing-cta__actions">
            <Link to="/register" className="button button--primary">
              Create Account
            </Link>
            <Link to="/login" className="button button--secondary">
              Sign In
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}