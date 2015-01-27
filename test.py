#!/usr/bin/env python

import sys, time
import xml.etree.cElementTree as ET

## Import arguments
import argparse
parser = argparse.ArgumentParser(description='Tracks stats on TVM & DUT connected interfaces')
parser.add_argument('-t', '--tool', help='Test tool (either tvm1 or tvm2)',required=True)
parser.add_argument('-d', '--dut', help='Gateway (either 11 or 21)',required=True)
args = parser.parse_args()
tool = str(args.tool)
dut = str(args.dut)
pub_ports = {"tvm1" : "4/1", "tvm2" : "4/2", "11" : "4/11", "21" : "4/28"}
pri_ports = {"tvm1" : "4/13", "tvm2" : "4/14", "11" : "4/23", "21" : "4/27"}

print "PUB PORTS = ",pub_ports
print "PRI PORTS = ",pri_ports
print "TOOL =",tool
print "DUT =",dut
# Determine DUT ports
if dut == "11":
    print "Its SeGW11"
    pubi = "Ethernet" + pub_ports["11"]
    prii = "Ethernet" + pri_ports["11"]
elif dut == "21":
    print "Its SeGW21"
    pubi = "Ethernet" + pub_ports["21"]
    prii = "Ethernet" + pri_ports["21"]
else:
    print "NO DUT SELECTED!"
# Determine TOOL ports
if tool == "tvm1":
    print "Its TVM1"
    pubo = "Ethernet" + pub_ports["tvm1"]
    prio = "Ethernet" + pri_ports["tvm1"]
elif tool == "tvm2":
    print "Its TVM2"
    pubo = "Ethernet" + pub_ports["tvm2"]
    prio = "Ethernet" + pri_ports["tvm2"]
else:
    print "NO TEST TOOL SELECTED!"
cmd = 'show interface %s, %s, %s, %s counters | xml | exclude "]]>]]>"' % (pubi, pubo, prii, prio)
# XML commands
raw = cli(cmd)
tree = ET.ElementTree(ET.fromstring(raw))
data = tree.getroot()
# Additional XML
if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
# Data
for i in data.iter(if_manager + 'ROW_rx_counters'):
	try:
		iface = i.find(if_manager + 'interface_rx').text
		if iface == pubi:
			pubi_pkts = str(i.find(if_manager + 'eth_inucast').text)
			pubi_bytes = str(i.find(if_manager + 'eth_inbytes').text)
			print "Public  (TOOL->Nexus):  %s  - RX Pkts: %s  RX Bytes: %s" % (pubi, pubi_pkts, pubi_bytes)
		if iface == prii:
			prii_pkts = str(i.find(if_manager + 'eth_inucast').text)
			prii_bytes = str(i.find(if_manager + 'eth_inbytes').text)
			print "Private  (DUT->Nexus):  %s  - RX Pkts: %s  RX Bytes: %s" % (prii, prii_pkts, prii_bytes)
	except AttributeError:
		pass
for i in data.iter(if_manager + 'ROW_tx_counters'):
	try:
		iface = i.find(if_manager + 'interface_tx').text
		if iface == pubo:
			pubo_pkts = str(i.find(if_manager + 'eth_outucast').text)
			pubo_bytes = str(i.find(if_manager + 'eth_outbytes').text)
			print "Public  (Nexus->DUT):  %s  - RX Pkts: %s  RX Bytes: %s" % (pubo, pubo_pkts, pubo_bytes)
		if iface == prio:
			prio_pkts = str(i.find(if_manager + 'eth_outucast').text)
			prio_bytes = str(i.find(if_manager + 'eth_outbytes').text)
			print "Private  (Nexus->TOOL):  %s  - RX Pkts: %s  RX Bytes: %s" % (prio, prio_pkts, prio_bytes)
	except AttributeError:
		pass	
print "-" * 75