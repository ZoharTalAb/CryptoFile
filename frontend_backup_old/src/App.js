import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// הייבוא של הדפים החדשים שלנו - ודאי שהשמות תואמים לקבצים בתיקיית pages
import StegoPage from './pages/StegoPage';
import SharePage from './pages/SharePage';
import FilesPage from './pages/FilesPage';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App" style={{ direction: 'rtl', minHeight: '100vh', backgroundColor: '#111827' }}>
          <Navbar />
          
          <Routes>
            {/* דפים ציבוריים */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* דפים מוגנים - הוספנו את הדפים החדשים כאן */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <div style={{ padding: '40px', textAlign: 'center', color: 'white' }}>
                  <h1 style={{ color: '#60a5fa' }}>ברוכים הבאים ל-CryptoFile! 🚀</h1>
                  <p>התשתית מוכנה. בחרי פעולה מהתפריט למעלה כדי להתחיל.</p>
                </div>
              </ProtectedRoute>
            } />

            <Route path="/stego" element={
              <ProtectedRoute>
                <StegoPage />
              </ProtectedRoute>
            } />

            <Route path="/share" element={
              <ProtectedRoute>
                <SharePage />
              </ProtectedRoute>
            } />

            <Route path="/files" element={
              <ProtectedRoute>
                <FilesPage />
              </ProtectedRoute>
            } />

            {/* ברירת מחדל - חזרה לדאשבורד */}
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;