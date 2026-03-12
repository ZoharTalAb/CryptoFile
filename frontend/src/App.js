import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App" style={{ direction: 'rtl', minHeight: '100vh', backgroundColor: '#111827' }}>
          {/* התפריט יופיע בכל דף (הוא מתוכנת להעלם אם לא מחוברים) */}
          <Navbar />
          
          <Routes>
            {/* דפים ציבוריים */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* דפים מוגנים - רק משתמש מחובר יכול לראות */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <div style={{ padding: '40px', textAlign: 'center', color: 'white' }}>
                  <h1 style={{ color: '#60a5fa' }}>ברוכים הבאים ל-CryptoFile! 🚀</h1>
                  <p>התשתית מוכנה ב-100%. כל הקריאות לשרת יעבדו עכשיו עם הטוקן שלך.</p>
                  
                  <div style={{ 
                    marginTop: '40px', 
                    padding: '20px', 
                    border: '1px dashed #4b5563', 
                    borderRadius: '8px',
                    display: 'inline-block' 
                  }}>
                    <h3 style={{ color: '#9ca3af' }}>הודעה לחברה שלך:</h3>
                    <p>היי! הכל מוכן. את יכולה להתחיל ליצור דפים חדשים בתיקיית pages <br/> 
                    ולהוסיף אותם כאן בתוך ה-Routes.</p>
                  </div>
                </div>
              </ProtectedRoute>
            } />

            {/* אם המשתמש מגיע לכתובת לא ידועה, נשלח אותו לדאשבורד */}
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;