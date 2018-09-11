#!/usr/bin/python

"""
Simple example of point-to-point link running ping
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.util import pmonitor
from mininet.log import setLogLevel

if __name__ == '__main__':
    setLogLevel('info')

    # Build the topology we want to play with:
    #
    #             +-----------------------+
    #             |     10Mbit/s link     |
    #             |     5ms delay         |
    #             |     10% packet loss   |
    #             |                       |
    #             +-----------+-----------+
    #                         |
    #                         |
    #                         |
    #                         |
    # +-------------+         v        +-------------+
    # |             |                  |             |
    # | host 1 (h1) +------------------+ host 2 (h2) |
    # |             |                  |             |
    # +-------------+                  +-------------+
    #
    topo = Topo()
    topo.addHost('h1')
    topo.addHost('h2')
    topo.addLink('h1', 'h2', bw=10, delay='5ms', loss=10)

    # The TCLink is needed for use to set the bandwidth, delay and loss
    # constraints on the link
    #
    # waitConnected
    net = Mininet(topo=topo,
                  link=TCLink,
                  waitConnected=True)
    net.start()

    h1, h2 = net.getNodeByName('h1', 'h2')

    # Will open the two ping processes on both hosts and read the output
    popens = {}
    popens[h1] = h1.popen('ping -c10 {}'.format(h2.IP()))
    popens[h2] = h2.popen('ping -c10 {}'.format(h1.IP()))

    for host, line in pmonitor(popens):
        if host:
            # Output each line written as "<hX>: some output", where X
            # will be replaced by the host number i.e. 1 or 2.
            print("<{}>: {}".format(host.name, line.strip()))

    net.stop()
