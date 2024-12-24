import React, { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom"; // Import Router, Route, and Navigate for redirection
import { useUser } from "./UserContext";  // Import the custom useUser hook
import Background from "./components/background.jsx"; // Import the background component
import Login from "./components/login.jsx"; // Login page component
import NewName from "./components/newname.jsx"; // New name page component
import Home from "./home.jsx"; // Home page component
import Confirmation from "./components/confirm.jsx";
import "./App.css";

function App() {
  const { user } = useUser(); // Use the custom hook to get the user from UserContext

  return (
    <Router>
      <div>
        <Background />
        <Routes>
          <Route
            path="/"
            element={user ? <Navigate to="/chat" /> : <Login />} // Redirect logged-in users to /chat
          />
          <Route
            path="/newname"
            element={user ? <Navigate to="/chat" /> : <NewName />} // Redirect logged-in users to /chat
          />
          <Route
            path="/chat"
            element={user ? <Home /> : <Navigate to="/" />} // Redirect non-logged-in users to /login
          />
          <Route path="/confirm" element={<Confirmation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
