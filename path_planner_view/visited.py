#!/usr/bin/env python3
import Pyro4
import sys

control = Pyro4.Proxy("PYRONAME:example.control");
nodes = control.get_Vector();
print(nodes);
