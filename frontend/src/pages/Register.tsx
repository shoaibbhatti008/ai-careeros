import { useForm } from "react-hook-form";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Brain } from "lucide-react";

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
    return <div className="flex h-screen items-center justify-center">Loading…</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
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
      navigate("/", { replace: true });
    } catch (error) {
      setError("root", { message: extractErrorMessage(error) });
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-8">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center">
          <Brain className="h-12 w-12 text-primary-600" />
          <h1 className="mt-4 text-2xl font-bold">Create your account</h1>
          <p className="mt-1 text-sm text-slate-500">
            Start your AI-powered career journey
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="first_name" className="label">
                First name
              </label>
              <input id="first_name" className="input" {...register("first_name")} />
            </div>
            <div>
              <label htmlFor="last_name" className="label">
                Last name
              </label>
              <input id="last_name" className="input" {...register("last_name")} />
            </div>
          </div>

          <div>
            <label htmlFor="email" className="label">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="input"
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
              className="input"
              {...register("password", {
                required: "Password is required",
                minLength: { value: 8, message: "At least 8 characters" },
              })}
            />
            {errors.password && (
              <p className="error-text">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password_confirm" className="label">
              Confirm password
            </label>
            <input
              id="password_confirm"
              type="password"
              className="input"
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
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {errors.root.message}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full"
          >
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>

          <p className="text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link to="/login" className="text-primary-600 hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}