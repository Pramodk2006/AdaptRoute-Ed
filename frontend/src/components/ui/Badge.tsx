import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors border",
  {
    variants: {
      variant: {
        default:  "bg-primary-50 text-primary-700 border-primary-200",
        accent:   "bg-emerald-50 text-emerald-700 border-emerald-200",
        warning:  "bg-amber-50 text-amber-700 border-amber-200",
        danger:   "bg-red-50 text-red-700 border-red-200",
        neutral:  "bg-zinc-100 text-zinc-700 border-zinc-300",
        success:  "bg-emerald-50 text-emerald-700 border-emerald-200",
        // High-contrast B&W badges
        black:    "bg-black text-white border-black",
        outline:  "bg-white text-black border-black",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
