import time
import pandas as pd

from delsys_trigno_client import TrignoClient


def run_client():
    client = TrignoClient(digital_server_ip="localhost")  # Mocked server
    client.pair_sensor(id=1)

    client.start_acquisition()
    time.sleep(3)
    client.stop_acquisition()

    readings = client.get_readings_emg()
    df = pd.DataFrame(readings.T)
    print(df.head())

    client.close()


if __name__ == "__main__":
    run_client()
