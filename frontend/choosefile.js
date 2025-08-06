import React, { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);

  const handleChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    // send formData to backend...
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" onChange={handleChange} accept=".pdf,.docx,.txt" />
      <button type="submit">Upload</button>
    </form>
  );
}

export default FileUpload;