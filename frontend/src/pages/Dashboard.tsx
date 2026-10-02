import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import {
  ArrowRight,
  Briefcase,
  FileText,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";

// ============================================================
// Getting Started Steps — Each links to a real page
// ============================================================

const GETTING_STARTED_STEPS = [
  {
    title: "Upload a resume to get an AI-powered analysis.",
    to: "/resumes",
    icon: FileText,
    cta: "Go to Resumes",
  },
  {
    title: "Browse jobs and see how your skills match.",
    to: "/jobs",
    icon: Briefcase,
    cta: "Browse Jobs",
  },
  {
    title: "Identify skill gaps for your target role.",
    to: "/resumes",
    icon: Target,
    cta: "Analyze Skills",
  },
  {
    title: "Practice mock interviews with the Interview Agent.",
    to: "/assistant",
    icon: Sparkles,
    cta: "Start Practice",
  },
];

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in">
      {/* Welcome Header */}
      <div className="animate-slide-up">
        <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
          Dashboard
        </p>
        <h1 className="mt-2 text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
          Welcome back{user?.first_name ? `, ${user.first_name}` : ""}
        </h1>
        <p className="mt-2 text-sm sm:text-base text-cream-600">
          Here's an overview of your career intelligence dashboard.
        </p>
      </div>

      {/* Stat Cards — Clickable */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4">
        <StatCard
          label="Resumes"
          value="0"
          hint="Upload your first resume"
          icon={FileText}
          delay={0}
          gradient="from-blue-500 to-cyan-500"
          to="/resumes"
        />
        <StatCard
          label="Job Matches"
          value="0"
          hint="Analyze job postings"
          icon={Briefcase}
          delay={1}
          gradient="from-purple-500 to-pink-500"
          to="/jobs"
        />
        <StatCard
          label="Skill Gaps"
          value="0"
          hint="Identify target skills"
          icon={Target}
          delay={2}
          gradient="from-orange-500 to-red-500"
          to="/resumes"
        />
        <StatCard
          label="AI Assistant"
          value="Ready"
          hint="Ask anything"
          icon={Sparkles}
          delay={3}
          gradient="from-green-500 to-emerald-500"
          to="/assistant"
        />
      </div>

      {/* Getting Started — Fully clickable */}
      <div
        className="card p-4 sm:p-6 animate-slide-up"
        style={{ animationDelay: "0.3s" }}
      >
        <div className="flex items-center gap-3 sm:gap-4 mb-5 sm:mb-6">
          <div className="flex h-10 w-10 sm:h-12 sm:w-12 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40">
            <TrendingUp className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg sm:text-2xl font-bold text-cream-900">
              Getting Started
            </h2>
            <p className="text-xs sm:text-sm text-cream-600">
              Four steps to unlock your career intelligence
            </p>
          </div>
        </div>

        <div className="space-y-2 sm:space-y-3">
          {GETTING_STARTED_STEPS.map((step, index) => (
            <GettingStartedItem
              key={index}
              index={index}
              title={step.title}
              to={step.to}
              icon={step.icon}
              cta={step.cta}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Getting Started Item
// ============================================================

interface GettingStartedItemProps {
  index: number;
  title: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  cta: string;
}

function GettingStartedItem({
  index,
  title,
  to,
  icon: Icon,
  cta,
}: GettingStartedItemProps) {
  return (
    <Link
      to={to}
      className="group flex items-center gap-3 sm:gap-4 rounded-xl bg-white/40 p-3 sm:p-4 transition-all duration-200 hover:bg-white/70 hover:translate-x-2 cursor-pointer border border-gold-400/10 hover:border-gold-400/30 animate-slide-in-right"
      style={{ animationDelay: `${0.4 + index * 0.05}s` }}
      aria-label={cta}
    >
      {/* Step number */}
      <span className="flex h-7 w-7 sm:h-8 sm:w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-gold-400 to-gold-600 text-xs sm:text-sm font-bold text-white shadow-lg shadow-gold-400/40 transition-transform duration-300 group-hover:scale-110">
        {index + 1}
      </span>

      {/* Icon — mobile visible, extra visual cue */}
      <div className="hidden sm:flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-gold-400/20 to-gold-500/10 border border-gold-400/20 transition-transform duration-300 group-hover:scale-110">
        <Icon className="h-4 w-4 text-gold-700" />
      </div>

      {/* Title */}
      <span className="flex-1 text-xs sm:text-sm font-medium text-cream-800">
        {title}
      </span>

      {/* Hover CTA (visible on desktop) */}
      <span className="hidden md:inline-flex items-center gap-1 text-xs font-semibold text-gold-700 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        {cta}
        <ArrowRight className="h-3 w-3 transition-transform duration-200 group-hover:translate-x-1" />
      </span>

      {/* Arrow always visible on mobile */}
      <ArrowRight className="h-4 w-4 flex-shrink-0 text-gold-500 transition-transform duration-200 group-hover:translate-x-1 md:hidden" />
    </Link>
  );
}

// ============================================================
// Stat Card
// ============================================================

interface StatCardProps {
  label: string;
  value: string;
  hint: string;
  icon: React.ComponentType<{ className?: string }>;
  delay: number;
  gradient: string;
  to: string;
}

function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  delay,
  gradient,
  to,
}: StatCardProps) {
  return (
    <Link
      to={to}
      className="glass-card-hover group block p-5 sm:p-6 animate-slide-up cursor-pointer"
      style={{ animationDelay: `${delay * 0.1}s` }}
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-widest text-cream-500">
          {label}
        </span>
        <div
          className={`flex h-10 w-10 sm:h-11 sm:w-11 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} shadow-lg transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6`}
        >
          <Icon className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
        </div>
      </div>
      <p className="mt-3 sm:mt-4 text-2xl sm:text-3xl font-bold bg-gradient-to-br from-gold-600 to-gold-400 bg-clip-text text-transparent">
        {value}
      </p>
      <p className="mt-1 text-[10px] sm:text-xs text-cream-500">{hint}</p>
    </Link>
  );
}