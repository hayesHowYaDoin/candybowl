import os

import discord
from discord import app_commands

from candybowl.ai import get_client


class CandyBowlBot(discord.Client):
    """Discord bot for the candy bowl application."""

    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced!")


bot = CandyBowlBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} and ready to receive commands!")


@bot.tree.command(name="candybowl", description="Chat with the Gemini model.")
async def candybowl(interaction: discord.Interaction, message: str):
    """Handles the /candybowl slash command to chat with the Gemini model."""
    await interaction.response.defer()
    try:
        # Send the message to the Gemini model
        response = get_client().models.generate_content(
            model="gemini-2.5-flash", contents=message
        )
        # Send the AI's response back to the Discord channel
        await interaction.followup.send(
            f"**You:** {message}\n**AI:** {response.text}"
        )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")


def start_bot() -> None:
    """Starts the Discord bot."""
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        raise ValueError(
            "DISCORD_BOT_TOKEN is not set in the environment variables."
        )
    bot.run(discord_token)
