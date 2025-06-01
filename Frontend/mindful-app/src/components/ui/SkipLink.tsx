'use client';

import React, { useState } from 'react';
import { cn } from '../../lib/utils';

interface SkipLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  /** The ID of the main content element to skip to */
  contentId: string;
  
  /** Optional custom text for the link */
  label?: string;
  
  /** Optional custom class name */
  className?: string;
}

/**
 * SkipLink component provides keyboard users a way to skip to the main content
 * It's visually hidden until focused, improving accessibility for keyboard and screen reader users
 */
export function SkipLink({
  contentId,
  label = 'Skip to main content',
  className,
  ...props
}: SkipLinkProps) {
  const [isFocused, setIsFocused] = useState(false);
  
  return (
    <a
      href={`#${contentId}`}
      className={cn(
        'absolute left-0 top-0 z-50 transform -translate-y-full p-3 bg-sage-700 text-white transition-transform focus:translate-y-0 rounded-br-md font-medium text-sm',
        isFocused && 'translate-y-0',
        className
      )}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      aria-label={label}
      {...props}
    >
      {label}
    </a>
  );
}

/**
 * ContentAnchor component to be placed at the start of the main content
 * for the SkipLink to target
 */
export function ContentAnchor({
  id,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div 
      id={id} 
      tabIndex={-1} 
      className="outline-none focus:outline-none" 
      {...props}
    />
  );
} 