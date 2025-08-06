import { useState } from 'react';
import './App.css';
import { keywords } from './keywords';

function App() {
  const [userInput, setUserInput] = useState('');
  const [dialogue, setDialogue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const MAX_LENGTH = 50;

  

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setIsLoading(true);
    setDialogue(''); // Clear previous dialogue

    try {
      const response = await fetch('http://localhost:5000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setDialogue(data.dialogue);
    } catch (error) {
      console.error('Error fetching dialogue:', error);
      setDialogue('Error: Could not generate dialogue. Check the backend.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    const newValue = value.slice(0, MAX_LENGTH); 
    setUserInput(newValue);
    
    // Filter suggestions based on user input
    if (newValue.length > 0) {
      const filtered = keywords.filter(
        (keyword) => keyword.toLowerCase().startsWith(value.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 3)); // Show top 5 suggestions
    } else {
      setSuggestions([]); // Clear suggestions if input is empty
    }
  };

  const handleSuggestionClick = (keyword) => {
    setUserInput(keyword.slice(0, MAX_LENGTH));
    setSuggestions([]); // Clear suggestions after selection
  };

  return (
    <div className="container">
      <div className='center-box'>
        <h2>The Nihilist's Kernel</h2>
        <form onSubmit={handleSubmit}>
            <div className='input-container'>
                <input
                    type="text"
                    value={userInput}
                    onChange={handleInputChange}
                    placeholder="Choose a keyword..."
                    maxLength={MAX_LENGTH}
                    disabled={isLoading}
                />
                <div className="char-count">
                    {userInput.length} / {MAX_LENGTH}
                </div>
                {suggestions.length > 0 && (
                    <ul className="suggestions-list">
                        {suggestions.map((keyword) => (
                            <li key={keyword} onClick={() => handleSuggestionClick(keyword)}>
                                {keyword}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
            <button type="submit" disabled={isLoading}>
                {isLoading ? 'Generating...' : 'Start Coversation'}
            </button>
        </form>

        {/* Clickable keywords below the input field */}
        <div className="keyword-buttons-container">
            {['API', 'Kernel', 'Bash', 'Database', 'LLM', 'OOPS', 'Compiler', 'Server', 'OS'].map((keyword) => ( // Display a subset of keywords to try
            <button 
                key={`try-${keyword}`} 
                onClick={() => handleSuggestionClick(keyword)}
                className="keyword-button"
            >
                {keyword}
            </button>
            ))}
        </div>
        {dialogue && (
            <div className="dialogue-box">
                {dialogue.split('\n').map((line, index) => {
                    // Simple check to identify character names
                    const isMarty = line.startsWith('Marty:');
                    const isRust = line.startsWith('Rust:');
                    
                    let lineContent = line;
                    if (isMarty) {
                        lineContent = <span className="marty-line">{line}</span>;
                    } else if (isRust) {
                        lineContent = <span className="rust-line">{line}</span>;
                    }

                    return <p key={index}>{lineContent}</p>;
                })}
            </div>
        )}
      </div>
    </div>
  );
}

export default App;