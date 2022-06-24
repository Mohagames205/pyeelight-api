import discoverer
import main

bulb = discoverer.get_bulbs()[0].get_controller()

bulb.set_power(True)