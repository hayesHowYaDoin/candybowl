import os

import discord
from discord import app_commands

from candybowl.ai import send_message


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
    if not isinstance(interaction.channel, discord.TextChannel):
        print("Command can only be used in text channels.")
        return

    await interaction.response.defer()

    try:
        thread = await interaction.channel.create_thread(
            name=f"CandyBowl - {interaction.user.name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,  # Auto-archive after 60 minutes of inactivity
            message=await interaction.original_response(),
        )

        # Send the message to the Gemini model
        response = send_message(message)

        # Send the AI's response back to the Discord channel
        await thread.send(f"{response}")
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
