import { useAuth } from "@/contexts/AuthContext";
import {
  ArrowRight,
  Briefcase,
  FileText,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";

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

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4">
        <StatCard
          label="Resumes"
          value="0"
          hint="Upload your first resume"
          icon={FileText}
          delay={0}
          gradient="from-blue-500 to-cyan-500"
        />
        <StatCard
          label="Job Matches"
          value="0"
          hint="Analyze job postings"
          icon={Briefcase}
          delay={1}
          gradient="from-purple-500 to-pink-500"
        />
        <StatCard
          label="Skill Gaps"
          value="0"
          hint="Identify target skills"
          icon={Target}
          delay={2}
          gradient="from-orange-500 to-red-500"
        />
        <StatCard
          label="AI Assistant"
          value="Ready"
          hint="Ask anything"
          icon={Sparkles}
          delay={3}
          gradient="from-green-500 to-emerald-500"
        />
      </div>

      {/* Getting Started */}
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
          {[
            "Upload a resume to get an AI-powered analysis.",
            "Browse jobs and see how your skills match.",
            "Identify skill gaps for your target role.",
            "Practice mock interviews with the Interview Agent.",
          ].map((step, index) => (
            <div
              key={index}
              className="group flex items-center gap-3 sm:gap-4 rounded-xl bg-white/40 p-3 sm:p-4 transition-all duration-200 hover:bg-white/70 hover:translate-x-2 cursor-pointer border border-gold-400/10 hover:border-gold-400/30 animate-slide-in-right"
              style={{ animationDelay: `${0.4 + index * 0.05}s` }}
            >
              <span className="flex h-7 w-7 sm:h-8 sm:w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-gold-400 to-gold-600 text-xs sm:text-sm font-bold text-white shadow-lg shadow-gold-400/40">
                {index + 1}
              </span>
              <span className="flex-1 text-xs sm:text-sm font-medium text-cream-800">
                {step}
              </span>
              <ArrowRight className="h-4 w-4 flex-shrink-0 text-gold-500 transition-transform duration-200 group-hover:translate-x-1" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  hint: string;
  icon: React.ComponentType<{ className?: string }>;
  delay: number;
  gradient: string;
}

function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  delay,
  gradient,
}: StatCardProps) {
  return (
    <div
      className="glass-card-hover group p-5 sm:p-6 animate-slide-up cursor-pointer"
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
    </div>
  );
}