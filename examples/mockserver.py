from delsys_trigno_client.mock import MockDelsysStation


def run_mocked_server():
    server = MockDelsysStation()
    server.run()


if __name__ == "__main__":
    run_mocked_server()
