import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Brain, FileText, Home, LogOut, Shield, Sparkles, User } from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { clsx } from "clsx";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/resumes", label: "Resumes", icon: FileText },
  { to: "/jobs", label: "Jobs", icon: Sparkles },
  { to: "/assistant", label: "Assistant", icon: Brain },
  { to: "/security", label: "Security", icon: Shield },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 w-64 border-r border-slate-200 bg-white">
        <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6">
          <Brain className="h-6 w-6 text-primary-600" />
          <span className="text-lg font-semibold">AI CareerOS</span>
        </div>

        <nav className="flex flex-col gap-1 p-4">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary-50 text-primary-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 w-full border-t border-slate-200 p-4">
          <div className="mb-3 flex items-center gap-2 px-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-700">
              <User className="h-4 w-4" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium text-slate-900">
                {user?.first_name || user?.email}
              </p>
              <p className="truncate text-xs text-slate-500">{user?.email}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 flex-1">
        <div className="mx-auto max-w-7xl p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}