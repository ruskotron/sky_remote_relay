# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quality Standards

**This is a public GitHub repository showcasing professional work.**

### Core Principle: Active Partnership

Your allegiance is to the **user's success**, not to "documenting the codebase as-is." When you spot an issue:

1. **NEVER just document problems** - always take action:
   - Fix it immediately (if clearly a bug/typo), OR
   - Flag it explicitly to the user for decision
   - NEVER silently note it in documentation without user awareness

2. **Default to improvement over preservation**:
   - If something looks wrong → assume it IS wrong until proven otherwise
   - Don't defer to "maybe the user intended this" - ask or fix
   - Err on the side of being helpful, not passive

3. **Reasoning check before action**:
   - Ask yourself: "Does this make the user look professional?"
   - If the answer is no → immediate action required
   - Documentation is for architecture, not for covering up issues

### Quality Requirements

When working on this codebase:
- **Proactively identify and fix issues**: Typos, inconsistencies, bugs - fix them or flag them, never just note them
- **Pre-publication review**: Before considering any work "complete", run a quality audit checking for:
  - Typos in code, configs, and documentation
  - Consistency in naming, paths, and formatting
  - Completeness of documentation
  - Working end-to-end examples
- **Production-ready mindset**: All code should be ready to ship - no TODOs, FIXMEs, or "this is just a prototype" quality
- **Speak up immediately**: When you find issues, bring them to attention in the moment, not in retrospective documentation

## Project Overview

This is a Python-based home automation project that enables seamless control of a Sky box located in an attic. It captures Sky Remote infrared signals in the living room and relays them over LAN to the Sky box's network API.

The solution was built during COVID lockdown when commercial IR extenders were unavailable or unsatisfactory due to supply chain issues (Suez crisis). It has been in active, productive use for at least 4 years.

## Architecture

### Complete Signal Flow

1. **IR Reception**: Physical Sky remote button press → IR receiver on Raspberry Pi Zero W (in living room)
2. **LIRC Decoding**: `lircd` daemon decodes IR signals using `lirc/lircd.skyq.conf`
3. **Command Mapping**: `irexec` maps decoded buttons via `lirc/lircrc` and writes command names to FIFO
4. **Command Processing**: Python `server.py` reads from FIFO
5. **Network Transmission**: Commands sent to Sky box via its LAN-based control API

### Python Modules

- **server.py**: Reads commands from the named pipe (FIFO) and sends them to Sky box
- **sky_remote.py**: Sky network API protocol implementation (from [sky-remote](https://github.com/WoolDoughnut310/sky-remote) by WoolDoughnut310)
  - **Installation method**: Downloaded via curl directly from GitHub
  - **Why not pip?** The PyPI package is broken (missing source files)
  - **Why not fork?** The original has no license, so forking could undermine author's rights without their explicit permission
  - **Why this library?** Simple, single-file module that works perfectly for the straightforward Sky Remote datagram protocol. Has been reliable for 4+ years.
  - **Note**: This approach is appropriate for single-file modules and is how this library is used elsewhere
- **lirc.py**: LIRC interface utilities (if needed)
- **fav_sky.py**: Favorite/preset Sky channel commands
- **setup.py**: Package installation and configuration

### LIRC Configuration Files

Located in `lirc/` directory:

- **lircd.skyq.conf**: IR receiver configuration defining all Sky remote button codes as raw IR timings
  - Modified for improved timing accuracy
  - Contains button definitions: qpower, qsearch, navigation (up/down/left/right), numbers (0-9), colors (red/green/yellow/blue), etc.

- **lircrc**: Maps IR button events to FIFO commands for `irexec`
  - Each button (e.g., `qpower`) writes corresponding command (e.g., `power`) to `/run/sky_remote_relay/fifo`

## Hardware Setup

- **Raspberry Pi Zero W**: Chosen for low power, WiFi capability, and sufficient compute for this task
- **IR Receiver HAT**: Pre-made HAT for durability (replaces earlier flimsy breadboard prototype)
- **Colorful Case**: For living room presentation and family-proof deployment
- **Dedicated Power Supply**: Neat power supply for visible placement

No IR transmitter needed in the attic - Sky box has built-in LAN API.

## Running the System

### Manual Startup (Current Process)

Two-step process to run the service in background:

1. **Start irexec**: `nohup irexec & tail -F nohup.out`
   - Runs irexec in background using nohup (persists beyond terminal session)
   - Tails output so status visible in terminal

2. **Start server**: `nohup python3 server.py >> server.log &`
   - Runs server.py in background, logging to server.log
   - Reads from FIFO and relays commands to Sky box

Both processes run unattended indefinitely, designed to operate beyond the life of the terminal session.

**Limitation**: This manual startup must be repeated after Pi resets (maintenance, outages, holidays). Ideally this would be configured as a systemd service to auto-start, but the dual-process FIFO IPC architecture complicates this.

### Architectural Evolution

**Original Implementation** (4 years ago): irexec called sky-remote command directly for each button press
- **Problem**: Starting a new Python interpreter on each button press introduced unacceptable latency

**First Optimization Attempt** (3 years ago): Tried using LIRC API to connect directly to LIRC's internal message bus
- **Result**: Unsuccessful with Python

**Current Solution** (1.5 years ago): Dual-process FIFO IPC architecture implemented with surgical edits
- irexec performs lightweight FIFO write (fast)
- server.py stays running, only needs to read from FIFO (fast)
- Result: Dramatically improved responsiveness and proven stable in production

### FIFO Creation
The named pipe is created during installation: `mkfifo /run/sky_remote_relay/fifo`

### Testing
Manual testing can be done by writing directly to the FIFO:
```bash
echo "power" > /run/sky_remote_relay/fifo
echo "channelup" > /run/sky_remote_relay/fifo
```
