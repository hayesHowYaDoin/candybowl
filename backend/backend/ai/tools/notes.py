from loguru import logger

from backend.notes import NotesFile


_notes_txt = "data/notes.txt"


def get_notes() -> str:
    """Retrieves the current notes.

    Returns:
        A string containing the current notes.
    """
    logger.info("Retrieving current notes.")

    try:
        notes_file = NotesFile(_notes_txt)
        notes_content = notes_file.read()
        logger.info(f"Current notes: {notes_content}")
        return notes_content

    except Exception as ex:
        logger.error(f"Error retrieving notes: {ex}")
        return f"Error: {ex}"


def add_note(note: str) -> str:
    """Adds a new note.

    Args:
        note: The note to add.

    Returns:
        A message indicating success or failure.
    """
    logger.info(f"Adding new note: {note}")

    try:
        notes_file = NotesFile(_notes_txt)
        notes_file.append(note)
        logger.info("Note added successfully.")
        return "Note added successfully."
    except Exception as ex:
        logger.error(f"Error adding note: {ex}")
        return f"Error: {ex}"
