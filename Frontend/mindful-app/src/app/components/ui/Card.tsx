import React from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'bordered';
}

export const Card = ({
  children,
  className,
  variant = 'default',
  ...props
}: CardProps) => {
  return (
    <div
      className={cn(
        'bg-cream-50/80 backdrop-blur-sm rounded-xl shadow-soft p-6',
        variant === 'bordered' && 'border border-cream-200',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardHeader = ({ children, className, ...props }: CardHeaderProps) => {
  return (
    <div className={cn('mb-4', className)} {...props}>
      {children}
    </div>
  );
};

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

export const CardTitle = ({ children, className, ...props }: CardTitleProps) => {
  return (
    <h3 className={cn('text-xl font-semibold text-sage-800', className)} {...props}>
      {children}
    </h3>
  );
};

interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export const CardDescription = ({
  children,
  className,
  ...props
}: CardDescriptionProps) => {
  return (
    <p className={cn('text-sm text-sage-600', className)} {...props}>
      {children}
    </p>
  );
};

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardContent = ({ children, className, ...props }: CardContentProps) => {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
};

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardFooter = ({ children, className, ...props }: CardFooterProps) => {
  return (
    <div className={cn('mt-4 pt-4 border-t border-cream-200', className)} {...props}>
      {children}
    </div>
  );
}; 