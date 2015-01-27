#!/usr/bin/env python
# DESCRIPTION: 
# Show detailed stas for an interface.  
# Refresh stats per the delay for until the count is reached. 
# Interface stats are cleared by default.
# Default dealy and count is 1
# Get interface information in XML format

import sys, time
import xml.etree.cElementTree as ET

## Import arguments
import argparse
parser = argparse.ArgumentParser(description='This script will show detailed interface stats (TX/RX Mbps, TX/RX pps, TX/RX %) for ALL interfaces per the configured load interval.')
#parser.add_argument('-d', '--delay', help='interface name',required=False, default=1)
#parser.add_argument('-c', '--count', help='count: number of interations, default 1',required=False, default=1)
args = parser.parse_args()

## Get the command arguments
#delay = float(args.delay)
#count = int(args.count)

# Status
print
print 'Collecting and processing interface statistics ...'
print
sys.stdout.flush()
raw = cli('show interface | xml | exclude "]]>]]>"')

# Load and parse XML
tree = ET.ElementTree(ET.fromstring(raw))
data = tree.getroot()

# Find and display interface rate information
if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
table = "{0:16}{1:9}{2:9}{3:9}{4:9}{5:9}{6:9}{7:9}"
print '---------------------------------------------------------------------------'
print table.format("Port", "Intvl", "Rx Mbps", "Rx %", "Rx pps", "Tx Mbps", "Tx %", "Tx pps")
print '---------------------------------------------------------------------------'
for i in data.iter(if_manager + 'ROW_interface'):
    try:
        interface = i.find(if_manager + 'interface').text
        bw = int(i.find(if_manager + 'eth_bw').text)
        rx_intvl = i.find(if_manager + 'eth_load_interval1_rx').text
        rx_bps = int(i.find(if_manager + 'eth_inrate1_bits').text)
        rx_mbps = round((rx_bps / 1000000), 1)
        rx_pcnt = round((rx_bps / 1000) * 100 / bw, 1)
        rx_pps = i.find(if_manager + 'eth_inrate1_pkts').text
        tx_intvl = i.find(if_manager + 'eth_load_interval1_tx').text
        tx_bps = int(i.find(if_manager + 'eth_outrate1_bits').text)
        tx_mbps = round((tx_bps / 1000000), 1)
        tx_pcnt = round((tx_bps / 1000) * 100 / bw, 1)
        tx_pps = i.find(if_manager + 'eth_outrate1_pkts').text
        print table.format(interface, rx_intvl + '/' + tx_intvl, str(rx_mbps), str(rx_pcnt) + '%', rx_pps, str(tx_mbps), str(tx_pcnt) + '%', tx_pps)
        sys.stdout.flush()
    except AttributeError:
        pass