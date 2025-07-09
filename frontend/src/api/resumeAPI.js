// src/api/resumeAPI.js
export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file); // key must match the backend: 'file'

  try {
    const response = await fetch("http://127.0.0.1:5000/upload_resume", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    return await response.json();
  } catch (error) {
    console.error("Error:", error);
    return { error: error.message };
  }
};
