#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

/* Raise the IPv6 link MTU above the stock 1280-byte cap so that the
 * 2272-byte ML-KEM-768 handshake payload is transmitted rather than
 * silently dropped by tcpip_ipv6_output(). */
#define UIP_CONF_BUFFER_SIZE 3000
#define UIP_LINK_MTU 3000

/* 6LoWPAN reassembly for large datagrams. */
#define SICSLOWPAN_CONF_FRAG 1
#define SICSLOWPAN_CONF_FRAGMENT_BUFFERS 24
#define QUEUEBUF_CONF_NUM 64
#define UIP_CONF_TCP 0

/* Logging used to record the on-air fragmentation behaviour. */
#define LOG_CONF_LEVEL_FRAMER LOG_LEVEL_INFO
#define LOG_CONF_LEVEL_6LOWPAN LOG_LEVEL_INFO
#define LOG_CONF_LEVEL_MAC LOG_LEVEL_WARN

#endif /* PROJECT_CONF_H_ */
