# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Android automation project focused on creating automation tools for mobile games, specifically "Rise of Kingdoms". The project is designed to run in a Docker Ubuntu environment without GUI.

## Project Structure

```
jnj-android/
├── frontend/nextjs/          # Next.js frontend application
├── database/                 # Database components
├── logs/                     # Application logs
├── _docs/                    # Project documentation
│   ├── planning/            # Planning documents and memos
│   ├── claudecode/          # Claude Code specific documentation
│   ├── backend/             # Backend documentation
│   ├── frontend/            # Frontend documentation
│   └── database/            # Database documentation
├── _backups/                # Backup files organized by component
└── _drafts/                 # Draft implementations

```

## Key Technologies

- **Android Automation**: This project involves Android emulator automation
- **Game Automation**: Specifically targeting "Rise of Kingdoms" mobile game
- **Image Recognition**: OCR capabilities may be required for automation
- **Input Control**: Mouse and keyboard control automation
- **Frontend**: Next.js application
- **Environment**: Docker Ubuntu environment (headless)

## Development Notes

- The project is in early planning/setup phase with mostly documentation and structure
- No build scripts, package.json, or gradle files are currently present
- The main planning document is located at `_docs/planning/memo.md`
- This is a containerized development environment without GUI components

## Architecture

The project follows a modular structure with separate frontend, backend, and database components, along with comprehensive documentation and backup systems. The focus is on Android emulator automation with potential for image recognition and input control automation.