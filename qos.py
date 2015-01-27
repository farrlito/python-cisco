#!/usr/bin/env python

import xml.etree.cElementTree as ET
import sys, time

ctr = 1
delay = 1
while (ctr < 5):
  qos = '{http://www.cisco.com/nxos:1.0:qosmgr}'
  inraw = cli('sh policy-map interface ethernet 4/23 input type queuing | xml | exclude "]]>]]>"')
  tree = ET.ElementTree(ET.fromstring(inraw))
  root = tree.getroot()
  print "-" , "Iteration %i" % (ctr), "-" * 55
  for i in root.iter(qos + 'ROW_cmap'):
    try:
		if i.find(qos + 'cmap-key').text == "2q4t-8e-in-q-default":
			drop_pkts = int(i.find(qos + 'que-dropped-pkts').text)
			print "Dropped Packets = ", drop_pkts
    except AttributeError:
      pass
  ctr += 1
  time.sleep(delay)