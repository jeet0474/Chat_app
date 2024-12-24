import React, { useState, useEffect } from "react";
import "./components/home.css";
import Sidebar from "./components/sidebar.jsx";
import Header from "./components/header.jsx";
import ListOfConnections from "./components/listconnections.jsx";
import ChatWindow from "./components/chatwindow.jsx";
import { useUser } from "./UserContext"; // Import useUser hook
import Confirmation from "./components/confirm.jsx"; // Import the confirmation component
import { useNavigate } from "react-router-dom"; // You forgot to import useNavigate here

const Home = () => {
  const { user, logoutUser } = useUser(); // Access user data from context
  const navigate = useNavigate(); // Add this to use navigate

  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [connections, setConnections] = useState(() => {
    const storedConnections = localStorage.getItem("connections");
    return storedConnections ? JSON.parse(storedConnections) : [];
  });
  const [searchResults, setSearchResults] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [isConfirmingLogout, setIsConfirmingLogout] = useState(false); // State to control logout confirmation
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      if (!localStorage.getItem("connections")) {
        fetchUserConnections();
      }
    }
  }, [user]);

  const fetchUserConnections = async () => {
    setIsLoading(true); // Show loader
    try {
      const response = await fetch(
        // `http://127.0.0.1:8000/api/get_user_connections/?username=${encodeURIComponent(user.username)}`
        `https://chat-app-42rc.onrender.com/api/get_user_connections/?username=${encodeURIComponent(user.username)}`
      );
      const data = await response.json();
      if (data.connections) {
        setConnections(data.connections);
        localStorage.setItem("connections", JSON.stringify(data.connections));
      } else {
        setConnections([]);
      }
    } catch (error) {
      console.error("Error fetching user connections:", error);
    } finally {
      setIsLoading(false); // Hide loader
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setConnections([]); // Reset to empty
      fetchUserConnections(); // Reload connections
      return;
    }

    setIsLoading(true); // Show loader during search
    try {
      const response = await fetch(
        // `http://127.0.0.1:8000/api/search_users/?query=${encodeURIComponent(searchQuery)}&current_user_id=${encodeURIComponent(user._id)}`
        `https://chat-app-42rc.onrender.com/api/search_users/?query=${encodeURIComponent(searchQuery)}&current_user_id=${encodeURIComponent(user._id)}`
      );
      const data = await response.json();
      const formattedResults = formatConnections(data);
      setConnections(formattedResults);
    } catch (error) {
      console.error("Error fetching connections:", error);
    } finally {
      setIsLoading(false); // Hide loader
    }
  };

  const formatConnections = (connections) => {
    return connections.map((connection) => ({
      connectionId: connection.id,
      name: connection.name || connection.username,
      image_link: connection.image_link,
    }));
  };

  const handleDeleteProfile = () => {
    setConnections([]);
    setSelectedConnection(null);
    localStorage.removeItem("connections");
  };

  const handleSearchToggle = () => {
    setIsSearching(!isSearching);
    setSearchQuery("");
    fetchUserConnections();
  };

  const handleSelectConnection = (connectionId) => {
    const connection = connections.find((c) => c.connectionId === connectionId);
    setSelectedConnection({
      connectionId: connection.connectionId,
      connectionName: connection.name || connection.username,
      image_link: connection.image_link,
    });
  };

  // Logic for logout
  const handleLogout = () => {
    setIsConfirmingLogout(true); // Show confirmation dialog
  };

  // Logic for confirming logout
  const confirmLogout = async () => {
    try {
      setSelectedConnection(null);
      // Proceed with clearing local storage and navigating to login
      localStorage.clear(); // Clear local storage
      logoutUser(); // Reset user context
      navigate("/", { replace: true }); // Navigate to the login screen
    } catch (error) {
      console.error("Error during logout:", error);
    } finally {
      setIsConfirmingLogout(false); // Hide confirmation dialog
    }
  };

  // Logic for canceling logout
  const cancelLogout = () => {
    setIsConfirmingLogout(false); // Close the confirmation dialog without logging out
  };

  const reloadConnections = () => {
    fetchUserConnections(); // This function will be passed to ChatWindow to reload connections
  };

  return (
    <div className="app">
      {/* Confirmation Dialog */}
      {isConfirmingLogout && (
        <Confirmation
          message="Do you want to logout?"
          onConfirm={confirmLogout}
          onCancel={cancelLogout}
        />
      )}
      
      <Sidebar
        onDeleteProfile={handleDeleteProfile}
        onSearchToggle={handleSearchToggle}
        onLogout={handleLogout} // Pass the logout function to Sidebar
      />
      <div className="main">
        <Header
          isSearching={isSearching}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          handleSearch={handleSearch}
          user={user}
        />
        <div className="content">
          <ListOfConnections
            searchQuery={searchQuery}
            isSearching={isSearching}
            connections={connections}
            onSelectConnection={(connectionId) =>
              handleSelectConnection(connectionId)
            }
            selectedConnection={selectedConnection?.connectionId}
            isLoading={isLoading}
          />
          <ChatWindow
            selectedConnection={selectedConnection}
            user={user} // Pass logged-in user details to the chat window
            reloadConnections={reloadConnections}
          />
        </div>
      </div>
    </div>
  );
};

export default Home;
