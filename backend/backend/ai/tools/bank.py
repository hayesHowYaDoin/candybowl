from loguru import logger

from backend.notes import NotesFile


_bank_txt = "data/bank.txt"


def get_account_balance() -> str:
    """Retrieves the current account balance.

    Returns:
        The current amount of money in the bank account in US dollars.
    """
    logger.info("Retrieving current account balance.")

    try:
        notes_file = NotesFile(_bank_txt)
        notes_content = notes_file.read()
        logger.info(f"Current account balance: {notes_content}")
        return notes_content

    except Exception as ex:
        logger.error(f"Error retrieving notes: {ex}")
        return f"Error: {ex}"
