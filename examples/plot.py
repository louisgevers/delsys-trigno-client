import time
import matplotlib.pyplot as plt

from argparse import ArgumentParser, Namespace

from delsys_trigno_client import TrignoClient


def plot_readings(debug: bool, duration: float, ids: list[int]):
    client = TrignoClient(digital_server_ip="localhost") if debug else TrignoClient()
    
    start = time.time()
    client.start_acquisition()
    delay = time.time() - start
    print(f"Started acquisition [{delay * 1_000:.2f}ms response time]")
    time.sleep(duration)
    elapsed = time.time() - start
    print(f"Stopping [{elapsed:.2f}s elapsed]")
    client.stop_acquisition()
    print(f"Stopped acquisition [{delay * 1_000:.2f}ms response time]")

    emg_data = client.get_readings_emg()
    for id in ids:
        plt.plot(emg_data[0, :], emg_data[id, :], label=f"sensor_{id}")
    plt.xlabel("time [s]")
    plt.ylabel("EMG [mV]")
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
