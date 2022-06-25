import socket
import threading
import time

from objprint import add_objprint
import pyeelight


class Packet:
    pass


class OutboundRequestPacket(Packet):

    def __init__(self, man, st):
        self.man = man
        self.st = st

    def process_headers(self):
        return f"""M-SEARCH * HTTP/1.1\r\nMAN: "{self.man}"\r\nST: {self.st}\r\n""".encode()


@add_objprint
class InboundAdvertisementPacket(Packet):
    pass


class AdvertisementSocket(pyeelight.Contextable):
    MULTICAST_IP = "239.255.255.250"
    MULTICAST_PORT = 1982

    def __init__(self):
        self.packets = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.get_ip(), 1234))
        self.logger = pyeelight.Logger(self)

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def send_packet(self, packet: OutboundRequestPacket):
        self.sock.sendto(packet.process_headers(), (self.MULTICAST_IP, self.MULTICAST_PORT))

    def ditch(self):
        self.sock.close()

    def init_waiter_thread(self):
        self.logger.info("DISCOVERER", "Starting discovery of bulbs...")
        e = threading.Event()
        x = threading.Thread(target=self.wait_on_response)
        x.start()

        # sync memory after running thread
        x.join(3)
        e.set()

        #self.ditch()
        return self.packets

    def wait_on_response(self):
        while True:
            data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            decoded_data = data.decode().rstrip()
            packet = InboundAdvertisementPacket()

            i = 0
            packet_dict = {}
            for element in decoded_data.split("\r\n"):
                if i == 0:
                    packet.http = element
                else:
                    key, value = element.split(":", 1)
                    packet_dict[key] = value.lstrip()
                i += 1

            packet.cache_control = packet_dict["Cache-Control"]
            packet.location = packet_dict["Location"]
            packet.data = packet_dict["Date"]
            packet.ext = packet_dict["Ext"]
            packet.id = packet_dict["id"]
            packet.model = packet_dict["model"]
            packet.fw_ver = packet_dict["fw_ver"]
            packet.supported_methods = packet_dict["support"].split(" ")
            packet.power = packet_dict["power"]
            packet.brightness = packet_dict["bright"]
            packet.color_mode = packet_dict["color_mode"]
            packet.ct = packet_dict["ct"]
            packet.rgb = packet_dict["rgb"]
            packet.hue = packet_dict["hue"]
            packet.sat = packet_dict["sat"]
            packet.name = packet_dict["name"]

            self.packets.append(packet)

    def get_context(self):
        return f"DISCOVERER::MULTICAST"


# WIP
@add_objprint
class BulbInfo:
    def __init__(self, name, location):
        self.name = name
        self.location = location

    def get_ip(self):
        pass

    def get_port(self):
        pass

    def get_name(self):
        return self.name

    def get_controller(self) -> pyeelight.Bulb:
        prefixed_address = ":".join(self.location.split(":", 2)[:2])
        ip_address = prefixed_address.split("//")[1]

        return pyeelight.Bulb.connect(ip_address)


def get_bulbs():
    ad_socket = AdvertisementSocket()
    ad_socket.send_packet(OutboundRequestPacket("ssdp:discover", "wifi_bulb"))

    return [BulbInfo(i.name, i.location) for i in ad_socket.init_waiter_thread()]