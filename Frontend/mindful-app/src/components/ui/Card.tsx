import * as React from "react";
import { cn } from "../../lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  // Add a role prop to allow overriding the default role
  role?: string;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, role = "region", ...props }, ref) => (
    <div
      ref={ref}
      role={role}
      className={cn(
        "rounded-lg border border-cream-200 bg-white shadow-sm transition-all",
        className
      )}
      {...props}
    />
  )
);
Card.displayName = "Card";

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  // Optional prop to provide an ID for linking header to content
  contentId?: string;
}

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, contentId, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col space-y-1.5 p-6", className)}
      // If contentId is provided, use aria-labelledby to associate header with content
      aria-labelledby={contentId}
      {...props}
    />
  )
);
CardHeader.displayName = "CardHeader";

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  // Allow control of heading level for proper document structure
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

const CardTitle = React.forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, as: Comp = 'h3', ...props }, ref) => {
    const HeadingComponent = Comp as any;
    return (
      <HeadingComponent
        ref={ref}
        className={cn(
          "text-lg font-semibold leading-none tracking-tight text-sage-800",
          className
        )}
        {...props}
      />
    );
  }
);
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-sage-600", className)}
    // Add a role to clarify that this is a descriptive element
    role="doc-subtitle"
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  // Optional prop to set the ID for ARIA associations
  id?: string;
}

const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, id, ...props }, ref) => (
    <div 
      ref={ref} 
      className={cn("p-6 pt-0", className)} 
      id={id}
      {...props} 
    />
  )
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    // Use contentinfo role to indicate this contains metadata about the card
    role="contentinfo"
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter }; 