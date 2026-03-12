import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // אם המשתמש לא מחובר או נמצא בדפי התחברות - לא מציגים את התפריט
  if (!user || location.pathname === '/login' || location.pathname === '/register') {
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // פונקציה לבדיקה אם לינק פעיל (בשביל העיצוב)
  const isActive = (path) => location.pathname === path;

  return (
    <nav style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      padding: '10px 20px', 
      backgroundColor: '#1f2937', 
      color: 'white',
      direction: 'rtl',
      borderBottom: '1px solid #374151'
    }}>
      <div style={{ display: 'flex', gap: '25px', alignItems: 'center' }}>
        <strong style={{ fontSize: '1.2rem', color: '#60a5fa', marginLeft: '10px' }}>CryptoFile</strong>
        
        <Link to="/dashboard" style={linkStyle(isActive('/dashboard'))}>דף הבית</Link>
        <Link to="/stego" style={linkStyle(isActive('/stego'))}>הטמנה/חילוץ</Link>
        <Link to="/files" style={linkStyle(isActive('/files'))}>הקבצים שלי</Link>
        <Link to="/share" style={linkStyle(isActive('/share'))}>שיתוף קבצים</Link>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <div style={{ textAlign: 'left' }}>
          <div style={{ fontSize: '0.85rem', color: '#60a5fa', fontWeight: 'bold' }}>מחוברת כ:</div>
          <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{user.email}</div>
        </div>
        <button 
          onClick={handleLogout} 
          style={{ 
            backgroundColor: '#ef4444', 
            color: 'white', 
            border: 'none', 
            padding: '6px 15px', 
            borderRadius: '6px', 
            cursor: 'pointer',
            fontWeight: 'bold',
            transition: '0.2s'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#dc2626'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#ef4444'}
        >
          התנתק
        </button>
      </div>
    </nav>
  );
}

// עיצוב דינמי ללינקים
const linkStyle = (active) => ({
  color: active ? '#60a5fa' : 'white', 
  textDecoration: 'none',
  fontSize: '0.95rem',
  fontWeight: active ? 'bold' : 'normal',
  borderBottom: active ? '2px solid #60a5fa' : 'none',
  paddingBottom: '5px'
});

export default Navbar;