#!/usr/bin/python

"""
Simple example of point-to-point link running ping
"""
import time

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel

from mininet_test import TestMonitor
from mininet_test import TestMonitorHost

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
    topo.addLink('h1', 'h2', bw=10, delay='5ms', loss=0)

    # The TCLink is needed for use to set the bandwidth, delay and loss
    # constraints on the link
    #
    # waitConnected
    net = Mininet(topo=topo,
                  link=TCLink,
                  waitConnected=True,
                  host=TestMonitorHost)
    net.start()

    test_monitor = TestMonitor()

    h1, h2 = net.getNodeByName('h1', 'h2')

    h1.set_test_monitor(test_monitor=test_monitor)
    h2.set_test_monitor(test_monitor=test_monitor)

    # Will open the two ping processes on both hosts and read the output

    h1_ping = h1.popen('ping -c10 {}'.format(h2.IP()))
    h2_ping = h2.popen('ping -c10 {}'.format(h1.IP()))

    end_time = time.time() + 15

    while test_monitor.run():
        if time.time() >= end_time:
            raise RuntimeError("Test timeout!")

    h1_ping.match(stdout="* 0% packet loss*")
    h2_ping.match(stdout="* 0% packet loss*")

    test_monitor.stop()
    net.stop()
