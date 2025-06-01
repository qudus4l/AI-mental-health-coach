import * as React from "react";
import { VariantProps, cva } from "class-variance-authority";
import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sage-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        default: "bg-sage-500 text-white hover:bg-sage-600",
        outline: "border border-sage-200 bg-transparent hover:bg-sage-50 text-sage-700",
        ghost: "bg-transparent hover:bg-sage-50 text-sage-700",
        link: "underline-offset-4 hover:underline text-sage-700 bg-transparent",
        secondary: "bg-cream-200 text-sage-800 hover:bg-cream-300",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-8 px-3 rounded-md text-xs",
        lg: "h-12 px-8 rounded-md text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    // Determine if this button needs a high contrast focus ring for accessibility
    const needsHighContrastFocus = variant === 'ghost' || variant === 'outline';
    
    return (
      <button
        className={cn(
          buttonVariants({ variant, size, className }),
          needsHighContrastFocus && 'focus-visible:ring-offset-cream-100'
        )}
        ref={ref}
        type={props.type || "button"} // Ensure buttons have an explicit type
        // Add aria-disabled when disabled to improve screen reader announcement
        aria-disabled={props.disabled}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants }; 