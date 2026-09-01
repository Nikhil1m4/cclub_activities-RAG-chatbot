import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [role, setRole] = useState('public');

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadRole, setUploadRole] = useState('public');
  const [uploadStatus, setUploadStatus] = useState('idle');

  const [isChatOpen, setIsChatOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (overrideMessage = null) => {
    const textToSend = typeof overrideMessage === 'string' ? overrideMessage : inputText.trim();
    if (!textToSend || isLoading) return;

    setMessages(prev => [...prev, { text: textToSend, sender: 'user' }]);
    if (typeof overrideMessage !== 'string') setInputText('');
    setIsLoading(true);

    try {
      const history = messages
        .filter(m => m.sender !== 'error')
        .map(m => ({
          role: m.sender === 'ai' ? 'assistant' : 'user',
          content: m.text,
        }));

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend, role, history }),
      });

      if (!response.ok) throw new Error('HTTP error!');

      const data = await response.json();
      let answerText = data.answer;
      let suggestions = [];
      let sources = data.sources || [];

      const suggestionsIndex = answerText.indexOf('SUGGESTIONS:');
      if (suggestionsIndex !== -1) {
        let suggestionsPart = answerText.slice(suggestionsIndex + 'SUGGESTIONS:'.length).trim();
        answerText = answerText.slice(0, suggestionsIndex).trim();

        if (suggestionsPart.includes('||')) {
          suggestions = suggestionsPart.split('||');
        } else {
          suggestions = suggestionsPart.split('?').map(s => s + '?');
        }

        suggestions = suggestions
          .map(s => s.trim().replace(/^(?:Question\s*\d+[:\-\.\?]*\s*|\d+[\.]\s*)/i, ''))
          .filter(s => s.length > 5 && !/^question\s*\d+\??$/i.test(s));
      }

      setMessages(prev => [...prev, { text: answerText, sender: 'ai', suggestions, sources }]);
    } catch (error) {
      console.error('Fetch error:', error);
      setMessages(prev => [
        ...prev,
        { text: 'Error connecting to server. Is FastAPI running on port 8000?', sender: 'error' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = e => {
    if (e.key === 'Enter') handleSend();
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploadStatus('uploading');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('role', uploadRole);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error(`Upload failed: ${response.status}`);

      setUploadStatus('success');
      setSelectedFile(null);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error');
    }
  };

  const handleLoginToggle = () => {
    if (role === 'public') {
      setRole('member');
    } else {
      setRole('public');
      setSelectedFile(null);
      setUploadStatus('idle');
    }
  };

  return (
    <div className="site-root">

      <nav className="site-nav">
        <div className="nav-wordmark">
          <span className="wordmark-primary">JUGAAD</span>
          <span className="wordmark-secondary">ROBOTICS</span>
        </div>

        <button
          className={`nav-login-btn ${role === 'member' ? 'logged-in' : ''}`}
          onClick={handleLoginToggle}
        >
          {role === 'member' ? '⬡ MEMBER SESSION' : 'LOG IN'}
        </button>
      </nav>

      <main className="site-main">

        <section className="hero">
          <div className="hero-content">
            <p className="hero-label">UIET Chandigarh // Student Technical Club</p>
            <h1 className="hero-headline">
              Build.<br />Break.<br />Iterate.
            </h1>
            <p className="hero-body">
              Jugaad Robotics is a student-run lab focused on embedded systems,
              autonomous robotics, and hands-on engineering. Ask our AI assistant
              anything about the club — or log in as a member to access internal docs.
            </p>
            {role === 'public' && (
              <p className="hero-hint">
                ↗ Log in (top right) to unlock member-only knowledge and document uploads.
              </p>
            )}
          </div>
        </section>

        {role === 'member' && (
          <section className="upload-section">
            <h2 className="upload-section-heading">Knowledge Base</h2>
            <p className="upload-section-sub">Upload PDFs to extend what the AI can answer. Tag each document with its access level before uploading.</p>

            <div className="upload-card">

              <div className="upload-group">
                <span className="upload-group-label">SELECT FILE</span>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  style={{ display: 'none' }}
                  onChange={e => {
                    setSelectedFile(e.target.files[0] || null);
                    setUploadStatus('idle');
                  }}
                />
                <button
                  className="file-trigger-btn"
                  onClick={() => fileInputRef.current.click()}
                >
                  {selectedFile ? `📄 ${selectedFile.name}` : '+ Choose PDF'}
                </button>
              </div>

              <div className="upload-divider" />

              <div className="upload-group">
                <span className="upload-group-label">ACCESS LEVEL</span>
                <div className="segment-toggle">
                  <button
                    className={`segment-option ${uploadRole === 'public' ? 'active' : ''}`}
                    onClick={() => setUploadRole('public')}
                  >
                    Public
                  </button>
                  <button
                    className={`segment-option ${uploadRole === 'member' ? 'active' : ''}`}
                    onClick={() => setUploadRole('member')}
                  >
                    Member Only
                  </button>
                </div>
              </div>

              <div className="upload-divider" />

              <div className="upload-group">
                <button
                  className="upload-submit-btn"
                  onClick={handleUpload}
                  disabled={!selectedFile || uploadStatus === 'uploading'}
                >
                  {uploadStatus === 'uploading' ? 'Indexing…' : 'Upload PDF'}
                </button>

                {uploadStatus === 'success' && (
                  <p className="upload-status success">✔ Indexed successfully.</p>
                )}
                {uploadStatus === 'error' && (
                  <p className="upload-status error">✖ Upload failed — is the backend running?</p>
                )}
              </div>

            </div>
          </section>
        )}

      </main>

      {isChatOpen && (
        <div className="chat-widget">

          <div className="chat-widget-header">
            <span className="chat-widget-title">
              {role === 'member' ? '⬡ MEMBER AI' : 'AI ASSISTANT'}
            </span>
            <button
              className="chat-widget-close"
              onClick={() => setIsChatOpen(false)}
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <p className="chat-empty-hint">
                Ask me anything about Jugaad Robotics Club.
              </p>
            )}
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                {msg.sender === 'ai' ? (
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                ) : (
                  <p>{msg.text}</p>
                )}

                {msg.sender === 'ai' && msg.sources && msg.sources.length > 0 && (
                  <div className="sources-container">
                    {msg.sources.map((src, i) => (
                      <span key={i} className="source-badge">
                        📄 {src}
                      </span>
                    ))}
                  </div>
                )}

                {msg.sender === 'ai' && msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="suggestions-container">
                    {msg.suggestions.map((sug, i) => (
                      <button
                        key={i}
                        className="suggestion-btn"
                        onClick={() => handleSend(sug)}
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="message ai">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              placeholder={`Ask as ${role}…`}
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            <button onClick={handleSend} disabled={isLoading || !inputText.trim()}>
              ➤
            </button>
          </div>
        </div>
      )}

      <button
        className={`chat-fab ${isChatOpen ? 'open' : ''}`}
        onClick={() => setIsChatOpen(prev => !prev)}
        aria-label="Toggle chat"
      >
        {isChatOpen ? '✕' : '💬'}
      </button>

    </div>
  );
}

export default App;
