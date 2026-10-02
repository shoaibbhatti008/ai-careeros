import { Link } from "react-router-dom";
import {
  ArrowRight,
  Brain,
  Briefcase,
  CheckCircle2,
  FileText,
  Lock,
  MessageSquare,
  Shield,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Decorative orbs */}
      <div
        className="orb orb-gold w-[600px] h-[600px] -top-40 -left-40 animate-float-slow"
        aria-hidden="true"
      />
      <div
        className="orb orb-amber w-[500px] h-[500px] top-1/3 -right-40 animate-float-slow"
        style={{ animationDelay: "3s" }}
        aria-hidden="true"
      />
      <div
        className="orb orb-cream w-[400px] h-[400px] bottom-0 left-1/3 animate-float-slow"
        style={{ animationDelay: "6s" }}
        aria-hidden="true"
      />

      {/* ============================================================
          NAVIGATION
      ============================================================ */}
      <nav className="relative z-20 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="block text-lg font-bold gradient-text">
                AI CareerOS
              </span>
              <span className="block text-[10px] font-medium uppercase tracking-widest text-cream-600">
                Career Intelligence
              </span>
            </div>
          </Link>

          {/* Nav links */}
          <div className="flex items-center gap-2 sm:gap-3">
            {isAuthenticated ? (
              <Link to="/" className="btn-primary text-sm">
                Dashboard
                <ArrowRight className="h-4 w-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hidden sm:inline-flex btn-ghost text-sm"
                >
                  Sign in
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Get started
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* ============================================================
          HERO
      ============================================================ */}
      <section className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-12 sm:pt-20 pb-16 sm:pb-24">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full glass-card px-4 py-2 mb-8 animate-fade-in">
            <Sparkles className="h-4 w-4 text-gold-500" />
            <span className="text-xs sm:text-sm font-medium text-cream-800">
              Open-source multi-agent AI platform
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-cream-900 leading-[1.1] text-shadow-soft animate-slide-up">
            Your AI-powered
            <br />
            <span className="gradient-text">career intelligence</span>
            <br />
            platform
          </h1>

          {/* Subheadline */}
          <p
            className="mt-6 sm:mt-8 text-base sm:text-lg md:text-xl text-cream-600 max-w-2xl mx-auto animate-slide-up"
            style={{ animationDelay: "0.1s" }}
          >
            Analyze resumes, discover job opportunities, identify skill gaps,
            practice interviews, and coordinate specialized AI agents —
            securely and privately.
          </p>

          {/* CTAs */}
          <div
            className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 animate-slide-up"
            style={{ animationDelay: "0.2s" }}
          >
            <Link
              to={isAuthenticated ? "/" : "/register"}
              className="btn-primary w-full sm:w-auto text-base px-6 py-3"
            >
              {isAuthenticated ? "Go to Dashboard" : "Start free"}
              <ArrowRight className="h-5 w-5" />
            </Link>
            <a
              href="#features"
              className="btn-secondary w-full sm:w-auto text-base px-6 py-3"
            >
              Explore features
            </a>
          </div>

          {/* Trust indicators */}
          <div
            className="mt-10 sm:mt-12 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-xs sm:text-sm text-cream-600 animate-slide-up"
            style={{ animationDelay: "0.3s" }}
          >
            <span className="inline-flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              No credit card required
            </span>
            <span className="inline-flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Open source
            </span>
            <span className="inline-flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Privacy-first
            </span>
          </div>
        </div>

        {/* Hero visual — mockup */}
        <div
          className="mt-16 sm:mt-20 relative animate-scale-in"
          style={{ animationDelay: "0.4s" }}
        >
          <div className="glass-card p-2 sm:p-4 shadow-2xl shadow-gold-400/20 max-w-5xl mx-auto">
            <div className="rounded-xl overflow-hidden bg-gradient-to-br from-cream-100 to-cream-200 p-4 sm:p-8">
              {/* Mock dashboard */}
              <div className="flex items-center gap-2 mb-4">
                <div className="h-3 w-3 rounded-full bg-red-400" />
                <div className="h-3 w-3 rounded-full bg-yellow-400" />
                <div className="h-3 w-3 rounded-full bg-green-400" />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
                <MockCard icon={FileText} label="Resumes" value="12" />
                <MockCard icon={Briefcase} label="Job Matches" value="48" />
                <MockCard icon={Target} label="Skill Gaps" value="7" />
              </div>
              <div className="mt-4 rounded-lg bg-white/60 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="h-4 w-4 text-gold-600" />
                  <span className="text-xs font-semibold text-cream-800">
                    AI Assistant
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="h-2 w-3/4 rounded bg-gold-400/20" />
                  <div className="h-2 w-1/2 rounded bg-gold-400/20" />
                  <div className="h-2 w-5/6 rounded bg-gold-400/20" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================
          FEATURES
      ============================================================ */}
      <section
        id="features"
        className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24"
      >
        <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
          <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
            Features
          </p>
          <h2 className="mt-3 text-3xl sm:text-4xl md:text-5xl font-bold text-cream-900 text-shadow-soft">
            Everything you need for
            <br />
            <span className="gradient-text">career intelligence</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-cream-600">
            Eight specialized AI agents working together to accelerate your
            career growth.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3">
          <FeatureCard
            icon={FileText}
            title="Resume Analysis"
            description="AI-powered resume parsing with skills extraction, ATS hints, and improvement suggestions."
            gradient="from-blue-500 to-cyan-500"
            delay={0}
          />
          <FeatureCard
            icon={Briefcase}
            title="Job Matching"
            description="Match your profile against job descriptions with detailed skill gap analysis."
            gradient="from-purple-500 to-pink-500"
            delay={1}
          />
          <FeatureCard
            icon={Target}
            title="Skill Gap Analysis"
            description="Identify missing skills prioritized by importance for your target role."
            gradient="from-orange-500 to-red-500"
            delay={2}
          />
          <FeatureCard
            icon={MessageSquare}
            title="Interview Prep"
            description="Mock interviews with behavioral, technical, and system design questions."
            gradient="from-green-500 to-emerald-500"
            delay={3}
          />
          <FeatureCard
            icon={Brain}
            title="Multi-Agent AI"
            description="Eight specialized agents orchestrated safely with budget controls."
            gradient="from-indigo-500 to-blue-500"
            delay={4}
          />
          <FeatureCard
            icon={Shield}
            title="Privacy-First"
            description="Your data stays yours. Ownership enforced at every layer."
            gradient="from-rose-500 to-pink-500"
            delay={5}
          />
        </div>
      </section>

      {/* ============================================================
          HOW IT WORKS
      ============================================================ */}
      <section className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
          <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
            How it works
          </p>
          <h2 className="mt-3 text-3xl sm:text-4xl md:text-5xl font-bold text-cream-900 text-shadow-soft">
            Four steps to career
            <span className="gradient-text"> success</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:gap-8 lg:grid-cols-4">
          <StepCard
            number={1}
            icon={FileText}
            title="Upload"
            description="Add your resume or paste text for instant AI analysis."
            delay={0}
          />
          <StepCard
            number={2}
            icon={Sparkles}
            title="Analyze"
            description="AI agents extract skills, strengths, and improvement areas."
            delay={1}
          />
          <StepCard
            number={3}
            icon={Briefcase}
            title="Match"
            description="See which jobs fit your profile and what skills you're missing."
            delay={2}
          />
          <StepCard
            number={4}
            icon={TrendingUp}
            title="Grow"
            description="Practice interviews, close skill gaps, and land your role."
            delay={3}
          />
        </div>
      </section>

      {/* ============================================================
          TRUST / SECURITY
      ============================================================ */}
      <section className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="glass-card p-6 sm:p-10 md:p-12">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 lg:gap-12 items-center">
            <div>
              <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40 mb-6">
                <Lock className="h-7 w-7 text-white" />
              </div>
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
                Security-first by
                <span className="gradient-text"> design</span>
              </h2>
              <p className="mt-4 text-base text-cream-600">
                AI CareerOS treats your data as yours. Every query enforces
                ownership. Every agent has permission boundaries. Every
                sensitive action requires your approval.
              </p>
              <ul className="mt-6 space-y-3">
                <TrustPoint text="Ownership enforced at database layer" />
                <TrustPoint text="Registered tools only — no arbitrary code" />
                <TrustPoint text="Prompt-injection defenses on all external content" />
                <TrustPoint text="Human-in-the-loop approval for sensitive actions" />
                <TrustPoint text="Full audit trail with trace IDs" />
              </ul>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <SecurityStat icon={Shield} label="4-Layer" value="Permissions" />
              <SecurityStat icon={Zap} label="Budget" value="Controlled" />
              <SecurityStat icon={Users} label="Multi" value="Tenant" />
              <SecurityStat icon={Lock} label="Ownership" value="Enforced" />
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================
          CTA
      ============================================================ */}
      <section className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="glass-card p-8 sm:p-12 md:p-16 text-center relative overflow-hidden">
          <div
            className="orb orb-gold w-96 h-96 -top-32 -right-32 animate-float-slow"
            aria-hidden="true"
          />
          <div className="relative z-10">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-cream-900 text-shadow-soft">
              Ready to accelerate
              <br />
              <span className="gradient-text">your career?</span>
            </h2>
            <p className="mt-4 text-base sm:text-lg text-cream-600 max-w-2xl mx-auto">
              Join AI CareerOS today. Analyze your resume, find matching jobs,
              and practice interviews — all in one platform.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
              <Link
                to={isAuthenticated ? "/" : "/register"}
                className="btn-primary text-base px-6 py-3 w-full sm:w-auto"
              >
                {isAuthenticated ? "Go to Dashboard" : "Get started free"}
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                to="/login"
                className="btn-secondary text-base px-6 py-3 w-full sm:w-auto"
              >
                Sign in
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================
          FOOTER
      ============================================================ */}
      <footer className="relative z-10 border-t border-gold-400/20 mt-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-gold-400 to-gold-600">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm font-semibold text-cream-800">
                AI CareerOS
              </span>
            </div>
            <p className="text-xs text-cream-500 text-center sm:text-right">
              Open-source · Apache 2.0 · Built with care
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ============================================================
// Sub-components
// ============================================================

function MockCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-white/70 p-3 sm:p-4 transition-transform duration-300 hover:scale-105">
      <div className="flex items-center justify-between">
        <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-widest text-cream-500">
          {label}
        </span>
        <Icon className="h-4 w-4 text-gold-500" />
      </div>
      <p className="mt-2 text-2xl sm:text-3xl font-bold gradient-text">
        {value}
      </p>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  gradient: string;
  delay: number;
}

function FeatureCard({
  icon: Icon,
  title,
  description,
  gradient,
  delay,
}: FeatureCardProps) {
  return (
    <div
      className="glass-card-hover group p-6 sm:p-7 animate-slide-up cursor-default"
      style={{ animationDelay: `${delay * 0.05}s` }}
    >
      <div
        className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${gradient} shadow-lg transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6`}
      >
        <Icon className="h-6 w-6 text-white" />
      </div>
      <h3 className="mt-5 text-lg font-bold text-cream-900">{title}</h3>
      <p className="mt-2 text-sm text-cream-600 leading-relaxed">
        {description}
      </p>
    </div>
  );
}

interface StepCardProps {
  number: number;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  delay: number;
}

function StepCard({ number, icon: Icon, title, description, delay }: StepCardProps) {
  return (
    <div
      className="glass-card-hover group p-6 sm:p-7 relative animate-slide-up"
      style={{ animationDelay: `${delay * 0.08}s` }}
    >
      <span className="absolute -top-3 -left-3 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-gold-400 to-gold-600 text-sm font-bold text-white shadow-lg shadow-gold-400/40 transition-transform duration-300 group-hover:scale-110">
        {number}
      </span>
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/30">
        <Icon className="h-6 w-6 text-white" />
      </div>
      <h3 className="mt-5 text-lg font-bold text-cream-900">{title}</h3>
      <p className="mt-2 text-sm text-cream-600 leading-relaxed">
        {description}
      </p>
    </div>
  );
}

function TrustPoint({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-3">
      <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
      <span className="text-sm text-cream-700">{text}</span>
    </li>
  );
}

function SecurityStat({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="glass-card p-4 sm:p-5 text-center transition-transform duration-300 hover:scale-105">
      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/30">
        <Icon className="h-5 w-5 text-white" />
      </div>
      <p className="mt-3 text-[10px] font-semibold uppercase tracking-widest text-cream-500">
        {label}
      </p>
      <p className="mt-1 text-sm font-bold text-cream-900">{value}</p>
    </div>
  );
}