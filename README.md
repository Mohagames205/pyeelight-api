Do not use, this is very much indev

[![PyPI version](https://badge.fury.io/py/pyeelight.svg)](https://badge.fury.io/py/pyeelight)

# Yeelight Python API

This library facilitates the communication between the user and the yeelight protocol.

## Basic usage

```py

import yeelight

bulb = yeelight.Bulb.connect("192.168.1.30")

# toggles the bulb
bulb.toggle()

# sets the power-state of the bulb
bulb.set_power("on") # accept "on" or "off"

# sets the brightness
bulb.set_brightness(50) # accepts a value between 0 - 100

# fetches one or more bulb properties
bulb.get_properties("power", "bright", ...") # see list with accepted values in table 1

# sets the color of the bulb to a certain rgb value
bulb.set_rgb(r, g, b)

```

## How does the protocol work?

The yeelight bulb communicates using the TCP protocol with the client.
