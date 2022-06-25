import pyeelight
import pyeelight.discoverer as discoverer

bulbs = discoverer.get_bulbs()

print(bulbs)