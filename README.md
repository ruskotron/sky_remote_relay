# Sky Remote Relay

Relay Sky Remote Control infrared signals over LAN using a Raspberry Pi and LIRC.

## Overview

This project enables seamless control of a Sky Q box located remotely (e.g., in an attic) by capturing IR signals from a physical Sky Remote in one location and relaying them to the Sky Q box via its network API.

I originally built this during the COVID-19 lockdown and couldn't get my hands on any off the shelf solutions. In the end, I think this has worked out to be a superior approach. This solution has seen active use for at least 4 years. It works reliably, with only a minor lag.

## How It Works

1. **IR Reception**: Physical Sky remote button press → IR receiver on Raspberry Pi Zero W
2. **LIRC Decoding**: `lircd` daemon decodes IR signals using Sky Q remote configuration
3. **Command Mapping**: `irexec` writes command names to a FIFO (named pipe)
4. **Network Relay**: Python server reads FIFO and sends commands to Sky Q box's LAN API

## Hardware Requirements

- Raspberry Pi Zero W (or any Pi with WiFi)
- IR receiver HAT/module
- Sky Q box on the same network

## Key Features

- **Low latency**: Dual-process FIFO architecture eliminates Python startup delay
- **Auto-start**: Systemd service integration for unattended operation
- **Battle-tested**: 4+ years of reliable production use
- **Simple setup**: Single command-line parameter (Sky Q IP address)

## Quick Start

```bash
# Install dependencies
sudo apt-get install lirc python3 python3-pip
pip3 install sky-remote

# Clone repository
sudo git clone https://github.com/ruskotron/sky_remote_relay /opt/sky_remote_relay
sudo chown -R $USER:$USER /opt/sky_remote_relay

# Follow installation guide
cat /opt/sky_remote_relay/INSTALL.md
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Usage

### Manual Operation

```bash
# Create FIFO in working directory
mkfifo my_fifo

# Start server with custom FIFO path (replace with your Sky Q IP)
nohup python3 server.py 192.168.0.66 my_fifo >> server.log &

# Start irexec (captures IR and writes to FIFO - requires lircrc configured)
nohup irexec & tail -F nohup.out

# Or test manually with client
python3 client.py power my_fifo
```

### Systemd Service (Recommended)

```bash
sudo systemctl enable sky-remote-irexec.service
sudo systemctl enable sky-remote-server.service
sudo systemctl start sky-remote-irexec.service
sudo systemctl start sky-remote-server.service
```

## Architecture Evolution

- **Original (4 years ago)**: Direct command execution - high latency due to Python interpreter startup
- **Attempted (3 years ago)**: Direct LIRC API integration - unsuccessful with Python
- **Current (1.5 years ago)**: Dual-process FIFO architecture - fast and stable

## Project Structure

```
sky_remote_relay/
├── server.py           # Reads FIFO and relays to Sky Q box
├── client.py           # Test client for manual FIFO writes
├── lirc/               # LIRC configuration files
│   ├── lircd.skyq.conf      # Sky Q IR remote codes
│   ├── lircd.skyq.conf-alt  # Alternative configuration
│   ├── lirc_options.conf    # LIRC daemon options
│   └── lircrc               # irexec button mappings
├── systemd/            # Systemd service files
│   ├── sky-remote-irexec.service
│   └── sky-remote-server.service
├── INSTALL.md          # Detailed installation guide
└── CLAUDE.md           # AI assistant context

```

## Credits

- Sky Q network API protocol implementation based on [sky-remote](https://github.com/RogerSelwyn/skyq_remote) by Roger Selwyn
- LIRC IR codes modified from configurations by Simon Walters

## License

See [LICENSE](LICENSE) file for details.
