#!/usr/bin/env python3

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import colorlight_5a_75b

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr import *
from litex.soc.cores.gpio import GPIOOut

from litedram.modules import M12L64322A
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII
from liteeth.core import LiteEthUDPIPCore
from liteeth.frontend.stream import LiteEthUDPStreamer
from liteeth.frontend.etherbone import LiteEthEtherbone
from litex.build.generic_platform import *

from litescope import LiteScopeAnalyzer

_gpios = [
    ("panel_r0",  1, Pins("j1:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  1, Pins("j1:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  1, Pins("j1:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  1, Pins("j1:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  1, Pins("j1:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  1, Pins("j1:6"), IOStandard("LVCMOS33")),
    ("panel_e",   1, Pins("j1:7"), IOStandard("LVCMOS33")),
    ("panel_a",   1, Pins("j1:8"), IOStandard("LVCMOS33")),
    ("panel_b",   1, Pins("j1:9"), IOStandard("LVCMOS33")),
    ("panel_c",   1, Pins("j1:10"), IOStandard("LVCMOS33")),
    ("panel_d",   1, Pins("j1:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 1, Pins("j1:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 1, Pins("j1:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  1, Pins("j1:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  2, Pins("j2:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  2, Pins("j2:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  2, Pins("j2:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  2, Pins("j2:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  2, Pins("j2:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  2, Pins("j2:6"), IOStandard("LVCMOS33")),
    ("panel_e",   2, Pins("j2:7"), IOStandard("LVCMOS33")),
    ("panel_a",   2, Pins("j2:8"), IOStandard("LVCMOS33")),
    ("panel_b",   2, Pins("j2:9"), IOStandard("LVCMOS33")),
    ("panel_c",   2, Pins("j2:10"), IOStandard("LVCMOS33")),
    ("panel_d",   2, Pins("j2:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 2, Pins("j2:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 2, Pins("j2:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  2, Pins("j2:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  3, Pins("j3:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  3, Pins("j3:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  3, Pins("j3:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  3, Pins("j3:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  3, Pins("j3:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  3, Pins("j3:6"), IOStandard("LVCMOS33")),
    ("panel_e",   3, Pins("j3:7"), IOStandard("LVCMOS33")),
    ("panel_a",   3, Pins("j3:8"), IOStandard("LVCMOS33")),
    ("panel_b",   3, Pins("j3:9"), IOStandard("LVCMOS33")),
    ("panel_c",   3, Pins("j3:10"), IOStandard("LVCMOS33")),
    ("panel_d",   3, Pins("j3:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 3, Pins("j3:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 3, Pins("j3:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  3, Pins("j3:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  4, Pins("j4:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  4, Pins("j4:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  4, Pins("j4:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  4, Pins("j4:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  4, Pins("j4:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  4, Pins("j4:6"), IOStandard("LVCMOS33")),
    ("panel_e",   4, Pins("j4:7"), IOStandard("LVCMOS33")),
    ("panel_a",   4, Pins("j4:8"), IOStandard("LVCMOS33")),
    ("panel_b",   4, Pins("j4:9"), IOStandard("LVCMOS33")),
    ("panel_c",   4, Pins("j4:10"), IOStandard("LVCMOS33")),
    ("panel_d",   4, Pins("j4:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 4, Pins("j4:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 4, Pins("j4:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  4, Pins("j4:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  5, Pins("j5:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  5, Pins("j5:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  5, Pins("j5:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  5, Pins("j5:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  5, Pins("j5:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  5, Pins("j5:6"), IOStandard("LVCMOS33")),
    ("panel_e",   5, Pins("j5:7"), IOStandard("LVCMOS33")),
    ("panel_a",   5, Pins("j5:8"), IOStandard("LVCMOS33")),
    ("panel_b",   5, Pins("j5:9"), IOStandard("LVCMOS33")),
    ("panel_c",   5, Pins("j5:10"), IOStandard("LVCMOS33")),
    ("panel_d",   5, Pins("j5:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 5, Pins("j5:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 5, Pins("j5:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  5, Pins("j5:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  6, Pins("j6:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  6, Pins("j6:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  6, Pins("j6:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  6, Pins("j6:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  6, Pins("j6:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  6, Pins("j6:6"), IOStandard("LVCMOS33")),
    ("panel_e",   6, Pins("j6:7"), IOStandard("LVCMOS33")),
    ("panel_a",   6, Pins("j6:8"), IOStandard("LVCMOS33")),
    ("panel_b",   6, Pins("j6:9"), IOStandard("LVCMOS33")),
    ("panel_c",   6, Pins("j6:10"), IOStandard("LVCMOS33")),
    ("panel_d",   6, Pins("j6:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 6, Pins("j6:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 6, Pins("j6:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  6, Pins("j6:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  7, Pins("j7:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  7, Pins("j7:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  7, Pins("j7:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  7, Pins("j7:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  7, Pins("j7:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  7, Pins("j7:6"), IOStandard("LVCMOS33")),
    ("panel_e",   7, Pins("j7:7"), IOStandard("LVCMOS33")),
    ("panel_a",   7, Pins("j7:8"), IOStandard("LVCMOS33")),
    ("panel_b",   7, Pins("j7:9"), IOStandard("LVCMOS33")),
    ("panel_c",   7, Pins("j7:10"), IOStandard("LVCMOS33")),
    ("panel_d",   7, Pins("j7:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 7, Pins("j7:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 7, Pins("j7:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  7, Pins("j7:14"), IOStandard("LVCMOS33")),

    ("panel_r0",  8, Pins("j8:0"), IOStandard("LVCMOS33")),
    ("panel_g0",  8, Pins("j8:1"), IOStandard("LVCMOS33")),
    ("panel_b0",  8, Pins("j8:2"), IOStandard("LVCMOS33")),
    ("panel_r1",  8, Pins("j8:4"), IOStandard("LVCMOS33")),
    ("panel_g1",  8, Pins("j8:5"), IOStandard("LVCMOS33")),
    ("panel_b1",  8, Pins("j8:6"), IOStandard("LVCMOS33")),
    ("panel_e",   8, Pins("j8:7"), IOStandard("LVCMOS33")),
    ("panel_a",   8, Pins("j8:8"), IOStandard("LVCMOS33")),
    ("panel_b",   8, Pins("j8:9"), IOStandard("LVCMOS33")),
    ("panel_c",   8, Pins("j8:10"), IOStandard("LVCMOS33")),
    ("panel_d",   8, Pins("j8:11"), IOStandard("LVCMOS33")),
    ("panel_clk", 8, Pins("j8:12"), IOStandard("LVCMOS33")),
    ("panel_stb", 8, Pins("j8:13"), IOStandard("LVCMOS33")),
    ("panel_oe",  8, Pins("j8:14"), IOStandard("LVCMOS33")),
]

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False, with_usb_pll=False, with_rst=True, sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_sys_div2 = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        if not use_internal_osc:
            clk = platform.request("clk25")
            clk_freq = 25e6
        else:
            clk = Signal()
            div = 5
            self.specials += Instance("OSCG",
                                p_DIV = div,
                                o_OSC = clk)
            clk_freq = 310e6/div

        self.rst_n = rst_n = 1 if not with_rst else platform.request("user_btn_n", 0)

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk, clk_freq)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.
        else:
           pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180) # Idealy 90° but needs to be increased.

        # display clock
        pll.create_clkout(self.cd_sys_div2, sys_clk_freq/2)

        # USB PLL
        if with_usb_pll:
            self.usb_pll = usb_pll = ECP5PLL()
            self.comb += usb_pll.reset.eq(~rst_n | self.rst)
            usb_pll.register_clkin(clk, clk_freq)
            self.cd_usb_12 = ClockDomain()
            self.cd_usb_48 = ClockDomain()
            usb_pll.create_clkout(self.cd_usb_12, 12e6, margin=0)
            usb_pll.create_clkout(self.cd_usb_48, 48e6, margin=0)

        # SDRAM clock
        sdram_clk = ClockSignal("sys2x_ps" if sdram_rate == "1:2" else "sys_ps")
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), sdram_clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, revision, sys_clk_freq=50e6, toolchain="trellis",
        eth_ip           = "192.168.10.30",
        eth_phy          = 0,
        use_internal_osc = False,
        sdram_rate       = "1:1",
        with_spi_flash   = False,
        rom              = None,
        **kwargs):
        platform = colorlight_5a_75b.Platform(revision=revision, toolchain=toolchain)

        # LED Panel --------------------------------------------------------------------------------
        s_shared_en = Signal(8)
        s_shared_addr = Signal(16)
        s_shared_wdat = Signal(24)

        s_j4_ctrl_en = Signal()
        s_j4_ctrl_addr = Signal(16)
        s_j4_ctrl_wdat = Signal(24)
        s_j4r0 = Signal()
        s_j4g0 = Signal()
        s_j4b0 = Signal()
        s_j4r1 = Signal()
        s_j4g1 = Signal()
        s_j4b1 = Signal()
        s_j4a = Signal()
        s_j4b = Signal()
        s_j4c = Signal()
        s_j4d = Signal()
        s_j4e = Signal()
        s_j4clk = Signal()
        s_j4stb = Signal()
        s_j4oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk = ClockSignal(),
            i_ctrl_en = s_j4_ctrl_en,
            i_ctrl_addr = s_j4_ctrl_addr,
            i_ctrl_wdat = s_j4_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0 = s_j4r0,
            o_panel_g0 = s_j4g0,
            o_panel_b0 = s_j4b0,
            o_panel_r1 = s_j4r1,
            o_panel_g1 = s_j4g1,
            o_panel_b1 = s_j4b1,
            o_panel_a = s_j4a,
            o_panel_b = s_j4b,
            o_panel_c = s_j4c,
            o_panel_d = s_j4d,
            o_panel_e = s_j4e,
            o_panel_clk = s_j4clk,
            o_panel_stb = s_j4stb,
            o_panel_oe = s_j4oe
        )
        platform.add_source("ledpanel.v")

        platform.add_extension(_gpios)
        j4r0 = platform.request("panel_r0", 4)
        j4g0 = platform.request("panel_g0", 4)
        j4b0 = platform.request("panel_b0", 4)
        j4r1 = platform.request("panel_r1", 4)
        j4g1 = platform.request("panel_g1", 4)
        j4b1 = platform.request("panel_b1", 4)
        j4E = platform.request("panel_e", 4)
        j4A = platform.request("panel_a", 4)
        j4B = platform.request("panel_b", 4)
        j4C = platform.request("panel_c", 4)
        j4D = platform.request("panel_d", 4)
        j4clk = platform.request("panel_clk", 4)
        j4stb = platform.request("panel_stb", 4)
        j4oe = platform.request("panel_oe", 4)

        # FIXME
        #self.panel_en = CSRStorage(size=4)
        #self.panel_addr = CSRStorage(size=16)
        #self.panel_wdat = CSRStorage(size=24)

        #self.comb += s_shared_en.eq(self.panel_en.storage)

        self.comb += j4r0.eq(s_j4r0)
        self.comb += j4g0.eq(s_j4g0)
        self.comb += j4b0.eq(s_j4b0)
        self.comb += j4r1.eq(s_j4r1)
        self.comb += j4g1.eq(s_j4g1)
        self.comb += j4b1.eq(s_j4b1)
        self.comb += j4A.eq(s_j4a)
        self.comb += j4B.eq(s_j4b)
        self.comb += j4C.eq(s_j4c)
        self.comb += j4D.eq(s_j4d)
        self.comb += j4E.eq(s_j4e)
        self.comb += j4clk.eq(s_j4clk)
        self.comb += j4stb.eq(s_j4stb)
        self.comb += j4oe.eq(s_j4oe)
        self.comb += s_j4_ctrl_en.eq(s_shared_en[0])
        self.comb += s_j4_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j4_ctrl_wdat.eq(s_shared_wdat)

        s_j3_ctrl_en = Signal()
        s_j3_ctrl_addr = Signal(16)
        s_j3_ctrl_wdat = Signal(24)
        s_j3r0 = Signal()
        s_j3g0 = Signal()
        s_j3b0 = Signal()
        s_j3r1 = Signal()
        s_j3g1 = Signal()
        s_j3b1 = Signal()
        s_j3a = Signal()
        s_j3b = Signal()
        s_j3c = Signal()
        s_j3d = Signal()
        s_j3e = Signal()
        s_j3clk = Signal()
        s_j3stb = Signal()
        s_j3oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk = ClockSignal(),
            i_ctrl_en = s_j3_ctrl_en,
            i_ctrl_addr = s_j3_ctrl_addr,
            i_ctrl_wdat = s_j3_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0 = s_j3r0,
            o_panel_g0 = s_j3g0,
            o_panel_b0 = s_j3b0,
            o_panel_r1 = s_j3r1,
            o_panel_g1 = s_j3g1,
            o_panel_b1 = s_j3b1,
            o_panel_a = s_j3a,
            o_panel_b = s_j3b,
            o_panel_c = s_j3c,
            o_panel_d = s_j3d,
            o_panel_e = s_j3e,
            o_panel_clk = s_j3clk,
            o_panel_stb = s_j3stb,
            o_panel_oe = s_j3oe
        )

        j3r0 = platform.request("panel_r0", 3)
        j3g0 = platform.request("panel_g0", 3)
        j3b0 = platform.request("panel_b0", 3)
        j3r1 = platform.request("panel_r1", 3)
        j3g1 = platform.request("panel_g1", 3)
        j3b1 = platform.request("panel_b1", 3)
        #j3E = platform.request("panel_e", 3)
        #j3A = platform.request("panel_a", 3)
        #j3B = platform.request("panel_b", 3)
        #j3C = platform.request("panel_c", 3)
        #j3D = platform.request("panel_d", 3)
        #j3clk = platform.request("panel_clk", 3)
        #j3stb = platform.request("panel_stb", 3)
        #j3oe = platform.request("panel_oe", 3)

        self.comb += j3r0.eq(s_j3r0)
        self.comb += j3g0.eq(s_j3g0)
        self.comb += j3b0.eq(s_j3b0)
        self.comb += j3r1.eq(s_j3r1)
        self.comb += j3g1.eq(s_j3g1)
        self.comb += j3b1.eq(s_j3b1)
        #self.comb += j3A.eq(s_j3a)
        #self.comb += j3B.eq(s_j3b)
        #self.comb += j3C.eq(s_j3c)
        #self.comb += j3D.eq(s_j3d)
        #self.comb += j3E.eq(s_j3e)
        #self.comb += j3clk.eq(s_j3clk)
        #self.comb += j3stb.eq(s_j3stb)
        #self.comb += j3oe.eq(s_j3oe)
        self.comb += s_j3_ctrl_en.eq(s_shared_en[1])
        self.comb += s_j3_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j3_ctrl_wdat.eq(s_shared_wdat)

        s_j2_ctrl_en = Signal()
        s_j2_ctrl_addr = Signal(16)
        s_j2_ctrl_wdat = Signal(24)
        s_j2r0 = Signal()
        s_j2g0 = Signal()
        s_j2b0 = Signal()
        s_j2r1 = Signal()
        s_j2g1 = Signal()
        s_j2b1 = Signal()
        s_j2a = Signal()
        s_j2b = Signal()
        s_j2c = Signal()
        s_j2d = Signal()
        s_j2e = Signal()
        s_j2clk = Signal()
        s_j2stb = Signal()
        s_j2oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk = ClockSignal(),
            i_ctrl_en = s_j2_ctrl_en,
            i_ctrl_addr = s_j2_ctrl_addr,
            i_ctrl_wdat = s_j2_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0 = s_j2r0,
            o_panel_g0 = s_j2g0,
            o_panel_b0 = s_j2b0,
            o_panel_r1 = s_j2r1,
            o_panel_g1 = s_j2g1,
            o_panel_b1 = s_j2b1,
            o_panel_a = s_j2a,
            o_panel_b = s_j2b,
            o_panel_c = s_j2c,
            o_panel_d = s_j2d,
            o_panel_e = s_j2e,
            o_panel_clk = s_j2clk,
            o_panel_stb = s_j2stb,
            o_panel_oe = s_j2oe
        )

        j2r0 = platform.request("panel_r0", 2)
        j2g0 = platform.request("panel_g0", 2)
        j2b0 = platform.request("panel_b0", 2)
        j2r1 = platform.request("panel_r1", 2)
        j2g1 = platform.request("panel_g1", 2)
        j2b1 = platform.request("panel_b1", 2)
        #j2E = platform.request("panel_e", 2)
        #j2A = platform.request("panel_a", 2)
        #j2B = platform.request("panel_b", 2)
        #j2C = platform.request("panel_c", 2)
        #j2D = platform.request("panel_d", 2)
        #j2clk = platform.request("panel_clk", 2)
        #j2stb = platform.request("panel_stb", 2)
        #j2oe = platform.request("panel_oe", 2)

        self.comb += j2r0.eq(s_j2r0)
        self.comb += j2g0.eq(s_j2g0)
        self.comb += j2b0.eq(s_j2b0)
        self.comb += j2r1.eq(s_j2r1)
        self.comb += j2g1.eq(s_j2g1)
        self.comb += j2b1.eq(s_j2b1)
        #self.comb += j2A.eq(s_j2a)
        #self.comb += j2B.eq(s_j2b)
        #self.comb += j2C.eq(s_j2c)
        #self.comb += j2D.eq(s_j2d)
        #self.comb += j2E.eq(s_j2e)
        #self.comb += j2clk.eq(s_j2clk)
        #self.comb += j2stb.eq(s_j2stb)
        #self.comb += j2oe.eq(s_j2oe)
        self.comb += s_j2_ctrl_en.eq(s_shared_en[2])
        self.comb += s_j2_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j2_ctrl_wdat.eq(s_shared_wdat)

        s_j1_ctrl_en = Signal()
        s_j1_ctrl_addr = Signal(16)
        s_j1_ctrl_wdat = Signal(24)
        s_j1r0 = Signal()
        s_j1g0 = Signal()
        s_j1b0 = Signal()
        s_j1r1 = Signal()
        s_j1g1 = Signal()
        s_j1b1 = Signal()
        s_j1a = Signal()
        s_j1b = Signal()
        s_j1c = Signal()
        s_j1d = Signal()
        s_j1e = Signal()
        s_j1clk = Signal()
        s_j1stb = Signal()
        s_j1oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk = ClockSignal(),
            i_ctrl_en = s_j1_ctrl_en,
            i_ctrl_addr = s_j1_ctrl_addr,
            i_ctrl_wdat = s_j1_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0 = s_j1r0,
            o_panel_g0 = s_j1g0,
            o_panel_b0 = s_j1b0,
            o_panel_r1 = s_j1r1,
            o_panel_g1 = s_j1g1,
            o_panel_b1 = s_j1b1,
            o_panel_a = s_j1a,
            o_panel_b = s_j1b,
            o_panel_c = s_j1c,
            o_panel_d = s_j1d,
            o_panel_e = s_j1e,
            o_panel_clk = s_j1clk,
            o_panel_stb = s_j1stb,
            o_panel_oe = s_j1oe
        )

        j1r0 = platform.request("panel_r0", 1)
        j1g0 = platform.request("panel_g0", 1)
        j1b0 = platform.request("panel_b0", 1)
        j1r1 = platform.request("panel_r1", 1)
        j1g1 = platform.request("panel_g1", 1)
        j1b1 = platform.request("panel_b1", 1)
        #j1E = platform.request("panel_e", 1)
        #j1A = platform.request("panel_a", 1)
        #j1B = platform.request("panel_b", 1)
        #j1C = platform.request("panel_c", 1)
        #j1D = platform.request("panel_d", 1)
        #j1clk = platform.request("panel_clk", 1)
        #j1stb = platform.request("panel_stb", 1)
        #j1oe = platform.request("panel_oe", 1)

        self.comb += j1r0.eq(s_j1r0)
        self.comb += j1g0.eq(s_j1g0)
        self.comb += j1b0.eq(s_j1b0)
        self.comb += j1r1.eq(s_j1r1)
        self.comb += j1g1.eq(s_j1g1)
        self.comb += j1b1.eq(s_j1b1)
        #self.comb += j1A.eq(s_j1a)
        #self.comb += j1B.eq(s_j1b)
        #self.comb += j1C.eq(s_j1c)
        #self.comb += j1D.eq(s_j1d)
        #self.comb += j1E.eq(s_j1e)
        #self.comb += j1clk.eq(s_j1clk)
        #self.comb += j1stb.eq(s_j1stb)
        #self.comb += j1oe.eq(s_j1oe)
        self.comb += s_j1_ctrl_en.eq(s_shared_en[3])
        self.comb += s_j1_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j1_ctrl_wdat.eq(s_shared_wdat)

        s_j5_ctrl_en = Signal()
        s_j5_ctrl_addr = Signal(16)
        s_j5_ctrl_wdat = Signal(24)
        s_j5r0 = Signal()
        s_j5g0 = Signal()
        s_j5b0 = Signal()
        s_j5r1 = Signal()
        s_j5g1 = Signal()
        s_j5b1 = Signal()
        s_j5a = Signal()
        s_j5b = Signal()
        s_j5c = Signal()
        s_j5d = Signal()
        s_j5e = Signal()
        s_j5clk = Signal()
        s_j5stb = Signal()
        s_j5oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk = ClockSignal(),
            i_ctrl_en = s_j5_ctrl_en,
            i_ctrl_addr = s_j5_ctrl_addr,
            i_ctrl_wdat = s_j5_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0 = s_j5r0,
            o_panel_g0 = s_j5g0,
            o_panel_b0 = s_j5b0,
            o_panel_r1 = s_j5r1,
            o_panel_g1 = s_j5g1,
            o_panel_b1 = s_j5b1,
            o_panel_a = s_j5a,
            o_panel_b = s_j5b,
            o_panel_c = s_j5c,
            o_panel_d = s_j5d,
            o_panel_e = s_j5e,
            o_panel_clk = s_j5clk,
            o_panel_stb = s_j5stb,
            o_panel_oe = s_j5oe
        )

        j5r0 = platform.request("panel_r0", 5)
        j5g0 = platform.request("panel_g0", 5)
        j5b0 = platform.request("panel_b0", 5)
        j5r1 = platform.request("panel_r1", 5)
        j5g1 = platform.request("panel_g1", 5)
        j5b1 = platform.request("panel_b1", 5)
        #j5E = platform.request("panel_e", 5)
        #j5A = platform.request("panel_a", 5)
        #j5B = platform.request("panel_b", 5)
        #j5C = platform.request("panel_c", 5)
        #j5D = platform.request("panel_d", 5)
        #j5clk = platform.request("panel_clk", 5)
        #j5stb = platform.request("panel_stb", 5)
        #j5oe = platform.request("panel_oe", 5)

        self.comb += j5r0.eq(s_j5r0)
        self.comb += j5g0.eq(s_j5g0)
        self.comb += j5b0.eq(s_j5b0)
        self.comb += j5r1.eq(s_j5r1)
        self.comb += j5g1.eq(s_j5g1)
        self.comb += j5b1.eq(s_j5b1)
        #self.comb += j5A.eq(s_j5a)
        #self.comb += j5B.eq(s_j5b)
        #self.comb += j5C.eq(s_j5c)
        #self.comb += j5D.eq(s_j5d)
        #self.comb += j5E.eq(s_j5e)
        #self.comb += j5clk.eq(s_j5clk)
        #self.comb += j5stb.eq(s_j5stb)
        #self.comb += j5oe.eq(s_j5oe)
        self.comb += s_j5_ctrl_en.eq(s_shared_en[4])
        self.comb += s_j5_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j5_ctrl_wdat.eq(s_shared_wdat)

        s_j6_ctrl_en = Signal()
        s_j6_ctrl_addr = Signal(16)
        s_j6_ctrl_wdat = Signal(24)
        s_j6r0 = Signal()
        s_j6g0 = Signal()
        s_j6b0 = Signal()
        s_j6r1 = Signal()
        s_j6g1 = Signal()
        s_j6b1 = Signal()
        s_j6a = Signal()
        s_j6b = Signal()
        s_j6c = Signal()
        s_j6d = Signal()
        s_j6e = Signal()
        s_j6clk = Signal()
        s_j6stb = Signal()
        s_j6oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk      = ClockSignal(),
            i_ctrl_en       = s_j6_ctrl_en,
            i_ctrl_addr     = s_j6_ctrl_addr,
            i_ctrl_wdat     = s_j6_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0      = s_j6r0,
            o_panel_g0      = s_j6g0,
            o_panel_b0      = s_j6b0,
            o_panel_r1      = s_j6r1,
            o_panel_g1      = s_j6g1,
            o_panel_b1      = s_j6b1,
            o_panel_a       = s_j6a,
            o_panel_b       = s_j6b,
            o_panel_c       = s_j6c,
            o_panel_d       = s_j6d,
            o_panel_e       = s_j6e,
            o_panel_clk     = s_j6clk,
            o_panel_stb     = s_j6stb,
            o_panel_oe      = s_j6oe
        )

        j6r0 = platform.request("panel_r0",    6)
        j6g0 = platform.request("panel_g0",    6)
        j6b0 = platform.request("panel_b0",    6)
        j6r1 = platform.request("panel_r1",    6)
        j6g1 = platform.request("panel_g1",    6)
        j6b1 = platform.request("panel_b1",    6)
        #j6E = platform.request("panel_e",     6)
        #j6A = platform.request("panel_a",     6)
        #j6B = platform.request("panel_b",     6)
        #j6C = platform.request("panel_c",     6)
        #j6D = platform.request("panel_d",     6)
        #j6clk = platform.request("panel_clk", 6)
        #j6stb = platform.request("panel_stb", 6)
        #j6oe = platform.request("panel_oe",   6)

        self.comb += j6r0.eq(s_j6r0)
        self.comb += j6g0.eq(s_j6g0)
        self.comb += j6b0.eq(s_j6b0)
        self.comb += j6r1.eq(s_j6r1)
        self.comb += j6g1.eq(s_j6g1)
        self.comb += j6b1.eq(s_j6b1)
        #self.comb += j6A.eq(s_j6a)
        #self.comb += j6B.eq(s_j6b)
        #self.comb += j6C.eq(s_j6c)
        #self.comb += j6D.eq(s_j6d)
        #self.comb += j6E.eq(s_j6e)
        #self.comb += j6clk.eq(s_j6clk)
        #self.comb += j6stb.eq(s_j6stb)
        #self.comb += j6oe.eq(s_j6oe)
        self.comb += s_j6_ctrl_en.eq(s_shared_en[4])
        self.comb += s_j6_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j6_ctrl_wdat.eq(s_shared_wdat)

        s_j7_ctrl_en = Signal()
        s_j7_ctrl_addr = Signal(16)
        s_j7_ctrl_wdat = Signal(24)
        s_j7r0 = Signal()
        s_j7g0 = Signal()
        s_j7b0 = Signal()
        s_j7r1 = Signal()
        s_j7g1 = Signal()
        s_j7b1 = Signal()
        s_j7a = Signal()
        s_j7b = Signal()
        s_j7c = Signal()
        s_j7d = Signal()
        s_j7e = Signal()
        s_j7clk = Signal()
        s_j7stb = Signal()
        s_j7oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk      = ClockSignal(),
            i_ctrl_en       = s_j7_ctrl_en,
            i_ctrl_addr     = s_j7_ctrl_addr,
            i_ctrl_wdat     = s_j7_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0      = s_j7r0,
            o_panel_g0      = s_j7g0,
            o_panel_b0      = s_j7b0,
            o_panel_r1      = s_j7r1,
            o_panel_g1      = s_j7g1,
            o_panel_b1      = s_j7b1,
            o_panel_a       = s_j7a,
            o_panel_b       = s_j7b,
            o_panel_c       = s_j7c,
            o_panel_d       = s_j7d,
            o_panel_e       = s_j7e,
            o_panel_clk     = s_j7clk,
            o_panel_stb     = s_j7stb,
            o_panel_oe      = s_j7oe
        )

        j7r0 = platform.request("panel_r0",    7)
        j7g0 = platform.request("panel_g0",    7)
        j7b0 = platform.request("panel_b0",    7)
        j7r1 = platform.request("panel_r1",    7)
        j7g1 = platform.request("panel_g1",    7)
        j7b1 = platform.request("panel_b1",    7)
        #j7E = platform.request("panel_e",     7)
        #j7A = platform.request("panel_a",     7)
        #j7B = platform.request("panel_b",     7)
        #j7C = platform.request("panel_c",     7)
        #j7D = platform.request("panel_d",     7)
        #j7clk = platform.request("panel_clk", 7)
        #j7stb = platform.request("panel_stb", 7)
        #j7oe = platform.request("panel_oe",   7)

        self.comb += j7r0.eq(s_j7r0)
        self.comb += j7g0.eq(s_j7g0)
        self.comb += j7b0.eq(s_j7b0)
        self.comb += j7r1.eq(s_j7r1)
        self.comb += j7g1.eq(s_j7g1)
        self.comb += j7b1.eq(s_j7b1)
        #self.comb += j7A.eq(s_j7a)
        #self.comb += j7B.eq(s_j7b)
        #self.comb += j7C.eq(s_j7c)
        #self.comb += j7D.eq(s_j7d)
        #self.comb += j7E.eq(s_j7e)
        #self.comb += j7clk.eq(s_j7clk)
        #self.comb += j7stb.eq(s_j7stb)
        #self.comb += j7oe.eq(s_j7oe)
        self.comb += s_j7_ctrl_en.eq(s_shared_en[4])
        self.comb += s_j7_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j7_ctrl_wdat.eq(s_shared_wdat)

        s_j8_ctrl_en = Signal()
        s_j8_ctrl_addr = Signal(16)
        s_j8_ctrl_wdat = Signal(24)
        s_j8r0 = Signal()
        s_j8g0 = Signal()
        s_j8b0 = Signal()
        s_j8r1 = Signal()
        s_j8g1 = Signal()
        s_j8b1 = Signal()
        s_j8a = Signal()
        s_j8b = Signal()
        s_j8c = Signal()
        s_j8d = Signal()
        s_j8e = Signal()
        s_j8clk = Signal()
        s_j8stb = Signal()
        s_j8oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk      = ClockSignal(),
            i_ctrl_en       = s_j8_ctrl_en,
            i_ctrl_addr     = s_j8_ctrl_addr,
            i_ctrl_wdat     = s_j8_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0      = s_j8r0,
            o_panel_g0      = s_j8g0,
            o_panel_b0      = s_j8b0,
            o_panel_r1      = s_j8r1,
            o_panel_g1      = s_j8g1,
            o_panel_b1      = s_j8b1,
            o_panel_a       = s_j8a,
            o_panel_b       = s_j8b,
            o_panel_c       = s_j8c,
            o_panel_d       = s_j8d,
            o_panel_e       = s_j8e,
            o_panel_clk     = s_j8clk,
            o_panel_stb     = s_j8stb,
            o_panel_oe      = s_j8oe
        )

        j8r0 = platform.request("panel_r0",    8)
        j8g0 = platform.request("panel_g0",    8)
        j8b0 = platform.request("panel_b0",    8)
        j8r1 = platform.request("panel_r1",    8)
        j8g1 = platform.request("panel_g1",    8)
        j8b1 = platform.request("panel_b1",    8)
        #j8E = platform.request("panel_e",     8)
        #j8A = platform.request("panel_a",     8)
        #j8B = platform.request("panel_b",     8)
        #j8C = platform.request("panel_c",     8)
        #j8D = platform.request("panel_d",     8)
        #j8clk = platform.request("panel_clk", 8)
        #j8stb = platform.request("panel_stb", 8)
        #j8oe = platform.request("panel_oe",   8)

        self.comb += j8r0.eq(s_j8r0)
        self.comb += j8g0.eq(s_j8g0)
        self.comb += j8b0.eq(s_j8b0)
        self.comb += j8r1.eq(s_j8r1)
        self.comb += j8g1.eq(s_j8g1)
        self.comb += j8b1.eq(s_j8b1)
        #self.comb += j8A.eq(s_j8a)
        #self.comb += j8B.eq(s_j8b)
        #self.comb += j8C.eq(s_j8c)
        #self.comb += j8D.eq(s_j8d)
        #self.comb += j8E.eq(s_j8e)
        #self.comb += j8clk.eq(s_j8clk)
        #self.comb += j8stb.eq(s_j8stb)
        #self.comb += j8oe.eq(s_j8oe)
        self.comb += s_j8_ctrl_en.eq(s_shared_en[4])
        self.comb += s_j8_ctrl_addr.eq(s_shared_addr)
        self.comb += s_j8_ctrl_wdat.eq(s_shared_wdat)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, int(sys_clk_freq),
            use_internal_osc = use_internal_osc,
            with_usb_pll     = False,
            with_rst         = False,
            sdram_rate       = sdram_rate
        )

        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self,
            platform,
            clk_freq=int(sys_clk_freq),
        )

        # LiteEth UDP/IP ---------------------------------------------------------------------------
        self.ethphy = LiteEthPHYRGMII(
            clock_pads = self.platform.request("eth_clocks", eth_phy),
            pads       = self.platform.request("eth", eth_phy),
            tx_delay   = 0e-9,
        )
        self.submodules.ethcore = udp_core = LiteEthUDPIPCore(
            self.ethphy,
            mac_address = 0x726b895bc2e2,
            ip_address  = eth_ip,
            clk_freq    = int(sys_clk_freq),
            dw          = 32,
            with_ip_broadcast = True,
            with_sys_datapath = True,
            endianness  = "big",
            #interface   = "crossbar",
        )

        # Instantiate a dummy port to make the UDP IP Core and ARP circuitry work
        udp_port = udp_core.udp.crossbar.get_port(2025, dw=32, cd="sys")
        self.comb += udp_port.source.ready.eq(1)

        udp_rx = udp_core.udp.rx.source

        s_udp_reset = Signal()
        s_udp_source_valid = Signal()
        s_udp_source_last = Signal()
        s_udp_source_ready = Signal()
        s_udp_source_src_port = Signal(16)
        s_udp_source_dst_port = Signal(16)
        s_udp_source_ip_address = Signal(32)
        s_udp_source_length = Signal(16)
        s_udp_source_data = Signal(32)
        s_udp_source_error = Signal(4)
        s_udp_led = Signal()
        self.specials += Instance("udp_panel_writer",
            i_clk = ClockSignal(),
            i_reset = s_udp_reset,
            i_udp_source_valid = s_udp_source_valid,
            i_udp_source_last = s_udp_source_last,
            o_udp_source_ready = s_udp_source_ready,
            i_udp_source_src_port = s_udp_source_src_port,
            i_udp_source_dst_port = s_udp_source_dst_port,
            i_udp_source_ip_address = s_udp_source_ip_address,
            i_udp_source_length = s_udp_source_length,
            i_udp_source_data = s_udp_source_data,
            i_udp_source_error = s_udp_source_error,
            o_ctrl_en = s_shared_en,
            o_ctrl_addr = s_shared_addr,
            o_ctrl_wdat = s_shared_wdat,
            o_led_reg = s_udp_led,
        )
        platform.add_source("udp_panel_writer.v")

        self.comb += s_udp_reset.eq(0)
        self.sync += s_udp_source_valid.eq(udp_rx.valid)
        self.sync += s_udp_source_last.eq(udp_rx.last)
        self.sync += udp_rx.ready.eq(s_udp_source_ready)
        self.sync += s_udp_source_dst_port.eq(udp_rx.param.dst_port)
        self.sync += s_udp_source_src_port.eq(15)
        self.sync += s_udp_source_data.eq(udp_rx.payload.data)
        self.sync += s_udp_source_error.eq(udp_rx.payload.error)

        s_test_port = Signal()
        self.comb += s_test_port.eq((udp_core.udp.rx.source.param.dst_port[15] == 1) & udp_core.udp.rx.source.valid)
        led = platform.request("user_led_n", 0)
        self.comb += led.eq(s_udp_led)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q32JV as SpiFlashModule

            from litespi.opcodes import SpiNorFlashOpCodes
            self.mem_map["spiflash"] = 0x20000000
            self.add_spi_flash(mode="1x", module=SpiFlashModule(SpiNorFlashOpCodes.READ_1_1_1), with_master=False)


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=colorlight_5a_75b.Platform, description="LiteX SoC on Colorlight 5A-75X.")
    parser.add_target_argument("--revision",          default="8.2",             help="Board revision (6.0, 6.1, 7.0, 8.0, or 8.2).")
    parser.add_target_argument("--sys-clk-freq",      default=50e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--eth-ip",            default="192.168.10.30",   help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-phy",           default=0, type=int,       help="Ethernet PHY (0 or 1).")
    parser.add_target_argument("--sdram-rate",        default="1:1",             help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    parser.add_target_argument("--with-spi-flash",    action="store_true",       help="Add SPI flash support to the SoC")
    parser.add_target_argument("--flash",             action="store_true",       help="Flash the code to the target FPGA")
    args = parser.parse_args()

    soc = BaseSoC(revision=args.revision,
        sys_clk_freq     = args.sys_clk_freq,
        toolchain        = args.toolchain,
        eth_ip           = args.eth_ip,
        eth_phy          = args.eth_phy,
        sdram_rate       = args.sdram_rate,
        with_spi_flash   = args.with_spi_flash
    )
    builder = Builder(soc, **parser.builder_argdict)

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

    if args.flash:
        prog = soc.platform.create_programmer()
        os.system("cp bit_to_flash.py build/colorlight_5a_75b/gateware/")
        os.system("cd build/colorlight_5a_75b/gateware/ && ./bit_to_flash.py colorlight_5a_75b.bit wyrm_flash.svf")
        prog.load_bitstream("build/colorlight_5a_75b/gateware/wyrm_flash.svf")

if __name__ == "__main__":
    main()
