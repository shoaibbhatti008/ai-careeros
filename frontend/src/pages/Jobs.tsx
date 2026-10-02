import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  Briefcase,
  Building2,
  Filter,
  Loader2,
  MapPin,
  Search,
  Sparkles,
  TrendingUp,
  X,
} from "lucide-react";
import { clsx } from "clsx";

import { listJobs, type Job, type JobFilters } from "@/lib/jobs";
import { extractErrorMessage } from "@/lib/api";

const EMPLOYMENT_TYPES = [
  { value: "", label: "All types" },
  { value: "full_time", label: "Full time" },
  { value: "part_time", label: "Part time" },
  { value: "contract", label: "Contract" },
  { value: "internship", label: "Internship" },
  { value: "freelance", label: "Freelance" },
];

const REMOTE_POLICIES = [
  { value: "", label: "All locations" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
];

export default function Jobs() {
  const [filters, setFilters] = useState<JobFilters>({});
  const [showFilters, setShowFilters] = useState(false);

  const {
    data: jobs = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => listJobs(filters),
  });

  function updateFilter(key: keyof JobFilters, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));
  }

  function clearFilters() {
    setFilters({});
  }

  const hasActiveFilters = Object.values(filters).some(Boolean);

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in">
      {/* Header */}
      <div className="animate-slide-up">
        <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
          Discover
        </p>
        <h1 className="mt-2 text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
          Job Opportunities
        </h1>
        <p className="mt-1 text-sm sm:text-base text-cream-600">
          Find roles that match your skills and career goals.
        </p>
      </div>

      {/* Search + Filter Toggle */}
      <div
        className="flex flex-col gap-3 sm:flex-row animate-slide-up"
        style={{ animationDelay: "0.1s" }}
      >
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gold-500" />
          <input
            type="text"
            placeholder="Search jobs, companies, locations..."
            value={filters.search || ""}
            onChange={(e) => updateFilter("search", e.target.value)}
            className="input pl-11"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowFilters((s) => !s)}
          className={clsx(
            "btn-secondary self-stretch sm:self-auto",
            hasActiveFilters && "border-gold-400 bg-gold-400/10"
          )}
        >
          <Filter className="h-4 w-4" />
          Filters
          {hasActiveFilters && (
            <span className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-gold-500 text-[10px] font-bold text-white">
              {Object.values(filters).filter(Boolean).length}
            </span>
          )}
        </button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="glass-card p-4 sm:p-6 animate-slide-down">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold uppercase tracking-widest text-gold-700">
              Filter Jobs
            </h3>
            <div className="flex items-center gap-2">
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="text-xs text-cream-600 hover:text-cream-900 underline"
                >
                  Clear all
                </button>
              )}
              <button
                type="button"
                onClick={() => setShowFilters(false)}
                className="flex h-7 w-7 items-center justify-center rounded-lg text-cream-600 hover:bg-gold-400/10"
                aria-label="Close filters"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <FilterField label="Company">
              <input
                type="text"
                placeholder="Any company"
                value={filters.company || ""}
                onChange={(e) => updateFilter("company", e.target.value)}
                className="input"
              />
            </FilterField>

            <FilterField label="Location">
              <input
                type="text"
                placeholder="Any location"
                value={filters.location || ""}
                onChange={(e) => updateFilter("location", e.target.value)}
                className="input"
              />
            </FilterField>

            <FilterField label="Remote policy">
              <select
                value={filters.remote_policy || ""}
                onChange={(e) => updateFilter("remote_policy", e.target.value)}
                className="input"
              >
                {REMOTE_POLICIES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </FilterField>

            <FilterField label="Employment type">
              <select
                value={filters.employment_type || ""}
                onChange={(e) =>
                  updateFilter("employment_type", e.target.value)
                }
                className="input"
              >
                {EMPLOYMENT_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </FilterField>
          </div>
        </div>
      )}

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
                Couldn't load jobs
              </p>
              <p className="text-sm text-cream-600">
                {extractErrorMessage(error)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Empty */}
      {!isLoading && !isError && jobs.length === 0 && (
        <EmptyState hasFilters={hasActiveFilters} onClear={clearFilters} />
      )}

      {/* Jobs Grid */}
      {jobs.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-2">
          {jobs.map((job, index) => (
            <JobCard key={job.id} job={job} delay={index} />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================
// Sub-components
// ============================================================

function FilterField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-cream-600">
        {label}
      </label>
      {children}
    </div>
  );
}

function EmptyState({
  hasFilters,
  onClear,
}: {
  hasFilters: boolean;
  onClear: () => void;
}) {
  return (
    <div className="glass-card p-8 sm:p-12 text-center animate-scale-in">
      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/40 animate-float-slow">
        <Briefcase className="h-10 w-10 text-white" />
      </div>
      <h2 className="mt-6 text-xl sm:text-2xl font-bold text-cream-900">
        {hasFilters ? "No matching jobs" : "No jobs yet"}
      </h2>
      <p className="mt-2 text-sm text-cream-600 max-w-md mx-auto">
        {hasFilters
          ? "Try adjusting your filters or search query."
          : "Jobs will appear here once available. Check back soon!"}
      </p>
      {hasFilters && (
        <button type="button" onClick={onClear} className="btn-primary mt-6">
          Clear filters
        </button>
      )}
    </div>
  );
}

interface JobCardProps {
  job: Job;
  delay: number;
}

function JobCard({ job, delay }: JobCardProps) {
  const salary =
    job.salary_min && job.salary_max
      ? `${job.currency || "$"}${job.salary_min.toLocaleString()} - ${job.currency || "$"}${job.salary_max.toLocaleString()}`
      : null;

  return (
    <div
      className="glass-card-hover group p-5 sm:p-6 animate-slide-up cursor-pointer"
      style={{ animationDelay: `${delay * 0.04}s` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
            <Building2 className="h-6 w-6 text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-base sm:text-lg font-bold text-cream-900 group-hover:text-gold-700 transition-colors">
              {job.title}
            </h3>
            <p className="mt-0.5 text-sm text-cream-700 font-medium">
              {job.company}
            </p>
          </div>
        </div>
        {job.status === "open" && (
          <span className="badge-success flex-shrink-0">Open</span>
        )}
      </div>

      {/* Meta */}
      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-cream-600">
        {job.location && (
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-gold-500" />
            {job.location}
          </span>
        )}
        <span className="inline-flex items-center gap-1.5">
          <Briefcase className="h-3.5 w-3.5 text-gold-500" />
          {job.employment_type.replace("_", " ")}
        </span>
        {job.remote_policy && (
          <span className="inline-flex items-center gap-1.5">
            <TrendingUp className="h-3.5 w-3.5 text-gold-500" />
            {job.remote_policy}
          </span>
        )}
      </div>

      {/* Salary */}
      {salary && (
        <p className="mt-3 text-sm font-semibold text-gold-700">{salary}</p>
      )}

      {/* Skills */}
      {job.skills.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {job.skills.slice(0, 6).map((skill) => (
            <span
              key={skill.id}
              className="inline-flex items-center rounded-full bg-gold-400/15 px-2.5 py-1 text-[10px] font-medium text-gold-800 border border-gold-400/30 transition-all duration-200 hover:bg-gold-400/25 hover:scale-105"
            >
              {skill.name}
            </span>
          ))}
          {job.skills.length > 6 && (
            <span className="inline-flex items-center rounded-full bg-cream-200/50 px-2.5 py-1 text-[10px] font-medium text-cream-700">
              +{job.skills.length - 6} more
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="mt-5 flex items-center justify-between pt-4 border-t border-gold-400/20">
        <span className="text-[10px] font-medium uppercase tracking-widest text-cream-500">
          {job.seniority || "—"}
        </span>
        <button
          type="button"
          className="btn-ghost text-xs group-hover:text-gold-700 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          <Sparkles className="h-3 w-3" />
          Match
        </button>
      </div>
    </div>
  );
}