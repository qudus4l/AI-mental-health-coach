import React from 'react';
import { render, screen } from '../../lib/test-utils';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter 
} from './Card';

describe('Card components', () => {
  describe('Card', () => {
    it('renders correctly with default props', () => {
      const { container } = render(<Card>Card content</Card>);
      const card = container.firstChild as HTMLElement;
      
      expect(card).toHaveAttribute('role', 'region');
      expect(card).toHaveClass('rounded-lg');
      expect(card).toHaveClass('border-cream-200');
    });
    
    it('accepts custom role', () => {
      render(<Card role="article">Card content</Card>);
      const card = screen.getByRole('article');
      
      expect(card).toHaveTextContent('Card content');
    });
    
    it('applies custom className', () => {
      const { container } = render(<Card className="custom-class">Card content</Card>);
      const card = container.firstChild as HTMLElement;
      
      expect(card).toHaveClass('custom-class');
      expect(card).toHaveClass('rounded-lg');
    });
  });
  
  describe('CardHeader', () => {
    it('renders correctly', () => {
      const { container } = render(<CardHeader>Header content</CardHeader>);
      const header = container.firstChild as HTMLElement;
      
      expect(header).toHaveClass('p-6');
      expect(header).toHaveClass('space-y-1.5');
    });
    
    it('uses aria-labelledby if contentId is provided', () => {
      const { container } = render(<CardHeader contentId="content-id">Header content</CardHeader>);
      const header = container.firstChild as HTMLElement;
      
      expect(header).toHaveAttribute('aria-labelledby', 'content-id');
    });
  });
  
  describe('CardTitle', () => {
    it('renders as h3 by default', () => {
      render(<CardTitle>Card title</CardTitle>);
      const title = screen.getByText('Card title');
      
      expect(title.tagName).toBe('H3');
      expect(title).toHaveClass('text-lg');
      expect(title).toHaveClass('font-semibold');
    });
    
    it('renders with custom heading level', () => {
      render(<CardTitle as="h2">Card title</CardTitle>);
      const title = screen.getByText('Card title');
      
      expect(title.tagName).toBe('H2');
    });
  });
  
  describe('CardDescription', () => {
    it('renders correctly', () => {
      render(<CardDescription>Description text</CardDescription>);
      const description = screen.getByText('Description text');
      
      expect(description.tagName).toBe('P');
      expect(description).toHaveClass('text-sm');
      expect(description).toHaveClass('text-sage-600');
      expect(description).toHaveAttribute('role', 'doc-subtitle');
    });
  });
  
  describe('CardContent', () => {
    it('renders correctly', () => {
      const { container } = render(<CardContent>Content text</CardContent>);
      const content = container.firstChild as HTMLElement;
      
      expect(content).toHaveClass('p-6');
      expect(content).toHaveClass('pt-0');
    });
    
    it('uses id if provided', () => {
      const { container } = render(<CardContent id="content-id">Content text</CardContent>);
      const content = container.firstChild as HTMLElement;
      
      expect(content).toHaveAttribute('id', 'content-id');
    });
  });
  
  describe('CardFooter', () => {
    it('renders correctly', () => {
      const { container } = render(<CardFooter>Footer content</CardFooter>);
      const footer = container.firstChild as HTMLElement;
      
      expect(footer).toHaveClass('flex');
      expect(footer).toHaveClass('items-center');
      expect(footer).toHaveClass('p-6');
      expect(footer).toHaveClass('pt-0');
      expect(footer).toHaveAttribute('role', 'contentinfo');
    });
  });
}); 