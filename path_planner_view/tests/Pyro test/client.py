#!/usr/bin/env python3
import  Pyro4
import sys

person_to_joke = sys.argv[1]

joke_control = Pyro4.Proxy("PYRONAME:example.jokegen")

print (joke_control.joke(person_to_joke))
