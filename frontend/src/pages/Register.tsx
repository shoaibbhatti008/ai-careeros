import { useForm } from "react-hook-form";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Brain, Loader2 } from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { extractErrorMessage } from "@/lib/api";

interface RegisterForm {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export default function Register() {
  const { register: authRegister, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<RegisterForm>();

  const password = watch("password");

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gold-500" />
      </div>
    );
  }

    if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function onSubmit(data: RegisterForm) {
    try {
      await authRegister({
        email: data.email,
        password: data.password,
        password_confirm: data.password_confirm,
        first_name: data.first_name,
        last_name: data.last_name,
      });
       navigate("/dashboard", { replace: true });
    } catch (error) {
      setError("root", { message: extractErrorMessage(error) });
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Decorative golden orbs */}
      <div
        className="orb orb-amber w-[500px] h-[500px] -top-40 -right-40 animate-float-slow"
        aria-hidden="true"
      />
      <div
        className="orb orb-gold w-[400px] h-[400px] -bottom-32 -left-32 animate-float-slow"
        style={{ animationDelay: "2s" }}
        aria-hidden="true"
      />

      <div className="w-full max-w-md relative z-10 animate-scale-in">
        {/* Header */}
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/50 animate-float-slow">
            <Brain className="h-10 w-10 text-white" />
          </div>
          <h1 className="mt-6 text-4xl font-bold text-cream-900 text-shadow-soft">
            Create your account
          </h1>
          <p className="mt-2 text-sm text-cream-600">
            Start your AI-powered career journey
          </p>
        </div>

        {/* Form Card */}
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="glass-card p-8 space-y-4 animate-slide-up"
          style={{ animationDelay: "0.1s" }}
        >
          <div
            className="grid grid-cols-2 gap-3 animate-slide-up"
            style={{ animationDelay: "0.15s" }}
          >
            <div>
              <label htmlFor="first_name" className="label">
                First name
              </label>
              <input
                id="first_name"
                className="input"
                placeholder="John"
                {...register("first_name")}
              />
            </div>
            <div>
              <label htmlFor="last_name" className="label">
                Last name
              </label>
              <input
                id="last_name"
                className="input"
                placeholder="Doe"
                {...register("last_name")}
              />
            </div>
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <label htmlFor="email" className="label">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="input"
              placeholder="you@example.com"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && (
              <p className="error-text">{errors.email.message}</p>
            )}
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.25s" }}>
            <label htmlFor="password" className="label">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="input"
              placeholder="••••••••"
              {...register("password", {
                required: "Password is required",
                minLength: { value: 8, message: "At least 8 characters" },
              })}
            />
            {errors.password && (
              <p className="error-text">{errors.password.message}</p>
            )}
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.3s" }}>
            <label htmlFor="password_confirm" className="label">
              Confirm password
            </label>
            <input
              id="password_confirm"
              type="password"
              className="input"
              placeholder="••••••••"
              {...register("password_confirm", {
                required: "Please confirm your password",
                validate: (value) =>
                  value === password || "Passwords do not match",
              })}
            />
            {errors.password_confirm && (
              <p className="error-text">{errors.password_confirm.message}</p>
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
            style={{ animationDelay: "0.35s" }}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating account…
              </>
            ) : (
              "Create account"
            )}
          </button>

          <p
            className="text-center text-sm text-cream-600 animate-slide-up"
            style={{ animationDelay: "0.4s" }}
          >
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-semibold text-gold-700 hover:underline transition-all duration-200 hover:text-gold-900"
            >
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}