import json
import socket
from abc import abstractmethod


class Contextable:

    @abstractmethod
    def get_context(self):
        pass


class Logger:

    def __init__(self, ctx):
        self.ctx = ctx

    def batch_received(self, messages):
        for message in messages.decode().strip().split("\r\n"):
            if "id" in json.loads(message):
                self.received(message)
            else:
                self.generic(message)

    def generic(self, message):
        received_obj = json.loads(message)
        final_msg = []
        for prop in received_obj:
            final_msg.append(f"{prop}: {received_obj[prop]}")
        print(f"[{self.ctx.get_context()}][GENERIC] {', '.join(final_msg)}")

    def received(self, message):
        try:
            received_obj = json.loads(message)
            self.info(received_obj["id"], ", ".join(received_obj["result"]))
        except:
            print("ERROR:", message)

    @staticmethod
    def dispatch(func):
        def wrapper(*args):
            bulb_obj = args[0]
            params = args[1:]
            bulb_obj.logger.info(bulb_obj.formatter.id + 1,
                                 f"Sent {func.__name__}({' '.join(map(lambda x: str(x), params))}) command to bulb")
            func(*args)
            bulb_obj.logger.batch_received(bulb_obj.socket_conn.recv(1024))

        return wrapper

    def sent(self, command):
        pass

    def info(self, protocol_id, message):
        print(f"[{self.ctx.get_context()}][{protocol_id}] {message}")


class Bulb(Contextable):

    def __init__(self, socket_conn):
        self.socket_conn = socket_conn
        self.formatter = CommandFormatter()
        self.logger = Logger(self)

    @staticmethod
    def connect(ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 55443))
        print("Connected to bulb!")
        return Bulb(s)

    @Logger.dispatch
    def set_power(self, state):
        self.socket_conn.sendall(self.formatter.format_command("set_power", "on" if state else "off").encode())

    @Logger.dispatch
    def set_brightness(self, brightness):
        self.socket_conn.sendall(self.formatter.format_command("set_bright", brightness).encode())

    @Logger.dispatch
    def get_properties(self, *properties):
        self.socket_conn.sendall(self.formatter.format_command("get_prop", *properties).encode())

    @Logger.dispatch
    def toggle(self):
        self.socket_conn.sendall(self.formatter.format_command("toggle").encode())

    @Logger.dispatch
    def set_rgb(self, r, g, b):
        self.socket_conn.sendall(self.formatter.format_command("set_rgb", ((r * 65536) + (g * 256) + b)).encode())

    @Logger.dispatch
    def reset(self):
        self.socket_conn.sendall(self.formatter.format_command("set_default").encode())

    @Logger.dispatch
    def set_name(self, name):
        self.socket_conn.sendall(self.formatter.format_command("set_name", name).encode())

    def get_context(self):
        return f"BULB::{self.socket_conn.getpeername()[0]}"


class CommandFormatter:

    def __init__(self):
        self.id = 0

    def format_command(self, method, *params):
        self.id += 1
        return json.dumps({"id": self.id, "method": method, "params": params}) + "\r\n"
