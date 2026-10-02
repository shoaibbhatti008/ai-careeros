import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Globe,
  History,
  Loader2,
  LogIn,
  Shield,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { clsx } from "clsx";

import {
  getOverview,
  listAuditLogs,
  listLoginHistory,
  listSecurityEvents,
  type AuditLog,
  type LoginAttempt,
  type SecurityEvent,
} from "@/lib/security";

type Tab = "overview" | "audit" | "logins" | "events";

const TABS: { id: Tab; label: string; icon: typeof Shield }[] = [
  { id: "overview", label: "Overview", icon: ShieldCheck },
  { id: "audit", label: "Audit Logs", icon: History },
  { id: "logins", label: "Login History", icon: LogIn },
  { id: "events", label: "Security Events", icon: AlertTriangle },
];

export default function Security() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in">
      {/* Header */}
      <div className="animate-slide-up">
        <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
          Privacy
        </p>
        <h1 className="mt-2 text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
          Security Center
        </h1>
        <p className="mt-1 text-sm sm:text-base text-cream-600">
          Monitor account activity, login history, and security events.
        </p>
      </div>

      {/* Tabs */}
      <div
        className="glass-card p-1.5 flex flex-wrap gap-1 animate-slide-up"
        style={{ animationDelay: "0.1s" }}
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={clsx(
              "flex flex-1 min-w-[120px] items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-xs sm:text-sm font-medium transition-all duration-200",
              activeTab === tab.id
                ? "bg-gradient-to-r from-gold-400 to-gold-500 text-white shadow-gold"
                : "text-cream-700 hover:bg-gold-400/10"
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="animate-slide-up" style={{ animationDelay: "0.15s" }}>
        {activeTab === "overview" && <OverviewTab />}
        {activeTab === "audit" && <AuditTab />}
        {activeTab === "logins" && <LoginsTab />}
        {activeTab === "events" && <EventsTab />}
      </div>
    </div>
  );
}

// ============================================================
// Overview Tab
// ============================================================

function OverviewTab() {
  const {
    data: overview,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["security", "overview"],
    queryFn: getOverview,
  });

  if (isLoading) return <Loading />;
  if (isError || !overview) return <ErrorState label="overview" />;

  return (
    <div className="space-y-6">
      {/* Account Status */}
      <div className="glass-card p-5 sm:p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-green-400 to-emerald-600 shadow-lg shadow-green-500/40">
            <ShieldCheck className="h-7 w-7 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-cream-500">
              Account Status
            </p>
            <p className="mt-1 text-xl sm:text-2xl font-bold text-cream-900">
              {overview.is_active ? "Active & Protected" : "Inactive"}
            </p>
            <p className="mt-0.5 text-xs text-cream-600">{overview.email}</p>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label="Successful logins"
          value={overview.recent_logins_count}
          icon={CheckCircle2}
          gradient="from-green-500 to-emerald-500"
          delay={0}
        />
        <StatTile
          label="Failed logins"
          value={overview.failed_logins_count}
          icon={XCircle}
          gradient="from-red-500 to-rose-500"
          delay={1}
        />
        <StatTile
          label="Open events"
          value={overview.unresolved_events_count}
          icon={AlertTriangle}
          gradient="from-orange-500 to-amber-500"
          delay={2}
        />
        <StatTile
          label="Last login"
          value={
            overview.last_login
              ? new Date(overview.last_login).toLocaleDateString()
              : "—"
          }
          icon={Clock}
          gradient="from-blue-500 to-cyan-500"
          delay={3}
        />
      </div>

      {/* Account info */}
      <div className="glass-card p-5 sm:p-6">
        <h3 className="text-base font-bold text-cream-900 mb-4">
          Account Information
        </h3>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <InfoRow
            label="Account ID"
            value={overview.user_id}
            mono
          />
          <InfoRow label="Email" value={overview.email} />
          <InfoRow
            label="Account created"
            value={new Date(overview.account_created).toLocaleString()}
          />
          <InfoRow
            label="Last login"
            value={
              overview.last_login
                ? new Date(overview.last_login).toLocaleString()
                : "Never"
            }
          />
        </dl>
      </div>
    </div>
  );
}

// ============================================================
// Audit Logs Tab
// ============================================================

