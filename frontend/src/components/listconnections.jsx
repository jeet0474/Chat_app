import React from "react";

const ListOfConnections = ({
  connections,
  onSelectConnection,
  selectedConnection,
  isSearching,
  searchQuery,
  isLoading, // New prop to indicate loading state
}) => {
  const filteredConnections = connections.filter((connection) =>
    (connection.name || connection.username).toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="connections">
      {isLoading ? (
        <div className="loaderconnections-container">
          <div className="loaderconnections"></div>
        </div>
      ) : filteredConnections.length > 0 ? (
        filteredConnections.map((connection) => (
          <div
            key={connection.connectionId}
            className={`connection ${
              selectedConnection === connection.connectionId ? "active" : ""
            }`}
            onClick={() => onSelectConnection(connection.connectionId)}
          >
            <img src={connection.image_link} alt={connection.name || connection.username} />
            <span>{connection.name || connection.username}</span>
          </div>
        ))
      ) : (
        <div className="no-connections">No connections found.</div>
      )}
    </div>
  );
};

export default ListOfConnections;
