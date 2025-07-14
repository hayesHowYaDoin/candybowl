import os

import discord
from discord import app_commands
from loguru import logger

from candybowl.ai.chat import create_chat, send_message


_thread_chats = {}


class CandyBowlBot(discord.Client):
    """Discord bot for the candy bowl application."""

    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Slash commands synced!")


_bot = CandyBowlBot()


@_bot.event
async def on_ready():
    logger.info(f"Logged in as {_bot.user} and ready to receive commands!")


@_bot.tree.command(name="candybowl", description="Chat with the Gemini model.")
async def candybowl(interaction: discord.Interaction):
    """Handles the /candybowl slash command to start a chat with the Gemini model."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error("Command can only be used in text channels.")
        return

    logger.info("Starting thread...")

    await interaction.response.defer()

    try:
        user_message = await interaction.followup.send(
            f"Hello, {interaction.user.name}! What can I do for you?"
        )

        thread = await interaction.channel.create_thread(
            name=f"CandyBowl - {interaction.user.name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,  # Auto-archive after 60 minutes of inactivity
            message=user_message,
        )

        _thread_chats[thread.id] = create_chat()

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")


@_bot.event
async def on_message(message: discord.Message):
    if len(message.content) == 0 or message.author == _bot.user:
        return

    chat = _thread_chats.get(message.channel.id)
    if chat:
        logger.info(
            f"Received message in thread {message.channel.id}: {message.content}"
        )
        response = send_message(chat, message.content[:2000])
        logger.info(f"Response from Gemini model: {response}")
        await message.channel.send(f"{response}")


def start_bot() -> None:
    """Starts the Discord bot."""
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        raise ValueError(
            "DISCORD_BOT_TOKEN is not set in the environment variables."
        )
    _bot.run(discord_token)
