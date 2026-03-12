import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

function SharePage() {
  const { user } = useAuth();
  const [ownedFiles, setOwnedFiles] = useState([]);
  const [inbox, setInbox] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // States לטופס השיתוף
  const [selectedFileId, setSelectedFileId] = useState('');
  const [targetEmail, setTargetEmail] = useState('');
  const [status, setStatus] = useState({ text: '', isError: false });

  // 1. טעינת נתונים (גם הקבצים שלי וגם האינבוקס מגיעים מאותו מקום)
  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/files/');
      setOwnedFiles(res.data.owned_files || []);
      setInbox(res.data.shared_with_me || []);
    } catch (err) {
      console.error("טעינת נתונים נכשלה");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  // 2. פונקציית השיתוף
  const handleShare = async (e) => {
    e.preventDefault();
    setStatus({ text: '', isError: false });

    if (!selectedFileId || !targetEmail) {
      setStatus({ text: 'נא לבחור קובץ ולהזין אימייל', isError: true });
      return;
    }

    try {
      // שליחה בדיוק לפי ה-ShareRequest בבאקנד
      await api.post('/share/', {
        file_id: parseInt(selectedFileId),
        target_email: targetEmail
      });

      setStatus({ text: `הקובץ שותף בהצלחה עם ${targetEmail}!`, isError: false });
      setTargetEmail('');
      setSelectedFileId('');
      fetchData(); // רענון כדי לראות אם משהו השתנה
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'השיתוף נכשל';
      setStatus({ text: errorMsg, isError: true });
    }
  };

  // פונקציית הורדה לקבצים שקיבלת
  const downloadFile = async (fileId, filename) => {
    try {
      const response = await api.get(`/files/${fileId}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("הורדה נכשלה");
    }
  };

  return (
    <div style={{ padding: '40px', direction: 'rtl', color: 'white', maxWidth: '1100px', margin: '0 auto' }}>
      <h1 style={{ color: '#60a5fa', marginBottom: '30px' }}>מרכז שיתוף קבצים</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '40px' }}>
        
        {/* חלק א': טופס שליחה */}
        <section style={{ background: '#1f2937', padding: '25px', borderRadius: '15px', border: '1px solid #374151', alignSelf: 'start' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '20px', color: '#10b981' }}>שתפי קובץ עם חברה</h2>
          
          <form onSubmit={handleShare}>
            <div style={{ marginBottom: '15px' }}>
              <label>בחרי קובץ מהארכיון שלך:</label>
              <select 
                value={selectedFileId} 
                onChange={(e) => setSelectedFileId(e.target.value)}
                style={inputStyle}
              >
                <option value="">-- בחרי קובץ מוטמן --</option>
                {ownedFiles.map(f => (
                  <option key={f.id} value={f.id}>{f.filename}</option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label>אימייל הנמענת:</label>
              <input 
                type="email" 
                placeholder="maya@example.com"
                value={targetEmail}
                onChange={(e) => setTargetEmail(e.target.value)}
                style={inputStyle}
              />
            </div>

            <button type="submit" style={buttonStyle}>שתפי עכשיו</button>

            {status.text && (
              <p style={{ marginTop: '15px', color: status.isError ? '#ef4444' : '#10b981', textAlign: 'center' }}>
                {status.text}
              </p>
            )}
          </form>
        </section>

        {/* חלק ב': Inbox - קבצים ששותפו איתי */}
        <section>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '20px', color: '#60a5fa' }}>תיבת נכנס (Inbox)</h2>
          {loading ? <p>טוען הודעות...</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {inbox.length === 0 ? (
                <p style={{ color: '#9ca3af', fontStyle: 'italic' }}>עוד לא שיתפו איתך קבצים.</p>
              ) : (
                inbox.map((item) => (
                  <div key={item.id} style={inboxItemStyle}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 'bold' }}>{item.filename}</div>
                      <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                        התקבל ב: {new Date(item.created_at).toLocaleDateString('he-IL')}
                      </div>
                    </div>
                    <button 
                      onClick={() => downloadFile(item.id, item.filename)}
                      style={downloadButtonStyle}
                    >
                      הורדה וחילוץ
                    </button>
                  </div>
                ))
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

// עיצובים
const inputStyle = { width: '100%', padding: '12px', marginTop: '8px', borderRadius: '8px', background: '#374151', color: 'white', border: '1px solid #4b5563' };
const buttonStyle = { width: '100%', padding: '12px', background: '#10b981', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' };
const inboxItemStyle = { background: '#374151', padding: '15px', borderRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #4b5563' };
const downloadButtonStyle = { padding: '8px 15px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem' };

export default SharePage;