/**
 * Button component — B&W theme: Accent (indigo) filled OR black outlined.
 */
import { ButtonHTMLAttributes, forwardRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";

const buttonVariants = cva(
  // Base
  "inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white disabled:opacity-40 disabled:pointer-events-none select-none",
  {
    variants: {
      variant: {
        // Accent filled — indigo bg, white text (primary CTA)
        primary:
          "bg-primary-600 hover:bg-primary-700 text-white shadow-glow-sm hover:shadow-glow focus:ring-primary-500",
        // Black outlined — white bg, black text, black border
        secondary:
          "bg-white hover:bg-zinc-50 text-black border-2 border-black focus:ring-black",
        // Ghost — transparent, black text
        ghost:
          "bg-transparent hover:bg-zinc-100 text-black focus:ring-zinc-300",
        // Danger — red filled, white text
        danger:
          "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500",
        // Accent (emerald)
        accent:
          "bg-emerald-600 hover:bg-emerald-700 text-white focus:ring-emerald-500",
      },
      size: {
        sm:   "text-sm px-3 py-1.5",
        md:   "text-sm px-5 py-2.5",
        lg:   "text-base px-6 py-3",
        xl:   "text-lg px-8 py-4",
        icon: "p-2.5",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={buttonVariants({ variant, size, className })}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          leftIcon
        )}
        {children}
        {!isLoading && rightIcon}
      </button>
    );
  }
);

Button.displayName = "Button";
