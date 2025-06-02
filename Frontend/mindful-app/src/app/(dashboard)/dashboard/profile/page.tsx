'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { AxiosError } from 'axios';

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../../components/ui/Card';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { getUserProfile, createUserProfile, updateUserProfile, UserProfile, UserProfileUpdate } from '../../../../lib/api/users';

// Form validation schema
const profileSchema = z.object({
  age: z.preprocess(
    (val) => val === '' ? null : Number(val),
    z.number().min(18, 'You must be at least 18 years old').max(120, 'Please enter a valid age').nullable()
  ),
  location: z.string().nullable().optional(),
  anxiety_score: z.preprocess(
    (val) => val === '' ? null : Number(val),
    z.number().min(0, 'Score must be at least 0').max(10, 'Score cannot exceed 10').nullable()
  ),
  depression_score: z.preprocess(
    (val) => val === '' ? null : Number(val),
    z.number().min(0, 'Score must be at least 0').max(10, 'Score cannot exceed 10').nullable()
  ),
  communication_preference: z.enum(['text', 'voice', 'both']),
  session_frequency: z.preprocess(
    (val) => Number(val),
    z.number().min(1, 'At least 1 session per week').max(7, 'Maximum 7 sessions per week')
  ),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

export default function ProfilePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      age: null,
      location: '',
      anxiety_score: null,
      depression_score: null,
      communication_preference: 'text',
      session_frequency: 2,
    },
  });
  
  // Load user profile data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true);
        const profileData = await getUserProfile();
        
        if (profileData) {
          setProfile(profileData);
          reset({
            age: profileData.age,
            location: profileData.location || '',
            anxiety_score: profileData.anxiety_score,
            depression_score: profileData.depression_score,
            communication_preference: profileData.communication_preference as 'text' | 'voice' | 'both',
            session_frequency: profileData.session_frequency,
          });
        } else {
          setIsCreating(true);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError('Failed to load profile. Please try again.');
      } finally {
      setIsLoading(false);
      }
    };
    
    fetchProfile();
  }, [reset]);
  
  const onSubmit = async (data: ProfileFormValues) => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (isCreating) {
        // Create new profile
        const newProfile = await createUserProfile(data);
        setProfile(newProfile);
        setIsCreating(false);
        setSuccessMessage('Profile created successfully!');
      } else {
        // Update existing profile
        const updatedProfile = await updateUserProfile(data);
        setProfile(updatedProfile);
        setSuccessMessage('Profile updated successfully!');
      }
    } catch (err) {
      console.error('Error saving profile:', err);
      
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || 'Failed to save profile. Please try again.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsSaving(false);
    }
  };
  
  return (
    <div className="container max-w-3xl mx-auto py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-2xl md:text-3xl font-bold text-sage-800 mb-2">Your Profile</h1>
        <p className="text-sage-600 mb-8">Manage your personal information and preferences</p>
        
        <Card>
          <CardHeader>
            <CardTitle>{isCreating ? 'Complete Your Profile' : 'Edit Profile'}</CardTitle>
            <CardDescription>
              {isCreating 
                ? 'Please provide some information to help us personalize your experience' 
                : 'Update your profile information and preferences'}
            </CardDescription>
              </CardHeader>
              
              <CardContent>
                {isLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin w-8 h-8 border-4 border-sage-200 border-t-sage-500 rounded-full"></div>
              </div>
            ) : (
              <>
                {error && (
                  <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                    {error}
                  </div>
                )}
                
                {successMessage && (
                  <div className="mb-6 p-3 bg-green-50 border border-green-200 text-green-600 rounded-lg text-sm">
                    {successMessage}
                  </div>
                )}
                
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Input
                      label="Age"
                      type="number"
                      placeholder="Enter your age"
                      error={errors.age?.message}
                      disabled={isSaving}
                      {...register('age')}
                      />
                    
                    <Input
                      label="Location"
                      placeholder="City, Country"
                      error={errors.location?.message}
                      disabled={isSaving}
                      {...register('location')}
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-sage-700 mb-1">
                        Anxiety Level (0-10)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="1"
                        className="w-full h-2 bg-cream-100 rounded-lg appearance-none cursor-pointer"
                        disabled={isSaving}
                        {...register('anxiety_score')}
                      />
                      {errors.anxiety_score && (
                        <p className="text-sm text-red-500 mt-1">{errors.anxiety_score.message}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-sage-700 mb-1">
                        Depression Level (0-10)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="1"
                        className="w-full h-2 bg-cream-100 rounded-lg appearance-none cursor-pointer"
                        disabled={isSaving}
                        {...register('depression_score')}
                      />
                      {errors.depression_score && (
                        <p className="text-sm text-red-500 mt-1">{errors.depression_score.message}</p>
                          )}
                    </div>
                      </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-sage-700 mb-1">
                      Communication Preference
                    </label>
                    <select
                      className="w-full px-4 py-2 rounded-lg border border-cream-300 bg-cream-50/50 focus:outline-none focus:ring-2 focus:ring-sage-200 focus:border-transparent"
                      disabled={isSaving}
                      {...register('communication_preference')}
                >
                      <option value="text">Text Only</option>
                      <option value="voice">Voice Only</option>
                      <option value="both">Both Text and Voice</option>
                    </select>
                    {errors.communication_preference && (
                      <p className="text-sm text-red-500 mt-1">{errors.communication_preference.message}</p>
                    )}
                  </div>
                  
                        <div>
                    <label className="block text-sm font-medium text-sage-700 mb-1">
                      Sessions Per Week
                    </label>
                    <select
                      className="w-full px-4 py-2 rounded-lg border border-cream-300 bg-cream-50/50 focus:outline-none focus:ring-2 focus:ring-sage-200 focus:border-transparent"
                      disabled={isSaving}
                      {...register('session_frequency')}
                    >
                      {[1, 2, 3, 4, 5, 6, 7].map(num => (
                        <option key={num} value={num}>{num} {num === 1 ? 'session' : 'sessions'}</option>
                      ))}
                    </select>
                    {errors.session_frequency && (
                      <p className="text-sm text-red-500 mt-1">{errors.session_frequency.message}</p>
                    )}
                  </div>
                  
                  <Button
                    type="submit"
                    fullWidth
                    disabled={isSaving}
                    className="mt-4"
                  >
                    {isSaving 
                      ? (isCreating ? 'Creating profile...' : 'Updating profile...') 
                      : (isCreating ? 'Create profile' : 'Update profile')
                    }
                  </Button>
                </form>
              </>
                )}
              </CardContent>
            </Card>
      </motion.div>
              </div>
  );
} 