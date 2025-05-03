import client
import gui
from time import sleep
import threading


def main():
    finished = False
    app = gui.ClientGUI()

    def start_client():
        nonlocal finished
        while not finished:
            connection = client.Client("127.0.0.1", 6627)
            try:
                connection.connect()
            except Exception as e:
                print(f"could not connect to server: {e}")
                sleep(0.5)
                continue

            connection.start()

            connection.gui_callback = app
            app.client = connection
            connection.join()
            finished = app.exit
    threading.Thread(target=start_client, daemon=True).start()
    app.activate()


if __name__ == '__main__':
    main()
