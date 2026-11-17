import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    if (!import.meta.env.DEV) return null;
    const saved = localStorage.getItem('jansahay_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => {
    return import.meta.env.DEV ? localStorage.getItem('jansahay_token') || null : null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isReady, setIsReady] = useState(false);

  const saveAuth = (userData, tokenStr) => {
    setUser(userData);
    if (import.meta.env.DEV && tokenStr) {
      setToken(tokenStr);
      localStorage.setItem('jansahay_user', JSON.stringify(userData));
      localStorage.setItem('jansahay_token', tokenStr);
    } else {
      setToken(null);
      localStorage.removeItem('jansahay_user');
      localStorage.removeItem('jansahay_token');
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    } catch (e) {
      console.warn('Could not confirm server logout; clearing local session state.', e);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('jansahay_user');
      localStorage.removeItem('jansahay_token');
    }
  };

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      const data = await res.json();
      saveAuth(data.user, data.access_token);
      return data;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email, password, fullName) => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
      const data = await res.json();
      saveAuth(data.user, data.access_token);
      return data;
    } finally {
      setIsLoading(false);
    }
  };

  const quickDemoLogin = async (type = 'citizen') => {
    if (import.meta.env.DEV) {
      if (type === 'admin') {
        return await login('admin@jansahay.gov.in', 'Admin@JanSahay2026');
      }
      return await login('demo@citizen.in', 'Citizen@2026');
    }
    throw new Error('Demo accounts are disabled in production.');
  };

  const refreshUser = async () => {
    try {
      const res = await fetch('/api/auth/me', {
        credentials: 'include',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const updated = await res.json();
        setUser(updated);
        if (import.meta.env.DEV) localStorage.setItem('jansahay_user', JSON.stringify(updated));
      } else {
        setUser(null);
        localStorage.removeItem('jansahay_user');
        localStorage.removeItem('jansahay_token');
        setToken(null);
      }
    } catch (e) {
      console.error("Failed to refresh user", e);
    } finally {
      setIsReady(true);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        isReady,
        login,
        register,
        logout,
        quickDemoLogin,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
