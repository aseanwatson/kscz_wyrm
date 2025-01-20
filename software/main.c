#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <generated/soc.h>
#include <generated/mem.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <libliteeth/udp.h>
#include <generated/csr.h>

void udp_cb(unsigned int src_ip, unsigned short src_port, unsigned short dst_port, void *data, unsigned int length);
void udp_cb(unsigned int src_ip, unsigned short src_port, unsigned short dst_port, void *data, unsigned int length)
{
    for (uint32_t i = 0; i < length; i += 4) {
        main_panel_en_write(0);
        uint32_t stuff = ((uint32_t)((uint8_t *)data)[i] << 24)
            | ((uint32_t)((uint8_t *)data)[i+1] << 16)
            | ((uint32_t)((uint8_t *)data)[i+2] << 8)
            | (uint32_t)((uint8_t *)data)[i+3];
        uint32_t addr = stuff >> 18;
        uint32_t b = (stuff >> 12) & 0x3f;
        uint32_t r = (stuff >> 6) & 0x3f;
        uint32_t g = (stuff >> 0) & 0x3f;
        main_panel_wdat_write((r << 16) | (g << 8) | b);
        main_panel_addr_write(addr);
        main_panel_en_write(dst_port & 0xf);
    }
    main_panel_en_write(0);
}

__attribute__((__used__)) int main(int argc, char **argv)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif

    uart_init();
    printf("Hello Wyrm!\r\n");

    printf("\n");
    printf("\e[1m  _       __ __  __ ____   __   __\e[0m\n");
    printf("\e[1m | | __  / // /_/ // __ \\ /  \\/   |\e[0m\n");
    printf("\e[1m | |/  \\/ //_  __//  ___// /\\__/| |\e[0m\n");
    printf("\e[1m |___/\\__/  /_/  /_/\\_\\ /_/     |_|\e[0m\n");
    printf("\n");
    printf(" WYRM built on "__DATE__" "__TIME__"\n");
    printf("\n");
    printf("--=============== \e[1mSoC\e[0m ==================--\n");
    printf("\e[1mCPU\e[0m:\t\t%s @ %dMHz\n",
        CONFIG_CPU_HUMAN_NAME,
#ifdef CONFIG_CPU_CLK_FREQ
        CONFIG_CPU_CLK_FREQ/1000000
#else
        CONFIG_CLOCK_FREQUENCY/1000000
#endif
    );
    printf("\e[1mBUS\e[0m:\t\t%s %d-bit @ %dGiB\n",
        CONFIG_BUS_STANDARD,
        CONFIG_BUS_DATA_WIDTH,
        (1 << (CONFIG_BUS_ADDRESS_WIDTH - 30)));
    printf("\e[1mCSR\e[0m:\t\t%d-bit data\n",
        CONFIG_CSR_DATA_WIDTH);

#ifdef CSR_ETHMAC_BASE
    eth_init();
#endif

    unsigned char mac[] = {0x72, 0x6b, 0x89, 0x5b, 0xc2, 0xe2};
    udp_start(mac, IPTOINT(192, 168, 10, 30));

    udp_set_callback(udp_cb);

    printf("Waiting for packets...\r\n");


    while(1) {
        udp_service();
    }

    return 0;
}
