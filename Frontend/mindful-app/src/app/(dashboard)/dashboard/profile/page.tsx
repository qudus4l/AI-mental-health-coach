'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion, AnimatePresence } from 'framer-motion';
import { FiUser, FiMail, FiLock, FiEdit, FiSave, FiCheck, FiX } from 'react-icons/fi';

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../../components/ui/Card';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { ChangePasswordForm } from '../../../components/auth/ChangePasswordForm';

// Form validation schema
const profileSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Please enter a valid email'),
  bio: z.string().optional(),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

// Demo user data
const demoUser = {
  first_name: 'Jamie',
  last_name: 'Johnson',
  email: 'jamie.johnson@example.com',
  bio: 'Working on managing stress and anxiety through mindfulness practices.',
};

export default function ProfilePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: demoUser,
  });
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  const onSubmit = async (data: ProfileFormValues) => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setIsEditing(false);
      setUpdateSuccess(true);
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setUpdateSuccess(false);
      }, 3000);
    }, 1000);
  };
  
  const handleCancel = () => {
    reset(demoUser);
    setIsEditing(false);
  };
  
  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="floating-delayed"
      >
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Your Profile</h1>
          <p className="text-sage-600 mt-2">Manage your personal information</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Profile Information */}
          <div className="md:col-span-2">
            <Card className="floating">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-lg font-medium flex items-center">
                  <FiUser className="mr-2 text-sage-500" />
                  Personal Information
                </CardTitle>
                
                {!isEditing && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setIsEditing(true)}
                    className="text-sage-600"
                  >
                    <FiEdit className="mr-1" />
                    Edit
                  </Button>
                )}
              </CardHeader>
              
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-12 bg-cream-100 animate-pulse rounded-lg"></div>
                    ))}
                  </div>
                ) : (
                  <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="First Name"
                        error={errors.first_name?.message}
                        disabled={!isEditing || isLoading}
                        {...register('first_name')}
                      />
                      
                      <Input
                        label="Last Name"
                        error={errors.last_name?.message}
                        disabled={!isEditing || isLoading}
                        {...register('last_name')}
                      />
                    </div>
                    
                    <Input
                      label="Email Address"
                      type="email"
                      error={errors.email?.message}
                      disabled={true} // Email cannot be edited
                      {...register('email')}
                    />
                    
                    <div>
                      <label className="block text-sm font-medium text-sage-700 mb-1">
                        Bio
                      </label>
                      <textarea
                        className="w-full px-4 py-2 rounded-lg border bg-cream-50/50 border-cream-300 focus:outline-none focus:ring-2 focus:ring-sage-200 focus:border-transparent resize-none transition-all"
                        rows={4}
                        disabled={!isEditing || isLoading}
                        placeholder="Tell us a bit about yourself"
                        {...register('bio')}
                      />
                    </div>
                    
                    {isEditing && (
                      <div className="flex justify-end space-x-2">
                        <Button
                          type="button"
                          variant="secondary"
                          onClick={handleCancel}
                          disabled={isLoading}
                        >
                          Cancel
                        </Button>
                        
                        <Button
                          type="submit"
                          disabled={isLoading}
                          className="flex items-center"
                        >
                          {isLoading ? 'Saving...' : (
                            <>
                              <FiSave className="mr-1" />
                              Save Changes
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                    
                    {updateSuccess && (
                      <div className="p-3 bg-sage-100 border border-sage-200 text-sage-700 rounded-lg flex items-center">
                        <FiCheck className="mr-2 text-sage-500" />
                        Profile updated successfully
                      </div>
                    )}
                  </form>
                )}
              </CardContent>
            </Card>
            
            {/* Security Section */}
            <Card className="mt-6 floating-delayed">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center">
                  <FiLock className="mr-2 text-sage-500" />
                  Security
                </CardTitle>
              </CardHeader>
              
              <CardContent>
                <Button 
                  className="w-full md:w-auto"
                  onClick={() => setShowPasswordModal(true)}
                >
                  Change Password
                </Button>
              </CardContent>
            </Card>
          </div>
          
          {/* Profile Summary */}
          <div>
            <Card className="floating">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center">
                  <FiUser className="mr-2 text-sage-500" />
                  Profile Summary
                </CardTitle>
              </CardHeader>
              
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    <div className="w-24 h-24 bg-cream-100 animate-pulse rounded-full mx-auto"></div>
                    <div className="h-8 bg-cream-100 animate-pulse rounded-lg"></div>
                    <div className="h-4 bg-cream-100 animate-pulse rounded-lg"></div>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="w-24 h-24 bg-sage-100 rounded-full mx-auto flex items-center justify-center">
                      <span className="text-sage-600 text-2xl font-semibold">
                        {demoUser.first_name[0]}{demoUser.last_name[0]}
                      </span>
                    </div>
                    
                    <h3 className="mt-4 text-lg font-semibold text-sage-800">
                      {demoUser.first_name} {demoUser.last_name}
                    </h3>
                    
                    <p className="text-sage-600 flex items-center justify-center mt-1">
                      <FiMail className="mr-1" size={14} />
                      {demoUser.email}
                    </p>
                    
                    <div className="mt-6 p-4 bg-cream-50 rounded-lg border border-cream-200">
                      <h4 className="font-medium text-sage-700 mb-2">Stats</h4>
                      <div className="grid grid-cols-2 gap-2 text-center">
                        <div>
                          <p className="text-lg font-bold text-sage-800">12</p>
                          <p className="text-xs text-sage-600">Sessions</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-sage-800">8</p>
                          <p className="text-xs text-sage-600">Homework</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </motion.div>
      
      {/* Password Change Modal */}
      <AnimatePresence>
        {showPasswordModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
              onClick={() => setShowPasswordModal(false)}
            />
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed inset-0 flex items-center justify-center z-50 p-4"
            >
              <div className="relative w-full max-w-md">
                <button
                  onClick={() => setShowPasswordModal(false)}
                  className="absolute -top-10 right-0 text-white bg-sage-500 hover:bg-sage-600 p-2 rounded-full"
                >
                  <FiX />
                </button>
                <ChangePasswordForm onClose={() => setShowPasswordModal(false)} />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
} 