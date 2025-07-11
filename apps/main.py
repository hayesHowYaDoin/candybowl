"""
main.py
---------
Defines an entrypoint for the example project.
"""

from dotenv import load_dotenv

from candybowl import discord


def main() -> None:
    """Runs the Discord bot."""
    load_dotenv()
    discord.start_bot()


if __name__ == "__main__":
    main()
