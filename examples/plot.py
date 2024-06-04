import time
import matplotlib.pyplot as plt

from argparse import ArgumentParser, Namespace

from delsys_trigno_client import TrignoClient


def plot_readings(debug: bool, duration: float, ids: list[int]):
    client = TrignoClient(digital_server_ip="localhost") if debug else TrignoClient()
    
    print("Starting acquisition")
    client.start_acquisition()
    time.sleep(duration)
    print("Stopping acquisition")
    client.stop_acquisition()

    emg_data = client.get_readings_emg()
    for id in ids:
        plt.plot(emg_data[id - 1, :], label=f"sensor_{id}")
    plt.legend()
    plt.show()

    client.close()

def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-t", "--time", type=int, default=5)
    parser.add_argument("-i", "--ids",  type=int, nargs="+", default=(1, 2, 3))
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    plot_readings(args.debug, args.time, args.ids)
