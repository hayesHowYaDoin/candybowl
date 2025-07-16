class NotesFile:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> str:
        """Returns the contents of the note file."""
        try:
            with open(self.file_path, "r") as file:
                return file.read()

        except FileNotFoundError:
            return "Note file not found."

    def append(self, content: str) -> None:
        """Appends content to the note file."""
        with open(self.file_path, "a") as file:
            file.write(content + "\n")

    def clear(self) -> None:
        """Clears the note file."""
        with open(self.file_path, "w") as file:
            file.write("")
