import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ResumeProvider } from './contexts/ResumeContext';
import { ToastProvider } from './hooks/useToast';
import { ToastContainer } from './components/ui/Toast';
import { ProtectedRoute } from './routes/ProtectedRoute';

import { LandingPage } from './pages/LandingPage';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { ATSPage } from './pages/ATSPage';
import { JobMatchPage } from './pages/JobMatchPage';
import { ImprovementPage } from './pages/ImprovementPage';
import { InterviewPage } from './pages/InterviewPage';
import { RoadmapPage } from './pages/RoadmapPage';
import { AnalyticsDashboardPage } from './pages/AnalyticsDashboardPage';
import { ProfilePage } from './pages/ProfilePage';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <ResumeProvider>
            <Routes>
              {/* Public */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Protected */}
              <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path="/upload" element={<ProtectedRoute><UploadPage /></ProtectedRoute>} />
              <Route path="/analysis/:resumeId" element={<ProtectedRoute><AnalysisPage /></ProtectedRoute>} />
              <Route path="/ats/:resumeId" element={<ProtectedRoute><ATSPage /></ProtectedRoute>} />
              <Route path="/job-match/:resumeId" element={<ProtectedRoute><JobMatchPage /></ProtectedRoute>} />
              <Route path="/improve/:resumeId" element={<ProtectedRoute><ImprovementPage /></ProtectedRoute>} />
              <Route path="/interview/:resumeId" element={<ProtectedRoute><InterviewPage /></ProtectedRoute>} />
              <Route path="/roadmap/:resumeId" element={<ProtectedRoute><RoadmapPage /></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute><AnalyticsDashboardPage /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <ToastContainer />
          </ResumeProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
};

export default App;
