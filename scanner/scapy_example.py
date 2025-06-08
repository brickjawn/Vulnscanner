from scapy.all import sniff

def capture_http_packets(interface="eth0", count=10):
    packets = sniff(iface=interface, filter="tcp port 80", count=count)
    for pkt in packets:
        print(pkt.summary())