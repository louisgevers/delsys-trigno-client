import time
import pandas as pd

from argparse import ArgumentParser, Namespace

from delsys_trigno_client import TrignoClient


def run_client(debug: bool, duration: float):
    client = TrignoClient(digital_server_ip="localhost") if debug else TrignoClient()
    client.pair_sensor(id=1)

    client.start_acquisition()
    time.sleep(duration)
    client.stop_acquisition()

    readings = client.get_readings_emg()
    df = pd.DataFrame(readings.T)
    print(df.head())

    client.close()

def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-t", "--time", type=int, default=5)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_client(args.debug, args.time)
