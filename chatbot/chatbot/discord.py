import os
import requests

import discord
from discord import app_commands
from loguru import logger

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

_thread_chats = {}


class CandyBowlBot(discord.Client):
    """Discord bot for the candy bowl application."""

    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Slash commands synced!")


bot = CandyBowlBot()


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} and ready to receive commands!")


@bot.tree.command(
    name="request", description="Make a request for the candy bowl."
)
async def request(interaction: discord.Interaction) -> None:
    """Handles the /request slash command to start a chat with the Gemini model."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error(
            f"Command can only be used in text channels. Channel type: {type(interaction.channel)}"
        )
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

        response = requests.get(f"{API_BASE_URL}/chat/request")
        response.raise_for_status()

        chat_id = response.json().get("chat_id")
        if not chat_id:
            raise ValueError("Chat ID not found in response.")

        _thread_chats[thread.id] = chat_id

    except Exception as ex:
        await interaction.followup.send(f"An error occurred: {ex}")
        logger.error(f"Error in /candybowl command: {ex}")


@bot.tree.command(
    name="haggle", description="Haggle over prices in the candy bowl."
)
async def haggle(interaction: discord.Interaction) -> None:
    """Handles the /haggle slash command to start a haggling session with the Gemini model."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error(
            f"Command can only be used in text channels. Channel type: {type(interaction.channel)}"
        )
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

        response = requests.get(f"{API_BASE_URL}/chat/haggle")
        response.raise_for_status()

        chat_id = response.json().get("chat_id")
        if not chat_id:
            raise ValueError("Chat ID not found in response.")

        _thread_chats[thread.id] = chat_id

    except Exception as ex:
        await interaction.followup.send(f"An error occurred: {ex}")
        logger.error(f"Error in /haggle command: {ex}")


@bot.tree.command(
    name="restock",
    description="Restock the candy bowl based on current market sentiment.",
)
async def restock(interaction: discord.Interaction) -> None:
    """Handles the /restock slash command to prompt the model to restock the candy bowl."""
    if not isinstance(interaction.channel, discord.TextChannel):
        logger.error(
            f"Command can only be used in text channels. Channel type: {type(interaction.channel)}"
        )
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

        response = requests.get(f"{API_BASE_URL}/chat/restock")
        response.raise_for_status()
        response = response.json()

        chat_id = response.get("chat_id")
        if not chat_id:
            raise ValueError("Chat ID not found in response.")

        response = response.get("response")
        if not response:
            raise ValueError("Response from the model is empty.")

        _thread_chats[thread.id] = chat_id

        logger.info(f"Response from Gemini model: {response}")
        for i in range(0, len(response), 2000):
            await thread.send(response[i : i + 2000])

    except Exception as ex:
        await interaction.followup.send(f"An error occurred: {ex}")
        logger.error(f"Error in /restock command: {ex}")


@bot.event
async def on_message(message: discord.Message) -> None:
    """Handles incoming messages in threads and sends them to the Gemini model."""
    logger.info(
        f"Received message: {message.content} from {message.author.name}"
    )

    if len(message.content) == 0 or message.author == bot.user:
        return

    chat_id = _thread_chats.get(message.channel.id)
    if chat_id:
        logger.info(
            f"Received message in thread {message.channel.id}: {message.content}"
        )

        data = {
            "chat_id": chat_id,
            "message": f"{message.author.name}: {message.content}"[:2000],
        }
        response = requests.post(f"{API_BASE_URL}/chat/message", json=data)

        logger.info(f"Response from Gemini model: {response}")
        await message.channel.send(f"{response}")


def start_bot() -> None:
    """Starts the Discord bot."""
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        raise ValueError(
            "DISCORD_BOT_TOKEN is not set in the environment variables."
        )
    bot.run(discord_token)
