#!/usr/bin/env python
# DESCRIPTION: 
# Show BGP neighbour status.  

import sys, time
import xml.etree.cElementTree as ET

## Import arguments
import argparse
parser = argparse.ArgumentParser(description='Show BGP neighbor IP, BGP state (ESTAB, IDLE, OPEN, etc...), & interface or status.  If a neighbor\'s \"up\" state is \"false\" it will show as \"DOWN\"')
parser.add_argument('-d', '--delay', help='delay to show each iteration, default 1',required=False, default=1)
parser.add_argument('-c', '--count', help='total number of interations to show, default 1',required=False, default=1)
args = parser.parse_args()

## Get the command arguments
delay = float(args.delay)
count = int(args.count)

# Status
print
print 'Getting BGP status ...'
print
sys.stdout.flush()

# Create table heading
table = "{0:40}{1:15}{2:15}"
print "-" * 70
print table.format("Neighbour", "BGP State", "Int/Status")
print "-" * 70

# Collect the stats
ctr = 0
while (ctr < count):
  time.sleep(delay)
  bgp = '{http://www.cisco.com/nxos:1.0:bgp}'
  inraw = cli('sh bgp vrf SEGWPRI all neighbors | xml | exclude "]]>]]>"')
  tree = ET.ElementTree(ET.fromstring(inraw))
  root = tree.getroot()
  print "-" , "Iteration %i of %i" % (ctr+1, count), "-" * 50
  for i in root.iter(bgp + 'ROW_neighbor'):
    try:
	  v4neighbor = i.find(bgp + 'neighbor').text
	  v4state = i.find(bgp + 'state').text
	  v4up = i.find(bgp + 'up').text
	  if v4up == "true":
		v4int = i.find(bgp + 'connectedif').text
		print table.format(v4neighbor, v4state, v4int)
	  else:
		print table.format(v4neighbor, v4state, 'N/A (Down)')
    except AttributeError:
      pass
  for i in root.iter(bgp + 'ROW_neighbor'):
    try:
	  v6neighbor = i.find(bgp + 'ipv6neighbor').text
	  v6state = i.find(bgp + 'state').text
	  v6up = i.find(bgp + 'up').text
	  if v6up == "true":
		v6int = i.find(bgp + 'connectedif').text
		print table.format(v6neighbor, v6state, v6int)
	  else:
		print table.format(v6neighbor, v6state, 'N/A (Down)')
    except AttributeError:
	pass
  ctr += 1