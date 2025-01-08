LiteX-based MCU for display via UDP packets

Getting started with LiteX on Arch linux:
* Setup dependencies: `sudo pacman -S riscv64-elf-binutils riscv64-elf-gcc riscv64-elf-gdb riscv64-elf-newlib`
* Setup dependencies: `paru -S yosys verilator python312 nextpnr-git`
  * You may need to patch nextpnr-git so that it doesn't build "himbaechel"
* Make a directory for litex: `mkdir ~/litex` and then `cd ~/litex`
* Make a virtual env: `python3 -m venv .venv`
* Set python 3.12 for the venv: `virtualenv -p 3.12 .venv`
* Source: `source .venv/bin/activate`
* Clone: `git clone git@github.com:enjoy-digital/litex.git` and `cd litex`
* Install: `./litex_setup.py --init --install --config=full`

Actually building:
* Run `./wyrm.py --build` to bootstrap the environment
* `cd software` and then `make` and then `cd ..`
* Run `./wyrm.py --build --rom=software/demo.bin`

Now you should have the image needed to flash onto the FPGA

Connect an FT232H to your computer, and connect D0 to TCK, D1 to TDI, D2 to TDO,
D3 to TMS, and ground to ground.

Run `./wyrm.py --flash` and you should see a successful connect and after some
time the write should complete.

Connect a 3.3V FTDI adapter to J19 -
* `DATA_LED-` should be connected to the FTDI's RX pin
* `KEY+` should be connected to FTDI's TX pin

Open up a serial terminal with baud 115200, 8 bits, no parity, 1 stop bit
