import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';

// Layouts
import { PublicLayout } from './layouts/PublicLayout';
import { AppLayout } from './layouts/AppLayout';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { DashboardPage } from './pages/DashboardPage';
import { BrowseSchemesPage } from './pages/BrowseSchemesPage';
import { SchemeDetailsPage } from './pages/SchemeDetailsPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { EligibilityPage } from './pages/EligibilityPage';
import { ChatPage } from './pages/ChatPage';
import { DocumentCenterPage } from './pages/DocumentCenterPage';
import { ProfilePage } from './pages/ProfilePage';
import { SettingsPage } from './pages/SettingsPage';
import { AdminPage } from './pages/AdminPage';

function AuthenticatedOnboarding() {
  const { user, isReady } = useAuth();
  if (!isReady) return <div className="p-8 text-center text-slate-600">Loading account…</div>;
  return user ? <OnboardingPage /> : <Navigate to="/signup" replace />;
}

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Layout */}
            <Route element={<PublicLayout />}>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<RegisterPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/onboarding" element={<AuthenticatedOnboarding />} />
            </Route>

            {/* Application Dashboard Layout */}
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/schemes" element={<BrowseSchemesPage />} />
              <Route path="/schemes/:id" element={<SchemeDetailsPage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="/eligibility" element={<EligibilityPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/documents" element={<DocumentCenterPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/admin" element={<AdminPage />} />
              <Route path="/admin/schemes" element={<AdminPage />} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
