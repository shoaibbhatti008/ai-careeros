import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  FileText,
  Loader2,
  RefreshCw,
  Sparkles,
  TrendingUp,
  Zap,
} from "lucide-react";

import { extractErrorMessage } from "@/lib/api";
import {
  analyzeResume,
  getResume,
  type ResumeAnalysis,
} from "@/lib/resumes";

export default function ResumeDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    data: resume,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["resume", id],
    queryFn: () => getResume(id as string),
    enabled: !!id,
  });

  const analyzeMutation = useMutation({
    mutationFn: () => analyzeResume(id as string),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume", id] });
    },
  });

  if (!id) {
    navigate("/resumes");
    return null;
  }

  const currentVersion = resume?.versions?.find((v) => v.is_current);
  const analysis: ResumeAnalysis | null =
    analyzeMutation.data?.analysis || currentVersion?.analysis || null;

  // Provider badge
  const providerName = analyzeMutation.data?.provider || "heuristic";
  const providerLabel =
    providerName === "groq"
      ? "Groq · GPT-OSS-120B"
      : providerName === "openai"
      ? "OpenAI"
      : providerName === "anthropic"
      ? "Anthropic"
      : "Heuristic AI";
  const isRealLLM = providerName !== "heuristic";

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in">
      {/* Back button */}
      <Link
        to="/resumes"
        className="inline-flex items-center gap-2 text-sm font-medium text-cream-600 hover:text-gold-700 transition-colors animate-slide-up"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Resumes
      </Link>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-gold-500" />
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="glass-card p-6 border-l-4 border-l-red-500">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-cream-900">
                Couldn't load resume
              </p>
              <p className="text-sm text-cream-600">
                {extractErrorMessage(error)}
              </p>
            </div>
          </div>
        </div>
      )}

      {resume && (
        <>
          {/* Header */}
          <div className="animate-slide-up">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-4">
                <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40">
                  <FileText className="h-7 w-7 text-white" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-gold-600">
                    Resume
                  </p>
                  <h1 className="mt-1 text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
                    {resume.title}
                  </h1>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <span className="badge-info">{resume.status}</span>
                    {resume.is_primary && (
                      <span className="badge-warning">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Primary
                      </span>
                    )}
                    <span className="text-[10px] text-cream-500">
                      Created{" "}
                      {new Date(resume.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => analyzeMutation.mutate()}
                disabled={analyzeMutation.isPending}
                className="btn-primary self-start sm:self-auto"
              >
                {analyzeMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing…
                  </>
                ) : analysis ? (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    Re-run Analysis
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Run AI Analysis
                  </>
                )}
              </button>
            </div>

            {/* Error */}
            {analyzeMutation.isError && (
              <div className="mt-4 rounded-xl bg-red-50 border border-red-200 p-3 text-sm text-red-700 animate-slide-down">
                {extractErrorMessage(analyzeMutation.error)}
              </div>
            )}
          </div>

          {/* Analysis Section */}
          <div
            className="glass-card p-6 sm:p-8 animate-slide-up"
            style={{ animationDelay: "0.1s" }}
          >
            {/* Header + Badge */}
            <div className="flex items-center gap-3 mb-6 flex-wrap">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-lg sm:text-xl font-bold text-cream-900">
                    AI Analysis
                  </h2>

                  {isRealLLM && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-green-800 border border-green-500/30">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                      {providerLabel}
                    </span>
                  )}

                  {analysis && !isRealLLM && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-gold-400/15 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-gold-800 border border-gold-400/30">
                      <Zap className="h-3 w-3" />
                      Heuristic
                    </span>
                  )}
                </div>
                <p className="text-xs sm:text-sm text-cream-600">
                  Powered by ResumeAgent
                </p>
              </div>
            </div>

            {!analysis ? (
              <div className="rounded-xl bg-gold-400/5 border border-gold-400/20 p-6 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/40 animate-float-slow">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
                <h3 className="mt-4 text-lg font-bold text-cream-900">
                  No analysis yet
                </h3>
                <p className="mt-2 text-sm text-cream-600 max-w-md mx-auto">
                  Click "Run AI Analysis" to extract skills, strengths, and
                  improvement areas from this resume.
                </p>
              </div>
            ) : (
              <>
                {/* Summary */}
                {analyzeMutation.data?.summary && (
                  <div className="mb-6 rounded-xl bg-gold-400/5 border border-gold-400/20 p-4">
                    <p className="text-sm text-cream-700">
                      {analyzeMutation.data.summary}
                    </p>
                  </div>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                  <MiniStat
                    label="Skills found"
                    value={String(analysis.skills?.length ?? 0)}
                  />
                  <MiniStat
                    label="Strengths"
                    value={String(analysis.strengths?.length ?? 0)}
                  />
                  <MiniStat
                    label="Improvements"
                    value={String(analysis.improvements?.length ?? 0)}
                  />
                </div>

                {/* Seniority */}
                {analysis.seniority_estimate && (
                  <div className="mb-6 flex flex-wrap items-center gap-3">
                    <span className="text-xs font-semibold uppercase tracking-widest text-cream-500">
                      Seniority
                    </span>
                    <span className="badge-info capitalize">
                      {analysis.seniority_estimate}
                    </span>
                  </div>
                )}

                {/* Skills */}
                {analysis.skills && analysis.skills.length > 0 && (
                  <div className="mb-6">
                    <h4 className="mb-3 text-sm font-bold uppercase tracking-widest text-gold-700">
                      Extracted Skills
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.skills.map((skill, i) => (
                        <span
                          key={i}
                          className="inline-flex items-center rounded-full bg-gold-400/15 px-3 py-1 text-xs font-medium text-gold-800 border border-gold-400/30 transition-all duration-200 hover:bg-gold-400/25 hover:scale-105"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Strengths + Improvements */}
          {analysis && (
            <div
              className="grid grid-cols-1 gap-6 lg:grid-cols-2 animate-slide-up"
              style={{ animationDelay: "0.2s" }}
            >
              <AnalysisSection
                icon={CheckCircle2}
                title="Strengths"
                gradient="from-green-500 to-emerald-500"
                items={analysis.strengths || []}
                emptyText="No specific strengths identified."
              />
              <AnalysisSection
                icon={AlertTriangle}
                title="Improvements"
                gradient="from-orange-500 to-amber-500"
                items={analysis.improvements || []}
                emptyText="No specific improvements suggested."
              />
            </div>
          )}

          {/* ATS Hints */}
          {analysis && analysis.ats_hints && analysis.ats_hints.length > 0 && (
            <div
              className="glass-card p-6 animate-slide-up"
              style={{ animationDelay: "0.25s" }}
            >
              <h3 className="text-base font-bold text-cream-900 mb-4">
                ATS Optimization Hints
              </h3>
              <ul className="space-y-2">
                {analysis.ats_hints.map((hint, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-3 rounded-lg bg-white/40 p-3 text-sm text-cream-700 transition-all duration-200 hover:bg-white/70 hover:translate-x-1"
                  >
                    <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gold-500" />
                    {hint}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ============================================================
// Sub-components
// ============================================================

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-white/40 p-3 sm:p-4 text-center">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-cream-500">
        {label}
      </p>
      <p className="mt-1 text-xl sm:text-2xl font-bold gradient-text">
        {value}
      </p>
    </div>
  );
}

interface AnalysisSectionProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  gradient: string;
  items: string[];
  emptyText: string;
}

function AnalysisSection({
  icon: Icon,
  title,
  gradient,
  items,
  emptyText,
}: AnalysisSectionProps) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-center gap-3 mb-4">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} shadow-lg`}
        >
          <Icon className="h-5 w-5 text-white" />
        </div>
        <h3 className="text-base font-bold text-cream-900">{title}</h3>
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-cream-500 py-4 text-center">{emptyText}</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item, i) => (
            <li
              key={i}
              className="flex items-start gap-3 rounded-lg bg-white/40 p-3 text-sm text-cream-700 transition-all duration-200 hover:bg-white/70 hover:translate-x-1"
            >
              <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gold-500" />
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}