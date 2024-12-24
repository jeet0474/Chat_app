import React, { useState } from 'react';

const Sidebar = ({ onDeleteProfile, onSearchToggle, onLogout }) => {
  const [isSearchActive, setIsSearchActive] = useState(false); // State to toggle between search and cross icon

  const handleSearchToggle = () => {
    setIsSearchActive(!isSearchActive); // Toggle between search and cross icons
    onSearchToggle(); // Call the onSearchToggle prop to trigger actions in the parent
  };

  const iconSize = "30px";

  return (
    <div className="sidebar">
      {/* Search Button */}
      <button onClick={handleSearchToggle} className="icon-button">
        {isSearchActive ? (
          <span className="icon cross">✖️</span> // Cross icon
        ) : (
          <span className="icon search">🔍</span> // Search icon
        )}
      </button>

      {/* Delete Profile Button */}
      <button onClick={onDeleteProfile}>🗑️</button>

      {/* Logout Button */}
      <button onClick={onLogout}>
        <img src="/images/logout.png" alt="Logout" style={{ width: iconSize, height: iconSize }} />
      </button>
    </div>
  );
};

export default Sidebar;
