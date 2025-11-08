import { useState } from "react";

export default function NoteForm({ onSubmit, isSubmitting }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!title.trim() || !content.trim()) {
      return;
    }
    onSubmit({ title: title.trim(), content: content.trim() });
    setTitle("");
    setContent("");
  };

  return (
    <form className="note-form" onSubmit={handleSubmit}>
      <h2>Create a note</h2>
      <label htmlFor="note-title">Title</label>
      <input
        id="note-title"
        type="text"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        placeholder="Add a short title"
        required
      />
      <label htmlFor="note-content">Content</label>
      <textarea
        id="note-content"
        value={content}
        onChange={(event) => setContent(event.target.value)}
        placeholder="Write your note content"
        rows={4}
        required
      />
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Save note"}
      </button>
    </form>
  );
}
