import React, { createContext, useState, useContext, useEffect } from "react";

// Create a context for the user
const UserContext = createContext();

// Create a Provider component to wrap the app
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Store the logged-in user data

  useEffect(() => {
    // Check if the user data is available in localStorage on initial load
    const storedUser = localStorage.getItem("user");
    const storedToken = localStorage.getItem("token");

    if (storedUser && storedToken) {
      // If user and token are found in localStorage, set them in state
      setUser(JSON.parse(storedUser)); // Parse and set the user object
    }
  }, []);

  // Set the user when they log in
  const loginUser = (userData) => {
    setUser(userData);
    // Save user data and token to localStorage
    localStorage.setItem("user", JSON.stringify(userData)); // Store user object
    localStorage.setItem("token", userData.token); // Store token
  };

  // Clear the user when they log out
  const logoutUser = () => {
    setUser(null);
    localStorage.removeItem("user"); // Remove user data from localStorage
    localStorage.removeItem("token"); // Remove token from localStorage
  };

  return (
    <UserContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </UserContext.Provider>
  );
};

// Custom hook to access the user context data
export const useUser = () => {
  return useContext(UserContext); // Return the user context
};
