import os

import discord
from discord import app_commands

from candybowl.ai import create_chat, initialize_chat, send_message


_thread_chats = {}


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
async def candybowl(interaction: discord.Interaction):
    """Handles the /candybowl slash command to start a chat with the Gemini model."""
    if not isinstance(interaction.channel, discord.TextChannel):
        print("Command can only be used in text channels.")
        return

    print("Starting thread...")

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
        response = initialize_chat(_thread_chats[thread.id])

        await thread.send(response)

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    chat = _thread_chats.get(message.channel.id)
    if chat:
        print(
            f"Received message in thread {message.channel.id}: {message.content}"
        )
        response = send_message(chat, message.content)
        await message.channel.send(f"{response}")


def start_bot() -> None:
    """Starts the Discord bot."""
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        raise ValueError(
            "DISCORD_BOT_TOKEN is not set in the environment variables."
        )
    bot.run(discord_token)
