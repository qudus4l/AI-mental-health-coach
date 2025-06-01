'use client';

import Image from 'next/image';
import { motion } from 'framer-motion';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex">
      {/* Left side: Auth form */}
      <div className="w-full md:w-1/2 flex items-center justify-center">
        {children}
      </div>
      
      {/* Right side: Decorative panel (hidden on mobile) */}
      <div className="hidden md:block md:w-1/2 bg-cream-50 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cream-100/80 to-sage-200/80"></div>
        
        <motion.div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] opacity-10"
          animate={{ 
            rotate: 360,
          }}
          transition={{ 
            duration: 150, 
            ease: "linear", 
            repeat: Infinity 
          }}
        >
          <div className="absolute inset-0 rounded-full border-[40px] border-sage-300/20"></div>
          <div className="absolute inset-[10%] rounded-full border-[30px] border-cream-300/20"></div>
          <div className="absolute inset-[20%] rounded-full border-[20px] border-mist-300/20"></div>
          <div className="absolute inset-[30%] rounded-full border-[10px] border-sage-300/20"></div>
        </motion.div>
        
        <div className="absolute top-8 left-8 flex items-center">
          <div className="w-10 h-10 bg-sage-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-lg">A</span>
          </div>
          <h1 className="ml-3 text-xl font-semibold text-sage-800">Ami</h1>
        </div>
        
        <div className="absolute bottom-8 left-8 right-8">
          <div className="bg-cream-50/40 backdrop-blur-sm p-6 rounded-xl border border-cream-100/20 shadow-soft">
            <p className="text-sage-700 font-medium leading-relaxed">
              "In the space between your thoughts lies the essence of mindfulness. 
              Take a moment to breathe and discover the peace that was always there."
            </p>
            <p className="mt-4 text-sage-600 font-medium">— Ami AI Coach</p>
          </div>
        </div>
      </div>
    </div>
  );
} 