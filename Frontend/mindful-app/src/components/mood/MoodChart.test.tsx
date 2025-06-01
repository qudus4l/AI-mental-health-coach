import React from 'react';
import { render, screen } from '../../lib/test-utils';
import { MoodChart } from './MoodChart';

// Mock the Canvas context to avoid errors
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock getBoundingClientRect to return predictable values
Element.prototype.getBoundingClientRect = jest.fn(() => {
  return {
    width: 500,
    height: 300,
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    x: 0,
    y: 0,
    toJSON: () => {}
  };
});

// Properly mock canvas and context
const originalGetContext = HTMLCanvasElement.prototype.getContext;
beforeAll(() => {
  // @ts-ignore - we're intentionally mocking this
  HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
    clearRect: jest.fn(),
    beginPath: jest.fn(),
    moveTo: jest.fn(),
    lineTo: jest.fn(),
    arc: jest.fn(),
    fill: jest.fn(),
    stroke: jest.fn(),
    fillText: jest.fn(),
    scale: jest.fn(),
    createRadialGradient: jest.fn(() => ({
      addColorStop: jest.fn()
    }))
  }));
});

afterAll(() => {
  HTMLCanvasElement.prototype.getContext = originalGetContext;
});

window.ResizeObserver = ResizeObserver;

describe('MoodChart', () => {
  const sampleData = [
    { date: '2023-07-01', mood: 3, note: 'Feeling neutral today' },
    { date: '2023-07-02', mood: 4, note: 'Better day' },
    { date: '2023-07-03', mood: 5, note: 'Great day!' },
    { date: '2023-07-04', mood: 4, note: 'Good day' },
    { date: '2023-07-05', mood: 3, note: 'Alright' },
  ];

  it('renders correctly with data', () => {
    render(<MoodChart data={sampleData} />);
    
    // Check that the canvas is rendered
    const canvas = document.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
    
    // Check that the trend indicator is shown
    expect(screen.getByText(/trend:/i)).toBeInTheDocument();
    
    // Check that the accessible table is present (for screen readers)
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    expect(table).toHaveClass('sr-only');
    
    // Check the table caption
    expect(screen.getByText('7-Day Mood Trend')).toBeInTheDocument();
  });
  
  it('displays a message when no data is available', () => {
    render(<MoodChart data={[]} />);
    
    expect(screen.getByText('No mood data available')).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });
  
  it('calculates mood trend correctly', () => {
    // Improving trend
    const { rerender } = render(<MoodChart data={[
      { date: '2023-07-01', mood: 2 },
      { date: '2023-07-02', mood: 4 }
    ]} />);
    
    expect(screen.getByText('Trend: Improving')).toBeInTheDocument();
    
    // Rerender with declining trend
    rerender(<MoodChart data={[
      { date: '2023-07-01', mood: 4 },
      { date: '2023-07-02', mood: 2 }
    ]} />);
    
    expect(screen.getByText('Trend: Declining')).toBeInTheDocument();
    
    // Rerender with stable trend
    rerender(<MoodChart data={[
      { date: '2023-07-01', mood: 3 },
      { date: '2023-07-02', mood: 3 }
    ]} />);
    
    expect(screen.getByText('Trend: Stable')).toBeInTheDocument();
    
    // Rerender with not enough data
    rerender(<MoodChart data={[
      { date: '2023-07-01', mood: 3 }
    ]} />);
    
    expect(screen.getByText('Trend: Not enough data')).toBeInTheDocument();
  });
  
  it('has appropriate accessibility attributes', () => {
    render(<MoodChart data={sampleData} />);
    
    // Main region should have appropriate role and label
    const regionElement = screen.getByRole('region');
    expect(regionElement).toHaveAttribute('aria-label', 'Mood tracking chart');
    
    // Table should have appropriate summary
    const table = screen.getByRole('table');
    expect(table).toHaveAttribute('summary', 'Mood tracking data for the past 7 days, showing date and mood level');
    
    // Trend indicator should have aria-label
    const trendIndicator = screen.getByText(/trend:/i).closest('div');
    expect(trendIndicator).toHaveAttribute('aria-label', expect.stringMatching(/mood trend/i));
  });
}); 