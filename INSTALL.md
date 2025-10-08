# Installation Guide

This guide will help you set up the Sky Remote Relay on a Raspberry Pi Zero W (or similar device).

## Prerequisites

- Raspberry Pi Zero W (or any Pi with WiFi)
- IR receiver HAT/module connected to GPIO
- LIRC installed and configured
- Sky Q box on the same network
- Python 3.x installed

## Dependencies

### System Packages

```bash
sudo apt-get update
sudo apt-get install lirc python3 python3-pip git
```

### Python Dependencies

The `sky-remote` Python library is required:

```bash
pip3 install sky-remote
```

Or clone and install from source:
```bash
git clone https://github.com/RogerSelwyn/skyq_remote
cd skyq_remote
pip3 install .
```

## Installation Steps

### 1. Clone Repository

```bash
sudo mkdir -p /opt
sudo git clone https://github.com/ruskotron/sky_remote_relay /opt/sky_remote_relay
cd /opt/sky_remote_relay
```

### 2. Configure LIRC

#### Install LIRC Configuration Files

Modern LIRC uses `/etc/lirc/lircd.conf.d/` for remote configurations:

```bash
sudo cp lirc/lircd.skyq.conf /etc/lirc/lircd.conf.d/skyq.conf
```

**Alternative configuration:** If the default doesn't work, try the alternate config:
```bash
sudo cp lirc/lircd.skyq.conf-alt /etc/lirc/lircd.conf.d/skyq.conf
```

#### Configure LIRC Options

Check `/etc/lirc/lirc_options.conf` and adjust the `device` setting if needed:
- Try `/dev/lirc0` or `/dev/lirc1` depending on your hardware
- Use `mode2` to test which device receives IR signals

Example configuration snippet:
```ini
[lircd]
device = /dev/lirc1
```

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

### 3. Find Your Sky Q Box IP Address

Find your Sky Q box's IP address from your router's DHCP table or Sky Q settings menu.

Example: `192.168.0.66`

### 4. Test Manual Operation

#### Create FIFO manually for testing:

```bash
sudo mkdir -p /run/sky-remote
mkfifo /run/sky-remote/my_fifo
```

#### Start irexec:

```bash
irexec &
```

#### Start the server (replace with your Sky Q IP):

```bash
cd /opt/sky_remote_relay
python3 server.py 192.168.0.66
```

#### Test with your Sky remote

Point your physical Sky remote at the IR receiver and press buttons. You should see:
- Commands appearing in the server output
- Your Sky Q box responding to the commands

### 5. Set Up Systemd Services (Automatic Start)

#### Edit Server Service

Update the Sky Q IP address in the server service file:

```bash
sudo nano /opt/sky_remote_relay/systemd/sky-remote-server.service
```

Change the `ExecStart` line to use your Sky Q box IP:
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
sudo mkdir -p /var/log/sky-remote
sudo chown pi:pi /var/log/sky-remote
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
tail -f /var/log/sky-remote/server.log

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
ls -la /run/sky-remote/my_fifo

# Check FIFO permissions
# Should be prw-rw-rw- (named pipe, writable)

# Manually recreate if needed
sudo rm -f /run/sky-remote/my_fifo
mkfifo -m 666 /run/sky-remote/my_fifo
```

### Sky Q Box Not Responding

- Verify Sky Q box IP address is correct
- Ensure Sky Q box and Pi are on same network
- Test connectivity: `ping YOUR_SKY_Q_IP`
- Check Sky Q box has network control enabled (should be default)

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
sudo rm -rf /var/log/sky-remote
```
