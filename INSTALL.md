# Installation Guide

This guide will help you set up the Sky Remote Relay on a Raspberry Pi Zero W (or similar device).

## Prerequisites

- Raspberry Pi Zero W (or any Pi with WiFi)
- Power supply for Raspberry Pi (5V micro-USB)
- IR receiver HAT/module connected to GPIO
- Sky box on the same network
- Python 3.x installed

## IR Receiver Hardware

You'll need an infrared receiver module connected to your Raspberry Pi's GPIO pins.

### Option 1: Pre-fabricated HAT/Module (Recommended)

Purchase a ready-made IR receiver HAT from:
- Amazon, eBay, AliExpress (search "Raspberry Pi IR receiver HAT")
- Electronics retailers (Adafruit, Pimoroni, etc.)

These typically come pre-configured and include mounting hardware for easy installation.

### Option 2: DIY Build

Build your own IR receiver circuit:
- Components needed: IR receiver module (e.g., TSOP38238, VS1838B), resistors, wires
- Circuit diagrams available on:
  - [LIRC Hardware Schemas](http://lirc.org/html/schemas.html)
  - Various Raspberry Pi IR receiver tutorials online

### Configuration

After hardware installation:
1. The IR receiver will typically appear as `/dev/lirc0` or `/dev/lirc1`
2. Configure LIRC to use the correct device (covered in LIRC Configuration section below)
3. Test reception with `mode2 -d /dev/lirc0` (or `/dev/lirc1`)

## Dependencies

### System Packages

```bash
sudo apt-get update
sudo apt-get install lirc python3 python3-pip git curl
```

## Installation Steps

### 1. Clone Repository

```bash
sudo git clone https://github.com/ruskotron/sky_remote_relay /opt/sky_remote_relay
sudo chown -R $USER:$USER /opt/sky_remote_relay
cd /opt/sky_remote_relay
```

### 2. Install Python Dependencies

Download the `sky-remote` library directly from GitHub (see Credits section in README for explanation of this installation method):

```bash
curl -o sky_remote.py https://raw.githubusercontent.com/WoolDoughnut310/sky-remote/main/sky_remote.py
```

### 3. Configure LIRC

#### Install LIRC Configuration Files

Modern LIRC uses `/etc/lirc/lircd.conf.d/` for remote configurations:

```bash
sudo cp lirc/lircd.skyq.conf /etc/lirc/lircd.conf.d/skyq.conf
```

**Note:** If you need to configure which IR device LIRC uses (`/dev/lirc0` vs `/dev/lirc1`), edit `/etc/lirc/lirc_options.conf` and adjust the `device` setting. Use `mode2` to test which device receives IR signals.

#### Install irexec Configuration

```bash
mkdir -p ~/.config/lirc
cp lirc/lircrc ~/.config/lirc/lircrc
```

#### Restart LIRC

```bash
sudo systemctl restart lircd
```

#### Test IR Reception

```bash
# Test that LIRC is receiving IR signals
irw

# Press buttons on your Sky remote - you should see output like:
# 0000000000000001 00 qpower skyq
# 0000000000000002 00 q1 skyq
```

### 4. Find Your Sky Box IP Address

Find your Sky box's IP address from your router's DHCP table or Sky box settings menu.

Example: `192.168.0.66`

### 5. Test Manual Operation

#### Create FIFO manually for testing:

```bash
sudo mkdir -p /run/sky_remote_relay
mkfifo /run/sky_remote_relay/fifo
```

#### Start irexec:

```bash
irexec &
```

#### Start the server (replace with your Sky box IP):

```bash
cd /opt/sky_remote_relay
python3 -u server.py 192.168.0.66
```

#### Test with your Sky remote

Point your physical Sky remote at the IR receiver and press buttons. You should see:
- Commands appearing in the server output
- Your Sky box responding to the commands

### 6. Set Up Systemd Services (Automatic Start)

#### Edit Server Service

Update the Sky box IP address in the server service file:

```bash
sudo nano /opt/sky_remote_relay/systemd/sky-remote-server.service
```

Change the `ExecStart` line to use your Sky box IP:
```ini
ExecStart=/usr/bin/python3 /opt/sky_remote_relay/server.py YOUR_SKY_Q_IP
```

#### Install Service Files

```bash
sudo cp systemd/sky-remote-irexec.service /etc/systemd/system/
sudo cp systemd/sky-remote-server.service /etc/systemd/system/
```

#### Create Log Directory

```bash
sudo mkdir -p /var/log/sky_remote_relay
sudo chown pi:pi /var/log/sky_remote_relay
```

#### Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable sky-remote-irexec.service
sudo systemctl enable sky-remote-server.service
sudo systemctl start sky-remote-irexec.service
sudo systemctl start sky-remote-server.service
```

#### Check Service Status

```bash
sudo systemctl status sky-remote-irexec.service
sudo systemctl status sky-remote-server.service
```

#### View Logs

```bash
# Server logs
tail -f /var/log/sky_remote_relay/server.log

# irexec logs
journalctl -u sky-remote-irexec.service -f
```

## Troubleshooting

### LIRC Not Receiving IR Signals

```bash
# Check LIRC is running
sudo systemctl status lircd

# Test IR reception
mode2 -d /dev/lirc0  # or /dev/lirc1

# Press buttons on Sky remote - you should see pulse/space timings
```

### FIFO Issues

```bash
# Check FIFO exists
ls -la /run/sky_remote_relay/fifo

# Check FIFO permissions
# Should be prw-rw-rw- (named pipe, writable)

# Manually recreate if needed
sudo rm -f /run/sky_remote_relay/fifo
mkfifo -m 666 /run/sky_remote_relay/fifo
```

### Sky Box Not Responding

- Verify Sky box IP address is correct
- Ensure Sky box and Pi are on same network
- Test connectivity: `ping YOUR_SKY_BOX_IP`
- Check Sky box has network control enabled (should be default)

### Service Won't Start

```bash
# Check for errors
sudo journalctl -xe

# Check user permissions (services run as user 'pi')
# Adjust User= in service files if needed
```

## Updating

```bash
cd /opt/sky_remote_relay
sudo git pull
sudo systemctl restart sky-remote-server.service
sudo systemctl restart sky-remote-irexec.service
```

## Uninstallation

```bash
# Stop and disable services
sudo systemctl stop sky-remote-server.service
sudo systemctl stop sky-remote-irexec.service
sudo systemctl disable sky-remote-server.service
sudo systemctl disable sky-remote-irexec.service

# Remove service files
sudo rm /etc/systemd/system/sky-remote-*.service
sudo systemctl daemon-reload

# Remove LIRC configs
sudo rm /etc/lirc/lircd.conf.d/skyq.conf
rm ~/.config/lirc/lircrc

# Remove installation
sudo rm -rf /opt/sky_remote_relay
sudo rm -rf /var/log/sky_remote_relay
```
