import time
import socket
import struct
import threading
import numpy as np
from typing import Optional

from delsys_trigno_client.constants import (
    TrignoPort,
    EMG_DATA_CHANNELS,
    AUX_DATA_CHANNELS,
)

DATA_FREQUENCY = 4_000  # Hz


def print_warning(message: str):
    print(f"\033[93m[WARNING]: {message}\033[0m")


def print_debug(message: str):
    print(f"\033[94m[DEBUG]: {message}\033[0m")


class MockDelsysStation:
    def __init__(self) -> None:
        # Create sockets
        self._command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._emg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Client connection handles
        self._client_com: Optional[socket.socket] = None
        self._client_emg: Optional[socket.socket] = None
        self._client_aux: Optional[socket.socket] = None

        # Data thread handles
        self._thread_emg: Optional[threading.Thread] = None
        self._thread_aux: Optional[threading.Thread] = None

        # Whether the server should run
        self._running = False
        # Whether data should be sent
        self._acquiring = False

    def run(self):
        # Bind to the correct ports
        self._command.bind(("localhost", TrignoPort.COMMAND.value))
        self._emg.bind(("localhost", TrignoPort.EMG_DATA.value))
        self._aux.bind(("localhost", TrignoPort.AUX_DATA.value))

        # Put in listening mode
        self._command.listen(1)
        self._emg.listen(1)
        self._aux.listen(1)

        # Wait for connections
        print("Waiting for client connection")
        self._client_com, address = self._command.accept()
        print_debug(f"Command client connected:\t{address}")
        self._client_emg, address = self._emg.accept()
        print_debug(f"EMG client connected:\t\t{address}")
        self._client_aux, address = self._aux.accept()
        print_debug(f"AUX client connected:\t\t{address}")

        # Initial answer is protocol version
        self._respond_command("Delsys Trigno Server PROTOCOL MOCK")

        # Listen for commands
        self._command_listener_loop()

        # Cleanup
        self.close()

    def close(self):
        print("Closing client connections")
        if self._client_com is not None:
            self._client_com.close()
        if self._client_emg is not None:
            self._client_emg.close()
        if self._client_aux is not None:
            self._client_aux.close()
        print("Closing server")
        self._command.close()
        self._emg.close()
        self._aux.close()

    def _command_listener_loop(self):
        self._running = True
        with self._client_com as connection:
            while self._running:
                data = connection.recv(1024).decode("ascii")
                if data.endswith("\r\n\r\n"):
                    command = data.strip()
                    resp = self._process_command(command)
                    if resp is not None:
                        self._respond_command(resp)

    def _process_command(self, command: str) -> Optional[str]:
        print_debug(f"Processing {command}")
        if command == "QUIT":
            self._running = False
            return "BYE"
        elif command == "MASTER":
            return "NEW MASTER"
        elif command == "START":
            self._thread_emg = threading.Thread(
                target=self._start_data_loop, args=(self._client_emg, EMG_DATA_CHANNELS)
            )
            self._thread_aux = threading.Thread(
                target=self._start_data_loop, args=(self._client_aux, AUX_DATA_CHANNELS)
            )
            self._thread_emg.start()
            self._thread_aux.start()
            return "OK"
        elif command == "STOP":
            self._acquiring = False
            # Wait for threads to finish
            self._thread_emg.join()
            self._thread_aux.join()
            return "OK"
        else:
            print_warning(f"Unknown command: {command}")
            return "INVALID COMMAND"

    def _start_data_loop(self, connection: socket.socket, nchannels: int):
        self._acquiring = True
        print_debug(f"Starting acquisition ({nchannels} channels)")
        with connection:
            target_time = 1 / DATA_FREQUENCY
            last_time = time.time()
            while self._acquiring:
                data = np.random.rand(nchannels).astype(np.float32)
                packet = bytes()
                for value in data:
                    packet = struct.pack("<f", value)
                connection.sendall(packet)
                # Emit at desired frequency
                diff = target_time - (time.time() - last_time)
                if diff > 0:
                    time.sleep(diff)
                last_time = time.time()
        print_debug(f"Finished acquisition ({nchannels} channels)")

    def _respond_command(self, response: str):
        message = f"{response}\r\n\r\n".encode("ascii")
        self._client_com.sendall(message)
