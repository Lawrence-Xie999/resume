// FileUpload.js
import React, { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5001/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setMessage("Upload successful: " + data.filename);
      } else {
        setMessage("Error: " + data.error);
      }
    } catch (err) {
      setMessage("Upload failed.");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept=".pdf,.docx" onChange={handleChange} />
      <button type="submit">Upload</button>
      <div>{message}</div>
    </form>
  );
}

export default FileUpload;