export default function NoteList({ items, onDelete }) {
  if (!items.length) {
    return <p className="empty-state">No notes yet. Create one to get started.</p>;
  }

  return (
    <ul className="note-list">
      {items.map((note) => (
        <li key={note.id}>
          <header>
            <h3>{note.title}</h3>
            <time dateTime={note.created_at}>
              {new Date(note.created_at).toLocaleString()}
            </time>
          </header>
          <p>{note.content}</p>
          <button type="button" onClick={() => onDelete(note.id)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
