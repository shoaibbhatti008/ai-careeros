import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Brain } from "lucide-react";

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
    return <div className="flex h-screen items-center justify-center">Loading…</div>;
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
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center">
          <Brain className="h-12 w-12 text-primary-600" />
          <h1 className="mt-4 text-2xl font-bold">Welcome back</h1>
          <p className="mt-1 text-sm text-slate-500">
            Sign in to your AI CareerOS account
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4">
          <div>
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
            {errors.email && <p className="error-text">{errors.email.message}</p>}
          </div>

          <div>
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
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {errors.root.message}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full"
          >
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>

          <p className="text-center text-sm text-slate-500">
            Don't have an account?{" "}
            <Link to="/register" className="text-primary-600 hover:underline">
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}