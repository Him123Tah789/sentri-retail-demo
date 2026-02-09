import { User, AuthResponse } from './types';

const TOKEN_KEY = 'sentri_token';
const USER_KEY = 'sentri_user';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

// Demo users for offline/demo mode
const DEMO_USERS: Record<string, { password: string; user: User }> = {
  'demo@sentri.demo': {
    password: 'demo123',
    user: { id: 1, email: 'demo@sentri.demo', fullName: 'Demo User', role: 'staff' },
  },
  'demo@sentri-retail.com': {
    password: 'demo123',
    user: { id: 1, email: 'demo@sentri-retail.com', fullName: 'Demo User', role: 'staff' },
  },
  'analyst@sentri.demo': {
    password: 'analyst123',
    user: { id: 2, email: 'analyst@sentri.demo', fullName: 'Security Analyst', role: 'hq_it' },
  },
  'admin@sentri.demo': {
    password: 'admin123',
    user: { id: 3, email: 'admin@sentri.demo', fullName: 'System Admin', role: 'admin' },
  },
};

export async function login(email: string, password: string): Promise<AuthResponse> {
  // Try API first
  try {
    const response = await fetch(`${API_URL}${API_PREFIX}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      return { accessToken: data.access_token, tokenType: 'bearer', user: data.user };
    }
  } catch (error) {
    console.log('API unavailable, using demo mode');
  }

  // Fallback to demo mode
  const demoUser = DEMO_USERS[email];
  if (demoUser && demoUser.password === password) {
    const token = `demo_token_${Date.now()}`;
    setToken(token);
    setUser(demoUser.user);
    return { accessToken: token, tokenType: 'bearer', user: demoUser.user };
  }

  throw new Error('Invalid email or password');
}

export async function signup(email: string, password: string, fullName: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}${API_PREFIX}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signup failed');
  }

  const data = await response.json();
  setToken(data.access_token);
  setUser(data.user);
  return { accessToken: data.access_token, tokenType: 'bearer', user: data.user };
}

export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function getUser(): User | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function setUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}
