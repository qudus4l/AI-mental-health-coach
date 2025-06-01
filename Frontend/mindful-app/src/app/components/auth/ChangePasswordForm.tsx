'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { FiLock, FiCheck } from 'react-icons/fi';

import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

// Form validation schema
const passwordSchema = z.object({
  currentPassword: z.string().min(6, 'Password must be at least 6 characters'),
  newPassword: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Confirm password is required'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type PasswordFormValues = z.infer<typeof passwordSchema>;

interface ChangePasswordFormProps {
  onClose: () => void;
}

export function ChangePasswordForm({ onClose }: ChangePasswordFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: PasswordFormValues) => {
    setIsLoading(true);
    setError(null);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setSuccess(true);
      
      // Auto close after success
      setTimeout(() => {
        onClose();
      }, 2000);
    }, 1000);
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-lg font-medium flex items-center">
          <FiLock className="mr-2 text-sage-500" />
          Change Password
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        {success ? (
          <div className="p-4 bg-sage-100 border border-sage-200 text-sage-700 rounded-lg flex items-center">
            <FiCheck className="mr-2 text-sage-500" />
            Password changed successfully
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <Input
              label="Current Password"
              type="password"
              placeholder="••••••••"
              error={errors.currentPassword?.message}
              disabled={isLoading}
              {...register('currentPassword')}
            />
            
            <Input
              label="New Password"
              type="password"
              placeholder="••••••••"
              error={errors.newPassword?.message}
              disabled={isLoading}
              {...register('newPassword')}
            />
            
            <Input
              label="Confirm New Password"
              type="password"
              placeholder="••••••••"
              error={errors.confirmPassword?.message}
              disabled={isLoading}
              {...register('confirmPassword')}
            />
            
            <div className="flex justify-end space-x-2 pt-2">
              <Button
                type="button"
                variant="secondary"
                onClick={onClose}
                disabled={isLoading}
              >
                Cancel
              </Button>
              
              <Button
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? 'Updating...' : 'Update Password'}
              </Button>
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  );
} 