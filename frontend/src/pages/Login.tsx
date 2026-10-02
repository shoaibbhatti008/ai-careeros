import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Brain, Loader2 } from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { extractErrorMessage } from "@/lib/api";

interface LoginForm {
  email: string;
  password: string;
}

export default function Login() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: Location })?.from?.pathname || "/";

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginForm>();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gold-500" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  async function onSubmit(data: LoginForm) {
    try {
      await login(data);
      navigate(from, { replace: true });
    } catch (error) {
      setError("root", { message: extractErrorMessage(error) });
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Decorative golden orbs */}
      <div
        className="orb orb-gold w-[500px] h-[500px] -top-40 -left-40 animate-float-slow"
        aria-hidden="true"
      />
      <div
        className="orb orb-amber w-[400px] h-[400px] -bottom-32 -right-32 animate-float-slow"
        style={{ animationDelay: "2s" }}
        aria-hidden="true"
      />
      <div
        className="orb orb-cream w-[350px] h-[350px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-float-slow"
        style={{ animationDelay: "4s" }}
        aria-hidden="true"
      />

      <div className="w-full max-w-md relative z-10 animate-scale-in">
        {/* Header */}
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/50 animate-float-slow">
            <Brain className="h-10 w-10 text-white" />
          </div>
          <h1 className="mt-6 text-4xl font-bold text-cream-900 text-shadow-soft">
            Welcome back
          </h1>
          <p className="mt-2 text-sm text-cream-600">
            Sign in to your AI CareerOS account
          </p>
        </div>

        {/* Form Card */}
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="glass-card p-8 space-y-5 animate-slide-up"
          style={{ animationDelay: "0.1s" }}
        >
          <div className="animate-slide-up" style={{ animationDelay: "0.15s" }}>
            <label htmlFor="email" className="label">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              className="input"
              placeholder="you@example.com"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && (
              <p className="error-text">{errors.email.message}</p>
            )}
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <label htmlFor="password" className="label">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="input"
              placeholder="••••••••"
              {...register("password", { required: "Password is required" })}
            />
            {errors.password && (
              <p className="error-text">{errors.password.message}</p>
            )}
          </div>

          {errors.root && (
            <div className="rounded-xl bg-red-50 border border-red-200 p-3 text-sm text-red-700 animate-slide-down">
              {errors.root.message}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full animate-slide-up"
            style={{ animationDelay: "0.25s" }}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Signing in…
              </>
            ) : (
              "Sign in"
            )}
          </button>

          <p
            className="text-center text-sm text-cream-600 animate-slide-up"
            style={{ animationDelay: "0.3s" }}
          >
            Don't have an account?{" "}
            <Link
              to="/register"
              className="font-semibold text-gold-700 hover:underline transition-all duration-200 hover:text-gold-900"
            >
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}