function AuditTab() {
  const { data: logs = [], isLoading, isError } = useQuery({
    queryKey: ["security", "audit"],
    queryFn: listAuditLogs,
  });

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState label="audit logs" />;

  if (logs.length === 0) {
    return <EmptyState
      icon={History}
      title="No audit logs"
      description="Activity will appear here as you use the platform."
    />;
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="border-b border-gold-400/20 p-4 sm:p-5">
        <h3 className="text-base font-bold text-cream-900">
          Recent Activity ({logs.length})
        </h3>
      </div>
      <ul className="divide-y divide-gold-400/10">
        {logs.map((log, i) => (
          <AuditRow key={log.id} log={log} delay={i} />
        ))}
      </ul>
    </div>
  );
}

function AuditRow({ log, delay }: { log: AuditLog; delay: number }) {
  const actionColors: Record<string, string> = {
    login_success: "text-green-700 bg-green-500/10 border-green-500/30",
    login_failed: "text-red-700 bg-red-500/10 border-red-500/30",
    logout: "text-blue-700 bg-blue-500/10 border-blue-500/30",
    password_change: "text-amber-700 bg-amber-500/10 border-amber-500/30",
    user_created: "text-emerald-700 bg-emerald-500/10 border-emerald-500/30",
    rate_limit_hit: "text-orange-700 bg-orange-500/10 border-orange-500/30",
    prompt_injection_blocked: "text-rose-700 bg-rose-500/10 border-rose-500/30",
  };
  const colors =
    actionColors[log.action] ||
    "text-cream-700 bg-cream-200/50 border-cream-300";

  return (
    <li
      className="group p-4 sm:p-5 hover:bg-gold-400/5 transition-colors animate-slide-in-right"
      style={{ animationDelay: `${delay * 0.02}s` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={clsx(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider",
                colors
              )}
            >
              {log.action.replace(/_/g, " ")}
            </span>
            <span className="text-[10px] text-cream-500">
              {new Date(log.created_at).toLocaleString()}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-cream-600">
            {log.ip_address && (
              <span className="inline-flex items-center gap-1">
                <Globe className="h-3 w-3 text-gold-500" />
                {log.ip_address}
              </span>
            )}
            {log.request_id && (
              <span className="font-mono text-[10px] text-cream-500">
                #{log.request_id.slice(0, 8)}
              </span>
            )}
          </div>
        </div>
      </div>
    </li>
  );
}

// ============================================================
// Login History Tab
// ============================================================

function LoginsTab() {
  const {
    data: logins = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["security", "logins"],
    queryFn: listLoginHistory,
  });

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState label="login history" />;

  if (logins.length === 0) {
    return (
      <EmptyState
        icon={LogIn}
        title="No login history"
        description="Successful and failed login attempts will appear here."
      />
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="border-b border-gold-400/20 p-4 sm:p-5">
        <h3 className="text-base font-bold text-cream-900">
          Login Attempts ({logins.length})
        </h3>
      </div>
      <ul className="divide-y divide-gold-400/10">
        {logins.map((login, i) => (
          <LoginRow key={login.id} login={login} delay={i} />
        ))}
      </ul>
    </div>
  );
}

function LoginRow({ login, delay }: { login: LoginAttempt; delay: number }) {
  return (
    <li
      className="flex items-center gap-4 p-4 sm:p-5 hover:bg-gold-400/5 transition-colors animate-slide-in-right"
      style={{ animationDelay: `${delay * 0.02}s` }}
    >
      <div
        className={clsx(
          "flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl shadow-lg",
          login.was_successful
            ? "bg-gradient-to-br from-green-400 to-emerald-600 shadow-green-500/40"
            : "bg-gradient-to-br from-red-400 to-rose-600 shadow-red-500/40"
        )}
      >
        {login.was_successful ? (
          <CheckCircle2 className="h-5 w-5 text-white" />
        ) : (
          <XCircle className="h-5 w-5 text-white" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-cream-900">
          {login.was_successful ? "Successful login" : "Failed login"}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-cream-600">
          <span>{login.email}</span>
          {login.ip_address && (
            <span className="inline-flex items-center gap-1">
              <Globe className="h-3 w-3 text-gold-500" />
              {login.ip_address}
            </span>
          )}
        </div>
      </div>
      <span className="hidden sm:block flex-shrink-0 text-xs text-cream-500">
        {new Date(login.created_at).toLocaleString()}
      </span>
    </li>
  );
}

// ============================================================
// Security Events Tab
// ============================================================

function EventsTab() {
  const {
    data: events = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["security", "events"],
    queryFn: listSecurityEvents,
  });

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState label="security events" />;

  if (events.length === 0) {
    return (
      <EmptyState
        icon={ShieldCheck}
        title="No security events"
        description="Security events (rate limits, suspicious activity) will appear here."
        success
      />
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="border-b border-gold-400/20 p-4 sm:p-5">
        <h3 className="text-base font-bold text-cream-900">
          Security Events ({events.length})
        </h3>
      </div>
      <ul className="divide-y divide-gold-400/10">
        {events.map((event, i) => (
          <EventRow key={event.id} event={event} delay={i} />
        ))}
      </ul>
    </div>
  );
}

function EventRow({ event, delay }: { event: SecurityEvent; delay: number }) {
  const severityColors: Record<string, string> = {
    low: "text-blue-700 bg-blue-500/10 border-blue-500/30",
    medium: "text-amber-700 bg-amber-500/10 border-amber-500/30",
    high: "text-orange-700 bg-orange-500/10 border-orange-500/30",
    critical: "text-red-700 bg-red-500/10 border-red-500/30",
  };
  const colors = severityColors[event.severity] || severityColors.low;

  return (
    <li
      className="group p-4 sm:p-5 hover:bg-gold-400/5 transition-colors animate-slide-in-right"
      style={{ animationDelay: `${delay * 0.02}s` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={clsx(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                colors
              )}
            >
              {event.severity}
            </span>
            <span className="text-xs font-semibold text-cream-900">
              {event.event_type.replace(/_/g, " ")}
            </span>
            {event.resolved && (
              <span className="badge-success text-[10px]">Resolved</span>
            )}
          </div>
          <p className="mt-2 text-sm text-cream-700">{event.description}</p>
          <div className="mt-1 flex flex-wrap items-center gap-x-3 text-xs text-cream-500">
            {event.ip_address && (
              <span className="inline-flex items-center gap-1">
                <Globe className="h-3 w-3 text-gold-500" />
                {event.ip_address}
              </span>
            )}
            <span>{new Date(event.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </li>
  );
}

// ============================================================
// Shared components
// ============================================================

function Loading() {
  return (
    <div className="flex items-center justify-center py-16">
      <Loader2 className="h-8 w-8 animate-spin text-gold-500" />
    </div>
  );
}

function ErrorState({ label }: { label: string }) {
  return (
    <div className="glass-card p-6 border-l-4 border-l-red-500">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold text-cream-900">
            Couldn't load {label}
          </p>
          <p className="text-sm text-cream-600">
            Please try refreshing the page.
          </p>
        </div>
      </div>
    </div>
  );
}

function EmptyState({
  icon: Icon,
  title,
  description,
  success = false,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  success?: boolean;
}) {
  return (
    <div className="glass-card p-8 sm:p-12 text-center animate-scale-in">
      <div
        className={clsx(
          "mx-auto flex h-20 w-20 items-center justify-center rounded-3xl shadow-2xl animate-float-slow",
          success
            ? "bg-gradient-to-br from-green-400 to-emerald-600 shadow-green-500/40"
            : "bg-gradient-to-br from-gold-400 to-gold-600 shadow-gold-400/40"
        )}
      >
        <Icon className="h-10 w-10 text-white" />
      </div>
      <h2 className="mt-6 text-xl sm:text-2xl font-bold text-cream-900">
        {title}
      </h2>
      <p className="mt-2 text-sm text-cream-600 max-w-md mx-auto">
        {description}
      </p>
    </div>
  );
}

interface StatTileProps {
  label: string;
  value: number | string;
  icon: React.ComponentType<{ className?: string }>;
  gradient: string;
  delay: number;
}

function StatTile({ label, value, icon: Icon, gradient, delay }: StatTileProps) {
  return (
    <div
      className="glass-card-hover group p-5 sm:p-6 animate-slide-up cursor-default"
      style={{ animationDelay: `${delay * 0.08}s` }}
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
    </div>
  );
}

function InfoRow({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-[10px] font-bold uppercase tracking-widest text-cream-500">
        {label}
      </dt>
      <dd
        className={clsx(
          "mt-1 text-sm font-medium text-cream-900 break-all",
          mono && "font-mono text-xs"
        )}
      >
        {value}
      </dd>
    </div>
  );
}