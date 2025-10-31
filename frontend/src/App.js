import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/userinfo')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }
        return response.json();
      })
      .then(data => {
        setUserData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="App">
        <div className="container">
          <h1>Loading...</h1>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="container">
          <h1>Error</h1>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="container">
        <h1>Hello, world!</h1>
        <div className="info">
          <strong>Your User Agent:</strong><br />
          {userData.userAgent}
        </div>
        <div className="info">
          <strong>Your IP Address:</strong><br />
          {userData.ipAddress}
        </div>
      </div>
    </div>
  );
}

export default App;
