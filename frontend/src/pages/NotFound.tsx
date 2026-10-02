import { Link } from "react-router-dom";
import { Home, Search } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 relative overflow-hidden">
      {/* Decorative orbs */}
      <div
        className="orb orb-gold w-96 h-96 -top-32 -left-32 animate-float-slow"
        aria-hidden="true"
      />
      <div
        className="orb orb-amber w-80 h-80 -bottom-32 -right-32 animate-float-slow"
        style={{ animationDelay: "2s" }}
        aria-hidden="true"
      />

      <div className="relative z-10 text-center animate-scale-in">
        <div className="flex items-center justify-center gap-6 mb-8">
          <span className="text-[120px] font-black gradient-text leading-none">
            4
          </span>
          <div className="flex h-28 w-28 items-center justify-center rounded-3xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/50 animate-float-slow">
            <Search className="h-14 w-14 text-white" />
          </div>
          <span className="text-[120px] font-black gradient-text leading-none">
            4
          </span>
        </div>

        <h1 className="text-3xl font-bold text-cream-900 text-shadow-soft">
          Page not found
        </h1>
        <p className="mt-3 text-sm text-cream-600 max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>

        <Link to="/" className="btn-primary mt-8 inline-flex">
          <Home className="h-4 w-4" />
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}