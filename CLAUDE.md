# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses `just` (a command runner) for task automation. All commands should be run from the project root:

- `just install` - Install Python dependencies via Poetry
- `just analyze` - Run linting (ruff check/format) and type checking (mypy)
- `just test` - Run all unit tests with pytest
- `just pre-commit` - Run pre-commit hooks on all files
- `just run` - Run the main application (chatbot)
- `just run backend` - Run the backend Flask server specifically

The project uses Poetry for dependency management and requires Python 3.13+.

## Architecture Overview

This is a dual-application AI-powered candy bowl simulation with two main components:

### 1. Chatbot (`chatbot/`)
- **Entry point**: `chatbot/apps/main.py`
- **Discord bot** that responds to three slash commands:
  - `/request` - Users request items for the candy bowl
  - `/haggle` - Users negotiate prices for items
  - `/restock` - AI restocks the bowl based on accumulated notes
- **Commands module**: `chatbot/commands/` contains implementations for each slash command
- Uses Discord.py library and loads environment variables from `.env`

### 2. Backend (`backend/`)
- **Entry point**: `backend/apps/main.py` 
- **Flask web server** running on port 5000
- **Routes**: `backend/routes/` contains Flask app factory and chat endpoints
- **AI Integration**: Uses Google Gemini 2.5-flash model via `google-genai` library

### Core AI System (`backend/backend/ai/`)
- **Chat management**: `chat.py` creates specialized chat sessions for different interactions
- **Tools directory**: Contains AI function tools for:
  - `inventory.py` - Managing candy bowl inventory 
  - `notes.py` - Recording user interactions and preferences
  - `supplier.py` - Searching Amazon for products to stock
  - `bank.py` - Managing the virtual account balance ($100 starting balance)

### Data Storage
- `data/inventory.csv` - Stores current inventory state
- Notes and balance are managed through the AI tools system

## Key Configuration

- **Line length**: 80 characters (configured in pyproject.toml)
- **Type checking**: mypy with incomplete features enabled for new generic syntax
- **Environment**: Uses devenv/nix for development environment setup
- **AI Model**: Google Gemini 2.5-flash with function calling capabilities

## Running Applications

- The chatbot and backend are separate applications that can run independently
- Use `just run` for the Discord chatbot or `just run backend` for the Flask server
- Both applications require appropriate environment variables (Google API key for AI, Discord token for bot)