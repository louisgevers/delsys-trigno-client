import time
from delsys_trigno_client.client import TrignoClient

def run_client():
    client = TrignoClient(digital_server_ip="localhost") # Mocked server
    client.is_sensor_paired(1)
    client.close()

if __name__ == "__main__":
    run_client()