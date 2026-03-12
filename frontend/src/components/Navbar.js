import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (!user || location.pathname === '/login' || location.pathname === '/register') {
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      padding: '10px 20px', 
      backgroundColor: '#1f2937', 
      color: 'white',
      direction: 'rtl' 
    }}>
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
        <strong style={{ fontSize: '1.2rem', color: '#60a5fa' }}>CryptoFile</strong>
        <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>דף הבית</Link>
        <Link to="/chat" style={{ color: 'white', textDecoration: 'none' }}>שיתוף</Link>
        <Link to="/stego" style={{ color: 'white', textDecoration: 'none' }}>הטמנה/חילוץ</Link>
        <Link to="/files" style={{ color: 'white', textDecoration: 'none' }}>הקבצים שלי</Link>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <span style={{ fontSize: '0.9rem', color: '#9ca3af' }}>{user.email}</span>
        <button 
          onClick={handleLogout} 
          style={{ 
            backgroundColor: '#ef4444', 
            color: 'white', 
            border: 'none', 
            padding: '5px 12px', 
            borderRadius: '4px', 
            cursor: 'pointer' 
          }}
        >
          התנתק
        </button>
      </div>
    </nav>
  );
}

export default Navbar;