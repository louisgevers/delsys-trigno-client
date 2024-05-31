import socket
from typing import Optional

from delsys_trigno_client.constants import DEFAULT_DIGITAL_SERVER_IP, TrignoPort

class TrignoClient():
    def __init__(self, digital_server_ip: str = DEFAULT_DIGITAL_SERVER_IP, timeout: Optional[float] = 5) -> None:
        self._sockets: dict[TrignoPort, socket.socket] = dict()
        for port in TrignoPort:
            self._sockets[port] = socket.create_connection((digital_server_ip, port.value), timeout=timeout)

    def close(self):
        for socket in self._sockets.values():
            socket.close()
            