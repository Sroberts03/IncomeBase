import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ZipVerificationPage from './pages/ZipVerificationPage';
import FileUploadPage from './pages/FileUploadPage';
import Home from './pages/HomePage';
import Header from './components/Header';
import Footer from './components/Footer';
import SuccessPage from './pages/SuccessPage';
import BorrowersDetailPage from './pages/BorrowersDetailPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { session, isLoading } = useAuth();
  if (isLoading) return <div>Loading Auth...</div>;
  if (!session) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div>
          <Header />
          <main>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/verify/:token" element={<ZipVerificationPage />} />
              <Route path="/upload/:token" element={<FileUploadPage />} />
              <Route path="/success" element={<SuccessPage />} />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route 
                path="/borrower/:borrowerId" 
                element={
                  <ProtectedRoute>
                    <BorrowersDetailPage />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
