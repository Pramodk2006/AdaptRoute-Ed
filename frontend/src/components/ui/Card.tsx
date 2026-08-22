/**
 * Card component — clean white surface with crisp border.
 */
import { HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  glow?: boolean;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, hover, glow, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "bg-white border border-zinc-200 rounded-2xl shadow-card p-6",
        hover && "card-hover cursor-pointer",
        glow && "ring-2 ring-primary-500/30",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);
Card.displayName = "Card";

export function CardHeader({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("mb-4", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn("font-display text-xl font-bold text-black", className)} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-sm text-zinc-600 mt-1", className)} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("", className)} {...props}>
      {children}
    </div>
  );
}
