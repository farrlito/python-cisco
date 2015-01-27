#!/usr/bin/env python
import sys, time, argparse, xml.etree.cElementTree as ET
# Get the arguments
parser = argparse.ArgumentParser(description='Tracks UNICAST packets on TVM & SeGW connected interfaces.')
parser.add_argument('-t', help='Test tool: tvm1, tvm2, dell',required=True)
parser.add_argument('-g', help='SeGW: 11 or 21',required=True)
parser.add_argument('-c', help='Number of interations (default is 1)',required=False, default=1)
parser.add_argument('-d', help='Delay per iteration (default is 1)',required=False, default=1)
parser.add_argument('-n', help='DO NOT clear the interface counters (default is to clear the counters)',required=False, action='store_const', const='no', default='yes')
args = parser.parse_args()
# Set variables
tool = str(args.t).lower()
gw = str(args.g)
count = int(args.c)
delay = float(args.d)
clear = str(args.n)
# Set Nexus ports 
pub_ports = {"tvm1" : "4/1", "tvm2" : "4/2", "11" : "4/11", "21" : "4/28", "dell" : "4/37", "3404" : "3/48"}
pri_ports = {"tvm1" : "4/13", "tvm2" : "4/14", "11" : "4/23", "21" : "4/27", "dell" : "4/38", "3404" : "3/48"}
# Format the port names
pub_tool = "Ethernet" + pub_ports[tool]
pri_tool = "Ethernet" + pri_ports[tool]
pub_gw = "Ethernet" + pub_ports[gw]
pri_gw = "Ethernet" + pri_ports[gw]
# Clear interface counters
if clear == 'yes':
	clearcmd = 'clear counters interface %s,  %s,  %s,  %s' % (pub_tool, pub_gw, pri_gw, pri_tool)
	print "Interface counters have been cleared"
	clip(clearcmd)
else:
	print "Not clearing interfaces"
	print 
# Build the CLI command
cmd = 'show interface %s, %s, %s, %s counters | xml | exclude "]]>]]>"' % (pub_tool, pub_gw, pri_gw, pri_tool)
sys.stdout.flush()
# Main stat collecting functions
def get_rx(port):
	for i in data.iter(if_manager + 'ROW_rx_counters'):
		try:
			iface = i.find(if_manager + 'interface_rx').text
			if iface == port:
				pkts = str(i.find(if_manager + 'eth_inucast').text)
				return pkts
		except AttributeError:
			pass
def get_tx(port):
	for i in data.iter(if_manager + 'ROW_tx_counters'):
		try:
			iface = i.find(if_manager + 'interface_tx').text
			if iface == port:
				pkts = str(i.find(if_manager + 'eth_outucast').text)
				return pkts
		except AttributeError:
			pass
ctr = 0
# Main stats collection code
while (ctr < count):
	# XML commands
	raw = cli(cmd)
	tree = ET.ElementTree(ET.fromstring(raw))
	data = tree.getroot()
	if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
	# RX data collection
	pub_tool_rx_pkts = get_rx(pub_tool)
	pub_gw_rx_pkts = get_rx(pub_gw)
	pri_tool_rx_pkts = get_rx(pri_tool)
	pri_gw_rx_pkts = get_rx(pri_gw)
	# TX data collection
	pub_tool_tx_pkts = get_tx(pub_tool)
	pub_gw_tx_pkts = get_tx(pub_gw)
	pri_tool_tx_pkts = get_tx(pri_tool)
	pri_gw_tx_pkts = get_tx(pub_tool)
	# Calculate packet difference
	pub_pri_results = int(pub_tool_rx_pkts) - int(pri_tool_tx_pkts)
	pri_pub_results = int(pri_tool_rx_pkts) - int(pub_tool_tx_pkts)
	# Format & print the results
	table = "{0:25}{1:3}{2:16}{3:4}{4:25}{5:3}{6:16}"
	table_header = "{0:46}{1:46}"
	print "-" , "Iteration %i of %i" % (ctr+1, count), "-"
	print "-" * 100
	print table_header.format("          Public to Private Flow          ", "          Private to Public Flow          ")
	print table.format("Interface", "|", "Packets", "||", "Interface", "|", "Packets")
	print table.format("[Tool]", "|", "", "||", "[Tool]", "|", "")
	print table.format("Pub RX: " + pub_tool, "|", pub_tool_rx_pkts, "||", "Pri RX: " + pri_tool, "|", pri_tool_rx_pkts)
	print table.format("Pub TX: " + pub_gw, "|", pub_gw_tx_pkts, "||", "Pri TX: " + pri_gw, "|", pri_gw_tx_pkts)
	print table.format("[GW]", "|", "", "||", "[GW]", "|", "")
	print table.format("Pri RX: " + pri_gw, "|", pri_gw_rx_pkts, "||", "Pub RX: " + pub_gw, "|", pub_gw_rx_pkts)
	print table.format("Pri TX: " + pri_tool, "|", pri_tool_tx_pkts, "||", "Pub TX: " + pub_tool, "|", pub_tool_tx_pkts)
	print table.format("[Tool]", "|", "", "||", "[Tool]", "|", "")
	print table.format("Pub RX - Pri TX:", "|", pub_pri_results, "||", "Pri RX - Pub TX:", "|", pri_pub_results)
	print "-" * 100
	print
	# Increment counter and sleep
	ctr += 1
	time.sleep(delay)