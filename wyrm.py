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
    # GPIOs.
    ("gpio", 0, Pins("j4:0"), IOStandard("LVCMOS33")),
    ("gpio", 1, Pins("j4:1"), IOStandard("LVCMOS33")),
    ("gpio", 2, Pins("j4:2"), IOStandard("LVCMOS33")),
    ("gpio", 3, Pins("j4:4"), IOStandard("LVCMOS33")),
    ("gpio", 4, Pins("j4:5"), IOStandard("LVCMOS33")),
    ("gpio", 5, Pins("j4:6"), IOStandard("LVCMOS33")),
    ("gpio", 6, Pins("j4:7"), IOStandard("LVCMOS33")),
    ("gpio", 7, Pins("j4:8"), IOStandard("LVCMOS33")),
    ("gpio", 8, Pins("j4:9"), IOStandard("LVCMOS33")),
    ("gpio", 9, Pins("j4:10"), IOStandard("LVCMOS33")),
    ("gpio", 10, Pins("j4:11"), IOStandard("LVCMOS33")),
    ("gpio", 11, Pins("j4:12"), IOStandard("LVCMOS33")),
    ("gpio", 12, Pins("j4:13"), IOStandard("LVCMOS33")),
    ("gpio", 13, Pins("j4:14"), IOStandard("LVCMOS33")),
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
        eth_ip           = "192.168.10.30",
        eth_phy          = 0,
        with_led_chaser  = False,
        use_internal_osc = False,
        sdram_rate       = "1:1",
        with_spi_flash   = False,
        rom              = None,
        **kwargs):
        platform = colorlight_5a_75b.Platform(revision=revision, toolchain=toolchain)

        # LED Panel --------------------------------------------------------------------------------
        panel_ctrl_en = Signal()
        panel_ctrl_addr = Signal(16)
        panel_ctrl_wdat = Signal(24)
        panel_r0 = Signal()
        panel_g0 = Signal()
        panel_b0 = Signal()
        panel_r1 = Signal()
        panel_g1 = Signal()
        panel_b1 = Signal()
        panel_a = Signal()
        panel_b = Signal()
        panel_c = Signal()
        panel_d = Signal()
        panel_e = Signal()
        panel_clk = Signal()
        panel_stb = Signal()
        panel_oe = Signal()
        self.specials += Instance("ledpanel",
            i_ctrl_clk = ClockSignal(),
            i_ctrl_en = panel_ctrl_en,
            i_ctrl_addr = panel_ctrl_addr,
            i_ctrl_wdat = panel_ctrl_wdat,
            i_display_clock = ClockSignal("sys"),
            o_panel_r0 = panel_r0,
            o_panel_g0 = panel_g0,
            o_panel_b0 = panel_b0,
            o_panel_r1 = panel_r1,
            o_panel_g1 = panel_g1,
            o_panel_b1 = panel_b1,
            o_panel_a = panel_a,
            o_panel_b = panel_b,
            o_panel_c = panel_c,
            o_panel_d = panel_d,
            o_panel_e = panel_e,
            o_panel_clk = panel_clk,
            o_panel_stb = panel_stb,
            o_panel_oe = panel_oe
        )
        platform.add_source("ledpanel.v")

        platform.add_extension(_gpios)
        r0 = platform.request("gpio", 0);
        g0 = platform.request("gpio", 1);
        b0 = platform.request("gpio", 2);
        r1 = platform.request("gpio", 3);
        g1 = platform.request("gpio", 4);
        b1 = platform.request("gpio", 5);
        muxE = platform.request("gpio", 6);
        muxA = platform.request("gpio", 7);
        muxB = platform.request("gpio", 8);
        muxC = platform.request("gpio", 9);
        muxD = platform.request("gpio", 10);
        j4clk = platform.request("gpio", 11);
        j4stb = platform.request("gpio", 12);
        j4oe = platform.request("gpio", 13);

        self.panel_en = CSRStorage(size=1)
        self.panel_addr = CSRStorage(size=16)
        self.panel_wdat = CSRStorage(size=24)

        self.comb += r0.eq(panel_r0)
        self.comb += g0.eq(panel_g0)
        self.comb += b0.eq(panel_b0)
        self.comb += r1.eq(panel_r1)
        self.comb += g1.eq(panel_g1)
        self.comb += b1.eq(panel_b1)
        self.comb += muxA.eq(panel_a)
        self.comb += muxB.eq(panel_b)
        self.comb += muxC.eq(panel_c)
        self.comb += muxD.eq(panel_d)
        self.comb += muxE.eq(panel_e)
        self.comb += j4clk.eq(panel_clk)
        self.comb += j4stb.eq(panel_stb)
        self.comb += j4oe.eq(panel_oe)
        self.comb += panel_ctrl_en.eq(self.panel_en.storage)
        self.comb += panel_ctrl_addr.eq(self.panel_addr.storage)
        self.comb += panel_ctrl_wdat.eq(self.panel_wdat.storage)

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
        kwargs["integrated_rom_size"] = 65536
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

        #self.r0 = GPIOOut(r0);
        #self.g0 = GPIOOut(g0);
        #self.b0 = GPIOOut(b0);
        #self.r1 = GPIOOut(r1);
        #self.g1 = GPIOOut(g1);
        #self.b1 = GPIOOut(b1);
        #self.muxE = GPIOOut(muxE);
        #self.muxA = GPIOOut(muxA);
        #self.muxB = GPIOOut(muxB);
        #self.muxC = GPIOOut(muxC);
        #self.muxD = GPIOOut(muxD);
        #self.j4clk = GPIOOut(j4clk);
        #self.j4stb = GPIOOut(j4stb);
        #self.j4oe = GPIOOut(j4oe);

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
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks", eth_phy),
                pads       = self.platform.request("eth", eth_phy),
                tx_delay   = 0e-9)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, data_width=32)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, data_width=32)

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
    parser.add_target_argument("--revision",          default="8.2",            help="Board revision (6.0, 6.1, 7.0, 8.0, or 8.2).")
    parser.add_target_argument("--sys-clk-freq",      default=50e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",           action="store_true",      help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",          action="store_true",      help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",            default="192.168.10.30",  help="Ethernet/Etherbone IP address.")
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
