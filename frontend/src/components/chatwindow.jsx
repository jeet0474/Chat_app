import React, { useEffect, useState, useRef } from "react";

const ChatWindow = ({ selectedConnection, user, reloadConnections }) => {
  const [newMessage, setNewMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [typedText, setTypedText] = useState("");
  const [webSocket, setWebSocket] = useState(null);
  const [loadingMessages, setLoadingMessages] = useState(true); // To track loading state for messages
  const [sendingMessage, setSendingMessage] = useState(false); // To track sending state for messages
  const messagesEndRef = useRef(null);
  const pingIntervalRef = useRef(null);

  const titleText = "WELCOME!!";

  useEffect(() => {
    let index = 0;
    const typingInterval = setInterval(() => {
      setTypedText((prevText) =>
        index < titleText.length ? titleText.slice(0, index + 1) : ""
      );
      index = (index + 1) % (titleText.length + 1);
    }, 300);

    return () => clearInterval(typingInterval);
  }, []);

  useEffect(() => {
    if (!selectedConnection || !user) return;

    let ws;

    const initializeWebSocket = async () => {
      try {
        const wsUrl = `ws://localhost:8000/ws/chat/?user_id=${user._id}&other_user_id=${selectedConnection.connectionId}`;
        console.log("Connecting to WebSocket:", wsUrl);

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log("WebSocket connected");

          pingIntervalRef.current = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: "ping" }));
              console.log("Ping sent");
            }
          }, 30000);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          if (data.type === "old_messages") {
            console.log("Old messages received:", data.messages);
            setMessages(data.messages || []);
            setLoadingMessages(false); // Stop loading when messages are received
          } else if (data.type === "new_message") {
            console.log("New message received:", data.message);
            setMessages((prev) => [...prev, data.message]);
          } else if (data.type === "pong") {
            console.log("Pong received");
          }
        };

        ws.onerror = (error) => console.error("WebSocket error:", error);

        ws.onclose = () => {
          console.log("WebSocket disconnected");
          clearInterval(pingIntervalRef.current);
          if (!selectedConnection) reloadConnections();
        };

        setWebSocket(ws);
      } catch (error) {
        console.error("WebSocket initialization error:", error);
      }
    };

    initializeWebSocket();

    return () => {
      if (ws) {
        ws.close();
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [selectedConnection, user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!newMessage.trim()) return;

    const message = {
      type: "new_message",
      message: newMessage,
    };

    if (webSocket && webSocket.readyState === WebSocket.OPEN) {
      setSendingMessage(true); // Show sending loader
      webSocket.send(JSON.stringify(message));
      setNewMessage("");

      setTimeout(() => {
        setSendingMessage(false); // Hide sending loader
      }, 550);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-window">
      {selectedConnection ? (
        <>
          <div className="chat-header">
            <img
              src={selectedConnection.image_link || "https://via.placeholder.com/50"}
              alt={selectedConnection.connectionName}
              className="chat-header-image"
            />
            <h2>{selectedConnection.connectionName || "Unnamed Connection"}</h2>
          </div>
          <div className="chat-messages">
            {loadingMessages ? (
              <div className="loaderMessage">Loading messages...</div> // Loader for fetching messages
            ) : messages.length > 0 ? (
              messages.map((chat, index) => (
                <div
                  key={index}
                  className={`chat-message ${
                    chat.senderId === user._id ? "sent" : "received"
                  }`}
                >
                  {chat.message}
                </div>
              ))
            ) : (
              <div className="no-messages">No messages yet. Start chatting...</div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="chat-input">
            <input
              type="text"
              placeholder="Type a message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={handleKeyPress}
            />
            <button onClick={handleSend}>
              {sendingMessage ? (
                <div className="loaderSend"></div> // Loader for sending message
              ) : (
                "Send"
              )}
            </button>
          </div>
        </>
      ) : (
        <div className="welcome-message">
          <span className="animated-text">{typedText}</span>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
