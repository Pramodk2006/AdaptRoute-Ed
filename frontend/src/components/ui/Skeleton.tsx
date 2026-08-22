/**
 * Skeleton Loader component — clean pulse animation replacing generic spinners.
 */
import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn("animate-pulse rounded-xl bg-zinc-200", className)}
      {...props}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white border border-zinc-200 rounded-2xl p-6 space-y-4 shadow-card">
      <div className="flex items-center gap-3">
        <Skeleton className="w-10 h-10 rounded-xl" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <Skeleton className="h-16 w-full" />
    </div>
  );
}

export function SkeletonRoadmap() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white border border-zinc-200 rounded-2xl p-5 flex items-center justify-between shadow-card">
          <div className="flex items-center gap-4 flex-1">
            <Skeleton className="w-10 h-10 rounded-xl" />
            <div className="space-y-2 flex-1 max-w-sm">
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-3 w-1/3" />
            </div>
          </div>
          <Skeleton className="w-24 h-2 rounded-full" />
        </div>
      ))}
    </div>
  );
}
