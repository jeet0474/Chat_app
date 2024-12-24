import React from "react";
import { useNavigate } from "react-router-dom";
import "./confirm.css"; // Import the CSS file

const Confirmation = ({ message, onConfirm, onCancel }) => {
  const navigate = useNavigate();

  return (
    <div className="confirmation-wrapper">
      <div className="confirmation-box">
        <h2 className="confirmation-message">{message}</h2>
        {/* <h2 className="confirmation-message">"Do you want to logout ?"</h2> */}
        <div className="confirmation-buttons">
          <button onClick={onCancel} className="confirmation-button cancel-button">
            Cancel
          </button>
          <button onClick={onConfirm} className="confirmation-button confirm-button">
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

export default Confirmation;
