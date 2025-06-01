'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiPlay, FiClock, FiAward, FiFilter, FiCalendar } from 'react-icons/fi';
import Link from 'next/link';

import { Card, CardHeader, CardTitle, CardContent } from '../../../../components/ui/Card';
import { Button } from '../../../../components/ui/Button';

// Demo exercise data
const demoExercises = [
  {
    id: '1',
    title: 'Mindful Breathing',
    description: 'A simple breathing exercise to calm your mind and reduce anxiety.',
    duration: 5,
    category: 'breathing',
    level: 'beginner',
    imageUrl: '/images/breathing.jpg',
    completions: 42,
  },
  {
    id: '2',
    title: 'Body Scan Meditation',
    description: 'A progressive relaxation technique to release tension in your body.',
    duration: 10,
    category: 'meditation',
    level: 'intermediate',
    imageUrl: '/images/body-scan.jpg',
    completions: 28,
  },
  {
    id: '3',
    title: 'Loving-Kindness Practice',
    description: 'Cultivate compassion for yourself and others through guided visualization.',
    duration: 15,
    category: 'meditation',
    level: 'intermediate',
    imageUrl: '/images/loving-kindness.jpg',
    completions: 15,
  },
  {
    id: '4',
    title: '4-7-8 Breathing Technique',
    description: 'A breathing pattern that promotes relaxation and helps with falling asleep.',
    duration: 3,
    category: 'breathing',
    level: 'beginner',
    imageUrl: '/images/4-7-8.jpg',
    completions: 35,
  },
  {
    id: '5',
    title: 'Mindful Walking',
    description: 'Practice mindfulness while walking to ground yourself in the present moment.',
    duration: 10,
    category: 'movement',
    level: 'beginner',
    imageUrl: '/images/walking.jpg',
    completions: 18,
  },
  {
    id: '6',
    title: 'Anxiety Relief Visualization',
    description: 'A guided visualization to help reduce anxiety and promote calmness.',
    duration: 12,
    category: 'visualization',
    level: 'intermediate',
    imageUrl: '/images/visualization.jpg',
    completions: 23,
  },
];

// Categories with icons
const categories = [
  { id: 'all', name: 'All Exercises', active: true },
  { id: 'breathing', name: 'Breathing', active: false },
  { id: 'meditation', name: 'Meditation', active: false },
  { id: 'visualization', name: 'Visualization', active: false },
  { id: 'movement', name: 'Movement', active: false },
];

