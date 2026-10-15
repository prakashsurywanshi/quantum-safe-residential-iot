#include "contiki.h"
#include "net/routing/routing.h"
#include "random.h"
#include "net/netstack.h"
#include "net/ipv6/simple-udp.h"
#include "sys/log.h"
#include <stdint.h>
#include <inttypes.h>

#define LOG_MODULE "Probe"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_CLIENT_PORT 8765
#define UDP_SERVER_PORT 5678
#define SEND_INTERVAL (20 * CLOCK_SECOND)

#ifndef QHSG_PAYLOAD_LEN
#define QHSG_PAYLOAD_LEN 64
#endif

#ifndef QHSG_RUNS
#define QHSG_RUNS 5
#endif

static struct simple_udp_connection udp_conn;
static uint8_t payload[QHSG_PAYLOAD_LEN];

PROCESS(qhsg_probe_process, "QHSG fragmentation probe");
AUTOSTART_PROCESSES(&qhsg_probe_process);

static void
udp_rx_callback(struct simple_udp_connection *c,
                const uip_ipaddr_t *sender_addr, uint16_t sender_port,
                const uip_ipaddr_t *receiver_addr, uint16_t receiver_port,
                const uint8_t *data, uint16_t datalen)
{
  (void)c; (void)sender_addr; (void)sender_port;
  (void)receiver_addr; (void)receiver_port; (void)data; (void)datalen;
}

PROCESS_THREAD(qhsg_probe_process, ev, data)
{
  static struct etimer periodic_timer;
  static struct etimer wait_timer;
  uip_ipaddr_t dest_ipaddr;
  static uint32_t seq;

  PROCESS_BEGIN();

  simple_udp_register(&udp_conn, UDP_CLIENT_PORT, NULL, UDP_SERVER_PORT, udp_rx_callback);

  LOG_INFO("QHSG cfg payload=%u uip_bufsize=%u\n",
           (unsigned)QHSG_PAYLOAD_LEN, (unsigned)UIP_BUFSIZE);

  for(uint16_t i = 0; i < QHSG_PAYLOAD_LEN; i++) {
    payload[i] = (uint8_t)('A' + (i % 26));
  }

  etimer_set(&periodic_timer, 15 * CLOCK_SECOND);

  while(seq < QHSG_RUNS) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));

    if(NETSTACK_ROUTING.node_is_reachable() &&
       NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)) {
      LOG_INFO("QHSG_TX_BEGIN seq=%" PRIu32 " len=%u\n", seq, (unsigned)QHSG_PAYLOAD_LEN);
      simple_udp_sendto(&udp_conn, payload, QHSG_PAYLOAD_LEN, &dest_ipaddr);

      etimer_set(&wait_timer, CLOCK_SECOND);
      PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&wait_timer));

      LOG_INFO("QHSG_TX_END seq=%" PRIu32 " len=%u\n", seq, (unsigned)QHSG_PAYLOAD_LEN);
      seq++;
    } else {
      LOG_INFO("QHSG waiting for root\n");
    }
    etimer_set(&periodic_timer, SEND_INTERVAL - CLOCK_SECOND + (random_rand() % (2 * CLOCK_SECOND)));
  }

  LOG_INFO("QHSG done\n");
  PROCESS_END();
}
