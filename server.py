#!/usr/bin/env python3

import sys
from sky_remote import SkyRemote

if len(sys.argv) < 2:
    print("Usage: server.py <sky_addr> [fifo_path]")
    print("  sky_addr: IP address of Sky Q box (required)")
    print("  fifo_path: Path to FIFO (default: /run/sky-remote/fifo)")
    sys.exit(1)

sky_addr = sys.argv[1]
fifo_path = sys.argv[2] if len(sys.argv) > 2 else '/run/sky-remote/fifo'

r = SkyRemote(sky_addr)

def do_read(f):

  while True:

    l = f.readline()
    k = l.strip()

    print(f'{k}')

    if not l:
        break

    try:
        r.press(int(k))
    except:
        r.press(k)


while True:
  with open(fifo_path) as f:
    do_read(f)



print('sky remote server end')

