"""
main.py
---------
Defines an entrypoint for running the Discord bot.
"""

from dotenv import load_dotenv

from chatbot.discord import start_bot


def main() -> None:
    """Runs the Discord bot."""
    load_dotenv()
    start_bot()


if __name__ == "__main__":
    main()
