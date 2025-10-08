# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based home automation project that relays Sky Remote infrared signals over a local area network (LAN). The system allows remote control of Sky TV equipment by translating network commands into IR signals using LIRC (Linux Infrared Remote Control).

## Architecture

The codebase consists of several Python modules working together:

- **server.py**: Reads commands from a named pipe (FIFO)
- **client.py**: Writes commands to the named pipe
- **sky_remote.py**: Core Sky Remote IR protocol implementation and signal encoding
- **lirc.py**: LIRC (Linux Infrared Remote Control) interface for hardware IR transmission
- **fav_sky.py**: Favorite/preset Sky channel commands
- **setup.py**: Package installation and configuration

The system follows an IPC-based architecture where:
1. A named pipe (FIFO) is created using `mkfifo` for inter-process communication
2. server.py listens on the named pipe for incoming commands
3. Commands are translated to Sky Remote IR codes
4. LIRC interface transmits the IR signals via hardware (GPIO-controlled IR LED)

## Development Setup

This is a Python project. The source files are gitignored (likely for local development), but the project structure is maintained in the repository's gitignore configuration.

### Running the System

1. Create a named pipe: `mkfifo <pipe_name>`
2. Run server.py to listen on the pipe
3. Use client.py to write commands to the pipe, which are then processed by the server and transmitted as IR signals

## Hardware Requirements

This project requires:
- Raspberry Pi or similar device with GPIO pins
- IR LED transmitter circuit
- LIRC configured on the host system
