import time
from delsys_trigno_client.client import TrignoClient


def run_client():
    client = TrignoClient(digital_server_ip="localhost")  # Mocked server
    client.pair_sensor(id=1)

    client.start_acquisition()
    time.sleep(5)
    client.stop_acquisition()

    client.close()


if __name__ == "__main__":
    run_client()
