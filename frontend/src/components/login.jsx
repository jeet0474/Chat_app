import React, { useState, useEffect } from "react";
import "./login.css";
import { useNavigate, Link } from "react-router-dom";
import { useUser } from "../UserContext";  // Import the useUser hook

const Login = () => {
  const [typedText, setTypedText] = useState(""); // State to store the animated text
  const [username, setUsername] = useState(""); // Username input
  const [password, setPassword] = useState(""); // Password input
  const [error, setError] = useState(""); // Error message
  const [loading, setLoading] = useState(false); // State to handle loading
  const titleText = "24hr"; // The text you want to animate
  const navigate = useNavigate(); // Navigation hook
  const { loginUser } = useUser();  // Get loginUser from context

  useEffect(() => {
    let index = 0;

    const typingInterval = setInterval(() => {
      setTypedText((prevText) =>
        index < titleText.length ? titleText.slice(0, index + 1) : ""
      );
      index = (index + 1) % (titleText.length + 1); // Reset index after typing completes
    }, 500);

    return () => clearInterval(typingInterval);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(""); // Clear any previous errors
    setLoading(true); // Start loading

    localStorage.clear(); // Clear all locally stored data

    try {
      const response = await fetch("http://127.0.0.1:8000/api/login_user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (response.ok) {
        // Login successful, store user data and token in context or local storage
        loginUser(data.user);  // Store the logged-in user in the context

        // Store the JWT token in localStorage for subsequent authenticated requests
        localStorage.setItem("token", data.token);

        // Redirect to chat page
        navigate("/chat");
      } else {
        setError(data.error || "Login failed. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setLoading(false); // Stop loading after the request is finished
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleLogin(e); // Trigger login when Enter is pressed
    }
  };

  return (
    <div className="login-wrapper">
      <h1 className="title">
        Chat For Next <span className="animated-text">{typedText}</span>
      </h1>
      <div className="login-box">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Name"
            className="login-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={handleKeyDown} // Listen for Enter key press
          />
          <input
            type="password"
            placeholder="Password"
            className="login-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown} // Listen for Enter key press
          />
          <button type="submit" className="login-button">
            {loading ? (
              <div className="loaderlogin"></div> // Display loader when loading is true
            ) : (
              "Let's Chat!" // Display button text when not loading
            )}
          </button>
        </form>
        {error && <div className="error-message">{error}</div>}
        <p className="register-text">
          <Link to="/newname" className="register-link">NOT Registered yet?</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
