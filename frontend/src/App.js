import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setResult(null); // clear previous result
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/upload_resume', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Something went wrong' });
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <span className="nth-flower1"></span>
      <span className="nth-flower2"></span>
      <span className="nth-flower3"></span>
      <span className="nth-flower4"></span>
      <span className="nth-flower5"></span>
      <span className="nth-flower6"></span>

      <header className="app-header">
        <h1>📄 Resume Analyzer</h1>
        <p>Upload your resume and get instant analysis and suggestions</p>
      </header>

      <main className="upload-section">
        <div className="upload-card">
          <label htmlFor="resumeUpload" className="upload-label">
            <span>Click to upload your resume</span>
          </label>
          <input
            id="resumeUpload"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
          />
          {fileName && <p className="file-name">Selected: {fileName}</p>}
          <button className="analyze-btn" onClick={handleUpload} disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>
        </div>

        {result && (
          <div className="result-card">
            <h2>Analysis Result</h2>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>🚀 Built for Hackathon | © 2025 Resume Analyzer Team</p>
      </footer>
    </div>
  );
}

export default App;
