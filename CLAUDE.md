# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses `just` (a command runner) for task automation. All commands should be run from the project root:

- `just install` - Install Python dependencies via Poetry and frontend npm packages
- `just analyze` - Run linting (ruff check/format) and type checking (mypy)
- `just test` - Run all unit tests with pytest
- `just pre-commit` - Run pre-commit hooks on all files
- `just run` - Run the main application (chatbot)
- `just run backend` - Run the backend Flask server specifically
- `just run frontend` - Run the React frontend development server

The project uses Poetry for Python dependency management and npm for frontend dependencies. Requires Python 3.13+.

## Architecture Overview

This is a three-component AI-powered candy bowl simulation with web interface:

### 1. Frontend (`frontend/`)
- **Entry point**: `frontend/src/main.tsx`
- **React application** built with TypeScript and Vite
- **UI Framework**: Mantine UI components with dark/light mode support
- **Key Features**:
  - JWT-based authentication system
  - User registration and login
  - Admin and regular user roles
  - Interactive chat interfaces for request, haggle, and restock operations
  - Real-time inventory viewing and management
- **Pages**: Located in `frontend/src/pages/`
  - `AuthPage.tsx` - Login/registration
  - `InventoryPage.tsx` - View candy bowl inventory
  - `RequestChatPage.tsx` - Request items via AI chat
  - `HaggleChatPage.tsx` - Negotiate prices via AI chat
  - `RestockChatPage.tsx` - Admin-only AI restocking interface
  - `AdminInventoryPage.tsx` - Admin inventory management

### 2. Backend (`backend/`)
- **Entry point**: `backend/apps/main.py` 
- **Flask web server** running on port 5000 with CORS enabled
- **Routes**: Located in `backend/backend/routes/`
  - `app.py` - Flask app factory and blueprint registration
  - `auth.py` - JWT authentication endpoints
  - `chat.py` - AI chat endpoints for different interaction types
  - `inventory.py` - Inventory management endpoints
- **Authentication**: JWT-based auth system in `backend/backend/auth/`
- **AI Integration**: Uses Google Gemini 2.5-flash model via `google-genai` library

### 3. Chatbot (`chatbot/`)
- **Entry point**: `chatbot/apps/main.py`
- **Discord bot** that responds to three slash commands:
  - `/request` - Users request items for the candy bowl
  - `/haggle` - Users negotiate prices for items
  - `/restock` - AI restocks the bowl based on accumulated notes
- **Commands module**: `chatbot/commands/` contains implementations for each slash command
- Uses Discord.py library and loads environment variables from `.env`

### Core AI System (`backend/backend/ai/`)
- **Chat management**: `chat.py` creates specialized chat sessions for different interactions
- **Tools directory**: Contains AI function tools for:
  - `inventory.py` - Managing candy bowl inventory 
  - `notes.py` - Recording user interactions and preferences
  - `supplier.py` - Searching Amazon for products to stock
  - `bank.py` - Managing the virtual account balance ($100 starting balance)

### Data Storage
- `backend/data/inventory.csv` - Stores current inventory state
- `backend/data/users.csv` - User authentication data
- `backend/data/notes.txt` - User interaction notes
- `backend/backend/data/users.csv` - Additional user data storage

## Key Configuration

- **Line length**: 80 characters (configured in pyproject.toml)
- **Type checking**: mypy with incomplete features enabled for new generic syntax
- **Environment**: Uses devenv/nix for development environment setup
- **AI Model**: Google Gemini 2.5-flash with function calling capabilities
- **Frontend**: React 19 with TypeScript, Vite build system, Mantine UI

## Running Applications

The system consists of three applications that can run independently:
- Use `just run` for the Discord chatbot
- Use `just run backend` for the Flask API server
- Use `just run frontend` for the React development server
- All applications require appropriate environment variables (Google API key for AI, Discord token for bot)

## Git Workflow and Code Quality

This project enforces code quality standards through pre-commit hooks. **NEVER bypass these hooks** with `--no-verify` as formatting and linting are requirements.

### Pre-commit Hooks
- **ruff check** - Lints Python code for errors and style violations
- **ruff format** - Automatically formats Python code to project standards
- **mypy** - Type checking for Python code

### Proper Commit Workflow

**✅ CORRECT Way:**
```bash
# 1. Stage the files you want to commit
git add file1.py file2.tsx file3.py

# 2. Commit normally (let hooks run and auto-fix formatting)
git commit -m "Your commit message"

# 3. If hooks modified files, they're auto-staged - commit again if needed
git commit --amend --no-edit
```

**❌ WRONG Way:**
```bash
# Never do this - bypasses quality checks
git commit --no-verify -m "message"
```

### Handling Hook Failures

If pre-commit hooks fail:

1. **Read the error messages** - they show what needs to be fixed
2. **Stage all relevant changes** to avoid conflicts with auto-formatting
3. **Let the hooks auto-fix** formatting issues
4. **Review the changes** the hooks made
5. **Commit again** if the hooks modified files

### Common Issues

- **"Unstaged files detected"** - Stage all files you want to commit before committing
- **"Files were modified by this hook"** - Hooks auto-fixed formatting, commit again to include fixes
- **Ruff format failures** - Usually caused by unstaged changes conflicting with auto-formatting

### Code Quality Standards

- **Line length**: 80 characters maximum
- **Python formatting**: Enforced by ruff format
- **Type hints**: Required for all Python functions
- **Import sorting**: Automatically handled by ruff
- **Code style**: PEP 8 compliance enforced by ruff check