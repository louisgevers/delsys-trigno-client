import struct
import socket
import select
import numpy as np
from typing import Optional

from delsys_trigno_client.constants import (
    TrignoPort,
    BYTES_PER_CHANNEL,
    DEFAULT_DIGITAL_SERVER_IP,
    EMG_DATA_CHANNELS,
    AUX_DATA_CHANNELS,
)


class TrignoClient:
    def __init__(
        self,
        digital_server_ip: str = DEFAULT_DIGITAL_SERVER_IP,
        timeout: Optional[float] = 5,
    ) -> None:
        self._sockets: dict[TrignoPort, socket.socket] = dict()
        for port in TrignoPort:
            self._sockets[port] = socket.create_connection(
                (digital_server_ip, port.value), timeout=timeout
            )
        # First response is protocol version
        protocol_version = self._receive_response(TrignoPort.COMMAND)
        print(f"Connected: {protocol_version}")
        # Make connection master
        self._send_command("MASTER")

    def start_acquisition(self):
        self._send_command("START")

    def stop_acquisition(self):
        self._send_command("STOP")

    def is_sensor_paired(self, id: int) -> bool:
        resp = self._send_command(f"SENSOR {id} PAIRED?")
        return resp == "YES"

    def pair_sensor(self, id: int) -> bool:
        resp = self._send_command(f"SENSOR {id} PAIR")
        # Check if initiated
        if "INITIATED" not in resp:
            return False
        # Wait for pairing to complete
        resp = self._receive_response(TrignoPort.COMMAND)
        return "COMPLETE" in resp

    def get_readings_emg(self, max_size: int = np.inf) -> np.ndarray:
        return self._read_data(TrignoPort.EMG_DATA, EMG_DATA_CHANNELS, max_size)

    def get_readings_aux(self, max_size: int = np.inf) -> np.ndarray:
        return self._read_data(TrignoPort.AUX_DATA, AUX_DATA_CHANNELS, max_size)

    def close(self):
        try:
            self._send_command("QUIT")
        finally:
            for socket in self._sockets.values():
                socket.close()

    def _send_command(self, command: str):
        message = f"{command}\r\n\r\n"
        self._sockets[TrignoPort.COMMAND].sendall(message.encode("ascii"))
        return self._receive_response(TrignoPort.COMMAND)

    def _receive_response(self, port: TrignoPort) -> str:
        # Wait for read to be available
        select.select([self._sockets[port]], [], [])
        return self._sockets[port].recv(1024).decode("ascii").strip()

    def _read_data(
        self, port: TrignoPort, nchannels: float, max_size: int
    ) -> np.ndarray:
        packet = bytes()
        remaining_bytes = 0
        expected_size = nchannels * BYTES_PER_CHANNEL
        connection = self._sockets[port]
        while True:
            try:
                msg = connection.recv(expected_size + remaining_bytes)
                packet += msg
                # Packets should be processed per block of channels
                if len(packet) % expected_size != 0:
                    remaining_bytes = expected_size - len(packet) % expected_size
                elif len(packet) >= max_size * expected_size:
                    break
                elif len(msg) == 0:  # Nothing to receive anymore
                    packet += b"\x00" * remaining_bytes
                    break
            except socket.timeout:
                packet += b"\x00" * remaining_bytes
                break
        nsamples = int(len(packet) / expected_size) * nchannels
        data = struct.unpack("<" + "f" * nsamples, packet)
        return np.array(data, dtype=np.float32).reshape((nchannels, -1))
