# Sky Remote Relay

Relay Sky Remote Control infrared signals over LAN using a Raspberry Pi and LIRC.

## Overview

This project enables seamless control of a Sky box located remotely (e.g., in an attic) by capturing IR signals from a physical Sky Remote in one location and relaying them to the Sky box via its network API.

I originally built this during the COVID-19 lockdown and couldn't get my hands on any off the shelf solutions. In the end, I think this has worked out to be a superior approach. This solution has seen active use for at least 4 years. It works reliably, with only a minor lag.

## How It Works

1. **IR Reception**: Physical Sky remote button press → IR receiver on Raspberry Pi Zero W
2. **LIRC Decoding**: `lircd` daemon decodes IR signals using Sky remote configuration
3. **Command Mapping**: `irexec` writes command names to a FIFO (named pipe)
4. **Network Relay**: Python server reads FIFO and sends commands to Sky box's LAN API

## Hardware Requirements

- **Raspberry Pi Zero W** (or any Pi with WiFi)
- **Power supply** for Raspberry Pi (5V micro-USB)
- **IR receiver HAT/module**
  - Can be purchased pre-made from Amazon and other retailers
  - Or built from scratch - see [LIRC documentation](http://lirc.org/html/schemas.html) and various online DIY projects
  - Must be configured in LIRC to use the correct GPIO pin and `/dev/lirc` device
- **Sky box** on the same network

## Key Features

- **Low latency**: Dual-process FIFO architecture eliminates Python startup delay
- **Auto-start**: Systemd service integration for unattended operation
- **Battle-tested**: 4+ years of reliable production use
- **Simple setup**: Single command-line parameter (Sky box IP address)

## Quick Start

```bash
# Install dependencies
sudo apt-get install lirc python3 git curl

# Clone repository
sudo git clone https://github.com/ruskotron/sky_remote_relay /opt/sky_remote_relay
sudo chown -R $USER:$USER /opt/sky_remote_relay
cd /opt/sky_remote_relay

# Install sky-remote library (see Credits section for why we use curl)
curl -o sky_remote.py https://raw.githubusercontent.com/WoolDoughnut310/sky-remote/main/sky_remote.py

# Configure LIRC
sudo cp lirc/lircd.skyq.conf /etc/lirc/lircd.conf.d/skyq.conf
mkdir -p ~/.config/lirc
cp lirc/lircrc ~/.config/lirc/lircrc
sudo systemctl restart lircd

# Test IR reception (press buttons on Sky remote)
irw

# Follow installation guide for complete setup
cat INSTALL.md
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Usage

### Manual Operation

```bash
# Create FIFO in working directory
mkfifo my_fifo

# Start server with custom FIFO path (replace with your Sky box IP)
nohup python3 -u server.py 192.168.0.66 my_fifo >> server.log &

# Start irexec (captures IR and writes to FIFO - requires lircrc configured)
nohup irexec & tail -F nohup.out

# Or test manually by writing to FIFO
echo "power" > my_fifo
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
├── server.py           # Reads FIFO and relays to Sky box
├── lirc/               # LIRC configuration files
│   ├── lircd.skyq.conf      # Sky IR remote codes
│   └── lircrc               # irexec button mappings
├── systemd/            # Systemd service files
│   ├── sky-remote-irexec.service
│   └── sky-remote-server.service
├── INSTALL.md          # Detailed installation guide
└── CLAUDE.md           # AI assistant context

```

## Credits

- Sky network API protocol implementation: [sky-remote](https://github.com/WoolDoughnut310/sky-remote) by WoolDoughnut310
- LIRC IR codes modified from configurations by Simon Walters

**Note**: The single-file `sky-remote` module is downloaded directly via curl rather than pip. The [PyPI package](https://pypi.org/project/sky-remote/ "sky-remote") is broken (missing source files), and forking was avoided to respect the author's rights (the repository has no license). This curl approach is appropriate for single-file modules, and is how the module is used elsewhere. I could I suppose explore other sky integration modules, but this single-file no-frills protocol implementation is reflective of the actual protocol itself which is refreshingly simple and uncomplicated.

## License

See [LICENSE](LICENSE) file for details.
