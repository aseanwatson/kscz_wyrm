#!/usr/bin/env python3

import time

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

print("Writing to uart...")
wb.regs.uart_rxtx.write(65)

# # #

wb.close()
