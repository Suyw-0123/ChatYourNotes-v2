"""Service layer for working with note entities."""

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Note


class NoteServiceError(Exception):
    """Base exception for note service failures."""


def list_notes() -> List[Note]:
    """Return all notes ordered by creation date descending."""
    return Note.query.order_by(Note.created_at.desc()).all()


def get_note(note_id: int) -> Optional[Note]:
    """Return a note by its identifier."""
    return Note.query.filter(Note.id == note_id).one_or_none()


def create_note(title: str, content: str) -> Note:
    """Persist a new note in the database."""
    note = Note(title=title, content=content)
    db.session.add(note)
    _commit_session()
    return note


def delete_note(note_id: int) -> bool:
    """Delete a note; return True when the note existed."""
    note = get_note(note_id)
    if note is None:
        return False
    db.session.delete(note)
    _commit_session()
    return True


def _commit_session() -> None:
    """Commit the current session and wrap exceptions."""
    try:
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise NoteServiceError("Failed to persist changes") from exc
