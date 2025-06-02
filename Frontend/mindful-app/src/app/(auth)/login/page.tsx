'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../../app/components/ui/Card';
import { Input } from '../../../app/components/ui/Input';
import { Button } from '../../../app/components/ui/Button';
import { login } from '../../../lib/api/auth';
import { AxiosError } from 'axios';

// Form validation schema
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Check for query parameters
  useEffect(() => {
    const registered = searchParams.get('registered');
    if (registered === 'true') {
      setSuccessMessage('Account created successfully! Please log in.');
    }
    
    const sessionExpired = searchParams.get('session_expired');
    if (sessionExpired === 'true') {
      setError('Your session has expired. Please log in again.');
    }
  }, [searchParams]);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await login({ email: data.email, password: data.password });
      router.push('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || 'Invalid email or password');
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
            <CardTitle className="text-center">Welcome Back</CardTitle>
            <CardDescription className="text-center">
              Sign in to continue your mindfulness journey
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            {successMessage && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-600 rounded-lg text-sm">
                {successMessage}
              </div>
            )}
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
              
              <Button
                type="submit"
                fullWidth
                disabled={isLoading}
                className="mt-2"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>
          </CardContent>
          
          <CardFooter className="flex justify-center">
            <p className="text-sm text-sage-600">
              Don&apos;t have an account?{' '}
              <Link href="/register" className="text-sage-600 hover:text-sage-700 font-medium">
                Create one
              </Link>
            </p>
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  );
} 