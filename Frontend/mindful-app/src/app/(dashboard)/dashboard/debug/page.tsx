'use client';

import { useState, useEffect } from 'react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import Cookies from 'js-cookie';
import api from '../../../../lib/api/axios';

interface DebugInfo {
  hasLocalStorageToken: boolean;
  hasCookieToken: boolean;
  localStorageToken: string;
  cookieToken: string;
  authData: any | null;
  apiBaseUrl: string;
}

interface ApiTestResult {
  status: 'success' | 'error';
  data?: any;
  error?: string;
  response?: any;
  status_code?: number;
}

interface ApiTests {
  healthCheck?: ApiTestResult;
  authEndpoint?: ApiTestResult;
  conversations?: ApiTestResult;
}

export default function DebugPage() {
  const [debugInfo, setDebugInfo] = useState<DebugInfo>({
    hasLocalStorageToken: false,
    hasCookieToken: false,
    localStorageToken: 'None',
    cookieToken: 'None',
    authData: null,
    apiBaseUrl: 'http://localhost:8000',
  });
  const [apiTest, setApiTest] = useState<ApiTests>({});
  
  useEffect(() => {
    // Gather debug information
    const token = localStorage.getItem('mindful-auth-token');
    const cookieToken = Cookies.get('mindful-auth-token');
    const authData = localStorage.getItem('mindful-auth');
    
    setDebugInfo({
      hasLocalStorageToken: !!token,
      hasCookieToken: !!cookieToken,
      localStorageToken: token ? `${token.substring(0, 20)}...` : 'None',
      cookieToken: cookieToken ? `${cookieToken.substring(0, 20)}...` : 'None',
      authData: authData ? JSON.parse(authData) : null,
      apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    });
  }, []);
  
  const testHealthCheck = async () => {
    try {
      const response = await fetch('http://localhost:8000/');
      const data = await response.json();
      setApiTest(prev => ({ ...prev, healthCheck: { status: 'success', data } }));
    } catch (error) {
      setApiTest(prev => ({ ...prev, healthCheck: { status: 'error', error: error instanceof Error ? error.message : 'Unknown error' } }));
    }
  };
  
  const testAuthEndpoint = async () => {
    try {
      const response = await api.get('/api/users/me');
      setApiTest(prev => ({ ...prev, authEndpoint: { status: 'success', data: response.data } }));
    } catch (error: any) {
      setApiTest(prev => ({ 
        ...prev, 
        authEndpoint: { 
          status: 'error', 
          error: error.message,
          response: error.response?.data,
          status_code: error.response?.status
        } 
      }));
    }
  };
  
  const testConversationsEndpoint = async () => {
    try {
      const response = await api.get('/api/conversations/');
      setApiTest(prev => ({ ...prev, conversations: { status: 'success', data: response.data } }));
    } catch (error: any) {
      setApiTest(prev => ({ 
        ...prev, 
        conversations: { 
          status: 'error', 
          error: error.message,
          response: error.response?.data,
          status_code: error.response?.status
        } 
      }));
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Debug Information</h1>
      
      <Card className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
        <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
          {JSON.stringify(debugInfo, null, 2)}
        </pre>
      </Card>
      
      <Card className="mb-6">
        <h2 className="text-xl font-semibold mb-4">API Tests</h2>
        <div className="space-y-4">
          <div>
            <Button onClick={testHealthCheck} className="mb-2">
              Test Health Check (No Auth)
            </Button>
            {apiTest.healthCheck && (
              <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
                {JSON.stringify(apiTest.healthCheck, null, 2)}
              </pre>
            )}
          </div>
          
          <div>
            <Button onClick={testAuthEndpoint} className="mb-2">
              Test Auth Endpoint (/api/users/me)
            </Button>
            {apiTest.authEndpoint && (
              <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
                {JSON.stringify(apiTest.authEndpoint, null, 2)}
              </pre>
            )}
          </div>
          
          <div>
            <Button onClick={testConversationsEndpoint} className="mb-2">
              Test Conversations Endpoint
            </Button>
            {apiTest.conversations && (
              <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
                {JSON.stringify(apiTest.conversations, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </Card>
      
      <Card>
        <h2 className="text-xl font-semibold mb-4">Instructions</h2>
        <ol className="list-decimal list-inside space-y-2">
          <li>Check if you have authentication tokens in localStorage and cookies</li>
          <li>Test the health check endpoint to verify backend connectivity</li>
          <li>Test the auth endpoint to verify your token is valid</li>
          <li>Test the conversations endpoint to see if it works with auth</li>
          <li>If you&apos;re not authenticated, go to <a href="/login" className="text-blue-600 underline">/login</a></li>
        </ol>
      </Card>
    </div>
  );
} 