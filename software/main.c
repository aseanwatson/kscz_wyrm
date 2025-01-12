#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <libliteeth/mdio.h>
#include <libliteeth/udp.h>
#include <generated/csr.h>

//void udp_cb(unsigned int src_ip, unsigned short src_port, unsigned short dst_port, void *data, unsigned int length)
//{
//    printf("Got a UDP packet!\r\n");
//}

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif
    uart_init();
    eth_init();

    printf("Hello Wyrm!\r\n");

//    unsigned char mac[] = {0x72, 0x6b, 0x89, 0x5b, 0xc2, 0xe4};
//    udp_start(mac, IPTOINT(192, 168, 10, 31));

    int res = mdio_read(0, 2);

    printf("Got MDIO phy ID: 0x%X\r\n", res);

//    udp_set_callback(udp_cb);

    printf("Waiting for packets...\r\n");
    while(1) {
//        udp_service();
    }

    return 0;
}
