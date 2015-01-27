#!/usr/bin/env python
# DESCRIPTION: 
# Compare the RX unicast packets for the inbound interface to the TX unicast packets for the outbound interface.  
# Refresh stats per the delay for until the count is reached. 
# Interface stats are cleared by default.
# Default dealy and count is 1

import sys, time
import xml.etree.cElementTree as ET

## Import arguments
import argparse
parser = argparse.ArgumentParser(description='This script will count the RX unicast packets on the inbound interface and the TX unicast packets on the outbound interface')
parser.add_argument('-i', '--inbound', help='inbound interface (RX packets) (i.e. 4/2)',required=True)
parser.add_argument('-o', '--outbound', help='outbound interface (TX packets) (i.e. 4/14)',required=True)
parser.add_argument('-d', '--delay', help='delay: to calculate results, default 1',required=False, default=1)
parser.add_argument('-c', '--count', help='count: number of interations, default 1',required=False, default=1)
parser.add_argument('-n', '--clear', help='do NOT clear the interface counters, default is to clear them',required=False, action='store_const', const='no', default='yes')
args = parser.parse_args()

## Get the command arguments
inbound = str(args.inbound)
outbound = str(args.outbound)
delay = float(args.delay)
count = int(args.count)
clear = str(args.clear)

## Print arguments
print ""
print "#" * 30
print ("Inbound interface: %s" % inbound )
print ("Outbound interface: %s" % outbound )
print ("Delay: %s" % delay )
print ("Count: %s" % count )
print ("Clear interfaces? %s" % clear )
print "#" * 30
print ""
 
# Clear interface counters
if clear == 'yes':
  print 'Clearing interface counters'
  clip('clear counters interface ethernet ' + inbound + ' , ethernet ' + outbound)

# Status
print
print 'Getting interface statistics ...'
print
sys.stdout.flush()

# Create table heading
table = "{0:14}{1:12}{2:14}{3:12}{4:12}"
print "-" * 75
print table.format("Inbound", "RX Pkts", "Outbound", "TX Pkts", "Difference")
print "-" * 75

# Collect the stats
ctr = 0
while (ctr < count):
  time.sleep(delay)
  # Get interface information in XML format
  inraw = cli('show interface ethernet ' + inbound + ' | xml | exclude "]]>]]>"')
  outraw = cli('show interface ethernet ' + outbound + '  | xml | exclude "]]>]]>"')
  # Load and parse XML IN
  intree = ET.ElementTree(ET.fromstring(inraw))
  indata = intree.getroot()
  # Load and parse XML OUT
  outtree = ET.ElementTree(ET.fromstring(outraw))
  outdata = outtree.getroot()
  # Specify the namespace
  if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
  # Find and display the inbound interface stats
  for i in indata.iter(if_manager + 'ROW_interface'):
     try:
         inint = i.find(if_manager + 'interface').text
         rx_pkts = int(i.find(if_manager + 'eth_inucast').text)
         sys.stdout.flush()
     except AttributeError:
         pass
  # Find and display the outbound interface stats
  for i in outdata.iter(if_manager + 'ROW_interface'):
    try:
        outint = i.find(if_manager + 'interface').text
        tx_pkts = int(i.find(if_manager + 'eth_outucast').text)
        sys.stdout.flush()
    except AttributeError:
        pass
  # Calculate the difference
  diff = (rx_pkts - tx_pkts)
  # Print the stats to the table
  print table.format(inint, str(rx_pkts), outint, str(tx_pkts), diff)
  ctr += 1