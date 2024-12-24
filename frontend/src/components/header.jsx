import React from "react";

const Header = ({ isSearching, searchQuery, setSearchQuery, handleSearch, user }) => {
  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch(); // Trigger search on Enter
    }
  };

  return (
    <div className="header">
      {isSearching ? (
        <div className="search-input">
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress} // Listen for Enter key
          />
          <button onClick={handleSearch}>Done</button> {/* Trigger search on click */}
        </div>
      ) : (
        <>
          <h1 className="titleheader">Chat_24hr</h1>
          <span className="username">{user?.username}</span>
        </>
      )}
    </div>
  );
};

export default Header;
