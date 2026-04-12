import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/dashboard'); 
    } catch (err) {
      setError('אופס! המייל או הסיסמה לא נכונים.');
    }
  };

  return (
    <div style={{ 
      display: 'flex', justifyContent: 'center', alignItems: 'center', 
      height: '80vh', direction: 'rtl' 
    }}>
      <form onSubmit={handleSubmit} style={{ 
        padding: '30px', border: '1px solid #374151', borderRadius: '12px',
        backgroundColor: '#1f2937', color: 'white', width: '350px'
      }}>
        <h2 style={{ textAlign: 'center', color: '#60a5fa' }}>כניסה למערכת</h2>
        
        {error && <p style={{ color: '#ef4444', fontSize: '0.9rem' }}>{error}</p>}

        <div style={{ marginBottom: '15px' }}>
          <label>אימייל:</label>
          <input 
            type="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', marginTop: '5px', borderRadius: '6px' }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label>סיסמה:</label>
          <input 
            type="password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', marginTop: '5px', borderRadius: '6px' }}
          />
        </div>

        <button type="submit" style={{ 
          width: '100%', padding: '12px', backgroundColor: '#2563eb', 
          color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer',
          fontWeight: 'bold'
        }}>
          התחבר
        </button>

        <p style={{ marginTop: '20px', fontSize: '0.9rem', textAlign: 'center' }}>
          עוד לא רשומה? <Link to="/register" style={{ color: '#60a5fa' }}>צרי חשבון חדש</Link>
        </p>
      </form>
    </div>
  );
}

export default LoginPage;