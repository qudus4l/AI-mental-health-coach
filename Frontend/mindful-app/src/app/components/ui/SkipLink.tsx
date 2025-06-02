import React from 'react';
import { cn } from '../../lib/utils';

interface SkipLinkProps {
  contentId: string;
  className?: string;
}

export function SkipLink({ contentId, className }: SkipLinkProps) {
  return (
    <a
      href={`#${contentId}`}
      className={cn(
        'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50',
        'bg-sage-600 text-white px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sage-500',
        className
      )}
    >
      Skip to main content
    </a>
  );
}

interface ContentAnchorProps {
  id: string;
}

export function ContentAnchor({ id }: ContentAnchorProps) {
  return <div id={id} className="sr-only" tabIndex={-1} aria-hidden="true" />;
} 