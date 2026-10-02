import { useAuth } from "@/contexts/AuthContext";
import { Briefcase, FileText, Sparkles, Target } from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">
          Welcome back{user?.first_name ? `, ${user.first_name}` : ""}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Here's an overview of your career intelligence dashboard.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Resumes"
          value="—"
          hint="Upload your first resume"
          icon={FileText}
        />
        <StatCard
          label="Job Matches"
          value="—"
          hint="Analyze job postings"
          icon={Briefcase}
        />
        <StatCard
          label="Skill Gaps"
          value="—"
          hint="Identify target skills"
          icon={Target}
        />
        <StatCard
          label="AI Assistant"
          value="Ready"
          hint="Ask anything"
          icon={Sparkles}
        />
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold">Getting Started</h2>
        <ol className="mt-3 space-y-2 text-sm text-slate-600">
          <li>1. Upload a resume to get an AI-powered analysis.</li>
          <li>2. Browse jobs and see how your skills match.</li>
          <li>3. Identify skill gaps for your target role.</li>
          <li>4. Practice mock interviews with the Interview Agent.</li>
        </ol>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  hint: string;
  icon: React.ComponentType<{ className?: string }>;
}

function StatCard({ label, value, hint, icon: Icon }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500">{label}</span>
        <Icon className="h-5 w-5 text-slate-400" />
      </div>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-slate-400">{hint}</p>
    </div>
  );
}