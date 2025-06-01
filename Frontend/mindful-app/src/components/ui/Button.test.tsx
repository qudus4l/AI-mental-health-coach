import React from 'react';
import { render, screen } from '../../lib/test-utils';
import { Button } from './Button';

describe('Button', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-sage-500');
    expect(button).toHaveClass('text-white');
  });
  
  it('renders with different variants', () => {
    const { rerender } = render(<Button variant="outline">Outline</Button>);
    let button = screen.getByRole('button', { name: /outline/i });
    
    expect(button).toHaveClass('border-sage-200');
    expect(button).toHaveClass('bg-transparent');
    
    rerender(<Button variant="ghost">Ghost</Button>);
    button = screen.getByRole('button', { name: /ghost/i });
    expect(button).toHaveClass('bg-transparent');
    
    rerender(<Button variant="link">Link</Button>);
    button = screen.getByRole('button', { name: /link/i });
    expect(button).toHaveClass('underline-offset-4');
    
    rerender(<Button variant="secondary">Secondary</Button>);
    button = screen.getByRole('button', { name: /secondary/i });
    expect(button).toHaveClass('bg-cream-200');
  });
  
  it('renders with different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    let button = screen.getByRole('button', { name: /small/i });
    
    expect(button).toHaveClass('h-8');
    expect(button).toHaveClass('px-3');
    
    rerender(<Button size="lg">Large</Button>);
    button = screen.getByRole('button', { name: /large/i });
    expect(button).toHaveClass('h-12');
    expect(button).toHaveClass('px-8');
    
    rerender(<Button size="icon">Icon</Button>);
    button = screen.getByRole('button', { name: /icon/i });
    expect(button).toHaveClass('h-10');
    expect(button).toHaveClass('w-10');
  });
  
  it('renders as disabled', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button', { name: /disabled/i });
    
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-disabled', 'true');
    expect(button).toHaveClass('disabled:opacity-50');
  });
  
  it('applies custom className', () => {
    render(<Button className="custom-class">Custom</Button>);
    const button = screen.getByRole('button', { name: /custom/i });
    
    expect(button).toHaveClass('custom-class');
    // Should still have the default classes
    expect(button).toHaveClass('bg-sage-500');
  });
  
  it('has default type of button', () => {
    render(<Button>Default Type</Button>);
    const button = screen.getByRole('button', { name: /default type/i });
    
    expect(button).toHaveAttribute('type', 'button');
  });
  
  it('allows type override', () => {
    render(<Button type="submit">Submit</Button>);
    const button = screen.getByRole('button', { name: /submit/i });
    
    expect(button).toHaveAttribute('type', 'submit');
  });
}); 