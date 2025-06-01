import React from 'react';
import { render, screen, act } from '../../lib/test-utils';
import { BreathingAnimation } from './BreathingAnimation';

// Explicitly use fake timers for this test
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

describe('BreathingAnimation', () => {
  const defaultPattern = {
    inhale: 4,
    hold: 2,
    exhale: 4,
    pause: 2
  };
  
  it('renders correctly when not playing', () => {
    render(<BreathingAnimation isPlaying={false} pattern={defaultPattern} />);
    
    // Should show "Press play to start" message
    expect(screen.getByText(/press play to start/i)).toBeInTheDocument();
    
    // Should show pattern info
    expect(screen.getByText(/4-2-4-2 pattern/i)).toBeInTheDocument();
  });
  
  it('shows inhale phase initially when playing', () => {
    render(<BreathingAnimation isPlaying={true} pattern={defaultPattern} />);
    
    // Should show "Inhale" text and the countdown
    expect(screen.getByText('Inhale')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    
    // Should not show "Press play to start" message anymore
    expect(screen.queryByText(/press play to start/i)).not.toBeInTheDocument();
  });
  
  it('counts down during inhale phase', () => {
    render(<BreathingAnimation isPlaying={true} pattern={defaultPattern} />);
    
    // Initially at 4
    expect(screen.getByText('4')).toBeInTheDocument();
    
    // Advance 1 second - should be at 3
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    expect(screen.getByText('3')).toBeInTheDocument();
  });
  
  it('updates when pattern changes', () => {
    const { rerender } = render(<BreathingAnimation isPlaying={false} pattern={defaultPattern} />);
    
    // Initial pattern display
    expect(screen.getByText(/4-2-4-2 pattern/i)).toBeInTheDocument();
    
    // Change the pattern
    const newPattern = {
      inhale: 5,
      hold: 0,
      exhale: 5,
      pause: 0
    };
    
    rerender(<BreathingAnimation isPlaying={false} pattern={newPattern} />);
    
    // Should display new pattern
    expect(screen.getByText(/5-0-5 pattern/i)).toBeInTheDocument();
  });
  
  it('stops and resets when isPlaying is toggled', () => {
    const { rerender } = render(<BreathingAnimation isPlaying={true} pattern={defaultPattern} />);
    
    // Initially in Inhale phase
    expect(screen.getByText('Inhale')).toBeInTheDocument();
    
    // Set isPlaying to false
    rerender(<BreathingAnimation isPlaying={false} pattern={defaultPattern} />);
    
    // Should reset to initial state with "Press play to start" message
    expect(screen.getByText(/press play to start/i)).toBeInTheDocument();
  });
  
  it('has appropriate ARIA attributes for accessibility', () => {
    render(<BreathingAnimation isPlaying={true} pattern={defaultPattern} />);
    
    // Main region should have appropriate roles and labels
    const regionElement = screen.getByRole('region');
    expect(regionElement).toHaveAttribute('aria-label', 'Breathing exercise animation');
    expect(regionElement).toHaveAttribute('aria-live', 'polite');
    
    // Should have a visually hidden element for screen readers
    const srElement = screen.getByText('Inhale 4');
    expect(srElement).toHaveClass('sr-only');
    expect(srElement).toHaveAttribute('aria-live', 'assertive');
  });
}); 