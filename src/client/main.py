import client
import gui

def main():
    connection = client.Client("127.0.0.1", 7766)
    app = gui.ClientGUI(connection)
    app.activate()

if __name__ == '__main__':
    main()