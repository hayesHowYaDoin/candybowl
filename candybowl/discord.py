import os

import discord
from discord import app_commands
from loguru import logger

from candybowl.ai.chat import (
    haggle_chat,
    restock_chat,
    request_chat,
    send_message,
)


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


@_bot.tree.command(
    name="request", description="Make a request for the candy bowl."
)
async def request(interaction: discord.Interaction) -> None:
    """Handles the /request slash command to start a chat with the Gemini model."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error("Command can only be used in text channels.")
        return

    logger.info("Starting thread...")

    await interaction.response.defer()

    try:
        intial_message = await interaction.followup.send(
            f"Hello, {interaction.user.name}! What can I do for you?"
        )

        thread = await interaction.channel.create_thread(
            name=f"CandyBowl - {interaction.user.name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,  # Auto-archive after 60 minutes of inactivity
            message=intial_message,
        )

        _thread_chats[thread.id] = request_chat()

    except Exception as ex:
        await interaction.followup.send(f"An error occurred: {ex}")
        logger.error(f"Error in /candybowl command: {ex}")


@_bot.tree.command(
    name="haggle", description="Haggle over prices in the candy bowl."
)
async def haggle(interaction: discord.Interaction) -> None:
    """Handles the /haggle slash command to start a haggling session with the Gemini model."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error("Command can only be used in text channels.")
        return

    logger.info("Starting haggling thread...")

    await interaction.response.defer()

    try:
        intial_message = await interaction.followup.send(
            f"Come on, {interaction.user.name}! You're breaking my heart over here! I got six kids and a Subaru to feed!"
        )

        thread = await interaction.channel.create_thread(
            name="CandyBowl - Haggle",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,  # Auto-archive after 60 minutes of inactivity
            message=intial_message,
        )

        chat = haggle_chat()
        _thread_chats[thread.id] = chat

    except Exception as ex:
        await interaction.followup.send(f"An error occurred: {ex}")
        logger.error(f"Error in /haggle command: {ex}")


@_bot.tree.command(
    name="restock",
    description="Restock the candy bowl based on current market sentiment.",
)
async def restock(interaction: discord.Interaction) -> None:
    """Handles the /restock slash command to prompt the model to restock the candy bowl."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error("Command can only be used in text channels.")
        return

    logger.info("Restocking candy bowl...")
    await interaction.response.defer()

    try:
        intial_message = await interaction.followup.send(
            "Okay! Let me think on what I've learned..."
        )

        thread = await interaction.channel.create_thread(
            name="CandyBowl - Restock",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,  # Auto-archive after 60 minutes of inactivity
            message=intial_message,
        )

        chat, response = restock_chat()
        _thread_chats[thread.id] = chat

        logger.info(f"Response from Gemini model: {response}")
        for i in range(0, len(response), 2000):
            await thread.send(response[i : i + 2000])

    except Exception as ex:
        await interaction.followup.send(f"An error occurred: {ex}")
        logger.error(f"Error in /restock command: {ex}")


@_bot.event
async def on_message(message: discord.Message):
    """Handles incoming messages in threads and sends them to the Gemini model."""
    logger.info(
        f"Received message: {message.content} from {message.author.name}"
    )

    if len(message.content) == 0 or message.author == _bot.user:
        return

    chat = _thread_chats.get(message.channel.id)
    if chat:
        logger.info(
            f"Received message in thread {message.channel.id}: {message.content}"
        )

        response = send_message(
            chat, message.author.name + ": " + message.content[:2000]
        )
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
