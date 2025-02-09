#!/usr/bin/env python3

from typing import Any, Generator
from migen import *
from migen.fhdl.structure import _Assign
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

class InstanceParamters(Record):
    def __init__(self, instance:Instance,
            name:str = None,
            **kwargs) -> None:
        layout = []
        self.instance = instance
        for item in instance.items:
            if isinstance(item, Instance.Input) \
                    and isinstance(item.expr, Signal):
                layout.append((item.name, item.expr.nbits, DIR_S_TO_M))
            elif isinstance(item, Instance.Output) \
                    and isinstance(item.expr, Signal):
                layout.append((item.name, item.expr.nbits, DIR_M_TO_S))
        Record.__init__(self,
            layout=layout,
            name=name,
            **kwargs)

    def attach(self):
        """
        Return the migen statements to connect the InstanceParameters(Record)
        to the Instance.
        """
        for item in self.instance.items:
            if isinstance(item, Instance.Input) \
                    and isinstance(item.expr, Signal):
                yield item.expr.eq(getattr(self, item.name))
            elif isinstance(item, Instance.Output) \
                    and isinstance(item.expr, Signal):
                yield getattr(self, item.name).eq(item.expr)

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

        # Extend Platform --------------------------------------------------------------------------
        platform.add_source("ledpanel.v")

        platform.add_extension([
            ("shared_output", 0,
                Subsignal("panel_e", Pins("j1:7")),
                Subsignal("panel_a", Pins("j1:8")),
                Subsignal("panel_b", Pins("j1:9")),
                Subsignal("panel_c", Pins("j1:10")),
                Subsignal("panel_d", Pins("j1:11")),
                Subsignal("panel_clk", Pins("j1:12")),
                Subsignal("panel_stb", Pins("j1:13")),
                Subsignal("panel_oe", Pins("j1:14")),
                IOStandard("LVCMOS33"))])

        for jumper in (1,2,3,4,5,6,7,8):
            platform.add_extension([
                ("rgb_output", jumper,
                Subsignal("panel_r0", Pins(f"j{jumper}:0")),
                Subsignal("panel_g0", Pins(f"j{jumper}:1")),
                Subsignal("panel_b0", Pins(f"j{jumper}:2")),
                Subsignal("panel_r1", Pins(f"j{jumper}:4")),
                Subsignal("panel_g1", Pins(f"j{jumper}:5")),
                Subsignal("panel_b1", Pins(f"j{jumper}:6")),
                IOStandard("LVCMOS33"))])

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

        # LED Panel --------------------------------------------------------------------------------
        self.add_ledpanel(jumper=4, select=0, main_panel=True)
        self.add_ledpanel(jumper=3, select=1)
        self.add_ledpanel(jumper=2, select=2)
        self.add_ledpanel(jumper=1, select=3)

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

    def add_ledpanel_csrs(self) -> None:
        if not getattr(self, "panel_en", False):
            self.panel_en = CSRStorage(size=4)
            self.panel_addr = CSRStorage(size=16)
            self.panel_wdat = CSRStorage(size=24)

    def add_ledpanel(self, jumper:int, select:int, main_panel:bool = False) -> None:
        platform = self.platform

        self.add_ledpanel_csrs()

        panel = Instance("ledpanel",
            Instance.Input("ctrl_clk", ClockSignal()),
            Instance.Input("ctrl_en"),
            Instance.Input("ctrl_addr", Signal(16)),
            Instance.Input("ctrl_wdat", Signal(24)),
            Instance.Input("display_clock", ClockSignal("sys")),
            Instance.Output("panel_r0"),
            Instance.Output("panel_g0"),
            Instance.Output("panel_b0"),
            Instance.Output("panel_r1"),
            Instance.Output("panel_g1"),
            Instance.Output("panel_b1"),
            Instance.Output("panel_a"),
            Instance.Output("panel_b"),
            Instance.Output("panel_c"),
            Instance.Output("panel_d"),
            Instance.Output("panel_e"),
            Instance.Output("panel_clk"),
            Instance.Output("panel_stb"),
            Instance.Output("panel_oe"),
        )

        panel_parameters = InstanceParamters(panel)
        self.comb += panel_parameters.attach()

        self.specials += panel

        if main_panel:
            shared_output = platform.request("shared_output")
            self.comb += panel_parameters.connect(
                shared_output,
                keep=[
                    "panel_a",
                    "panel_b",
                    "panel_c",
                    "panel_d",
                    "panel_e",
                    "panel_clk",
                    "panel_stb",
                    "panel_oe",
                ])

        rgb_output = platform.request("rgb_output", number=jumper)
        self.comb += panel_parameters.connect(
            rgb_output,
            keep = [
                "panel_r0",
                "panel_b0",
                "panel_g0",
                "panel_r1",
                "panel_b1",
                "panel_g1",
            ]
        )

        s_ctrl_en = panel_parameters.ctrl_en
        s_ctrl_addr = panel_parameters.ctrl_addr
        s_ctrl_wdat = panel_parameters.ctrl_wdat

        self.comb += [
            s_ctrl_en.eq(self.panel_en.storage[select]),
            s_ctrl_addr.eq(self.panel_addr.storage),
            s_ctrl_wdat.eq(self.panel_wdat.storage),
        ]


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
