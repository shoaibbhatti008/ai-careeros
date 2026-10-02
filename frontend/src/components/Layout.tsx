import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Brain,
  FileText,
  Home,
  LogOut,
  Menu,
  Shield,
  Sparkles,
  User,
  X,
} from "lucide-react";
import { clsx } from "clsx";

import { useAuth } from "@/contexts/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: Home },
  { to: "/resumes", label: "Resumes", icon: FileText },
  { to: "/jobs", label: "Jobs", icon: Sparkles },
  { to: "/assistant", label: "Assistant", icon: Brain },
  { to: "/security", label: "Security", icon: Shield },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  function closeSidebar() {
    setIsSidebarOpen(false);
  }

  return (
    <div className="flex min-h-screen relative">
      {/* Decorative orbs — hidden on mobile */}
      <div
        className="hidden md:block orb orb-gold w-96 h-96 -top-32 -left-32 animate-float-slow"
        aria-hidden="true"
      />
      <div
        className="hidden md:block orb orb-amber w-80 h-80 bottom-0 -right-40 animate-float-slow"
        style={{ animationDelay: "2s" }}
        aria-hidden="true"
      />

      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm md:hidden"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* Mobile menu button */}
      <button
        type="button"
        onClick={() => setIsSidebarOpen(true)}
        className="fixed top-4 left-4 z-30 flex h-11 w-11 items-center justify-center rounded-xl glass-card-hover md:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5 text-gold-700" />
      </button>

      {/* Sidebar */}
      <aside
        className={clsx(
          "glass-sidebar fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ease-smooth",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full",
          "md:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className="flex h-20 items-center justify-between gap-3 border-b border-gold-400/20 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40 transition-transform duration-300 hover:scale-110 hover:rotate-3">
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
          </div>
          {/* Close button — mobile only */}
          <button
            type="button"
            onClick={closeSidebar}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-cream-600 hover:bg-gold-400/10 md:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1.5 p-5">
          <p className="px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-cream-600">
            Menu
          </p>
          {NAV_ITEMS.map((item, index) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/dashboard"}
              onClick={closeSidebar}
              className={({ isActive }) =>
                clsx(
                  "group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 animate-slide-in-right",
                  `stagger-${index + 1}`,
                  isActive
                    ? "bg-gradient-to-r from-gold-400/30 to-gold-500/20 text-gold-900 border border-gold-400/40 shadow-gold"
                    : "text-cream-700 hover:bg-gold-400/10 hover:text-gold-800 hover:translate-x-1"
                )
              }
            >
              <item.icon className="h-4 w-4 transition-transform duration-300 group-hover:scale-110" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User info + Logout */}
        <div className="absolute bottom-0 w-full border-t border-gold-400/20 p-5">
          <div className="mb-4 flex items-center gap-3 rounded-xl bg-white/60 p-3 transition-all duration-300 hover:bg-white/80 hover:shadow-cream">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-gold-400 to-gold-600 text-white shadow-lg shadow-gold-400/40">
              <User className="h-5 w-5" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-semibold text-cream-800">
                {user?.first_name || user?.email}
              </p>
              <p className="truncate text-xs text-cream-500">{user?.email}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-cream-700 transition-all duration-200 hover:bg-red-50 hover:text-red-700"
          >
            <LogOut className="h-4 w-4 transition-transform duration-300 group-hover:-translate-x-1" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 md:ml-72 relative z-10">
        <div className="mx-auto max-w-7xl p-4 pt-20 md:p-8 md:pt-8 animate-fade-in-slow">
          <Outlet />
        </div>
      </main>
    </div>
  );
}