#!/usr/bin/env python

import xml.etree.cElementTree as ET

table = "{0:40}{1:15}{2:15}"
ctr = 0
while (ctr < 1):
  bgp = '{http://www.cisco.com/nxos:1.0:bgp}'
  inraw = cli('sh bgp vrf SEGWPRI all neighbors | xml | exclude "]]>]]>"')
  tree = ET.ElementTree(ET.fromstring(inraw))
  root = tree.getroot()
  print "-" , "Iteration %i" % (ctr+1), "-" * 55
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