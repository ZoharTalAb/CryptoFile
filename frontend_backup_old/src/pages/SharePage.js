import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

function SharePage() {
  const { user } = useAuth();
  const [ownedFiles, setOwnedFiles] = useState([]);
  const [inbox, setInbox] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // טופס שיתוף
  const [selectedFileId, setSelectedFileId] = useState('');
  const [targetEmail, setTargetEmail] = useState('');
  const [statusMsg, setStatusMsg] = useState({ text: '', isError: false });

  // פונקציה למשיכת כל הנתונים במכה אחת (לפי ה-ListFilesUseCase)
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await api.get('/files/'); // וודאי שזה הנתיב שמפעיל את ListFilesUseCase
      setOwnedFiles(response.data.owned_files || []);
      setInbox(response.data.shared_with_me || []);
    } catch (err) {
      console.error("שגיאה בטעינת קבצים:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleShare = async (e) => {
    e.preventDefault();
    setStatusMsg({ text: '', isError: false });

    try {
      await api.post('/share/', {
        file_id: parseInt(selectedFileId),
        target_email: targetEmail
      });
      setStatusMsg({ text: 'הקובץ שותף בהצלחה!', isError: false });
      setTargetEmail('');
      fetchData(); // רענון הרשימות
    } catch (err) {
      setStatusMsg({ text: err.response?.data?.detail || 'שיתוף נכשל', isError: true });
    }
  };

  return (
    <div style={{ padding: '40px', direction: 'rtl', color: 'white' }}>
      <h1 style={{ color: '#60a5fa' }}>ניהול ושיתוף קבצים</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '30px' }}>
        
        {/* שליחת קובץ */}
        <section style={{ background: '#1f2937', padding: '20px', borderRadius: '10px' }}>
          <h3>שיתוף קובץ חדש</h3>
          <form onSubmit={handleShare}>
            <label>בחר קובץ מהמאגר שלך:</label>
            <select 
              value={selectedFileId} 
              onChange={(e) => setSelectedFileId(e.target.value)}
              style={{ width: '100%', padding: '10px', margin: '10px 0', borderRadius: '5px' }}
            >
              <option value="">-- בחר קובץ --</option>
              {ownedFiles.map(f => (
                <option key={f.id} value={f.id}>{f.original_filename || f.filename}</option>
              ))}
            </select>

            <input 
              type="email" 
              placeholder="אימייל הנמען" 
              value={targetEmail}
              onChange={(e) => setTargetEmail(e.target.value)}
              style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '5px' }}
            />
            <button type="submit" style={{ width: '100%', padding: '10px', background: '#10b981', color: 'white', border: 'none', borderRadius: '5px' }}>
              שתף קובץ
            </button>
            {statusMsg.text && <p style={{ color: statusMsg.isError ? '#ef4444' : '#10b981' }}>{statusMsg.text}</p>}
          </form>
        </section>

        {/* Inbox */}
        <section style={{ background: '#1f2937', padding: '20px', borderRadius: '10px' }}>
          <h3>קבצים ששותפו איתי</h3>
          {inbox.length === 0 ? <p>אין קבצים חדשים.</p> : (
            inbox.map(file => (
              <div key={file.id} style={{ borderBottom: '1px solid #374151', padding: '10px 0', display: 'flex', justifyContent: 'space-between' }}>
                <span>{file.original_filename}</span>
                <button onClick={() => window.open(`${process.env.REACT_APP_API_URL}/files/download/${file.id}`)} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px' }}>
                  הורד
                </button>
              </div>
            ))
          )}
        </section>
      </div>
    </div>
  );
}

export default SharePage;