import React, { useEffect, useState } from 'react';
import api from '../api/axios';

function FilesPage() {
  const [ownedFiles, setOwnedFiles] = useState([]);
  const [sharedFiles, setSharedFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  // 1. משיכת רשימת הקבצים לפי ה-Schema ששלחת
  const fetchFiles = async () => {
    try {
      const res = await api.get('/files/'); 
      setOwnedFiles(res.data.owned_files || []);
      setSharedFiles(res.data.shared_with_me || []);
    } catch (err) {
      console.error("טעינת קבצים נכשלה");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchFiles(); }, []);

  // 2. פונקציית הורדה מאובטחת (עם הטוקן)
  const downloadFile = async (fileId, filename) => {
    try {
      const response = await api.get(`/files/${fileId}/download`, {
        responseType: 'blob', // חשוב כדי לטפל בקובץ בינארי
      });

      // יצירת לינק זמני להורדה בדפדפן
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename); 
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("ההורדה נכשלה. ודאי שאת עדיין מחוברת.");
    }
  };

  if (loading) return <div style={{ color: 'white', textAlign: 'center', marginTop: '50px' }}>טוען קבצים...</div>;

  return (
    <div style={{ padding: '40px', direction: 'rtl', color: 'white', maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ color: '#60a5fa', marginBottom: '30px' }}>ארכיון הקבצים שלי</h1>

      {/* קבצים שהמשתמש יצר (Owned) */}
      <section style={{ marginBottom: '50px' }}>
        <h2 style={{ fontSize: '1.4rem', borderBottom: '2px solid #374151', paddingBottom: '10px' }}>קבצים שהטמנתי</h2>
        <div style={gridStyle}>
          {ownedFiles.length === 0 ? <p style={{ color: '#9ca3af' }}>עוד לא יצרת קבצים מוטמנים.</p> : ownedFiles.map(file => (
            <FileCard key={file.id} file={file} onDownload={downloadFile} />
          ))}
        </div>
      </section>

      {/* קבצים ששותפו איתי (Shared) */}
      <section>
        <h2 style={{ fontSize: '1.4rem', borderBottom: '2px solid #374151', paddingBottom: '10px' }}>קבצים ששותפו איתי</h2>
        <div style={gridStyle}>
          {sharedFiles.length === 0 ? <p style={{ color: '#9ca3af' }}>אין קבצים ששותפו איתך כרגע.</p> : sharedFiles.map(file => (
            <FileCard key={file.id} file={file} onDownload={downloadFile} />
          ))}
        </div>
      </section>
    </div>
  );
}

// קומפוננטה קטנה לכרטיס קובץ
const FileCard = ({ file, onDownload }) => (
  <div style={{ background: '#1f2937', padding: '20px', borderRadius: '12px', border: '1px solid #374151', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
    <div>
      <div style={{ fontSize: '1rem', fontWeight: 'bold', marginBottom: '8px', wordBreak: 'break-all' }}>{file.filename}</div>
      <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
        תאריך: {new Date(file.created_at).toLocaleDateString('he-IL')}
      </div>
    </div>
    <button 
      onClick={() => onDownload(file.id, file.filename)} 
      style={{ marginTop: '20px', padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', transition: '0.2s' }}
      onMouseOver={(e) => e.target.style.background = '#2563eb'}
      onMouseOut={(e) => e.target.style.background = '#3b82f6'}
    >
      הורדה מאובטחת
    </button>
  </div>
);

const gridStyle = { 
  display: 'grid', 
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
  gap: '25px', 
  marginTop: '20px' 
};

export default FilesPage;