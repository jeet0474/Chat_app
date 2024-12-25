import React, { useState } from 'react';

const Sidebar = ({ onSearchToggle, onLogout }) => {
  const [isSearchActive, setIsSearchActive] = useState(false);

  const handleSearchToggle = () => {
    setIsSearchActive(!isSearchActive);
    onSearchToggle();
  };

  const iconSize = "30px";

  return (
    <div className="sidebar">
      {/* Search Button at the Top */}
      <button onClick={handleSearchToggle} className="icon-button">
        {isSearchActive ? (
          <span className="icon cross">✖️</span>
        ) : (
          <span className="icon search">🔍</span>
        )}
      </button>

      {/* Spacer to push logout button to the bottom */}
      <div className="spacer"></div>

      {/* Logout Button at the Bottom */}
      <button onClick={onLogout} className="logout-button">
        <img src="/images/logout.png" alt="Logout" style={{ width: iconSize, height: iconSize }} />
      </button>
    </div>
  );
};

export default Sidebar;
