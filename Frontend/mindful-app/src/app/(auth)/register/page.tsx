'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { AxiosError } from 'axios';

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../../app/components/ui/Card';
import { Input } from '../../../app/components/ui/Input';
import { Button } from '../../../app/components/ui/Button';
import { register as registerUser } from '../../../lib/api/auth';

// Form validation schema
const registerSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Confirm password is required'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: RegisterFormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      // Format name for the register function (expects 'name')
      const formattedName = `${data.first_name} ${data.last_name}`;
      
      // Register user
      await registerUser({
        name: formattedName,
        email: data.email,
        password: data.password
      });
      
      // Redirect to login page after successful registration
      router.push('/login?registered=true');
    } catch (err) {
      console.error('Registration error:', err);
      
      if (err instanceof AxiosError) {
        // Handle specific API errors
        if (err.response?.status === 400 && err.response?.data?.detail?.includes('Email already registered')) {
          setError('This email is already registered. Please try logging in instead.');
        } else {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="text-center">Begin Your Journey</CardTitle>
            <CardDescription className="text-center">
              Create an account to start your mindfulness practice
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="First Name"
                  placeholder="John"
                  error={errors.first_name?.message}
                  disabled={isLoading}
                  {...register('first_name')}
                />
                
                <Input
                  label="Last Name"
                  placeholder="Doe"
                  error={errors.last_name?.message}
                  disabled={isLoading}
                  {...register('last_name')}
                />
              </div>
              
              <Input
                label="Email"
                type="email"
                placeholder="your.email@example.com"
                error={errors.email?.message}
                disabled={isLoading}
                {...register('email')}
              />
              
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                error={errors.password?.message}
                disabled={isLoading}
                {...register('password')}
              />
              
              <Input
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                error={errors.confirmPassword?.message}
                disabled={isLoading}
                {...register('confirmPassword')}
              />
              
              <Button
                type="submit"
                fullWidth
                disabled={isLoading}
                className="mt-2"
              >
                {isLoading ? 'Creating account...' : 'Create account'}
              </Button>
            </form>
          </CardContent>
          
          <CardFooter className="flex justify-center">
            <p className="text-sm text-sage-600">
              Already have an account?{' '}
              <Link href="/login" className="text-sage-600 hover:text-sage-700 font-medium">
                Sign in
              </Link>
            </p>
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  );
} 