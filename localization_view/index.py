#!/usr/bin/env python3
import Pyro4
import sys,json
try:
   pos = json.loads( sys.argv[1]);
   p = int(pos);
except:
   print("ERROR")
   sys.exit(1)

control = Pyro4.Proxy("PYRONAME:example.control");
control.set_index(p);

print(p);