export default function ExercisesPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [exercises, setExercises] = useState(demoExercises);
  const [activeCategory, setActiveCategory] = useState('all');
  const [featuredExercise, setFeaturedExercise] = useState(demoExercises[0]);
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Filter exercises by category
  const filterExercises = (categoryId: string) => {
    setActiveCategory(categoryId);
    if (categoryId === 'all') {
      setExercises(demoExercises);
    } else {
      setExercises(demoExercises.filter(exercise => exercise.category === categoryId));
    }
  };
  
  // Get stats
  const completedExercises = demoExercises.reduce((sum, ex) => sum + ex.completions, 0);
  const totalMinutes = demoExercises.reduce((sum, ex) => sum + (ex.duration * ex.completions), 0);
  const streakDays = 7; // Demo streak
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Mindfulness Exercises</h1>
        <p className="text-sage-600 mt-2">Practice mindfulness to reduce stress and improve well-being</p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Completed Exercises */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiAward className="mr-2 text-sage-500" />
              Exercises Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{completedExercises}</div>
                <p className="text-sage-600 text-sm mt-1">practice sessions</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-sage-500 h-full rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Minutes Practiced */}
        <Card className="floating-delayed">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiClock className="mr-2 text-sage-500" />
              Total Practice Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{totalMinutes}</div>
                <p className="text-sage-600 text-sm mt-1">minutes of mindfulness</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-sage-500 h-full rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Current Streak */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiCalendar className="mr-2 text-sage-500" />
              Current Streak
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{streakDays}</div>
                <p className="text-sage-600 text-sm mt-1">days in a row</p>
                <div className="mt-4 flex space-x-1">
                  {Array(7).fill(0).map((_, i) => (
                    <div 
                      key={i} 
                      className={`h-6 w-6 rounded-full flex items-center justify-center text-xs
                        ${i < streakDays ? 'bg-sage-500 text-white' : 'bg-cream-200 text-sage-500'}`}
                    >
                      {i + 1}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Featured Exercise */}
      <Card className="w-full mb-8 overflow-hidden floating-delayed">
        <div className="flex flex-col md:flex-row">
          <div className="md:w-2/3 p-6">
            <h2 className="text-xl font-semibold text-sage-800">Featured Exercise</h2>
            
            {isLoading ? (
              <div className="space-y-4 mt-4">
                <div className="h-8 bg-cream-100 animate-pulse rounded-lg w-2/3"></div>
                <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
                <div className="h-10 bg-cream-100 animate-pulse rounded-lg w-1/3"></div>
              </div>
            ) : (
              <>
                <h3 className="text-2xl font-bold text-sage-700 mt-4">{featuredExercise.title}</h3>
                <p className="text-sage-600 mt-2">{featuredExercise.description}</p>
                
                <div className="flex items-center mt-4 space-x-3">
                  <span className="text-sm font-medium bg-sage-100 text-sage-700 px-3 py-1 rounded-full">
                    {featuredExercise.duration} minutes
                  </span>
                  <span className="text-sm font-medium bg-cream-100 text-sage-700 px-3 py-1 rounded-full capitalize">
                    {featuredExercise.level}
                  </span>
                </div>
                
                <div className="mt-6">
                  <Link href={`/dashboard/exercises/${featuredExercise.id}`}>
                    <Button className="flex items-center gap-2">
                      <FiPlay /> Start Exercise
                    </Button>
                  </Link>
                </div>
              </>
            )}
          </div>
          
          <div className="md:w-1/3 bg-sage-100 flex items-center justify-center">
            {isLoading ? (
              <div className="w-full h-full bg-cream-100 animate-pulse"></div>
            ) : (
              <div className="w-full h-full min-h-[200px] bg-sage-200 flex items-center justify-center">
                <FiPlay className="text-4xl text-sage-500" />
              </div>
            )}
          </div>
        </div>
      </Card>
      
      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex items-center mb-2">
          <FiFilter className="mr-2 text-sage-500" />
          <h2 className="text-lg font-semibold text-sage-800">Filter Exercises</h2>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => filterExercises(category.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors
                ${activeCategory === category.id 
                  ? 'bg-sage-500 text-white' 
                  : 'bg-cream-100 text-sage-700 hover:bg-cream-200'}`}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>
      
      {/* Exercise Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array(6).fill(0).map((_, i) => (
            <Card key={i} className="h-64 animate-pulse bg-cream-100"></Card>
          ))
        ) : (
          exercises.map((exercise) => (
            <Card key={exercise.id} className="overflow-hidden floating">
              <div className="h-32 bg-sage-100 flex items-center justify-center">
                <FiPlay className="text-3xl text-sage-500" />
              </div>
              
              <CardContent className="p-4">
                <h3 className="font-semibold text-sage-800">{exercise.title}</h3>
                <p className="text-sage-600 text-sm mt-1 line-clamp-2">{exercise.description}</p>
                
                <div className="flex items-center justify-between mt-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-medium bg-sage-100 text-sage-700 px-2 py-1 rounded-full">
                      {exercise.duration} min
                    </span>
                    <span className="text-xs font-medium bg-cream-100 text-sage-700 px-2 py-1 rounded-full capitalize">
                      {exercise.level}
                    </span>
                  </div>
                  
                  <Link href={`/dashboard/exercises/${exercise.id}`}>
                    <Button size="sm" variant="ghost" className="text-sage-700">
                      <FiPlay className="mr-1" /> Start
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </motion.div>
  );
} 