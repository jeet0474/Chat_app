import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import "./login.css"; // Import the same login CSS

const NewName = () => {
  const [typedText, setTypedText] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [loading, setLoading] = useState(false); // Loading state

  const titleText = "24hr";
  const passwordRegex = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;

  const navigate = useNavigate(); // Use the navigate hook to redirect

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);

    if (!passwordRegex.test(newPassword)) {
      setErrorMessage(
        "Password must be at least 8 characters long, contain at least one alphabet, one number, and one special character."
      );
    } else {
      setErrorMessage("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    // Clear any previous messages
    setErrorMessage("");
    setSuccessMessage("");
  
    setLoading(true); // Set loading state to true
  
    // Check if passwords match and fields are filled
    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      setLoading(false); // Set loading to false on error
      return;
    }
  
    if (!name || !password) {
      setErrorMessage("All fields are required.");
      setLoading(false); // Set loading to false on error
      return;
    }
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/create_user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: name, password: password }),
      });
  
      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(data.message); // Use backend success message dynamically
  
        // Redirect to login page after successful account creation
        setTimeout(() => {
          navigate("/"); // Redirect to the login page
        }, 1000); // Delay redirect by 1 second to let the success message show
  
        // Clear form fields
        setName("");
        setPassword("");
        setConfirmPassword("");
      } else if (response.status === 409) {
        const data = await response.json();
        setErrorMessage(data.error || "Username already in use.");
      } else {
        const data = await response.json();
        setErrorMessage(data.error || "Failed to create account.");
      }
    } catch (error) {
      setErrorMessage("An error occurred. Please try again.");
    } finally {
      setLoading(false); // Set loading to false after the request is completed
    }
  };
  

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSubmit(e); // Trigger submit on Enter key press
    }
  };

  useEffect(() => {
    let index = 0;
    const typingInterval = setInterval(() => {
      setTypedText((prevText) =>
        index < titleText.length ? titleText.slice(0, index + 1) : ""
      );
      index = (index + 1) % (titleText.length + 1);
    }, 500);

    return () => clearInterval(typingInterval);
  }, []);

  return (
    <div className="login-wrapper">
      <h1 className="title">
        Chat For Next <span className="animated-text">{typedText}</span>
      </h1>
      <div className="login-box">
        <h2>Create New Account</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Name"
            className="login-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={handleKeyDown} // Listen for Enter key press on this input
          />
          <input
            type="password"
            placeholder="New Password"
            className="login-input"
            value={password}
            onChange={handlePasswordChange}
            onKeyDown={handleKeyDown} // Listen for Enter key press on this input
          />
          <input
            type="password"
            placeholder="Confirm Password"
            className="login-input"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            onKeyDown={handleKeyDown} // Listen for Enter key press on this input
          />
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? (
              <div className="loaderlogin"></div>
            ) : (
              "Let's Chat!"
            )}
          </button>
        </form>
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        {successMessage && <p className="success-message">{successMessage}</p>}
      </div>
    </div>
  );
};

export default NewName;
