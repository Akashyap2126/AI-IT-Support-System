import { useState } from "react";
import Dashboard from "./components/Dashboard";
import "./App.css";

function App() {
  const existingToken = localStorage.getItem("access_token");

  const [isLoggedIn, setIsLoggedIn] = useState(
    Boolean(existingToken)
  );

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.message || "Login failed");
        return;
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "refresh_token",
        data.refresh_token
      );

      localStorage.setItem(
        "user",
        JSON.stringify(data.user)
      );

      setIsLoggedIn(true);

    } catch (error) {
      setMessage(
        "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  if (isLoggedIn) {
    return <Dashboard />;
  }

  return (
    <div className="app">

      <div className="login-card">

        <div className="logo">
          🛡️
        </div>

        <h1>AI IT Support</h1>

        <p className="subtitle">
          Intelligent IT Support & Ticket Management
        </p>

        <form onSubmit={handleLogin}>

          <div className="form-group">

            <label>Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />

          </div>

          <div className="form-group">

            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />

          </div>

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign In"}
          </button>

        </form>

        {message && (
          <div className="message">
            {message}
          </div>
        )}

        <div className="security-info">
          🔐 Secure authentication
          <br />
          🤖 AI-powered ticket management
        </div>

      </div>

    </div>
  );
}

export default App;