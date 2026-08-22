import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  // State management
  const [messages, setMessages] = useState([]);
  const [role, setRole] = useState("public");
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Auto-scroll to bottom of chat whenever messages update
  const messagesEndRef = useRef(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Chat functionality
  const handleSend = async (overrideMessage = null) => {
    // Determine the text to send (either from the button click or the input box)
    const textToSend = typeof overrideMessage === 'string' ? overrideMessage : inputText.trim();
    
    // Prevent sending empty messages or double-sending
    if (!textToSend || isLoading) return;
    
    // Add user message to UI immediately
    setMessages(prev => [...prev, { text: textToSend, sender: "user" }]);
    
    // Only clear input if we sent from the input box
    if (typeof overrideMessage !== 'string') {
      setInputText("");
    }
    setIsLoading(true);

    try {
      // Format the existing messages into the history array expected by the backend
      const history = messages
        .filter(m => m.sender !== "error")
        .map(m => ({
          role: m.sender === "ai" ? "assistant" : "user",
          content: m.text
        }));

      // Send request to backend
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: textToSend,
          role: role, // Send the current state of the toggle
          history: history // Send the conversation history!
        })
      });

      if (!response.ok) throw new Error(`HTTP error!`);

      // Parse response
      const data = await response.json();
      let answerText = data.answer;
      let suggestions = [];
      let sources = data.sources || [];

      // Intercept the hidden SUGGESTIONS string
      const suggestionsIndex = answerText.indexOf("SUGGESTIONS:");
      if (suggestionsIndex !== -1) {
        let suggestionsPart = answerText.slice(suggestionsIndex + "SUGGESTIONS:".length).trim();
        // Remove the SUGGESTIONS from the visible text
        answerText = answerText.slice(0, suggestionsIndex).trim();
        
        // Fallback: if the LLM forgot to use ||, split by question marks instead
        if (suggestionsPart.includes("||")) {
          suggestions = suggestionsPart.split("||");
        } else {
          // Split by ?, then re-append the ? to each part
          suggestions = suggestionsPart.split("?").map(s => s + "?");
        }
        
        // Clean up whitespace, remove leading numbers/Question labels, and filter empty strings
        suggestions = suggestions
          .map(s => s.trim().replace(/^(?:Question\s*\d+[:\-\.\?]*\s*|\d+[\.\)]\s*)/i, ''))
          .filter(s => s.length > 5 && !/^question\s*\d+\??$/i.test(s));
      }

      // Update UI with response
      setMessages(prev => [...prev, { text: answerText, sender: "ai", suggestions, sources }]);
    } catch (error) {
      console.error("Fetch error:", error);
      // Fallback UI error handling so the app doesn't crash
      setMessages(prev => [...prev, { text: "Error connecting to server. Is FastAPI running on port 8000?", sender: "error" }]);
    } finally {
      // Turn off loading indicator
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="chat-container">
      
      {/* HEADER & ROLE TOGGLE */}
      <div className="chat-header">
        <h1>Jugaad Robotics Club Assistant</h1>
        <div className="role-toggle">
          <button 
            className={`role-btn ${role === 'public' ? 'active' : ''}`}
            onClick={() => setRole("public")}
          >
            🌐 Public Visitor
          </button>
          <button 
            className={`role-btn ${role === 'member' ? 'active' : ''}`}
            onClick={() => setRole("member")}
          >
            🔒 Verified Member
          </button>
        </div>
      </div>

      {/* CHAT MESSAGES */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.sender === "ai" ? (
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            ) : (
              <p>{msg.text}</p>
            )}
            
            {/* AI Source Citations */}
            {msg.sender === "ai" && msg.sources && msg.sources.length > 0 && (
              <div className="sources-container">
                {msg.sources.map((src, i) => (
                  <span key={i} className="source-badge">
                    📄 Source: {src}
                  </span>
                ))}
              </div>
            )}
            
            {/* AI Suggestion Buttons */}
            {msg.sender === "ai" && msg.suggestions && msg.suggestions.length > 0 && (
              <div className="suggestions-container">
                {msg.suggestions.map((sug, i) => (
                  <button key={i} className="suggestion-btn" onClick={() => handleSend(sug)}>
                    {sug}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {/* LOADING DOTS */}
        {isLoading && (
          <div className="message ai">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* INPUT AREA */}
      <div className="chat-input-area">
        <input 
          type="text" 
          placeholder={`Ask a question as a ${role}...`}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !inputText.trim()}>
          ➤
        </button>
      </div>

    </div>
  );
}

export default App;
