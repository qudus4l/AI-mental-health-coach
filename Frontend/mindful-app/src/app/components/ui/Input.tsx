import React, { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="space-y-1.5">
        {label && (
          <label 
            htmlFor={props.id} 
            className="block text-sm font-medium text-sage-700"
          >
            {label}
          </label>
        )}
        <input
          className={cn(
            "w-full px-4 py-2 rounded-lg border bg-cream-50/50 placeholder:text-sage-400",
            "focus:outline-none focus:ring-2 focus:border-transparent transition-all",
            error 
              ? "border-red-300 focus:ring-red-200" 
              : "border-cream-300 focus:ring-sage-200",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input }; 