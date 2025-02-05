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

from litedram.modules import M12L16161A, M12L64322A
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from liteeth.phy.ecp5rgmii import LiteEthPHYRGMII
from litex.build.generic_platform import *

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

        rst_n = 1 if not with_rst else platform.request("user_btn_n", 0)

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

class BaseSoC(SoCCore):
    def __init__(self, revision, sys_clk_freq=50e6, toolchain="trellis",
        with_ethernet    = False,
        with_etherbone   = False,
        with_litescope   = False,
        eth_ip           = "192.168.1.91",
        eth_phy          = 0,
        use_internal_osc = False,
        sdram_rate       = "1:1",
        with_spi_flash   = False,
        rom              = None,
        **kwargs):
        platform = colorlight_5a_75b.Platform(revision=revision, toolchain=toolchain)

        # LED Panel --------------------------------------------------------------------------------
        s_shared_en = Signal(4)
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
        j4r0 = platform.request("panel_r0", 4);
        j4g0 = platform.request("panel_g0", 4);
        j4b0 = platform.request("panel_b0", 4);
        j4r1 = platform.request("panel_r1", 4);
        j4g1 = platform.request("panel_g1", 4);
        j4b1 = platform.request("panel_b1", 4);
        j4E = platform.request("panel_e", 4);
        j4A = platform.request("panel_a", 4);
        j4B = platform.request("panel_b", 4);
        j4C = platform.request("panel_c", 4);
        j4D = platform.request("panel_d", 4);
        j4clk = platform.request("panel_clk", 4);
        j4stb = platform.request("panel_stb", 4);
        j4oe = platform.request("panel_oe", 4);

        self.panel_en = CSRStorage(size=4)
        self.panel_addr = CSRStorage(size=16)
        self.panel_wdat = CSRStorage(size=24)

        self.comb += s_shared_en.eq(self.panel_en.storage)

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
        self.comb += s_j4_ctrl_addr.eq(self.panel_addr.storage)
        self.comb += s_j4_ctrl_wdat.eq(self.panel_wdat.storage)

        # CRG --------------------------------------------------------------------------------------
        with_rst     = kwargs["uart_name"] not in ["serial", "crossover"] # serial_rx shared with user_btn_n.
        with_usb_pll = kwargs.get("uart_name", None) == "usb_acm"
        self.crg = _CRG(platform, sys_clk_freq,
            use_internal_osc = use_internal_osc,
            with_usb_pll     = with_usb_pll,
            with_rst         = with_rst,
            sdram_rate       = sdram_rate
        )

        # ROM --------------------------------------------------------------------------------------
        kwargs["integrated_rom_size"] = 12288
        if rom is not None:
            kwargs["integrated_rom_init"] = get_mem_data(rom, endianness="little")

        kwargs["integrated_sram_size"] = 8192

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self,
            platform,
            int(sys_clk_freq),
            ident="Wyrmies",
            **kwargs
        )

        # GPIOs ------------------------------------------------------------------------------------

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            sdram_cls  = M12L64322A
            self.add_sdram("sdram",
                phy                     = self.sdrphy,
                module                  = sdram_cls(sys_clk_freq, sdram_rate),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_full_memory_we = False,

            )

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone or with_litescope:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy),
                tx_delay   = 0e-9)
        if with_ethernet:
            self.add_ethernet(phy=self.ethphy, data_width=32)
        if with_etherbone or with_litescope:
            self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, data_width=32, with_ethmac=True)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q32JV as SpiFlashModule

            from litespi.opcodes import SpiNorFlashOpCodes
            self.mem_map["spiflash"] = 0x20000000
            self.add_spi_flash(mode="1x", module=SpiFlashModule(SpiNorFlashOpCodes.READ_1_1_1), with_master=False)

        if with_litescope:
            analyzer_signals = [
                # IBus (could also just added as self.cpu.ibus)
                self.cpu.ibus.stb,
                self.cpu.ibus.cyc,
                self.cpu.ibus.adr,
                self.cpu.ibus.we,
                self.cpu.ibus.ack,
                self.cpu.ibus.sel,
                self.cpu.ibus.dat_w,
                self.cpu.ibus.dat_r,

                # DBus (could also just added as self.cpu.dbus)
                self.cpu.dbus.stb,
                self.cpu.dbus.cyc,
                self.cpu.dbus.adr,
                self.cpu.dbus.we,
                self.cpu.dbus.ack,
                self.cpu.dbus.sel,
                self.cpu.dbus.dat_w,
                self.cpu.dbus.dat_r,
            ]

            from litescope import LiteScopeAnalyzer
            self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
                depth        = 512,
                clock_domain = "sys",
                samplerate   = sys_clk_freq,
                csr_csv      = "analyzer.csv"
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=colorlight_5a_75b.Platform, description="LiteX SoC on Colorlight 5A-75X.")
    parser.add_target_argument("--revision",          default="8.2",            help="Board revision (6.0, 6.1, 7.0, 8.0, or 8.2).")
    parser.add_target_argument("--sys-clk-freq",      default=50e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",           action="store_true",      help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",          action="store_true",      help="Enable Etherbone support.")
    ethopts.add_argument("--with-litescope",          action="store_true",      help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",            default="192.168.1.91",   help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--eth-phy",           default=0, type=int,      help="Ethernet PHY (0 or 1).")
    parser.add_target_argument("--use-internal-osc",  action="store_true",      help="Use internal oscillator.")
    parser.add_target_argument("--sdram-rate",        default="1:1",            help="SDRAM Rate (1:1 Full Rate or 1:2 Half Rate).")
    parser.add_target_argument("--with-spi-flash",    action="store_true",      help="Add SPI flash support to the SoC")
    parser.add_target_argument("--flash",             action="store_true",      help="Flash the code to the target FPGA")
    parser.add_target_argument("--rom",               default=None,             help="ROM default contents.")
    args = parser.parse_args()

    soc = BaseSoC(revision=args.revision,
        sys_clk_freq     = args.sys_clk_freq,
        toolchain        = args.toolchain,
        with_ethernet    = args.with_ethernet,
        with_etherbone   = args.with_etherbone,
        with_litescope   = args.with_litescope,
        eth_ip           = args.eth_ip,
        eth_phy          = args.eth_phy,
        use_internal_osc = args.use_internal_osc,
        sdram_rate       = args.sdram_rate,
        with_spi_flash   = args.with_spi_flash,
        rom              = args.rom,
        **parser.soc_argdict
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
