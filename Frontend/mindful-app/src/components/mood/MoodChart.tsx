'use client';

import { useEffect, useRef } from 'react';

interface MoodEntry {
  date: string;
  mood: number;
  note?: string;
}

interface MoodChartProps {
  data: MoodEntry[];
}

export function MoodChart({ data }: MoodChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const tableRef = useRef<HTMLTableElement>(null);
  
  useEffect(() => {
    if (!canvasRef.current || !data.length) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Get device pixel ratio to handle high DPI displays
    const dpr = window.devicePixelRatio || 1;
    
    // Set canvas dimensions
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    
    // Scale the context to ensure correct drawing operations
    ctx.scale(dpr, dpr);
    
    // Set display size (CSS)
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    
    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height);
    
    // Chart settings
    const padding = { top: 40, right: 20, bottom: 40, left: 40 };
    const chartWidth = rect.width - padding.left - padding.right;
    const chartHeight = rect.height - padding.top - padding.bottom;
    
    // Sort data by date
    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    // Calculate x and y scales
    const xScale = chartWidth / (sortedData.length - 1 || 1);
    const yScale = chartHeight / 4; // Mood is 1-5
    
    // Draw grid lines
    ctx.beginPath();
    ctx.strokeStyle = '#F1EBE4'; // cream-100
    ctx.lineWidth = 1;
    
    // Horizontal grid lines
    for (let i = 1; i <= 5; i++) {
      const y = padding.top + chartHeight - (i - 1) * yScale;
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartWidth, y);
    }
    
    // Vertical grid lines
    for (let i = 0; i < sortedData.length; i++) {
      const x = padding.left + i * xScale;
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, padding.top + chartHeight);
    }
    
    ctx.stroke();
    
    // Draw x-axis labels (dates)
    ctx.font = '10px sans-serif';
    ctx.fillStyle = '#6B7770'; // sage-600
    ctx.textAlign = 'center';
    
    sortedData.forEach((entry, i) => {
      const x = padding.left + i * xScale;
      const date = new Date(entry.date);
      const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      ctx.fillText(formattedDate, x, padding.top + chartHeight + 20);
    });
    
    // Draw y-axis labels (mood levels)
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    const moodLabels = ['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'];
    moodLabels.forEach((label, i) => {
      const y = padding.top + chartHeight - i * yScale;
      ctx.fillText(label, padding.left - 10, y);
    });
    
    // Draw data points and connecting line
    if (sortedData.length > 0) {
      // Draw the line connecting points
      ctx.beginPath();
      ctx.strokeStyle = '#9CAB8F'; // sage-400
      ctx.lineWidth = 2;
      
      sortedData.forEach((entry, i) => {
        const x = padding.left + i * xScale;
        const y = padding.top + chartHeight - (entry.mood - 1) * yScale;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();
      
      // Draw data points
      sortedData.forEach((entry, i) => {
        const x = padding.left + i * xScale;
        const y = padding.top + chartHeight - (entry.mood - 1) * yScale;
        
        // Gradient fill for points
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 8);
        gradient.addColorStop(0, '#7C8D70'); // sage-500
        gradient.addColorStop(1, '#9CAB8F'); // sage-400
        
        ctx.beginPath();
        ctx.fillStyle = gradient;
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();
        
        // White border
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    }
    
    // Draw title
    ctx.font = 'bold 14px sans-serif';
    ctx.fillStyle = '#4A5548'; // sage-800
    ctx.textAlign = 'center';
    ctx.fillText('7-Day Mood Trend', rect.width / 2, 20);
    
  }, [data]);
  
  const getMoodTrend = (): string => {
    if (data.length < 2) return 'Not enough data';
    
    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    const firstMood = sortedData[0].mood;
    const lastMood = sortedData[sortedData.length - 1].mood;
    
    if (lastMood > firstMood) return 'Improving';
    if (lastMood < firstMood) return 'Declining';
    return 'Stable';
  };
  
  // Function to get human-readable mood label
  const getMoodLabel = (moodValue: number): string => {
    const moodLabels = ['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'];
    return moodLabels[moodValue - 1] || `Level ${moodValue}`;
  };
  
  // Sort data for consistent display
  const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  
  return (
    <div 
      className="relative w-full h-full"
      role="region"
      aria-label="Mood tracking chart"
    >
      {data.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <p className="text-sage-600">No mood data available</p>
        </div>
      ) : (
        <>
          {/* Canvas-based chart (visual representation) */}
          <canvas 
            ref={canvasRef} 
            className="w-full h-full"
            aria-hidden="true" // Hide from screen readers as we provide accessible table
          />
          
          {/* Screen reader accessible table with the same data */}
          <table 
            ref={tableRef} 
            className="sr-only"
            summary="Mood tracking data for the past 7 days, showing date and mood level"
          >
            <caption>7-Day Mood Trend</caption>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Mood</th>
                <th scope="col">Note</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((entry, index) => (
                <tr key={index}>
                  <td>
                    {new Date(entry.date).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </td>
                  <td>{getMoodLabel(entry.mood)}</td>
                  <td>{entry.note || 'No note'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {/* Trend indicator */}
          <div 
            className="absolute top-2 right-4 bg-cream-50 px-3 py-1 rounded-full text-xs font-medium text-sage-700"
            aria-label={`Mood trend: ${getMoodTrend()}`}
          >
            Trend: {getMoodTrend()}
          </div>
        </>
      )}
    </div>
  );
} 