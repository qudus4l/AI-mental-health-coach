'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Cookies from 'js-cookie';
import { FiHome, FiMessageCircle, FiClipboard, FiUser, FiLogOut, FiMenu, FiX, FiActivity, FiHeart, FiCalendar } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

import { SkipLink, ContentAnchor } from '../components/ui/SkipLink';
import { logout } from '../../lib/api/auth';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobileView, setIsMobileView] = useState(false);
  
  // Initialize mobile view state after component mounts
  useEffect(() => {
    setIsMobileView(window.innerWidth < 768);
    
    const handleResize = () => {
      setIsMobileView(window.innerWidth < 768);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);
  
  // Close mobile menu when Escape key is pressed
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isMobileMenuOpen]);
  
  const handleLogout = () => {
    // First clear all auth state directly
    Cookies.remove('mindful-auth-token', { path: '/' });
    localStorage.removeItem('mindful-auth-token');
    localStorage.removeItem('mindful-auth');
    sessionStorage.clear();
    
    // Then call the logout function (as a fallback)
    logout();
    
    // Redirect with a full page reload
    window.location.href = '/login';
  };
  
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: FiHome },
    { name: 'Conversations', href: '/dashboard/conversations', icon: FiMessageCircle },
    { name: 'Mood Tracking', href: '/dashboard/mood', icon: FiActivity },
    { name: 'Exercises', href: '/dashboard/exercises', icon: FiHeart },
    { name: 'Homework', href: '/dashboard/homework', icon: FiClipboard },
    { name: 'Schedule', href: '/dashboard/schedule', icon: FiCalendar },
    { name: 'Profile', href: '/dashboard/profile', icon: FiUser },
  ];
  
  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Skip link for keyboard users */}
      <SkipLink contentId="main-content" />
      
      {/* Mobile header */}
      <header 
        className="md:hidden py-4 px-4 border-b border-cream-200 flex justify-between items-center bg-cream-50/90 backdrop-blur-sm z-10"
        aria-label="Mobile header"
      >
        <div className="flex items-center">
          <div 
            className="w-8 h-8 bg-sage-500 rounded-full flex items-center justify-center"
            aria-hidden="true"
          >
            <span className="text-white font-semibold text-sm">A</span>
          </div>
          <h1 className="ml-2 text-lg font-semibold text-sage-800">Ami</h1>
        </div>
        
        <button 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-lg text-sage-700 hover:bg-cream-100"
          aria-expanded={isMobileMenuOpen}
          aria-controls="mobile-menu"
          aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
        >
          {isMobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
      </header>
      
      {/* Mobile menu overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-20 md:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
          />
        )}
      </AnimatePresence>
      
      {/* Sidebar */}
      <motion.aside
        className={`fixed md:relative inset-y-0 left-0 z-30 w-64 bg-cream-50/90 backdrop-blur-sm shadow-soft md:shadow-none 
                    transition-transform duration-300 transform ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'} 
                    overflow-y-auto border-r border-cream-200 p-4 flex flex-col`}
        id="mobile-menu"
        aria-label="Main navigation"
        aria-hidden={!isMobileMenuOpen && isMobileView}
      >
        {/* Logo */}
        <div className="flex items-center mb-8 mt-2">
          <div 
            className="w-10 h-10 bg-sage-500 rounded-full flex items-center justify-center"
            aria-hidden="true"
          >
            <span className="text-white font-semibold text-lg">A</span>
          </div>
          <h1 className="ml-3 text-xl font-semibold text-sage-800">Ami</h1>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 space-y-1" aria-label="Dashboard navigation">
          <ul role="list">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-sage-50 text-sage-700' 
                        : 'text-sage-600 hover:text-sage-800 hover:bg-cream-100'
                    }`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <item.icon 
                      className={`mr-3 ${isActive ? 'text-sage-500' : 'text-sage-400'}`}
                      aria-hidden="true" 
                    />
                    <span className="font-medium">{item.name}</span>
                    
                    {isActive && (
                      <motion.div
                        className="w-1 h-6 bg-sage-500 absolute right-0 rounded-l-full"
                        layoutId="activeNav"
                        aria-hidden="true"
                      />
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        
        {/* Logout button */}
        <div className="mt-auto pt-4 border-t border-cream-200">
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-4 py-3 rounded-lg text-sage-600 hover:text-sage-800 hover:bg-cream-100 transition-colors"
            aria-label="Logout from the application"
          >
            <FiLogOut className="mr-3 text-sage-400" aria-hidden="true" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </motion.aside>
      
      {/* Main content */}
      <main 
        className="flex-1 md:ml-64 p-4 md:p-8"
        id="main-content"
        tabIndex={-1}
      >
        <ContentAnchor id="main-content" />
        {children}
      </main>
    </div>
  );
} 