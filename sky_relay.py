#!/usr/bin/env python3

import sys
from sky_remote import SkyRemote

# Default configuration
DEFAULT_FIFO_PATH = '/run/sky_remote_relay/fifo'

if len(sys.argv) < 2:
    print("Usage: sky_relay.py <sky_addr> [fifo_path]")
    print("  sky_addr: Address of Sky box (required)")
    print(f"  fifo_path: Path to FIFO (default: {DEFAULT_FIFO_PATH})")
    sys.exit(1)

sky_addr = sys.argv[1]
fifo_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FIFO_PATH

r = SkyRemote(sky_addr)

def do_read(f):

    while True:

        l = f.readline()
        k = l.strip()

        print(f'{k}')

        if not l:
            break

        try:
            # sky-remote defines int keys for the numbers
            r.press(int(k))
        except:
            # ah must be a non-int key
            r.press(k)

while True:
    with open(fifo_path) as f:
        do_read(f)

print('sky remote server end')
