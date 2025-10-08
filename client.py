#!/usr/bin/env python3

import sys
from server import DEFAULT_FIFO_PATH

message = sys.argv[1] if len(sys.argv) > 1 else 'hello'
fifo_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FIFO_PATH

with open(fifo_path, 'w') as f:
  f.write(f'{message}\n')
