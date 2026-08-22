import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SpinnerProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

const sizes = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-10 h-10" };

export function Spinner({ className, size = "md" }: SpinnerProps) {
  return (
    <Loader2 className={cn("animate-spin text-primary-600", sizes[size], className)} />
  );
}

export function FullPageSpinner() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-white/90 backdrop-blur-sm z-50">
      <div className="flex flex-col items-center gap-4">
        <Spinner size="lg" />
        <p className="text-zinc-500 text-sm animate-pulse">Loading…</p>
      </div>
    </div>
  );
}
