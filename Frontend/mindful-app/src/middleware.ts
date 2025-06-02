import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware to protect routes and handle authentication redirects
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if user is accessing a protected route (dashboard)
  const isProtectedRoute = pathname.startsWith('/dashboard');
  
  // Check if user is authenticated - only check on protected routes or login/register
  const authToken = request.cookies.get('mindful-auth-token')?.value;
  const isAuthenticated = Boolean(authToken);
  
  // Debug info in headers (only in development)
  const response = NextResponse.next();
  if (process.env.NODE_ENV === 'development') {
    response.headers.set('x-middleware-path', pathname);
    response.headers.set('x-middleware-authenticated', String(isAuthenticated));
    response.headers.set('x-middleware-protected-route', String(isProtectedRoute));
  }
  
  // If trying to access protected route while not authenticated, redirect to login
  if (isProtectedRoute && !isAuthenticated) {
    console.log(`[Middleware] Redirecting from ${pathname} to /login (not authenticated)`);
    const url = new URL('/login', request.url);
    url.searchParams.set('redirect', pathname);
    return NextResponse.redirect(url);
  }
  
  // If already authenticated and trying to access login/register, redirect to dashboard
  if ((pathname === '/login' || pathname === '/register' || pathname === '/') && isAuthenticated) {
    console.log(`[Middleware] Redirecting from ${pathname} to /dashboard (already authenticated)`);
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return response;
}

// Configure which paths should be checked by the middleware
export const config = {
  matcher: [
    '/',
    '/dashboard/:path*',
    '/login',
    '/register',
  ],
}; 