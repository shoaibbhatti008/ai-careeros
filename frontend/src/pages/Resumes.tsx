import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  FileText,
  Loader2,
  Plus,
  Search,
  Sparkles,
  Trash2,
  Upload,
  X,
} from "lucide-react";

import {
  createResume,
  deleteResume,
  listResumes,
  updateResume,
  type Resume,
} from "@/lib/resumes";
import { extractErrorMessage } from "@/lib/api";

export default function Resumes() {
  const [search, setSearch] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const queryClient = useQueryClient();

  const {
    data: resumes = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["resumes", search],
    queryFn: () => listResumes({ search: search || undefined }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });

  const setPrimaryMutation = useMutation({
    mutationFn: (id: string) => updateResume(id, { is_primary: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between animate-slide-up">
        <div>
          <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
            Library
          </p>
          <h1 className="mt-2 text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
            Your Resumes
          </h1>
          <p className="mt-1 text-sm sm:text-base text-cream-600">
            Manage, analyze, and track resume versions.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="btn-primary self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" />
          New Resume
        </button>
      </div>

      {/* Search */}
      <div className="relative animate-slide-up" style={{ animationDelay: "0.1s" }}>
        <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gold-500" />
        <input
          type="text"
          placeholder="Search resumes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input pl-11"
        />
      </div>

      {/* Loading / Error / Empty states */}
      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-gold-500" />
        </div>
      )}

      {isError && (
        <div className="glass-card p-6 border-l-4 border-l-red-500">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-cream-900">
                Couldn't load resumes
              </p>
              <p className="text-sm text-cream-600">
                {extractErrorMessage(error)}
              </p>
            </div>
          </div>
        </div>
      )}

      {!isLoading && !isError && resumes.length === 0 && (
        <EmptyState onCreate={() => setIsCreateOpen(true)} />
      )}

      {/* Resume grid */}
      {resumes.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3">
          {resumes.map((resume, index) => (
            <ResumeCard
              key={resume.id}
              resume={resume}
              delay={index}
              onDelete={() => {
                if (confirm(`Delete "${resume.title}"?`)) {
                  deleteMutation.mutate(resume.id);
                }
              }}
              onSetPrimary={() => setPrimaryMutation.mutate(resume.id)}
              isDeleting={
                deleteMutation.isPending &&
                deleteMutation.variables === resume.id
              }
            />
          ))}
        </div>
      )}

      {/* Create modal */}
      {isCreateOpen && (
        <CreateResumeModal
          onClose={() => setIsCreateOpen(false)}
          onCreated={() => {
            setIsCreateOpen(false);
            queryClient.invalidateQueries({ queryKey: ["resumes"] });
          }}
        />
      )}
    </div>
  );
}

// ============================================================
// Empty State
// ============================================================

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div
      className="glass-card p-8 sm:p-12 text-center animate-scale-in"
      style={{ animationDelay: "0.2s" }}
    >
      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/40 animate-float-slow">
        <FileText className="h-10 w-10 text-white" />
      </div>
      <h2 className="mt-6 text-xl sm:text-2xl font-bold text-cream-900">
        No resumes yet
      </h2>
      <p className="mt-2 text-sm text-cream-600 max-w-md mx-auto">
        Upload your first resume to get an AI-powered analysis with skills,
        strengths, and improvement suggestions.
      </p>
      <button type="button" onClick={onCreate} className="btn-primary mt-6">
        <Plus className="h-4 w-4" />
        Create your first resume
      </button>
    </div>
  );
}

// ============================================================
// Resume Card
// ============================================================

interface ResumeCardProps {
  resume: Resume;
  delay: number;
  onDelete: () => void;
  onSetPrimary: () => void;
  isDeleting: boolean;
}

function ResumeCard({
  resume,
  delay,
  onDelete,
  onSetPrimary,
  isDeleting,
}: ResumeCardProps) {
  return (
    <div
      className="glass-card-hover group p-5 sm:p-6 animate-slide-up"
      style={{ animationDelay: `${delay * 0.05}s` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-10 w-10 sm:h-11 sm:w-11 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
            <FileText className="h-5 w-5 text-white" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm sm:text-base font-semibold text-cream-900">
              {resume.title}
            </p>
            <p className="text-[10px] sm:text-xs text-cream-500">
              {new Date(resume.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        {resume.is_primary && (
          <span className="badge-warning flex-shrink-0">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Primary
          </span>
        )}
      </div>

      {/* Status */}
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="badge-info">{resume.status}</span>
        {typeof resume.versions_count === "number" && (
          <span className="badge">
            {resume.versions_count} version
            {resume.versions_count === 1 ? "" : "s"}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="mt-5 flex flex-wrap items-center gap-2 pt-4 border-t border-gold-400/20">
        <button
          type="button"
          disabled
          className="btn-ghost text-xs flex-1"
          title="Coming soon"
        >
          <Sparkles className="h-3 w-3" />
          Analyze
        </button>
        {!resume.is_primary && (
          <button
            type="button"
            onClick={onSetPrimary}
            className="btn-ghost text-xs"
          >
            Set primary
          </button>
        )}
        <button
          type="button"
          onClick={onDelete}
          disabled={isDeleting}
          className="btn-ghost text-xs text-red-600 hover:bg-red-50"
        >
          {isDeleting ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <Trash2 className="h-3 w-3" />
          )}
        </button>
      </div>
    </div>
  );
}

// ============================================================
// Create Modal
// ============================================================

interface CreateResumeModalProps {
  onClose: () => void;
  onCreated: () => void;
}

function CreateResumeModal({ onClose, onCreated }: CreateResumeModalProps) {
  const [title, setTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [isPrimary, setIsPrimary] = useState(false);

  const mutation = useMutation({
    mutationFn: createResume,
    onSuccess: onCreated,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({
      title,
      raw_text: rawText || undefined,
      is_primary: isPrimary,
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="relative w-full max-w-lg glass-card p-6 sm:p-8 animate-scale-in">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-cream-900">
            New Resume
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-cream-600 hover:bg-gold-400/10"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="title" className="label">
              Resume title
            </label>
            <input
              id="title"
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Senior Backend Engineer"
              className="input"
            />
          </div>

          <div>
            <label htmlFor="raw_text" className="label">
              Resume text (optional)
            </label>
            <textarea
              id="raw_text"
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              rows={6}
              placeholder="Paste your resume text here for instant analysis..."
              className="input resize-none"
            />
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={isPrimary}
              onChange={(e) => setIsPrimary(e.target.checked)}
              className="h-4 w-4 rounded border-gold-400 text-gold-600 focus:ring-gold-500"
            />
            <span className="text-sm text-cream-700">
              Set as primary resume
            </span>
          </label>

          {mutation.isError && (
            <div className="rounded-xl bg-red-50 border border-red-200 p-3 text-sm text-red-700 animate-slide-down">
              {extractErrorMessage(mutation.error)}
            </div>
          )}

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending || !title.trim()}
              className="btn-primary flex-1"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating…
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Create
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}