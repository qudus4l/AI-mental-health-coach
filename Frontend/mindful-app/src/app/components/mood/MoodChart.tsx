'use client';

import { useEffect, useRef } from 'react';

interface MoodEntry {
  date: string;
  mood: number;
  note: string;
}

interface MoodChartProps {
  data: MoodEntry[];
}

export function MoodChart({ data }: MoodChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    if (!canvasRef.current || data.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Set canvas size to match parent
    const parent = canvas.parentElement;
    if (parent) {
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    }
    
    // Sort data by date
    const sortedData = [...data].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
    
    // Define colors based on our theme
    const gradientColors = [
      { stop: 0, color: 'rgba(212, 192, 158, 0.2)' }, // Cream color for low mood
      { stop: 0.3, color: 'rgba(183, 198, 174, 0.4)' }, // Mix
      { stop: 0.7, color: 'rgba(128, 143, 118, 0.6)' }, // Sage color for medium mood
      { stop: 1, color: 'rgba(106, 119, 97, 0.8)' }  // Darker sage for high mood
    ];
    
    // Constants
    const padding = 30;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;
    const maxMood = 5; // Assuming mood scale is 1-5
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw axes
    ctx.strokeStyle = 'rgba(106, 119, 97, 0.2)';
    ctx.lineWidth = 1;
    
    // Y-axis
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, padding + chartHeight);
    ctx.stroke();
    
    // X-axis
    ctx.beginPath();
    ctx.moveTo(padding, padding + chartHeight);
    ctx.lineTo(padding + chartWidth, padding + chartHeight);
    ctx.stroke();
    
    // Draw y-axis labels
    ctx.fillStyle = 'rgba(68, 76, 64, 0.7)'; // sage-800
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'right';
    
    for (let i = 0; i <= maxMood; i++) {
      const y = padding + chartHeight - (i / maxMood) * chartHeight;
      ctx.fillText(i.toString(), padding - 10, y + 4);
      
      // Draw light grid lines
      ctx.strokeStyle = 'rgba(106, 119, 97, 0.1)';
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + chartWidth, y);
      ctx.stroke();
    }
    
    // Draw data points and lines
    if (sortedData.length > 0) {
      const xStep = chartWidth / (sortedData.length - 1 || 1);
      
      // Draw the line connecting points
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(128, 143, 118, 0.8)';
      ctx.lineWidth = 2;
      
      // Create gradient fill
      const gradient = ctx.createLinearGradient(0, padding, 0, padding + chartHeight);
      gradientColors.forEach(({ stop, color }) => {
        gradient.addColorStop(stop, color);
      });
      
      // Start point
      const firstX = padding;
      const firstY = padding + chartHeight - ((sortedData[0].mood / maxMood) * chartHeight);
      ctx.moveTo(firstX, firstY);
      
      // Draw line and collect points for fill
      const points = [{ x: firstX, y: firstY }];
      
      sortedData.forEach((entry, index) => {
        if (index === 0) return; // Skip first point as we've already moved to it
        
        const x = padding + index * xStep;
        const y = padding + chartHeight - ((entry.mood / maxMood) * chartHeight);
        
        // Add some subtle curve to the line
        if (index > 0) {
          const prevX = padding + (index - 1) * xStep;
          const prevY = padding + chartHeight - ((sortedData[index - 1].mood / maxMood) * chartHeight);
          
          // Control points for curve
          const cpX1 = prevX + xStep / 3;
          const cpY1 = prevY;
          const cpX2 = x - xStep / 3;
          const cpY2 = y;
          
          ctx.bezierCurveTo(cpX1, cpY1, cpX2, cpY2, x, y);
        }
        
        points.push({ x, y });
      });
      
      ctx.stroke();
      
      // Fill area under the curve
      ctx.beginPath();
      ctx.moveTo(points[0].x, padding + chartHeight); // Bottom left
      
      // Add points from the line
      points.forEach(point => {
        ctx.lineTo(point.x, point.y);
      });
      
      ctx.lineTo(points[points.length - 1].x, padding + chartHeight); // Bottom right
      ctx.closePath();
      
      ctx.fillStyle = gradient;
      ctx.fill();
      
      // Draw points
      sortedData.forEach((entry, index) => {
        const x = padding + index * xStep;
        const y = padding + chartHeight - ((entry.mood / maxMood) * chartHeight);
        
        // Outer circle
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.strokeStyle = 'rgba(128, 143, 118, 0.8)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Inner circle
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(128, 143, 118, 0.8)';
        ctx.fill();
        
        // Draw date labels for first, last, and middle points
        if (index === 0 || index === sortedData.length - 1 || index === Math.floor(sortedData.length / 2)) {
          const date = new Date(entry.date);
          const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          
          ctx.fillStyle = 'rgba(68, 76, 64, 0.7)';
          ctx.font = '11px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(formattedDate, x, padding + chartHeight + 20);
        }
      });
    }
    
  }, [data]);
  
  return (
    <div className="w-full h-full flex items-center justify-center">
      {data.length === 0 ? (
        <p className="text-sage-500">No mood data available yet</p>
      ) : (
        <canvas 
          ref={canvasRef} 
          className="w-full h-full"
          style={{ maxHeight: '100%' }}
        />
      )}
    </div>
  );
} 