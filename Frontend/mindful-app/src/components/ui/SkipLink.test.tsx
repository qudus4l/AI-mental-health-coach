import React from 'react';
import { render, screen, fireEvent } from '../../lib/test-utils';
import { SkipLink, ContentAnchor } from './SkipLink';

describe('SkipLink', () => {
  it('renders correctly with default props', () => {
    render(<SkipLink contentId="main-content" />);
    
    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    
    expect(skipLink).toHaveAttribute('href', '#main-content');
    expect(skipLink).toHaveClass('-translate-y-full');
  });
  
  it('renders with custom label', () => {
    render(<SkipLink contentId="main-content" label="Skip to content" />);
    
    const skipLink = screen.getByRole('link', { name: /skip to content/i });
    
    expect(skipLink).toBeInTheDocument();
  });
  
  it('becomes visible on focus', () => {
    render(<SkipLink contentId="main-content" />);
    
    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    
    // Initially hidden
    expect(skipLink).toHaveClass('-translate-y-full');
    expect(skipLink).not.toHaveClass('translate-y-0');
    
    // Focus the link
    fireEvent.focus(skipLink);
    
    // Should be visible
    expect(skipLink).toHaveClass('translate-y-0');
    
    // Blur the link
    fireEvent.blur(skipLink);
    
    // Should be hidden again
    expect(skipLink).not.toHaveClass('translate-y-0');
  });
  
  it('applies custom className', () => {
    render(<SkipLink contentId="main-content" className="custom-class" />);
    
    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    
    expect(skipLink).toHaveClass('custom-class');
    expect(skipLink).toHaveClass('absolute');
  });
});

describe('ContentAnchor', () => {
  it('renders correctly', () => {
    const { container } = render(<ContentAnchor id="main-content" />);
    
    const anchor = container.querySelector('#main-content');
    
    expect(anchor).toHaveAttribute('id', 'main-content');
    expect(anchor).toHaveAttribute('tabIndex', '-1');
    expect(anchor).toHaveClass('outline-none');
  });
}); 