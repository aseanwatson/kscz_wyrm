#!/usr/bin/env python3

#
# This file is part of Colorlite.
#
# Copyright (c) 2020-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import sys

from migen import *
from migen.genlib.misc import WaitTimer
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex_boards.platforms import colorlight_5a_75b

from litex.soc.cores.clock import *
from litex.soc.cores.spi_flash import ECP5SPIFlash
from litex.soc.cores.gpio import GPIOOut
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII
from litex.build.generic_platform import *

# IOs ----------------------------------------------------------------------------------------------

# TODO - figure out if we have anything here

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.cd_sys = ClockDomain()
        # # #

        # Clk / Rst.
        clk25 = platform.request("clk25")

        # PLL.
        self.pll = pll = ECP5PLL()
        # self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk25, 25e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# ColorLite ----------------------------------------------------------------------------------------

class Wyrm(SoCMini):
    def __init__(self, sys_clk_freq=int(50e6), ip_address=None, mac_address=None, rom=None):
        SoCMini.mem_map = {
            "sram":         0x10000000,
            "spiflash":     0x20000000,
            "sdram":        0x40000000,
            "csr":          0x82000000,
        }
        platform = colorlight_5a_75b.Platform(revision="8.2")

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self,
            platform,
            clk_freq=sys_clk_freq,
            cpu_type="vexriscv",
            cpu_variant="standard+debug",
            integrated_sram_size=8*KB,
            with_uart=True,
            with_timer=True,
            cpu_reset_address=0x0,
            max_sdram_size=0x400000
        )

        # Boot rom --------------------------------------------------------------------------------
        if rom != None:
            self.add_rom("rom", 0x0, 32*KB, contents=get_mem_data(rom, endianness="little"))
        else:
            self.add_rom("rom", 0x0, 32*KB)

        # Etherbone --------------------------------------------------------------------------------
        self.ethphy = LiteEthPHYRGMII(
            clock_pads = self.platform.request("eth_clocks"),
            pads       = self.platform.request("eth"),
            tx_delay   = 0e-9)
        self.add_etherbone(
            phy          = self.ethphy,
            ip_address   = ip_address,
            mac_address  = mac_address,
            data_width   = 32,
        )
        self.add_ethernet(
            phy          = self.ethphy,
            local_ip     = ip_address,
            mac_address  = mac_address,
            data_width   = 32,
        )

        # JTAG -------------------------------------------------------------------------------------
        # self.add_jtagbone()

        # SPIFlash ---------------------------------------------------------------------------------
        self.spiflash = ECP5SPIFlash(
            pads         = platform.request("spiflash"),
            sys_clk_freq = sys_clk_freq,
            spi_clk_freq = 5e6,
        )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ColorLight FPGA board with LiteX/LiteEth")
    parser.add_argument("--build",       action="store_true",      help="Build bitstream")
    parser.add_argument("--load",        action="store_true",      help="Load bitstream")
    parser.add_argument("--flash",       action="store_true",      help="Flash bitstream")
    parser.add_argument("--rom",         default=None,             help="Bin file of firmware to load to internal ROM")
    parser.add_argument("--ip-address",  default="192.168.10.30",  help="Ethernet IP address of the board (default: 192.168.10.30).")
    parser.add_argument("--mac-address", default="0x726b895bc2e2", help="Ethernet MAC address of the board (defaullt: 0x726b895bc2e2).")
    args = parser.parse_args()

    soc     = Wyrm(ip_address=args.ip_address, mac_address=int(args.mac_address, 0), rom=args.rom)
    builder = Builder(soc, output_dir="build", csr_csv="csr.csv")
    builder.build(build_name="wyrm", run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".svf"))

    if args.flash:
        prog = soc.platform.create_programmer()
        os.system("cp bit_to_flash.py build/gateware/")
        os.system("cd build/gateware && ./bit_to_flash.py wyrm.bit wyrm_flash.svf")
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + "_flash.svf"))

if __name__ == "__main__":
    main()
