import React, { useState } from 'react';
import api from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage('');
    setIsError(false);

    try {
      await api.post('/auth/register', { email, password });
      
      setMessage('ההרשמה בוצעה בהצלחה! מעביר אותך להתחברות...');
      setIsError(false);
      
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setIsError(true);
      setMessage('ההרשמה נכשלה. ודאי שהסיסמה באורך 6 תווים לפחות או שהמייל לא תפוס.');
    }
  };

  return (
    <div style={{ 
      display: 'flex', justifyContent: 'center', alignItems: 'center', 
      height: '80vh', direction: 'rtl' 
    }}>
      <form onSubmit={handleRegister} style={{ 
        padding: '30px', border: '1px solid #374151', borderRadius: '12px',
        backgroundColor: '#1f2937', color: 'white', width: '350px'
      }}>
        <h2 style={{ textAlign: 'center', color: '#60a5fa' }}>יצירת חשבון חדש</h2>
        
        {message && (
          <p style={{ 
            color: isError ? '#ef4444' : '#10b981', 
            fontSize: '0.9rem',
            textAlign: 'center'
          }}>
            {message}
          </p>
        )}

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
          <label>סיסמה (לפחות 6 תווים):</label>
          <input 
            type="password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', marginTop: '5px', borderRadius: '6px' }}
          />
        </div>

        <button type="submit" style={{ 
          width: '100%', padding: '12px', backgroundColor: '#10b981', 
          color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer',
          fontWeight: 'bold'
        }}>
          הירשם עכשיו
        </button>

        <p style={{ marginTop: '20px', fontSize: '0.9rem', textAlign: 'center' }}>
          כבר יש לך חשבון? <Link to="/login" style={{ color: '#60a5fa' }}>התחברי כאן</Link>
        </p>
      </form>
    </div>
  );
}

export default RegisterPage;