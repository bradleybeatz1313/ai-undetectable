import { useEffect, useRef, useState } from "react";

export default function LandingPage() {
  const navRef = useRef<HTMLElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (navRef.current) {
        if (window.scrollY > 40) {
          navRef.current.classList.add("scrolled");
        } else {
          navRef.current.classList.remove("scrolled");
        }
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const observerOptions = {
      threshold: 0.15,
      rootMargin: "0px 0px -40px 0px",
    };
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          (entry.target as HTMLElement).style.animationPlayState = "running";
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    document
      .querySelectorAll(".step, .bento-card, .pricing-card")
      .forEach((el, i) => {
        const elem = el as HTMLElement;
        elem.style.opacity = "0";
        elem.style.animation = "fadeUp 0.6s ease-out forwards";
        elem.style.animationDelay = `${(i % 3) * 0.1 + 0.1}s`;
        elem.style.animationPlayState = "paused";
        observer.observe(el);
      });

    return () => observer.disconnect();
  }, []);

  const handleSignupClick = () => {
    alert("Coming soon: Sign up form");
  };

  return (
    <>
      {/* Dot Grid Background */}
      <div className="dot-grid-bg" aria-hidden="true" />

      {/* Navigation */}
      <header className="nav-wrapper" ref={navRef} role="banner">
        <nav aria-label="Main navigation">
          <div className="logo">
            AI <span>Undetectable</span>
          </div>
          <button
            className="mobile-menu-btn"
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <span />
            <span />
            <span />
          </button>
          <div className={`nav-links${menuOpen ? " open" : ""}`}>
            <a href="#features" onClick={() => setMenuOpen(false)}>
              Features
            </a>
            <a href="#pricing" onClick={() => setMenuOpen(false)}>
              Pricing
            </a>
            <a href="#docs" onClick={() => setMenuOpen(false)}>
              Docs
            </a>
            <a
              href="#"
              className="nav-cta"
              onClick={(e) => {
                e.preventDefault();
                setMenuOpen(false);
                handleSignupClick();
              }}
            >
              Get API Key
            </a>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main>
        {/* Hero */}
        <section className="hero" aria-labelledby="hero-heading">
          <div className="hero-glow" aria-hidden="true" />
          <h1 id="hero-heading" className="animate-on-load delay-1">
            Make AI Images
            <br />
            <span className="gradient-text">Undetectable</span>
          </h1>
          <p className="subtitle animate-on-load delay-2">
            Transform AI-generated images to pass detection tests
          </p>
          <p className="description animate-on-load delay-3">
            AI detection tools like ZeroGPT, Copyleaks, and Turnitin can
            identify AI-generated images. That limits where you can use them. AI
            Undetectable fixes that — one API call away.
          </p>
          <div className="cta-group animate-on-load delay-4">
            <button className="btn btn-filled" onClick={handleSignupClick}>
              Start Free
            </button>
            <a href="#docs" className="btn btn-ghost">
              Read API Docs
            </a>
          </div>

          {/* Terminal Hero Visual */}
          <div className="terminal animate-on-load delay-5">
            <div className="terminal-header">
              <div className="terminal-dot red" />
              <div className="terminal-dot yellow" />
              <div className="terminal-dot green" />
              <span className="terminal-title">terminal</span>
            </div>
            <div className="terminal-body">
              <span className="comment"># Process an AI-generated image</span>
              <br />
              <span className="prompt">$</span>{" "}
              <span className="cmd">curl</span>{" "}
              <span className="flag">-X POST</span>{" "}
              <span className="str">/api/process</span> \<br />
              &nbsp;&nbsp;<span className="flag">-H</span>{" "}
              <span className="str">"X-API-Key: sk_live_abc123"</span> \<br />
              &nbsp;&nbsp;<span className="flag">-F</span>{" "}
              <span className="str">"file=@ai-image.jpg"</span>
              <br />
              <br />
              <span className="comment"># Response</span>
              <br />
              <span style={{ color: "var(--text-secondary)" }}>{"{"}</span>
              <br />
              &nbsp;&nbsp;
              <span style={{ color: "var(--accent-cyan)" }}>"success"</span>:{" "}
              <span style={{ color: "var(--accent-violet)" }}>true</span>,<br />
              &nbsp;&nbsp;
              <span style={{ color: "var(--accent-cyan)" }}>"upload_id"</span>:{" "}
              <span style={{ color: "#28c840" }}>"550e8400-e29b..."</span>,
              <br />
              &nbsp;&nbsp;
              <span style={{ color: "var(--accent-cyan)" }}>
                "remaining_quota"
              </span>
              : <span style={{ color: "#febc2e" }}>9</span>
              <br />
              <span style={{ color: "var(--text-secondary)" }}>{"}"}</span>
              <span className="cursor-block" />
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="how-it-works" aria-labelledby="hiw-heading">
          <div className="section-header">
            <p className="section-label">How it works</p>
            <h2 className="section-title" id="hiw-heading">
              Three steps. That's it.
            </h2>
          </div>
          <div className="steps-row">
            <div className="step">
              <div className="step-number">01</div>
              <h3 className="step-title">Upload</h3>
              <p className="step-desc">Send your AI-generated image via API</p>
            </div>
            <div className="step">
              <div className="step-number">02</div>
              <h3 className="step-title">Process</h3>
              <p className="step-desc">
                Our engine adds imperceptible noise, adjusts frequencies, and
                re-encodes
              </p>
            </div>
            <div className="step">
              <div className="step-number">03</div>
              <h3 className="step-title">Download</h3>
              <p className="step-desc">
                Get back a visually identical image that passes detection
              </p>
            </div>
          </div>
        </section>

        {/* Features Bento Grid */}
        <section
          className="features-section"
          id="features"
          aria-labelledby="features-heading"
        >
          <div className="section-header">
            <p className="section-label">Capabilities</p>
            <h2 className="section-title" id="features-heading">
              Built for production
            </h2>
            <p className="section-subtitle">
              Everything you need to integrate undetectable images into your
              workflow.
            </p>
          </div>

          <div className="bento-grid">
            <article className="bento-card span-2">
              <div className="bento-icon" aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ color: "var(--accent-cyan)" }}
                >
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
              </div>
              <h3>Sub-5 Second Processing</h3>
              <p>
                Fast image transformation. Upload, process, download — all in
                seconds. Our pipeline is optimized for speed without sacrificing
                quality.
              </p>
            </article>
            <article className="bento-card">
              <div className="bento-icon" aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ color: "var(--accent-violet)" }}
                >
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 16v-4" />
                  <path d="M12 8h.01" />
                </svg>
              </div>
              <h3>Proven Undetectable</h3>
              <p>
                Passes ZeroGPT, Copyleaks, and other major AI detection tools.
              </p>
            </article>

            <article className="bento-card">
              <div className="bento-icon" aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ color: "var(--accent-cyan)" }}
                >
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </div>
              <h3>Privacy First</h3>
              <p>
                Files deleted after 7 days (free) or 30 days (pro). No logs.
                Simple.
              </p>
            </article>
            <article className="bento-card span-2">
              <div className="bento-icon" aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ color: "var(--accent-cyan)" }}
                >
                  <polyline points="16 18 22 12 16 6" />
                  <polyline points="8 6 2 12 8 18" />
                </svg>
              </div>
              <h3>Simple API</h3>
              <p>
                One endpoint. Multipart form upload. JSON response. Done. No
                complex SDKs or dependencies required — just curl and go.
              </p>
            </article>

            <article className="bento-card span-2">
              <div className="bento-icon" aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ color: "var(--accent-violet)" }}
                >
                  <line x1="12" y1="20" x2="12" y2="10" />
                  <line x1="18" y1="20" x2="18" y2="4" />
                  <line x1="6" y1="20" x2="6" y2="16" />
                </svg>
              </div>
              <h3>Freemium Model</h3>
              <p>
                10 free images/month. Pro tier: 500/month for $9.99. Start for
                free and scale when you're ready.
              </p>
            </article>
            <article className="bento-card">
              <div className="bento-icon" aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ color: "var(--accent-cyan)" }}
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
              </div>
              <h3>No Limits on Growth</h3>
              <p>Scale your content creation. Unlimited images on enterprise.</p>
            </article>
          </div>
        </section>

        {/* Pricing */}
        <section
          className="pricing-section"
          id="pricing"
          aria-labelledby="pricing-heading"
        >
          <div className="section-header">
            <p className="section-label">Pricing</p>
            <h2 className="section-title" id="pricing-heading">
              Simple Pricing
            </h2>
            <p className="section-subtitle">Start free. Scale as you grow.</p>
          </div>

          <div className="pricing-grid">
            <div className="pricing-card">
              <h3>Free</h3>
              <div className="price">$0</div>
              <span className="price-period">per month</span>
              <ul className="pricing-features">
                <li>10 images/month</li>
                <li>Max 2MB per image</li>
                <li>7-day storage</li>
                <li>Email support</li>
              </ul>
              <button className="btn btn-ghost" onClick={handleSignupClick}>
                Start Free
              </button>
            </div>

            <div className="pricing-card popular">
              <div className="popular-badge">Most Popular</div>
              <h3>Pro</h3>
              <div className="price">$9.99</div>
              <span className="price-period">per month</span>
              <ul className="pricing-features">
                <li>500 images/month</li>
                <li>Max 10MB per image</li>
                <li>30-day storage</li>
                <li>Batch API access</li>
                <li>Priority support</li>
              </ul>
              <button className="btn btn-filled" onClick={handleSignupClick}>
                Upgrade to Pro
              </button>
            </div>

            <div className="pricing-card">
              <h3>Enterprise</h3>
              <div className="price">Custom</div>
              <span className="price-period">per month</span>
              <ul className="pricing-features">
                <li>Unlimited images</li>
                <li>Unlimited file size</li>
                <li>Dedicated endpoint</li>
                <li>SLA support</li>
                <li>Custom integrations</li>
              </ul>
              <button className="btn btn-ghost">Contact Sales</button>
            </div>
          </div>
        </section>

        {/* API Docs */}
        <section
          className="docs-section"
          id="docs"
          aria-labelledby="docs-heading"
        >
          <div
            className="section-header"
            style={{ textAlign: "left", marginBottom: "48px" }}
          >
            <p className="section-label">Reference</p>
            <h2 className="section-title" id="docs-heading">
              API Documentation
            </h2>
          </div>

          <div className="docs-grid">
            <nav className="docs-nav" aria-label="Documentation sections">
              <a href="#auth">Authentication</a>
              <a href="#process">Process Image</a>
              <a href="#download">Download</a>
              <a href="#usage">Check Usage</a>
            </nav>

            <div className="docs-content">
              <div className="endpoint-block" id="auth">
                <h3>Authentication</h3>
                <p>
                  All requests require an <code>X-API-Key</code> header. Get
                  your key by signing up.
                </p>
              </div>

              <div className="endpoint-block" id="process">
                <h3>Process Image</h3>
                <p>
                  <span className="method-badge post">POST</span>
                  <span className="endpoint-path">/api/process</span>
                </p>
                <p>Upload an image for processing.</p>
                <pre>
                  <span className="kw">curl</span>{" "}
                  <span className="flag">-X POST</span>{" "}
                  <span className="url">/api/process</span> \{"\n"}
                  {"  "}
                  <span className="flag">-H</span>{" "}
                  <span className="str">"X-API-Key: your_api_key_here"</span>{" "}
                  \{"\n"}
                  {"  "}
                  <span className="flag">-F</span>{" "}
                  <span className="str">"file=@image.jpg"</span>
                </pre>
                <p>
                  <strong style={{ color: "var(--text-heading)" }}>
                    Response:
                  </strong>
                </p>
                <pre>
                  {`{
  `}
                  <span className="key">"success"</span>:{" "}
                  <span className="val-bool">true</span>,{"\n  "}
                  <span className="key">"message"</span>:{" "}
                  <span className="val-str">"Image processed successfully"</span>
                  ,{"\n  "}
                  <span className="key">"upload_id"</span>:{" "}
                  <span className="val-str">
                    "550e8400-e29b-41d4-a716-446655440000"
                  </span>
                  ,{"\n  "}
                  <span className="key">"remaining_quota"</span>:{" "}
                  <span className="val-num">9</span>,{"\n  "}
                  <span className="key">"tier"</span>:{" "}
                  <span className="val-str">"free"</span>
                  {"\n}"}
                </pre>
              </div>

              <div className="endpoint-block" id="download">
                <h3>Download Processed Image</h3>
                <p>
                  <span className="method-badge get">GET</span>
                  <span className="endpoint-path">
                    /api/result/&#123;upload_id&#125;
                  </span>
                </p>
                <p>Download your processed image.</p>
                <pre>
                  <span className="kw">curl</span>{" "}
                  <span className="flag">-H</span>{" "}
                  <span className="str">"X-API-Key: your_api_key_here"</span>{" "}
                  \{"\n"}
                  {"  "}
                  <span className="url">
                    /api/result/550e8400-e29b-41d4-a716-446655440000
                  </span>{" "}
                  \{"\n"}
                  {"  "}
                  <span className="flag">-o</span>{" "}
                  <span className="str">undetectable.jpg</span>
                </pre>
              </div>

              <div className="endpoint-block" id="usage">
                <h3>Check Usage</h3>
                <p>
                  <span className="method-badge get">GET</span>
                  <span className="endpoint-path">/api/usage</span>
                </p>
                <p>Get your current usage stats.</p>
                <pre>
                  <span className="kw">curl</span>{" "}
                  <span className="flag">-H</span>{" "}
                  <span className="str">"X-API-Key: your_api_key_here"</span>{" "}
                  \{"\n"}
                  {"  "}
                  <span className="url">/api/usage</span>
                </pre>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer role="contentinfo">
        <p>&copy; 2024 AI Undetectable. All rights reserved.</p>
        <p>
          Built by{" "}
          <a href="https://bradbarroso.com" target="_blank" rel="noreferrer">
            Brad Barroso
          </a>
        </p>
        <p>
          <a href="mailto:support@aidetectable.com">
            support@aidetectable.com
          </a>
        </p>
      </footer>
    </>
  );
}
