import React, { useState } from 'react';
import './App.css';


function App() {
  const [fileName, setFileName] = useState('');


  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) setFileName(file.name);
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
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
          />
          {fileName && <p className="file-name">Selected: {fileName}</p>}
          <button className="analyze-btn">Analyze Resume</button>
        </div>
      </main>


      <footer className="footer">
        <p>🚀 Built for Hackathon | © 2025 Resume Analyzer Team</p>
      </footer>
    </div>
  );
}


export default App;
