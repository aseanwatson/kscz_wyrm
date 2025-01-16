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
    printf("Got a UDP packet!\r\n");
}

__attribute__((__used__)) int main(int i, char **c)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif

    uart_init();
    printf("Hello Wyrm!\r\n");

    printf("\n");
    printf("\e[1m  _        __ __  __ ____  __   __\e[0m\n");
    printf("\e[1m | | __   / // /_/ // _  //  \\/   |\e[0m\n");
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

    for (unsigned int i = 0; i < 0x1000000; ++i) {
        if (i == 0x800000) {
            printf("...\r\n");
        }
    }

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
