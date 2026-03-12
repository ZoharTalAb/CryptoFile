import React, { useState } from 'react';
import api from '../api/axios';

function StegoPage() {
  const [activeTab, setActiveTab] = useState('embed');
  const [file, setFile] = useState(null);
  const [secretData, setSecretData] = useState('');
  const [stegoType, setStegoType] = useState('image');
  const [loading, setLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState('');

  const handleAction = async (e) => {
    e.preventDefault();
    alert("הקוד התחיל לרוץ!");
    if (!file) return alert("נא לבחור קובץ");

    const formData = new FormData();
    formData.append('file', file);
    formData.append('stego_type', stegoType);
    
    setLoading(true);
    setResultMessage('');

    try {
      if (activeTab === 'embed') {
        formData.append('secret_data', secretData);
        const res = await api.post('/stego/embed', formData);
        setResultMessage(`הסוד הוטמן בהצלחה! הקובץ נשמר כ: ${res.data.filename}`);
      } else {
        const res = await api.post('/stego/extract', formData);
        setResultMessage(`הסוד שחולץ: ${res.data.extracted_message}`);
      }
    } catch (err) {
      setResultMessage(`שגיאה: ${err.response?.data?.detail || 'הפעולה נכשלה'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', direction: 'rtl', color: 'white', maxWidth: '700px', margin: '0 auto' }}>
      <div style={{ display: 'flex', marginBottom: '20px', borderBottom: '2px solid #374151' }}>
        <button onClick={() => setActiveTab('embed')} style={tabStyle(activeTab === 'embed')}>הטמנת סוד</button>
        <button onClick={() => setActiveTab('extract')} style={tabStyle(activeTab === 'extract')}>חילוץ סוד</button>
      </div>

      <form onSubmit={handleAction} style={{ background: '#1f2937', padding: '30px', borderRadius: '15px', border: '1px solid #374151' }}>
        <h2 style={{ color: '#60a5fa', marginBottom: '20px' }}>{activeTab === 'embed' ? 'החבאת הודעה בקובץ' : 'חילוץ הודעה מקובץ'}</h2>
        
        <div style={{ marginBottom: '15px' }}>
          <label>סוג המדיה:</label>
          <select value={stegoType} onChange={(e) => setStegoType(e.target.value)} style={inputStyle}>
            <option value="image">תמונה (Image)</option>
            <option value="audio">אודיו (Audio)</option>
            <option value="text">טקסט (Text)</option>
            <option value="video">וידאו (Video)</option>
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>בחרי קובץ:</label>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} style={{ ...inputStyle, background: 'transparent' }} />
        </div>

        {activeTab === 'embed' && (
          <div style={{ marginBottom: '15px' }}>
            <label>ההודעה הסודית:</label>
            <textarea value={secretData} onChange={(e) => setSecretData(e.target.value)} style={{ ...inputStyle, height: '80px' }} placeholder="מה את רוצה להחביא?" />
          </div>
        )}

        <button type="submit" disabled={loading} style={buttonStyle}>
          {loading ? 'מעבד...' : activeTab === 'embed' ? 'בצע הטמנה' : 'חלץ סוד'}
        </button>

        {resultMessage && (
          <div style={{ marginTop: '20px', padding: '15px', background: '#374151', borderRadius: '8px', textAlign: 'center', border: '1px solid #60a5fa' }}>
            {resultMessage}
          </div>
        )}
      </form>
    </div>
  );
}

// עיצובים קטנים כדי שהקוד יהיה מלא
const tabStyle = (active) => ({
  padding: '10px 20px', cursor: 'pointer', background: active ? '#3b82f6' : 'transparent',
  border: 'none', color: 'white', fontWeight: 'bold', borderRadius: '8px 8px 0 0', transition: '0.3s'
});
const inputStyle = { width: '100%', padding: '10px', marginTop: '10px', borderRadius: '6px', background: '#374151', color: 'white', border: '1px solid #4b5563' };
const buttonStyle = { width: '100%', padding: '12px', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' };

export default StegoPage;